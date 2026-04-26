import sqlite3
from pathlib import Path
 
DB_PATH = Path("academia.db")
 
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fechamentos_diarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                faturamento REAL NOT NULL,
                frequencia_alunos INTEGER NOT NULL,
                observacao TEXT
             )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS despesas(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
               data TEXT NOT NULL,
               tipo TEXT NOT NULL,
               categoria TEXT NOT NULL,
               valor REAL NOT NULL,
               observacao TEXT
            )
        """)

         
