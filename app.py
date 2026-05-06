from datetime import date
from calculations import previsao_mes, previsao_diaria
from flask import Flask, render_template, request, redirect
#from datetime import datetime
from db import init_db, get_connection
from calculations import(
                    total_faturamento_mes,
                    total_frequencia_mes,
                    total_despesas_mes,
                    lucro_mensal,
                    listar_fechamentos_mes,
                    listar_despesas_mes)
#import os

app = Flask(__name__)
init_db()

#def limpa_tela():
#    os.system('cls' if os.name == 'nt' else 'clear')

#def pausar():
#    input("\nPressione enter para continuar...")    

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/financeiro")
def financeiro():
    return render_template("financeiro.html")


@app.route("/alunos")
def alunos():
    return render_template("alunos.html")
    

@app.route("/alunos/novo", methods = ["GET", "POST"] )
def alunos_novo():
  if request.method == "POST":
    #id = request.form[""]
    nome = request.form["nome"]
    telefone = request.form["telefone"]
    plano = request.form["plano"]
    data_da_matricula = date.today().strftime("%Y-%m-%d")
    esta_ativo = request.form["esta_ativo"]

    with get_connection as conn:
      cur = conn.cursor()
      cur.execute("""
          INSERT INTO alunos( nome, telefone, plano, data_da_matricula, esta_ativo)
          VALUES(%s, %s, %s, %s, %s)
      """,(nome, telefone, plano, data_da_matricula, esta_ativo))
      conn.commit()
    return redirect("/alunos")
  return render_template("alunos_novo.html")
    
#idapp.route("/alunos/editar/<int:id>")
#def alunos_editar():

#@app.route("/alunos/excluir/<int:id>")
#def alunos_excluir():



  
@app.route("/fechamento", methods=["GET", "POST"])
def fechamento():
    if request.method == "POST":
        data = request.form["data"]
        faturamento = float(request.form["faturamento"])
        frequencia = int(request.form["frequencia"])
        observacao = request.form["observacao"]

        print("DATASALVA", data)
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO fechamentos_diarios (data, faturamento, frequencia_alunos, observacao)
                VALUES(%s, %s, %s, %s)
            """,(data, faturamento, frequencia, observacao))
            conn.commit()
            
            #vai copiar despesas fixa de mes anteriroe
            #caso nao tenha cadastro de despesa
            #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
            prefixo = request.form["data"]
            prefixo = prefixo[:7]

            cur.execute("""
                SELECT COUNT(*) 
                FROM despesas
                WHERE data::text LIKE %s
            """, (prefixo + '%',))
            
            despesa_virgem = cur.fetchone()[0]
            if (int(data[0:4]) == date.today().year and int(data[5:7]) == date.today().month and despesa_virgem == 0):
                mes_anterior = int(prefixo[5:7]) - 1
                if mes_anterior < 1:
                    mes_anterior = 12
                    prefixo = str(int(prefixo[:4]) - 1)
                prefixo = prefixo[:4] + '-' + f"{mes_anterior:02d}"
                
                cur.execute("""
                    INSERT INTO despesas(data, tipo, categoria, valor, observacao)
                    SELECT ((date_trunc('month', %s::date) + (data::date - date_trunc('month', data::date)))::date)::text, tipo, categoria, valor, observacao
                    FROM despesas
                    WHERE data::text LIKE %s                 
                """,(data, prefixo + '%', ))
                conn.commit()
            #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #WHERE data::text LIKE %s
            # é semelhante a ->>  if str(data) == %s
        return redirect("/financeiro")
    return render_template("fechamento.html")


@app.route("/despesa", methods=["GET", "POST"])
def despesa():
    if request.method == "POST":
        data = request.form["data"]
        tipo = request.form["tipo"]
        categoria = request.form["categoria"]
        valor = float(request.form["valor"])
        observacao = request.form["observacao"]

        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO despesas (data, tipo, categoria, valor, observacao)
                VALUES (%s, %s, %s, %s, %s)
            """,(data, tipo, categoria, valor, observacao))
            conn.commit()
        return redirect("/financeiro")
    return render_template("despesa.html")
        

@app.route("/resumo", methods=["GET", "POST"])
def resumo():
    lista_meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"] 
    if request.method == "POST":
        ano = int(request.form["ano"])
        mes = int(request.form["mes"])
        return redirect(f"/resumo?ano={ano}&mes={mes}")

    ano = request.args.get("ano")
    mes = request.args.get("mes")

    if ano and mes:
        ano = int(ano)
        mes = int(mes)

        hoje = date.today() #pega a data de hj

        #a preveisao sera feito sobre todos o s meses mas so sera mostrado quanto  o foco do resumo for 
        # o mes atual pq se nao da merda na previsao 
              
        dados = listar_fechamentos_mes(ano, mes)
        fechamentos = dados["lista"]
        ultimo_dia_da_lista = dados["ultimo_dia_da_lista"]
        faturamento_ultimo_dia_da_lista = dados["faturamento_ultimo_dia_da_lista"]
        ultimo_dia_da_lista = (ultimo_dia_da_lista == hoje.strftime("%Y-%m-%d"))
        despesas = listar_despesas_mes(ano, mes)
        previsao = previsao_mes(ano, mes)
        previsao_hoje = previsao_diaria(hoje.year, hoje.month, hoje.day)
        mes_atual = ( ano == hoje.year and mes == hoje.month )    # verifica se resumo sera sobre o mes atual   
        mes_em_foco_str = lista_meses[ mes - 1]
        return render_template("resumo.html",
                                fechamentos = fechamentos,
                                despesas = despesas,
                                faturamento = total_faturamento_mes(ano, mes),
                                frequencia = total_frequencia_mes(ano, mes),
                                despesas_total = total_despesas_mes(ano, mes),
                                lucro = lucro_mensal(ano, mes),
                                mes_em_foco_str = mes_em_foco_str, # leva a resposta se a previsao dsera sobre o mes ata
                                previsao = previsao["previsao"],
                                fator = previsao["fator"],
                                acomulado = previsao["acomulado"],
                                mes_atual = mes_atual,
                                ultimo_dia_da_lista_e_hj = ultimo_dia_da_lista,
                                faturamento_ultimo_dia_da_lista = faturamento_ultimo_dia_da_lista,
                                previsao_hoje = previsao_diaria(hoje.year, hoje.month, hoje.day))
      
    return render_template("resumo.html")
  
@app.route("/fechamento/editar/<int:id>", methods=["GET", "POST"])
def editar_fechamento(id):
  with get_connection() as conn:
    cur = conn.cursor()

    if request.method == "POST":
      data = request.form["data"]
      faturamento = float(request.form["faturamento"])
      frequencia = int(request.form["frequencia"])
      observacao = request.form["observacao"]

      cur.execute("""
          UPDATE fechamentos_diarios
          SET data = %s, faturamento = %s, frequencia_alunos = %s, observacao = %s
          WHERE id = %s
      """, (data, faturamento, frequencia, observacao, id))
      conn.commit()
      return redirect("/resumo")
      
    cur.execute("""
        SELECT id, data, faturamento, frequencia_alunos, observacao
        FROM fechamentos_diarios
        WHERE id = %s
    """, (id,))
    fechamento = cur.fetchone()

  return render_template("fechamento.html", fechamento = fechamento, form_action=f"/fechamento/editar/{id}")


@app.route("/despesa/editar/<int:id>", methods=["GET", "POST"])
def editar_despesa(id):
    with get_connection() as conn: 
        cur = conn.cursor()
        if request.method == "POST":
            data = request.form["data"]
            tipo = request.form["tipo"]
            categoria = request.form["categoria"]
            valor = float(request.form["valor"])
            observacao = request.form["observacao"]
            
            cur.execute("""
                UPDATE despesas
                SET data = %s, tipo = %s, categoria = %s, valor = %s, observacao = %s
                WHERE id = %s
            """, (data, tipo, categoria, valor, observacao, id))
            conn.commit()
            return redirect("/resumo")
            
        cur.execute("""
            SELECT id, data, tipo, categoria, valor, observacao
            FROM despesas
            WHERE id = %s
        """,(id,))
        despesa = cur.fetchone()
    return render_template(
        "despesa.html",
        despesa = despesa,
        form_action = f"/despesa/editar/{id}")
    

@app.route("/fechamento/excluir/<int:id>", methods = ["POST"])###
def excluir_fechamento(id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM fechamentos_diarios WHERE id = %s", (id,))
        conn.commit()
    return redirect("/resumo")

@app.route("/despesa/excluir/<int:id>", methods=["POST"])
def excluir_despesa(id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM despesas WHERE id = %s", (id,))
        conn.commit()
    return redirect("/resumo")
        

if __name__ == "__main__":



  
    app.run(debug = True, host="0.0.0.0")
