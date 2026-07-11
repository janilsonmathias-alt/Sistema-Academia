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
  
              
              
       
