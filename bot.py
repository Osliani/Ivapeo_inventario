from flask import Flask, request
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from waitress import serve
import os, re
import mongo, utils
from assistant import Assistant

load_dotenv()


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
        print(f"- User {user_number}: {incoming_msg}")
        
        thread_id = mongo.get_thread(user_number)
        
        if not thread_id:
            thread_id = mongo.create_thread(user_number)
            
        mongo.update_chat(user_number, "User", incoming_msg)
        
        try:
            jumo_bot = Assistant('IVAPEO_BOT', IVAPEO_ASSISTANT_ID, "http://127.0.0.1:8000")
            ans, status = jumo_bot.submit_message(incoming_msg, user_number, thread_id)
            print(status)
            
        except Exception as error:
            print(f"Error: {error}")
            utils.send_twilio_message("Ha ocurrido un error. Por favor, realice la consulta más tarde.", BOT_NUMBER, user_number)
            return str(MessagingResponse())
        
        mongo.update_chat(user_number, "Assistant", ans, status)
        
        if len(ans) > WORDS_LIMIT:
            print("Respuesta recortada por exceder el límite de Twilio.")
            ans = ans[:WORDS_LIMIT]
            
        utils.send_twilio_message(ans, BOT_NUMBER, user_number)
        
        return str(MessagingResponse())
        
    return app


if __name__ == '__main__':
    app = crear_app()
    print("Bot Online!")
    serve(app, host="0.0.0.0", port=3032)