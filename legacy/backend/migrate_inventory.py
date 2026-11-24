"""Install the inventory schema. Optionally seed the named loopback rehearsal."""
import argparse
import os
from urllib.parse import urlsplit

from app.document_store import connect
from app.inventory import SCHEMA

CUSTOMERS = [
    ('bennett', 'Riley Bennett', 'Bennett, Riley', '312-555-0148', 'riley.bennett@example.com'),
    ('brooks', 'Casey Brooks', 'Brooks, Casey', None, None),
    ('ellis', 'Jordan Ellis', 'Ellis, Jordan', None, None),
    ('morgan', 'Alex Morgan', 'Morgan, Alex', None, None),
    ('parker', 'Jamie Parker', 'Parker, Jamie', None, None),
    ('reed', 'Taylor Reed', 'Reed, Taylor', None, None),
]
VEHICLES = [
    ('audi', 'bennett', '2021 Audi Q5', 'WA1BAAFY1M2000104'),
    ('subaru', 'bennett', '2024 Subaru Outback', None),
    ('escape', 'brooks', '2023 Ford Escape', None),
    ('mazda', 'ellis', '2022 Mazda CX-5', None),
    ('outback', 'morgan', '2022 Subaru Outback', None),
    ('rav4', 'parker', '2021 Toyota RAV4', None),
    ('crv', 'reed', '2020 Honda CR-V', None),
]
SETS = [
    ('rc-104', 'bennett', 'audi', 'Pirelli P Zero', '235/60R18', 'tire-wheel', 'A', 161, None, '247810', 'Black factory wheels', 'Inspect tire wear before next installation.', True, True, None),
    ('rc-105', 'bennett', 'audi', 'Nokian Hakkapeliitta', '235/60R18', 'tires', 'B, C', 175, None, '247790', None, None, None, None, None),
    ('rc-108', 'bennett', 'subaru', 'Michelin X-Ice Snow', '225/60R18', 'tire-wheel', 'D', 170, None, '248010', None, None, None, None, None),
    ('rc-110', 'bennett', None, 'Bridgestone Blizzak', '225/65R17', 'tires', None, 172, None, '248011', None, None, None, None, None),
    ('rc-112', 'brooks', 'escape', 'Nokian Hakkapeliitta', '225/60R18', 'tires', 'B', 130, None, '247812', None, None, None, None, None),
    ('rc-113', 'ellis', 'mazda', 'Michelin X-Ice Snow', '225/65R17', 'tires', 'C', 15, None, '247813', None, None, None, None, None),
    ('rc-114', 'morgan', 'outback', 'Michelin X-Ice Snow', '225/60R18', 'tire-wheel', 'A', 120, None, '247814', None, None, None, None, None),
    ('rc-115', 'parker', 'rav4', 'Bridgestone Blizzak', '225/65R17', 'tires', None, 25, None, '247815', None, None, None, None, None),
    ('rc-116', 'reed', 'crv', 'Continental VikingContact', '235/60R18', 'tire-wheel', 'D', -5, None, '247816', None, None, None, None, None),
    ('rc-117', 'reed', 'crv', 'Continental VikingContact', '235/60R18', 'tires', None, -60, -45, '247801', None, None, None, None, None),
]


def seed(connection):
    with connection.cursor() as cursor:
        cursor.executemany('INSERT INTO inventory_customers VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING', CUSTOMERS)
        cursor.executemany('INSERT INTO inventory_vehicles VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING', VEHICLES)
        cursor.executemany("""
            INSERT INTO inventory_sets (id, customer_id, vehicle_id, name, tire_size, kind,
                location, due_on, removed_on, work_order, wheels, notes, lug_nuts, center_caps, centering_rings)
            VALUES (%s,%s,%s,%s,%s,%s,%s,CURRENT_DATE + %s::int,CURRENT_DATE + %s::int,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, SETS)
        cursor.executemany("""
            INSERT INTO inventory_history VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, [
            ('bennett', '2026-11-01', 'RO 247810 · New storage'),
            ('bennett', '2026-10-30', 'RO 247790 · Renewal'),
            ('bennett', '2026-09-20', 'Vehicle reassignment · Preserved previous association'),
        ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed-rehearsal', action='store_true')
    args = parser.parse_args()
    if args.seed_rehearsal:
        url = urlsplit(os.environ.get('DATABASE_URL', ''))
        if (url.hostname, url.port, url.path) != ('127.0.0.1', 55439, '/rollcall_rehearsal'):
            parser.error('Synthetic seeding requires the disposable local Rollcall rehearsal database.')
    try:
        with connect() as connection:
            connection.execute(SCHEMA)
            if args.seed_rehearsal:
                seed(connection)
    except Exception:
        raise SystemExit('Inventory migration failed. Check database configuration and run the document migration first.') from None
    print('Inventory schema is ready.')


if __name__ == '__main__':
    main()
