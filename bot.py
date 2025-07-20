import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# UltraMsg credentials from .env
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

# Hugging Face API
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_API_KEY = os.getenv("HF_API_KEY")

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

def query_huggingface(prompt):
    try:
        payload = {
            "inputs": f"User: {prompt}\nAssistant:",
            "parameters": {"max_new_tokens": 150, "return_full_text": False},
        }
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data[0]['generated_text'].strip() if isinstance(data, list) else "Sorry, I couldn't understand that."
    except Exception as e:
        print(f"Error in Hugging Face API: {e}")
        return "Sorry, I couldn't process that."

def send_whatsapp_message(to, message):
    url = f"https://api.ultramsg.com/instance133623/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    try:
        response = requests.post(url, data=payload)
        print(f"UltraMsg Response: {response.status_code} {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"UltraMsg Send Error: {e}")
        return False

@app.route('/')
def home():
    return "🤖 WhatsApp AI Chatbot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        msg_data = data.get("data", {})
        sender = msg_data.get("from")
        msg_text = msg_data.get("body")

        if not sender or not msg_text:
            print("Missing sender or message text.")
            return jsonify({"status": "ignored"}), 200

        reply = query_huggingface(msg_text)
        success = send_whatsapp_message(sender, reply)
        return jsonify({"status": "sent" if success else "failed"}), 200

    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

