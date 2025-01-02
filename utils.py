from dotenv import load_dotenv
from twilio.rest import Client
import os

load_dotenv()


def send_twilio_message(body, from_, to):
    try:
        twilio_client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
        twilio_client.messages.create(
            body = body,
            from_ = f"whatsapp:+{from_}",
            to = f"whatsapp:+{to}"
        )
        print("Respuesta Enviada:", body, sep='\n')
        return True
    
    except Exception as exc:
        print(f"Error al enviar el mensaje de Twilio: {str(exc)}")
        return False
    