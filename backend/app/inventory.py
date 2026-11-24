"""PostgreSQL-backed inventory views and accessory updates."""
import re
from typing import Annotated, Literal

import psycopg
from psycopg import sql
from pydantic import BaseModel, StrictBool
from fastapi import APIRouter, HTTPException, Query

from .document_store import connect, StoreUnavailable

router = APIRouter(prefix='/api/inventory')

SCHEMA = """
CREATE TABLE IF NOT EXISTS inventory_customers (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, sort_name TEXT NOT NULL,
    phone TEXT, email TEXT
);
CREATE TABLE IF NOT EXISTS inventory_vehicles (
    id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES inventory_customers(id),
    description TEXT NOT NULL, vin TEXT,
    UNIQUE (customer_id, id)
);
CREATE TABLE IF NOT EXISTS inventory_sets (
    id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES inventory_customers(id),
    vehicle_id TEXT, name TEXT NOT NULL, tire_size TEXT,
    kind TEXT NOT NULL CHECK (kind IN ('tire-wheel', 'tires', 'wheels')),
    location TEXT, due_on DATE, removed_on DATE, work_order TEXT, wheels TEXT, notes TEXT,
    lug_nuts BOOLEAN, center_caps BOOLEAN, centering_rings BOOLEAN,
    document_id UUID REFERENCES storage_documents(id),
    FOREIGN KEY (customer_id, vehicle_id) REFERENCES inventory_vehicles(customer_id, id)
);
CREATE INDEX IF NOT EXISTS inventory_sets_customer ON inventory_sets(customer_id);
CREATE TABLE IF NOT EXISTS inventory_history (
    customer_id TEXT NOT NULL REFERENCES inventory_customers(id),
    occurred_on DATE NOT NULL, description TEXT NOT NULL,
    PRIMARY KEY (customer_id, occurred_on, description)
);
"""

SET_SELECT = """
SELECT s.*, c.name AS customer, c.sort_name, v.description AS vehicle, v.vin,
       CASE WHEN s.removed_on IS NOT NULL THEN 'Removed'
            WHEN s.due_on < CURRENT_DATE THEN 'Overdue'
            WHEN s.due_on <= CURRENT_DATE + 30 THEN 'Due soon'
            WHEN s.due_on IS NULL THEN 'Date unknown'
            ELSE 'Current' END AS status
FROM inventory_sets s
JOIN inventory_customers c ON c.id = s.customer_id
LEFT JOIN inventory_vehicles v ON v.id = s.vehicle_id
"""


def read(operation):
    try:
        with connect() as connection:
            connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY')
            return operation(connection)
    except (psycopg.Error, StoreUnavailable):
        raise HTTPException(503, 'Inventory is unavailable.') from None


@router.get('')
def list_sets(q: Annotated[str, Query(max_length=160)] = ''):
    query = q.strip().lower()
    size = re.sub(r'[^0-9]', '', query) if re.fullmatch(r'\d[\d/ .rx-]*', query) else ''

    def select(connection):
        counts = connection.execute("""
            SELECT count(*) FILTER (WHERE removed_on IS NULL) AS active,
                   count(*) FILTER (WHERE removed_on IS NULL AND due_on BETWEEN CURRENT_DATE AND CURRENT_DATE + 30) AS due,
                   count(*) FILTER (WHERE removed_on IS NULL AND due_on < CURRENT_DATE) AS overdue
            FROM inventory_sets
        """).fetchone()
        sets = connection.execute(SET_SELECT + """
            WHERE strpos(lower(concat_ws(' ', c.name, c.sort_name, v.description, v.vin,
                        s.name, s.tire_size, s.work_order)), %s) > 0
               OR (%s <> '' AND strpos(regexp_replace(s.tire_size, '[^0-9]', '', 'g'), %s) > 0)
            ORDER BY c.sort_name, s.id
        """, (query, size, size)).fetchall()
        return {'sets': sets, 'counts': counts}

    return read(select)


@router.get('/sets/{set_id}')
def set_detail(set_id: str):
    row = read(lambda conn: conn.execute(SET_SELECT + ' WHERE s.id = %s', (set_id,)).fetchone())
    if row is None:
        raise HTTPException(404, 'Stored set not found.')
    return row


@router.get('/customers/{customer_id}')
def customer_detail(customer_id: str):
    def select(connection):
        customer = connection.execute('SELECT * FROM inventory_customers WHERE id = %s', (customer_id,)).fetchone()
        if customer is None:
            raise HTTPException(404, 'Customer not found.')
        return {
            **customer,
            'vehicles': connection.execute('SELECT * FROM inventory_vehicles WHERE customer_id = %s ORDER BY description', (customer_id,)).fetchall(),
            'sets': connection.execute(SET_SELECT + ' WHERE s.customer_id = %s ORDER BY s.id', (customer_id,)).fetchall(),
            'history': connection.execute('SELECT occurred_on, description FROM inventory_history WHERE customer_id = %s ORDER BY occurred_on DESC, description', (customer_id,)).fetchall(),
        }

    return read(select)


class AccessoryChange(BaseModel):
    present: StrictBool


@router.patch('/sets/{set_id}/accessories/{accessory}')
def update_accessory(set_id: str, accessory: Literal['lug_nuts', 'center_caps', 'centering_rings'], change: AccessoryChange):
    try:
        with connect() as connection:
            row = connection.execute(
                sql.SQL('UPDATE inventory_sets SET {} = %s WHERE id = %s AND removed_on IS NULL RETURNING id')
                .format(sql.Identifier(accessory)), (change.present, set_id),
            ).fetchone()
    except (psycopg.Error, StoreUnavailable):
        raise HTTPException(503, 'Inventory is unavailable.') from None
    if row is None:
        raise HTTPException(404, 'Active stored set not found.')
    return {'present': change.present}
