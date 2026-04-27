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
            
        return redirect("/")
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
        return redirect("/")
    return render_template("despesa.html")
        

@app.route("/resumo", methods=["GET", "POST"])
def resumo():
    if request.method == "POST":
        ano = int(request.form["ano"])
        mes = int(request.form["mes"])
        return redirect(f"/resumo?ano={ano}&mes={mes}")

    ano = request.args.get("ano")
    mes = request.args.get("mes")

    if ano and mes:
        ano = int(ano)
        mes = int(mes)
        
        fechamentos = listar_fechamentos_mes(ano, mes)
        despesas = listar_despesas_mes(ano, mes)

              
        return render_template("resumo.html",
                               fechamentos = fechamentos,
                               despesas = despesas,
                               faturamento = total_faturamento_mes(ano, mes),
                               frequemcia = total_frequencia_mes(ano, mes),
                               despesas_total = total_despesas_mes(ano, mes),
                               lucro = lucro_mensal(ano, mes))
    
    return render_template("resumo.html")

if __name__ == "__main__":
    app.run(debug = True, host="0.0.0.0")

