import os
import sqlite3
from typing import Optional
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", "/data/livraria.db")
INIT_SQL = os.environ.get("INIT_SQL", "/app/init.sql")

def get_connection():
    db_file = Path(DB_PATH)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER,
            preco REAL
        );
        """)
        conn.commit()
        init_file = Path(INIT_SQL)
        if init_file.exists():
            with open(init_file, "r", encoding="utf-8") as f:
                sql = f.read()
            conn.executescript(sql)
            conn.commit()
    finally:
        conn.close()
