from datetime import datetime
from db import get_connection
from calculations import status_mensalidade_do_aluno
from controlid_api import liberar_usuario
from controlid_api import bloquear_usuario



def atualizar_status_aluno(aluno_id):
  with get_connection() as conn:
    cur = conn.cursor()

    cur.execute("""

    """,)
    
