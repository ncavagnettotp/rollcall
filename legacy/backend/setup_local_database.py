"""Run manually to create a dedicated local development login and database."""
from getpass import getpass
from pathlib import Path
import secrets
import sys
import psycopg
from psycopg import sql


def main():
    config = Path(__file__).with_name('.env')
    if config.exists():
        raise SystemExit('backend/.env already exists. No changes made; ask for help checking it.')
    if '--password-window' in sys.argv:
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        try:
            password = simpledialog.askstring(
                'PostgreSQL setup',
                'Enter the administrator password chosen during installation:',
                show='*', parent=root)
        finally:
            root.destroy()
        if password is None:
            raise SystemExit('Setup cancelled. No changes made.')
    else:
        password = getpass('PostgreSQL administrator password (hidden): ')
    app_password = secrets.token_hex(24)
    with psycopg.connect(host='127.0.0.1', port=5432, dbname='postgres',
                         user='postgres', password=password, connect_timeout=5,
                         autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'storage'")
            role_exists = cursor.fetchone() is not None
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'tire_storage'")
            if role_exists or cursor.fetchone() is not None:
                raise SystemExit('Login storage or database tire_storage already exists. No changes made; ask for help checking it.')
            cursor.execute(sql.SQL('CREATE ROLE storage LOGIN PASSWORD {}').format(sql.Literal(app_password)))
            cursor.execute('CREATE DATABASE tire_storage OWNER storage')
    # Exclusive creation prevents overwriting an existing project configuration.
    with config.open('x', encoding='utf-8') as output:
        output.write(f'DATABASE_URL=postgresql://storage:{app_password}@127.0.0.1:5432/tire_storage\n')
    with psycopg.connect(host='127.0.0.1', port=5432, dbname='tire_storage',
                         user='storage', password=app_password, connect_timeout=5) as conn:
        assert conn.execute('SELECT 1').fetchone() == (1,)
    print('PASS: project database created, backend/.env saved, database connection verified.')
    print('Restart the backend, then refresh the dashboard.')


if __name__ == '__main__':
    try:
        main()
    except psycopg.Error:
        raise SystemExit('Database setup failed. Check that PostgreSQL is running on port 5432 and the administrator password is correct. If retry reports existing objects, ask for help; do not delete them.') from None
