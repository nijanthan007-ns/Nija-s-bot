import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = Flask(__name__)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")


def ask_openai(question):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": question}
            ]
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()

    except Exception as e:
        print("Error in OpenAI call:", e)
        return "Sorry, I couldn't process that."


def send_whatsapp_message(to, text):
    try:
        url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ULTRAMSG_TOKEN}"
        }

        payload = {
            "to": to,
            "body": text
        }

        response = requests.post(url, headers=headers, json=payload)
        print("UltraMsg Response:", response.status_code, response.text)
        return response.status_code == 200

    except Exception as e:
        print("Error sending message to WhatsApp:", e)
        return False


@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Chatbot is live!"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("Incoming webhook data:", data)

        msg = data.get("data", {})
        sender = msg.get("from")
        text = msg.get("body")

        print("Sender:", sender)
        print("Text:", text)

        if sender and text:
            reply = ask_openai(text)
            print("Reply:", reply)
            success = send_whatsapp_message(sender, reply)
            print("Message sent:", success)
        else:
            print("Missing sender or text.")

    except Exception as e:
        print("Error in /webhook:", e)

    return '', 200


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
