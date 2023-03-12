import os
import json
import bcrypt
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ESCRIBIR LA UBICACION DEL ARCHIVO JSON
path_file = os.path.join(BASE_DIR,'files\openAi_B.json')

menu={
    "resumen": "Summarize",
    "traductor": "Translater",
    "ensayo": "Assesment",
    "email": "Email",
    "reporte": "report",
    "ideas": "Ideas",   
}

def connect_to_database():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user=os.getenv("user_db"),
        password= os.getenv("password_db"),
        database= os.getenv("name_db")
    )
    c = conn.cursor()
    return c,conn

def get_user(username, password):
   
        c,conn = connect_to_database()
        c.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = c.fetchone()
        if user:
            # compare the entered password hash with the stored password hash
            if bcrypt.checkpw(password.encode('utf-8'), user[5].encode('utf-8')):
                return user
            else:
                return None
        conn.commit()
        
      
    

def create_user(username,email,phone,chat_id, password):
  
        # hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        c,conn = connect_to_database()
        c.execute("INSERT INTO users (username,email,phone,chat_id, password) VALUES (%s, %s,%s, %s, %s)", (username,email,phone,chat_id, hashed_password))
        result = c.fetchone()
        conn.commit()
        return result


def variables_chatgpt(option):
    variables_chatgpt="null"
    with open(path_file,encoding="utf-8") as json_file:
        data = json.load(json_file)
    if option in menu:
        if menu[option] in list(data[0].keys()):
            variables_chatgpt= data[0][menu[option]]
            print("opcion esta dentro de lista")  
    
    return variables_chatgpt  
    

    