import os
import psycopg2
from flask import Flask, request, jsonify


app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
  return psycopg2.connect(DATABASE_URL)

@app.route("/login.fcgi", methods=["POST"])
