import psycopg

def probe_database(url: str) -> bool:
    # One bounded connection per health request; no implicit schema changes.
    with psycopg.connect(url, connect_timeout=3, options='-c statement_timeout=3000') as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
            return cursor.fetchone() == (1,)
