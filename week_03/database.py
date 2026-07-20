import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skillforge.db')

def get_db_connection():
    """Returns a connection to the SQLite database with row_factory enabled and foreign keys enforced."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(schema_sql_path):
    """Initializes the database using the schema SQL file."""
    conn = get_db_connection()
    with open(schema_sql_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries, or a single dictionary if one=True."""
    conn = get_db_connection()
    try:
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        cur.close()
    except Exception as e:
        conn.close()
        raise e
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Executes an INSERT, UPDATE, or DELETE query and returns the last inserted row ID."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        last_id = cur.lastrowid
        cur.close()
    except Exception as e:
        conn.close()
        raise e
    conn.close()
    return last_id