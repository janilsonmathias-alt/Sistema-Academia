from db import get_connection


def total_faturamento_mes(ano: int, mes: int) -> float:
    prefixo = f"{ano:04d}-{mes:02d}"
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(faturamento),0)
            FROM fechamentos_diarios
            WHERE data LIKE %s
        """, (prefixo + "%",))
        return float(cur.fetchone()[0])

def total_despesas_mes(ano: int, mes: int) -> float:
    prefixo = f"{ano:04d}-{mes:02d}"
    
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(valor),0)
            FROM despesas
            WHERE data LIKE %s
        """, (prefixo + "%",))
        return float(cur.fetchone()[0])
    
def total_frequencia_mes(ano: int, mes: int) -> int:
    prefixo = f"{ano:04d}-{mes:02d}"
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(frequencia_alunos),0)
            FROM fechamentos_diarios
            WHERE data LIKE %s
        """, (prefixo + "%",))
        return int(cur.fetchone()[0])

def lucro_mensal(ano: int, mes: int) -> float:
    faturamento = total_faturamento_mes(ano, mes)
    despesas = total_despesas_mes(ano, mes)
    return faturamento - despesas

def listar_fechamentos_mes(ano: int, mes: int):
    prefixo = f"{ano:04d}-{mes:02d}"
    print("PREFIXO: ", prefixo)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT data, faturamento, frequencia_alunos, observacao
            FROM fechamentos_diarios
            WHERE data LIKE %s
            ORDER BY data
        """, (prefixo + "%", ))
        
        #cur.execute("SELECT * FROM fechamentos_diarios")
               
        resultado = cur.fetchall()
        print(resultado)
        return resultado
        
def listar_despesas_mes(ano: int, mes: int):
    prefixo = f"{ano:04d}-{mes:02d}"
    print("PREFIXO: ", prefixo)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT data, tipo, categoria, valor, observacao
            FROM despesas
            WHERE data LIKE %s
            ORDER BY data
        """, (prefixo + "%", ))

        
        #cur.execute("SELECT * FROM despesas")
    
        
        resultado = cur.fetchall()
        print(resultado)
        return resultado




















    

    
