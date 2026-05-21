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
                data TEXT NOT NULL,
                faturamento NUMERIC NOT NULL,
                frequencia_alunos INTEGER NOT NULL,
                observacao TEXT
             )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS despesas(
                id SERIAL PRIMARY KEY,
               data TEXT NOT NULL,
               tipo TEXT NOT NULL,
               categoria TEXT NOT NULL,
               valor NUMERIC NOT NULL,
               observacao TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS alunos(
               id SERIAL PRIMARY KEY,
               nome TEXT NOT NULL,
               telefone TEXT NOT NULL,
               plano TEXT, 
               data_da_matricula TEXT,
               esta_ativo BOOLEAN
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS pagamentos_de_mensalidade(
               id SERIAL PRIMARY KEY,
               aluno_id INTEGER NOT NULL,
               data_pagamento TEXT NOT NULL,
               valor NUMERIC(10,2) NOT NULL,
               mes_referencia TEXT,
               observacao TEXT,
               FOREIGN KEY (aluno_id) REFERENCES alunos(id)
            )
        """)

        cur.execute("""
           ALTER TABLE despesas
           ADD COLUMN IF NOT EXISTS pago BOOLEAN NOT NULL DEFAULT FALSE
        """)
        
        conn.commit()
         

      
