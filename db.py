import psycopg2
import os
from pathlib import Path
 
 
def get_connection():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
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

         
