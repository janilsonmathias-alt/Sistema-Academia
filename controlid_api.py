import requests

CONTROLID_IP = "192.168.0.100"
CONTROLID_PORTA = 80

URL = f"http://{CONTROLID_IP}:{CONTROLID_PORTA}"

def liberar_usuario(controlid_id):
  dados = {
    "users":[
      { 
        "id" : controlid_id,
        "registration_enable" : True
      }
    ]
  }
  
  r = requests.post(
    URL + "/user_set.cgi",
    json = dados,
    timeout = 10
  )

  return r.status_code == 200


def bloquear_usuario(controlid_id):
  dados = {
    "users":[
      {
        "id" : controlid_id,
        "registration_enable" : False
      }
    ]
  }

  r = requests.post(
    URL + "/user_set.cgi",
    json = dados,
    timeout = 10
  )

  return r.status_code == 200


