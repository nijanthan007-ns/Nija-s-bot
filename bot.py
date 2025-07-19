import os
from flask import Flask, request
import requests
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load secrets from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ULTRAMSG_API_URL = os.getenv("ULTRAMSG_API_URL")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

openai.api_key = OPENAI_API_KEY

@app.route('/')
def home():
    return "🤖 WhatsApp AI bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook received:", data)

    if not data or "data" not in data or not data["data"]:
        print("Invalid data format")
        return "Invalid", 400

    message = data["data"][0]
    text = message.get("body")
    sender = message.get("from")

    print(f"User said: {text}")

    if not text or not sender:
        print("Missing text or sender")
        return "Missing info", 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": text}]
        )
        reply = response.choices[0].message.content.strip()
        print(f"AI Reply: {reply}")

        # Send reply via UltraMsg
        send_url = f"{ULTRAMSG_API_URL}messages/chat"
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": sender,
            "body": reply
        }

        send_response = requests.post(send_url, data=payload)
        print("Send response:", send_response.text)

        return "OK", 200

    except Exception as e:
        print("Error:", e)
        return "Error", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
