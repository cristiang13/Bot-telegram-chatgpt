import os
import re
import telebot
import chatGpt
from telebot import types
from utils import utils
from telebot.types import ForceReply,ReplyKeyboardRemove
from mysql.connector import  IntegrityError
from dotenv import load_dotenv
load_dotenv()

bot= telebot.TeleBot(os.getenv("TOKEN"))
user = {}
variables={}

# responde al comando /start
@bot.message_handler(commands=["start"])
def start(message):

    # Envía un mensaje al usuario pidiéndole que inicie sesión con el teclado personalizado 
    bot.send_message(message.chat.id,"Por favor inicia sesión")
    # Se crea una teclado de respuesta obligatoria.
    markup = ForceReply()
    msg= bot.send_message(message.chat.id,"Ingresa tu nombre de usuario",reply_markup=markup)
    bot.register_next_step_handler(msg, into_password)
   
# responde al comando /close
@bot.message_handler(commands=["close"])
def close(message):
    print("function close")
    # Verifica si el ID de la conversación actual está en la lista de usuarios
    if message.chat.id in user:
        # Envía un mensaje al usuario preguntando si desea cerrar el chat
        msg= bot.send_message(message.chat.id,"desea cerrar el chat?")
        # Registra el siguiente controlador de pasos, que será la función "closeChat"
        bot.register_next_step_handler(msg, closeChat)
    else:
        # Si el ID de la conversación no está en la lista de usuarios, invoca la función "start"
        start(message)

# responde al comando /ejemplo
@bot.message_handler(commands=["ejemplo"])
def ejemplo(message):
    # Verifica si el ID de la conversación actual está en la lista de usuarios
    if message.chat.id in user:
        # Obtiene la pregunta y la respuesta de las variables asociadas al ID de la conversación
        question, answer = variables[message.chat.id]['variables']['ejemplo'].split("***") 
        # Envía la pregunta y repuesta ejemplo al usuario
        bot.send_message(message.chat.id, "Pregunta:\n "+question)
        bot.send_message(message.chat.id, "Respuesta:\n "+answer)


# Define la función  que se activa cuando el usuario envia /registrar
@bot.message_handler(commands=["registrar"])
def registrar(message):
    # Elimina el teclado personalizado anterior
    markup = ReplyKeyboardRemove()
    # Se crea una teclado de respuesta obligatoria.
    markup = ForceReply()
    bot.send_message(message.chat.id, "Bienvenido al chatbot")
    # Envía un mensaje al usuario pidiendo su nombre de usuario
    msg = bot.send_message(message.chat.id, "Ingresar nombre de usuario ", reply_markup=markup)
    bot.register_next_step_handler(msg, set_email)
    
# Este handler se ejecuta cuando el usuario envía un mensaje con uno de los textos "Traductor", "Resumen", "Ensayos", "Email", "Reporte" o "Ideas".          
@bot.message_handler(func=lambda message: message.text in ['/traductor', '/resumen', '/ensayo','/email','/reporte','/ideas'])
def handle_message(message):
    print(user)
    if message.chat.id in user:
        # Se llama a la función "variables_chatgpt" en el módulo "utils" para obtener las variables correspondientes al texto enviado por el usuario.
        print(message.text, "--",message.text.replace("/", ""))
        variables_chatgpt= utils.variables_chatgpt(message.text.replace("/", ""))
        #  Se almacenan las variables en un diccionario con la clave del ID del chat del usuario.
        variables[message.chat.id] = {}
        variables[message.chat.id]={}
        variables[message.chat.id]['variables']= variables_chatgpt
        # Se envía un mensaje al usuario con la descripción de la función correspondiente y una invitación a ver un ejemplo.
        bot.send_message(message.chat.id, variables_chatgpt['descripcion']+'. Deseas ver un ejemplo, presiona 👉 /ejemplo')
    else:
        # Si el usuario no está autorizado, se llama a la función "start" para iniciar el registro del usuario.
        start(message)

# Función que maneja los mensajes recibidos por el bot de Telegram         
@bot.message_handler(content_types=["text"])
def message_text(message):
    data = {}
    try:
        # Verifica si el ID del chat del usuario se encuentra en la lista de usuarios autorizados.
        if message.chat.id in user:
            # Almacenar el texto del mensaje en el diccionario de datos
            data['message']= message.text
           
            # Verificar si existen variables para la conversación actual
            if len(variables)>0: 
                print("con variables")
                # Almacenar las variables de los parametros del chatgpt en el diccionario de datos
                data['variables']=variables[message.chat.id]['variables']
                # Obtener la respuesta de ChatGpt
                textChatGpt= chatGpt.getResponseChatGpt(data)
                print("respuesta exitosa de chatgpt")
                # Eliminar las variables de la conversación actual
                del variables[message.chat.id]
            else:
                print("sin variables")
                # Obtener la respuesta de ChatGpt sin variables parametros por default
                textChatGpt= chatGpt.getResponseChatGpt(data)
            bot.send_message(message.chat.id,textChatGpt)
            
        # si el usuario no esta registrado se envia un mensaje y despliega el menu de inicio de sesion
        else:
            start(message)
    except ConnectionError as error_conection:
        print('An exception occurred of conection',error_conection)
    # En caso de error, notificar al usuario y solicitar que inicie sesión nuevamente
    except Exception as e:
            del user[message.chat.id]
            if len(variables)>0:
                del variables[message.chat.id] 
            bot.send_message(message.chat.id,"Ocurrio un error por favor vuelva a intentarlo presiona  👉 /start")
            start(message)
            print('An exception occurred en chatgpt',e)
   


# Función que permite al usuario ingresar contraseña para iniciar sesión.
def into_password(message):
    if validar(message):
        # Se agrega el ID del chat del usuario a la lista de usuarios.
        user[message.chat.id]={}
        # Se almacena el nombre del usuario en la lista de usuarios.
        name = re.sub(r'[^a-zA-Z0-9\s]', '', message.text)
        user[message.chat.id]['name']= name
        # Se crea una teclado de respuesta obligatoria.
        markup = ForceReply()
        # Se envía un mensaje al usuario solicitando su contraseña.
        msg = bot.send_message(message.chat.id, "ingresa tu contraseña",reply_markup=markup)
        # Se registra el siguiente manejador de eventos para la función de inicio de sesión.
        bot.register_next_step_handler(msg,login_user)

# Función que permite al usuario ingresar su  correo electrónico para registrarse.
def set_email(message):
    if validar(message):
        # Se agrega el ID del chat del usuario a la lista de usuarios.
        user[message.chat.id]={}
        # Se almacena el nombre del usuario en la lista de usuarios.
        
        name = re.sub(r'[^a-zA-Z0-9\s]', '', message.text)
        print(name)
        user[message.chat.id]['name']= name
        # Se crea un teclado de respuesta obligatoria.
        markup = ForceReply()
        # Se envía un mensaje al usuario solicitando su correo electrónico.
        msg = bot.send_message(message.chat.id, "ingresa correo electronico",reply_markup=markup)
        # Se registra el siguiente manejador de eventos para la función de establecimiento de contraseña.
        bot.register_next_step_handler(msg,set_num_tel) 

def set_num_tel(message):
    if validar(message):
        # Se almacena el correo electrónico del usuario en la lista de usuarios.
        user[message.chat.id]['email']= message.text
        # Se crea un teclado de respuesta obligatoria.
        markup = ForceReply()
        # Se envía un mensaje al usuario solicitando su correo electrónico.
        msg = bot.send_message(message.chat.id, "ingresa numero telefonico", reply_markup=markup)
        # Se registra el siguiente manejador de eventos para la función de establecimiento de contraseña.
        bot.register_next_step_handler(msg,set_password) 
        return None 

# Función que permite al usuario ingresar su contraseña durante el proceso de registro.
def set_password(message):
    if validar(message):
        # Se almacena el correo electrónico del usuario en la lista de usuarios.
        user[message.chat.id]['phone']= message.text
        # Se crea un teclado de respuesta obligatoria.
        markup = ForceReply()
        # Se envía un mensaje al usuario solicitando su contraseña.
        msg = bot.send_message(message.chat.id, "ingresa password",reply_markup=markup)
        # Se registra el siguiente manejador de eventos para la función de confirmación.
        bot.register_next_step_handler(msg, confirmation)

# Función que permite al usuario confirmar su información durante el proceso de registro.
def confirmation(message):
    if validar(message):
        # Se almacena la contraseña del usuario en la lista de usuarios.
        user[message.chat.id]['password']= message.text
        # Se crea un mensaje para confirmar la información ingresada por el usuario.
        text= f"Tu nombre es {user[message.chat.id]['name']}, tu correo es {user[message.chat.id]['email']} y tu password es {user[message.chat.id]['password']}. es correcto?"
        # Se envía el mensaje de confirmación al usuario.
        msg = bot.send_message(message.chat.id, text)
        # Se registra el siguiente manejador de eventos para la función de obtener opción.
        bot.register_next_step_handler(msg,get_option)

# Función para obtener la opción del usuario    
def get_option(message):
    print(message.text)
    if validar(message):
        # Verificar si la respuesta es "si"
        if message.text.lower() =='si' or message.text.lower() =='sí':
            # Llama a la función de registro
            register(message)
        else:
            # Eliminar al usuario de la lista
            del user[message.chat.id]
            # Enviar mensaje al usuario para que vuelva a ingresar los datos
            bot.send_message(message.chat.id, "Por favor vuelva a introducir los datos de nuevo presiona 👉 /start")  

# Función para iniciar sesión de usuario
def login_user(message):
  
    # Obtener el nombre de usuario y la contraseña del usuario
    username = user[message.chat.id]['name']
    password = message.text
    # Obtener al usuario de la base de datos
    user_db= utils.get_user(username,password)
    
    # Verificar si el usuario existe en la base de datos y si hay algún registro de él
    if user_db is not None and len(user_db) > 0:
        # Eliminar teclado personalizado
        markup = ReplyKeyboardRemove()
         # Enviar mensaje de bienvenida al usuario y mostrar opciones de menú
        msg= bot.send_message(message.chat.id, "Bienvenido en que te puedo ayudar.\nRecuerda \n❎  Cerrar  presiona  👉 /close. \n",reply_markup=markup)

    else:
        # Eliminar al usuario de la lista
        del user[message.chat.id]
        # Enviar mensaje de error al usuario para que vuelva a ingresar los datos
        bot.send_message(message.chat.id, "Usuario o Password incorrectos")
        bot.send_message(message.chat.id, "Para intentar de nuevo presiona  👉 /start")
        bot.send_message(message.chat.id, "Para registrarse presiona 👉 /registrar ")
      
# Función para registrar un nuevo usuario
def register(message):
    try:
        # Obtener el nombre de usuario, el correo electrónico, el ID de chat y la contraseña del usuario
        username = user[message.chat.id]['name']
        email = user[message.chat.id]['email']
        phone = user[message.chat.id]['phone']
        chat_id= str(message.chat.id)
        password = user[message.chat.id]['password']
    
        # Crear un nuevo usuario en la base de datos
        utils.create_user(username,email,phone,chat_id,password)
        # Eliminar al usuario de la lista
        del user[message.chat.id]
        # Enviar mensaje de éxito al usuario
        bot.send_message(message.chat.id,"Registro exitoso. Presiona  👉 /start")
    except IntegrityError as e:
        # Eliminar al usuario de la lista
        del user[message.chat.id]
        # Verificar si el error es debido a un correo electrónico repetido
        if e.errno == 1062:
            print("Error: Email already exists.")
            # Enviar mensaje de error al usuario para que ingrese un correo electrónico diferente
            bot.send_message(message.chat.id,"Email ya existe. Por favor ingresar datos nuevamente presiona  👉 /start")
        else:
            print(e)
            # Enviar mensaje de error al usuario para que vuelva a ingresar los datos
            bot.send_message(message.chat.id,"Ocurrio un error al registrar los datos.\n Por favor ingresar datos nuevamente. Presiona aqui 👉 /start")
    except Exception as error:
            print(error)
            # Eliminar al usuario de la lista
            del user[message.chat.id]
            # Enviar mensaje de error al usuario para que vuelva a ingresar los datos
            bot.send_message(message.chat.id,"Ocurrio un error al registrar los datos.\n Por favor ingresar datos nuevamente. Presiona aqui 👉 /start")
#  Función que cierra la sesión de chat actual.  
def closeChat(message):
     # Si el usuario responde 'si' o 'sí', se eliminan sus datos del diccionario 'user' y 'variables'
    if message.text.lower() =='si' or message.text.lower()=='sí':
        if len(user)>0:
             del user[message.chat.id]
        if len(variables)>0:
            del variables[message.chat.id] 
        # Se envía un mensaje al usuario confirmando que la sesión ha sido cerrada
        bot.send_message(message.chat.id,"Sesion cerrada, para abrir de nuevo presiona  👉 /start") 
    else:
        # Si el usuario responde con cualquier otra cosa, se envía un mensaje confirmando que el chat sigue activo 
        bot.send_message(message.chat.id,"Chat activo!") 

def validar(message):
    if message.text[0] == '/':
        if message.text == '/registrar':
           print("dentro de if: ",message.text)
           user.clear()
           registrar(message)
           
        elif message.text == '/start':
            user.clear()
            start(message)
        elif message.text == '/close':
            close(message)
        else:
           user.clear()
           bot.send_message(message.chat.id, "campo contiene caracter / . Presiona 👉 /start")
    else:
        return True
 
# Punto de inicio del programa.
if __name__ == '__main__':
    print("iniciando bot")
    # Se inicia el polling del bot para escuchar nuevos mensajes
    bot.infinity_polling()
    
