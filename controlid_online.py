from flask import request, jsonify
from datetime import datetime
import secrets
from db import get_connection
from calculations import status_mensalidade_do_aluno



def registrar_rotas_controlid(app):
  @app.route("/login.cfgi", methods = ["POST"] )
  def controlid_login():
    dados = request.get_json(silent = True) or {}

    usuario = dados.get("login")
    senha = dados.get("password")

    token = secrets.token_hex(32)

    with get_connection() as conn:
      cur = conn.cursor()
      cur.execute("""
        CREATE TABLE IF NOT EXISTS controlid_sessions(
          token TEXT PRIMARY KEY,
          criado_em TIMESTAMP NOT NULL,
          valido BOOLEAN NOT NULL
        )        
      """)

    cur.execute("""
      INSERT INTO controlid_sessions
      (token, criado_em, valido)
      VALUES(%s, NOW(), True)      
    """,(token,))

    conn.commit()

  return jsonify({
    "session" : token
  })


@app.rout("/session_is_valid.fcgi", methods = ["POST"])
def session_is_valid():
  dados = request.get_json(silent = True) or {}
  token = dados.get("sessions")

  with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
      SELECT valido
      FROM controlid_sessions
      WHERE token = %s      
    """,(token,))
    r = cur.fetchone()

  return jsonify({
    "valid" : bool(r or r[0])
  })
  

@app.route("/user_identified.cfgi", methods = ["POST"])
def user_identified():
  dados = request.get_json(silent = True) or {}

  print("=====================================")
  print("         C O N T R O L  I D")
  print(dados)
  print("=====================================")

  controlid_id = dados.get("user_id")

  if controlid_id is None:
    return jsonify({
      "access" : "denied"
    })


  with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
      SELECT id
      FROM alunos
      WHERE controlid_id = %s
    """,(controlid_id,))

    aluno = cur.fetchone()
    
    if aluno is None:
      return jsonifY({
        "access" : "denied"
      })

    status = status_mensalidade_do_aluno(
      aluno[0],
      datetime.today().date()
    )

    permitido = status["status"] != "atrasado"

    cur.execute("""
      CREATE TABLE IF NOT EXISTS controlid_eventos(
        id SERIAL PRIMARY KEY,
        aluno_id INTEGER,
        controlid_id INTEGER,
        data_evento TIMESTAMP,
        payload JSONB,
        permitido BOOLEAN        
      )
    """)

    cur.exetuce("""
      INSERT INTO controlid_eventos
      (
        aluno_id,
        controlid_id,
        data_evento,
        payload,
        permitido
      )    
    VALUES
    (
      %s,
      %s,
      NOW(),
      %s,
      %s
    )
    """, (
      aluno[0],
      controlid_id,
      jsonify(dados).get_data(as_Text = True),
      permitido
    ))

    conn.commit()


  if permitido:
    return jsonify({
      "access" : "granted"
    })

  return jsonify({
    "access" : "denied"
  })
  


@app.route("/new_user_identified.cfgi", methods = ["POST"]
def new_user_identified():
  dados = request.get_json(silent = True) or {}

  print(dados)
  
  return jsonify({
    "status" : "registered"
  })



@app.route("/monitor.cfgi", methods = ["POST"])
def monitor():
  dados = request.get_json(silent = True) or {}

  print(dados)

  return jsonify({
    "ack" : True
  })


@app.route("/push.cfgi", methods = ["POST"])
def push():
  return jsonify({})


@app.route("/alarms.cfgi", methods = ["POST"])
def alarms():

  dados = request.get_json(silent = True) or {}

  print(dados)

  return jsonify({
    "ack" : True
  })


