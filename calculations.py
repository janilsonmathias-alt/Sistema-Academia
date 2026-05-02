import calendar
from db import get_connection
from datetime import datetime

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
            SELECT id, data, faturamento, frequencia_alunos, observacao
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
            SELECT id, data, tipo, categoria, valor, observacao
            FROM despesas
            WHERE data LIKE %s
            ORDER BY data
        """, (prefixo + "%", ))

        
        #cur.execute("SELECT * FROM despesas")
    
        
        resultado = cur.fetchall()
        print(resultado)
        return resultado

def acomulado_ate_dia(ano: int, mes: int, dia: int) -> float:
    prefixo = f"{ano:04d}-{mes:02d}"

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(faturamento),0)
            FROM fechamentos_diarios
            WHERE data LIKE %s
            AND CAST(SUBSTRING(data, 9,2) AS INTEGER) <= %s
        """, (prefixo + "%", dia))
        return float(cur.fetchone()[0])


def ultimo_dia_do_mes(ano: int, mes: int) -> int:
    return calendar.monthrange(ano, mes)[1]


def fator_mes(ano:int, mes:int, dia:int) -> float:
    dia_efetivo = min(dia, ultimo_dia_do_mes(ano, mes))
    total = total_faturamento_mes(ano, mes)
    acomulado = acomulado_ate_dia(ano, mes, dia_efetivo)

    if acomulado == 0:
        return 0        
    return total/acomulado


def fator_medio(dia:int, ano_atual:int, mes_atual:int) -> float:
    fatores = []
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT SUBSTRING(data, 1, 7)
            FROM fechamentos_diarios
            WHERE data IS NOT NULL
            AND data <> ''
            AND LENGTH(data) >= 7 
            AND SUBSTRING(data, 1, 7) < %s
        """, (f"{ano_atual:04d}-{mes_atual:02d}",))
        meses = cur.fetchall()
    print("MESES ENCONTRADOS: ", meses)
    for m in meses:
        valor_mes = m[0]
        if not valor_mes or "-"  not in valor_mes:
            continue
            
    print("MES: ", valor_mes[0])
    print("FATURAMENTO: ", total_faturamento_mes(ano, mes))
    print("ACOMULADO: ", acomulado_ate_dia(ano, mes, dia) )    
    print("FATOR: ", fator_mes(ano, mes, dia))
        
        ano, mes = map(int, valor_mes.split("-"))
        f = fator_mes(ano, mes, dia)
        if f > 0:
            fatores.append(f)
    if not fatores:
        return 0

    return sum(fatores) / len(fatores)


def previsao_mes(ano:int, mes: int) -> dict:
    
    hoje = datetime.today()
    
    if ano == hoje.year and mes == hoje.month:
        dia = hoje.day
    else:
        dia = calendar.monthrange(ano, mes)[1]
        
    acomulado_atual = acomulado_ate_dia(ano, mes, dia)
    fator_atual = fator_medio(dia, ano, mes)

    previsao = acomulado_atual * fator_atual if fator_atual > 0 else 0

    return {
        "acomulado": acomulado_atual,
        "fator": fator_atual,
        "previsao": previsao
    }

















    

    
