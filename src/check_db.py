import psycopg
from psycopg.rows import dict_row

DB_URL = "postgresql://day6:day6_local_only@127.0.0.1:55433/day6_lab"
with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = [r['table_name'] for r in cur.fetchall()]
        print("Tables in public schema:", tables)
        for t in tables:
            cur.execute(f"SELECT count(*) FROM {t};")
            print(f" - {t}: {cur.fetchone()['count']} rows")
