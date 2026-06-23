from datetime import date as _date, datetime
from zoneinfo import ZoneInfo
from flask import Flask, render_template, request, redirect
#from datetime import datetime
from db import init_db, get_connection

from calculations import(
                    previsao_mes,
                    previsao_diaria,
                    total_faturamento_mes,
                    total_frequencia_mes,
                    total_despesas_mes,
                    lucro_mensal,
                    listar_fechamentos_mes,
                    listar_despesas_mes,
                    listar_alunos_cadastrados,
                    quadro_mensal,
                    comparativo_corte_atual_entre_meses,
                    buscar_aluno_por_id,
                    listar_pagamentos_do_aluno,
                    status_mensalidade_do_aluno
)


class date(_date):
  @classmethod
  def today(cls):
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()

def classe_dia_semana(mes_ano, dia):
  data = datetime.strptime(f"{mes_ano}-{int(dia):02d)}","%Y-%m-%d").date()
  classes = [
    "dow-seg", # segunda
    "dow-ter",
    "dow-quar",
    "dow-qui",
    "dow-sex",
    "dow-sab",
    "dow-dom",
  ]
  return classes[data.weekday()]


def buscar_pagamento_por_id(pagamento_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, aluno_id, data_pagamento, valor, mes_referencia, observacao
            FROM pagamentos_mensalidade
            WHERE id = %s
        """,(pagamento_id,))
        return cur.fetchone()

def ajustar_fechamento_por_data(data_referencia, delta_valor):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, faturamento
            FROM fechamentos_diarios
            WHERE data = %s
        """,(data_referencia,))
        fechamento = cur.fetchone()

        if fechamento:
            novo_faturamento = float(fechamento[1]) + float(delta_valor)

            cur.execute("""
                UPDATE fechamentos_diarios
                SET faturamento = %s
                WHERE id = %s
            """,(novo_faturamento, fechamento[0]))

        elif float(delta_valor) > 0:
            cur.execute("""
                INSERT INTO fechamentos_diarios
                (data, faturamento, frequencia_alunos, observacao)
                VALUES( %s, %s, %s, %s )
            """, (data_referencia, float(delta_valor), 0, "Mensalidade"))

            conn.commit()

            


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
    esta_ativo = "esta_ativo" in request.form

    with get_connection() as conn:
      cur = conn.cursor()  
      cur.execute("""
          INSERT INTO alunos( nome, telefone, plano, data_da_matricula, esta_ativo)
          VALUES(%s, %s, %s, %s, %s)
      """,(nome, telefone, plano, data_da_matricula, esta_ativo))
      conn.commit()
    return redirect("/alunos")
  return render_template(
    "alunos_novo.html",
    aluno = None,
    form_action = "/alunos/novo")


@app.route("/alunos/editar/<int:id>", methods = ["GET", "POST"])
def alunos_editar(id):
  with get_connection() as conn:
    cur = conn.cursor()

    if request.method == "POST":
      nome = request.form["nome"]
      telefone = request.form["telefone"]
      plano = request.form["plano"]
      esta_ativo = "esta_ativo" in request.form
          
      cur.execute("""
        UPDATE alunos
        SET nome = %s,
          telefone = %s,
          plano = %s,
          esta_ativo = %s
        WHERE id = %s
      """, (nome, telefone, plano, esta_ativo, id))
      conn.commit()

      return redirect(f"/alunos/ficha/{ id }")

    cur.execute("""
      SELECT id, nome, telefone, plano, data_da_matricula, esta_ativo
      FROM alunos
      WHERE id = %s
    """, (id,))
    aluno = cur.fetchone()

    if not aluno:
      return redirect("/alunos/listar_alunos_cadastrados/") 

    return render_template(
      "alunos_novo.html",
      aluno = aluno,
      form_action = f"/alunos/editar/{id}"
    )


#@app.route("/alunos/excluir/<int:id>")
#def alunos_excluir():

@app.route("/mensalidade/nova", methods=["GET", "POST"])
def mensalidade_nova():
  with get_connection() as conn:
    cur = conn.cursor()

    if request.method == "POST":
      aluno_id_str = request.form.get("aluno_id","").strip()
      if not aluno_id_str.isdigit():
        return "selecione um aluno valido na lista",400
                  
      aluno_id = int(aluno_id_str)
      data_pagamento = request.form["data_pagamento"]
      valor = float(request.form["valor"])
      mes_referencia = request.form["mes_referencia"]
      observacao = request.form.get("observacao","").strip()

      cur.execute("""
          SELECT nome
          FROM alunos
          WHERE id = %s
      """, (aluno_id,))
      aluno = cur.fetchone()
      nome_aluno = aluno[0] if aluno else "Aluno"

      cur.execute("""
          INSERT INTO pagamentos_mensalidade
          (aluno_id, data_pagamento, valor, mes_referencia,  observacao)
          VALUES(%s, %s, %s, %s, %s)          
      """, (
          aluno_id,
          data_pagamento,
          valor,
          mes_referencia,
          observacao
        ))

      cur.execute("""
          SELECT id, faturamento, frequencia_alunos, observacao
          FROM fechamentos_diarios
          WHERE data = %s
      """, (data_pagamento,))
      fechamento = cur.fetchone()
          
      texto_obs = f"Mensalidade: {nome_aluno}"
      if observacao:
          texto_obs += f" | {observacao}"

      if fechamento:
        obs_antiga = fechamento[3] or ""
        if obs_antiga:
          obs_final = obs_antiga + " | " + texto_obs
        else:
          obs_final = texto_obs
  
        cur.execute("""
            UPDATE fechamentos_diarios
            SET faturamento = faturamento + %s,
            observacao = %s
            WHERE id = %s
        """,(valor, obs_final, fechamento[0]))
      else:
        cur.execute("""
            INSERT INTO fechamentos_diarios
            (data, faturamento, frequencia_alunos, observacao)
            values( %s, %s, %s, %s )
            
        """,(data_pagamento, valor, 0, texto_obs))
      conn.commit()
      return redirect("/resumo")


    cur.execute("""
        SELECT id, nome, plano
        FROM alunos
        WHERE esta_ativo = TRUE
        ORDER BY nome
    """)
    alunos = cur.fetchall()

  hoje = date.today().strftime("%Y-%m-%d")
  competencia = date.today().strftime("%Y-%m")    

  return render_template(
        "mensalidade_nova.html",
        alunos = alunos,
        hoje = hoje,
        competencia = competencia
  )



@app.route("/alunos/ficha/<int:id>")
def ficha_aluno(id):
  aluno = buscar_aluno_por_id(id)
  if not aluno:
    return redirect("/alunos/listar_alunos_cadastados/")

  pagamentos = listar_pagamentos_do_aluno(id)
  hoje = date.today()
  status_atual = status_mensalidade_do_aluno(id, hoje)
  return render_template(
    "aluno_ficha.html",
    aluno = aluno,
    pagamentos = pagamentos,
    status_atual = status_atual
  )



@app.route("/mensalidade/editar/<int:id>", methods=[ "GET", "POST" ])
def editar_pagamento(id):
  pagamento = buscar_pagamento_por_id(id)

  if not pagamento:
    return redirect("/alunos/listar_alunos_cadastrados/")

  with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
      SELECT id, nome
      FROM alunos
      WHERE id = %s
    """,( pagamento[1],))
    aluno = cur.fetchone()

  if not aluno:
    return redirect("/alunos/listar_alunos_cadastrados/")

  if request.method == "POST":
    data_antiga = pagamento[2]
    valor_antigo = float(pagamento[3])

    nova_data = request.form["data_pagamento"]
    novo_valor = float(request.form["valor"])
    nova_competencia = request.form["mes_referencia"]
    nova_obs = request.form.get("observacao","").strip()


    cur.execute("""
      UPDATE pagamentos_mensalidade
      SET data_pagamento = %s,
          valor = %s,
          mes_referencia = %s,
          observacao = %s
      WHERE id = %s
    """,(nova_data, novo_valor, nova_competencia, nova_obs, id ))
        
    conn.commit()

    if data_antiga == nova_data:
      ajustar_fechamento_por_data(nova_data, novo_valor - valor_antigo)
    else:
      ajustar_fechamento_por_data(data_antiga, -valor_antigo)
      ajustar_fechamento_por_data(nova_data, novo_valor)

    return redirect(f"/alunos/ficha/{ aluno[0] }")

  return render_template(
    "mensalidade_editar.html",
    pagamento = pagamento,
    aluno = aluno,
    form_action = f"/me1nsalidade/editar/{id}"
  )


@app.route("/mensalidade/excluir/<int:id>", methods = ["POST"])
def excluir_pagamento(id):
  pagamento = buscar_pagamento_por_id(id)

  if not pagamento:
    return redirect("/alunos/listar_alunos_cadastrados/")

  ajustar_fechamento_por_data(pagamento[2], -float(pagamento[3]))

  with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
      DELETE FROM pagamentos_mensalidade
      WHERE id = %s      
    """,(id,))
    conn.commit()
  return redirect(f"/alunos/ficha/{pagamento[1]}")
  

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
        pago = request.form.get("pago") == "on"
      
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO despesas (data, tipo, categoria, valor, observacao, pago)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,(data, tipo, categoria, valor, observacao, pago))
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
        data_str = str(hoje)
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
        comparativo_corte_atual = comparativo_corte_atual_entre_meses(data_str)
        dados_quadro_mensal = quadro_mensal()
        return render_template("resumo.html",
                                dia = hoje.day,
                                meses = dados_quadro_mensal["meses"],
                                dias = dados_quadro_mensal["dias"],
                                quadro = dados_quadro_mensal["quadro"],
                                lista_resultado_dos_meses_corte_atual = comparativo_corte_atual,
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
                                previsao_hoje = previsao_diaria(hoje.year, hoje.month, hoje.day)),
                                classe_dia_semana = classe_dia_semana(mes_ano, dia)
    return render_template("resumo.html")





@app.route("/alunos/listar_alunos_cadastrados/", methods=["GET"])
def listar_alunos():
  lista_de_alunos_cadastrados = listar_alunos_cadastrados() 
  return render_template("lista_de_alunos_cadastrados.html",
                        lista = lista_de_alunos_cadastrados)


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
            pago = request.form.get("pago") == "on"
          
            cur.execute("""
                UPDATE despesas
                SET data = %s, tipo = %s, categoria = %s, valor = %s, observacao = %s, pago = %s
                WHERE id = %s
            """, (data, tipo, categoria, valor, observacao, pago, id))
            conn.commit()
            return redirect("/resumo")
            
        cur.execute("""
            SELECT id, data, tipo, categoria, valor, observacao, pago
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
