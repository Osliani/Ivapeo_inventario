from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv('DATABASE_URL')
#MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client['wa_ivapeo']
threads_collection = db['threads']

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def create_thread(user_id):
    thread = openai_client.beta.threads.create()
    threads_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "thread_id": thread.id, 
            "interactions": 1, 
            "messages": []
        }},
        upsert=True
    )
    return thread.id


def update_thread(user_id, thread_id):
    threads_collection.update_one(
        {"user_id": user_id},
        {"$set": {"thread_id": thread_id}},
        upsert=True
    )
    
    
def update_chat(user_id, role, message, status = "NO_STATUS"):
    try:
        if role == "Assistant":
            new_message = {
                "role": role,
                "message": message,
                "status": status,
            }
        else:
            new_message = {
                "role": role,
                "message": message,
            }
            
        threads_collection.update_one(
            {"user_id": user_id},
            {"$push": {"messages": new_message}},
            upsert=True
        )
        return True
    
    except Exception as exc:
        print(f"Error actualizando chat: {exc}")
        return False
    

def get_chat(user_id):
    print("="*50, "Obteniendo Chats...", "="*50)
    
    thread = threads_collection.find_one({"user_id": user_id})
    if thread:
        chats = thread['messages']
        chats_str = ""
        
        for chat in chats:
            chats_str += f"{chat['role']}: {chat['message']} \n"
        
        print("Chats:", chats_str, sep="\n")
        return chats_str
    
    return False
    

def get_thread(user_id):
    thread = threads_collection.find_one({"user_id": user_id})
    if thread:
        interactions = int(thread["interactions"])
        threads_collection.update_one(
            {"user_id": user_id},
            {"$set": {"interactions": interactions + 1}},
            upsert=True
        )
        return thread["thread_id"]
    
    return None


def get_interactions(user_id):
    thread = threads_collection.find_one({"user_id": user_id})
    if thread:
        interactions = int(thread["interactions"])
        return interactions
    
    return 0