"""Database connection and query functions."""
import sqlite3
from flask import g

def get_connection():
    """Open a database connection and enable foreign keys."""
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    """Execute a database command and store its last inserted ID."""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()

def last_insert_id():
    """Return the ID of the last inserted database row."""
    return g.last_insert_id

def query(sql, params=None):
    """Execute a database query and return all matching rows."""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
