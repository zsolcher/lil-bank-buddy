# db_utils.py
import sqlite3
from contextlib import contextmanager

DB_PATH = 'data/usaa_transactions.db'

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def execute_query(query, params=None):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params or [])
        conn.commit()
        return cur

def fetch_all(query, params=None):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params or [])
        return cur.fetchall()
