import os
import psycopg2
from flask import Flask, request, jsonify


app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
  return psycopg2.connect(DATABASE_URL)

@app.route("/login.fcgi", methods=["POST"])
def login():
  data = request.get_json()
  usuario = data.get("usuario")
  senha = data.get("senha")
  
if usuario == "admin" and senha == "admin123":
  token = "sessao_valida_token"
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute("""
    "INSERT INTO sessions (token, valid, validate) VALUES (%s, %s, NOW() + interval '1 hour')",
    (token, True)
  """)
  conn.commit()
  conn.close()
  return jsonify({"sessions" : token})
else:
  return jsonify({"error" : "Invalid credentials"}), 401


@app.rout("/session_is_valid.fcgi", methods = ["POST"])
def session_is_valid():
  

              
              
       
