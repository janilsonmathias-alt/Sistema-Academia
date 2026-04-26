import psycopg2
import os
 
 
def get_connection():    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    return conn
                        
    
def init_db():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fechamentos_diarios (
                id SERIAL PRIMARY KEY,
                data DATE NOT NULL,
                faturamento NUMERIC NOT NULL,
                frequencia_alunos INTEGER NOT NULL,
                observacao TEXT
             )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS despesas(
                id SERIAL PRIMARY KEY,
               data DATE NOT NULL,
               tipo TEXT NOT NULL,
               categoria TEXT NOT NULL,
               valor NUMERIC NOT NULL,
               observacao TEXT
            )
        """)
    conn.commit()
         
