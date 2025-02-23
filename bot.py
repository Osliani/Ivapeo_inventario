from flask import Flask, request
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from waitress import serve
from colorama import init, Fore, Style
import os, re
import mongo, utils
from assistant import Assistant

load_dotenv()

init(autoreset = True)


def crear_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    IVAPEO_ASSISTANT_ID = os.getenv("IVAPEO_ASSISTANT_ID")
    BOT_NUMBER = os.getenv("BOT_NUMBER")
    WORDS_LIMIT = 1599
    
    @app.route('/whatsapp', methods=['POST'])
    def whatsapp_reply():
        
        user_number = re.sub(r'^whatsapp:\+', '', request.values.get('From', ''))
        incoming_msg = request.form['Body'].strip()
        print(Fore.GREEN + f"- User {user_number}: " + Fore.LIGHTWHITE_EX + incoming_msg)
        
        thread_id = mongo.get_thread(user_number)
        
        if not thread_id:
            thread_id = mongo.create_thread(user_number)
            
        mongo.update_chat(user_number, "User", incoming_msg)
        
        try:
            TOOLS_API_URL = os.getenv('TOOLS_API_URL')
            if os.getenv('ENVIRONMENT') == 'dev':
                TOOLS_API_URL = "http://127.0.0.1:8000"

            jumo_bot = Assistant('IVAPEO_BOT', IVAPEO_ASSISTANT_ID, TOOLS_API_URL)
            ans, tools_called = jumo_bot.submit_message(incoming_msg, user_number, thread_id)
            print(Fore.BLUE + f"{tools_called}")
            
        except Exception as error:
            print(Fore.RED + f"Error: {error}")
            utils.send_twilio_message("Ha ocurrido un error. Por favor, realice la consulta más tarde.", BOT_NUMBER, user_number)
            return str(MessagingResponse())
        
        mongo.update_chat(user_number, "Assistant", ans, tools_called)
        
        if len(ans) > WORDS_LIMIT:
            print(Fore.YELLOW + "Respuesta recortada por exceder el límite de Twilio.")
            ans = ans[:WORDS_LIMIT]
            
        utils.send_twilio_message(ans, BOT_NUMBER, user_number)
        
        return str(MessagingResponse())
        
    return app


if __name__ == '__main__':
    app = crear_app()
    PORT = os.getenv('PORT')
    if os.getenv('ENVIRONMENT') == 'dev':
        print(Fore.YELLOW + "Ejecutando en entorno de desarrollo")

    print("Bot Online en el puerto " + Fore.BLUE + PORT)
    serve(app, host = "0.0.0.0", port = PORT)
    