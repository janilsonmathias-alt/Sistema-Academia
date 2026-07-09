from datetime import datetime
from db import get_connection
from calculations import status_mensalidade_do_aluno
from controlid_api import liberar_usuario
from controlid_api import bloquear_usuario



def atualizar_status_aluno(aluno_id):
  with get_connection() as conn:
    cur = conn.cursor()
    
    cur.execute("""
      SELECT
        id,
        controlid_id,
        esta_ativo
      FROM alunos
      WHERE id=%s
    """, (aluno_id,))
    
    aluno = cur.fetchone()

  if not aluno:
    return

  controlid = aluno[1]

  if controlid is None:
    return

  hoje = datetime.today().date()

  status = status_mensalidade_do_aluno(aluno_id, hoje)

  ativo = status["status"] != "atrasado"

  with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
      UPDATE alunos
        SET esta_ativo=%s,
            ultimo_sync = NOW()

      WHERE id=%s
    """,(ativo, aluno_id))

    conn.commit()

    if ativo:
      liberar_usuario(controlid)

    else:
      bloquear_usuario(controlid)



def atualizar_todos_alunos():
  with get_connection() as conn:
    cur = conn.cursor()
    cur.execute("""
      SELECT id
      FROM alunos
    """)

    alunos = cur.fetchall()

  for aluno in alunos:
    atualizar_status_aluno(aluno[0])



