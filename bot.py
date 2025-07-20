import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load credentials from environment
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

ULTRAMSG_URL = f"https://api.ultramsg.com/instance133623/messages/chat"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}


def ask_groq(message):
    try:
        payload = {
            "messages": [{"role": "user", "content": message}],
            "model": "llama3-8b-8192"
        }
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return reply.strip()
    except Exception as e:
        print("Error from Groq:", str(e))
        return "Sorry, I couldn't process that."


def send_whatsapp_reply(to, message):
    try:
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": to,
            "body": message
        }
        response = requests.post(ULTRAMSG_URL, data=payload)
        print("UltraMsg Response:", response.status_code, response.text)
        return response.status_code == 200
    except Exception as e:
        print("Error sending message to WhatsApp:", e)
        return False


@app.route('/')
def home():
    return "Groq WhatsApp Bot is running!"


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    try:
        if "body" in data and "text" in data["body"]:
            sender = data["body"]["from"]
            text = data["body"]["text"]

            print("Text:", text)
            reply = ask_groq(text)
            print("Reply:", reply)

            sent = send_whatsapp_reply(sender, reply)
            print("Message sent:", sent)
        else:
            print("No text found in request.")

    except Exception as e:
        print("Webhook error:", e)

    return jsonify({"status": "received"}), 200

