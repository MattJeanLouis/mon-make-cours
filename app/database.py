import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "cours.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS cours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        theme TEXT NOT NULL,
        sommaire TEXT,
        fichier_path TEXT,
        status TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()