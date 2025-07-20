import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

ULTRAMSG_URL = f"https://api.ultramsg.com/instance133623/messages/chat"

app = Flask(__name__)

@app.route("/")
def index():
    return "WhatsApp + Groq bot is live!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.get_json()
    print("Incoming:", incoming)

    if not incoming or "data" not in incoming:
        return jsonify({"error": "Invalid format"}), 400

    data = incoming["data"]
    sender = data.get("from")
    message_text = data.get("body")

    if not sender or not message_text:
        print("No sender or message found.")
        return jsonify({"status": "ignored"}), 200

    print(f"Message from {sender}: {message_text}")

    # Call Groq API
    try:
        groq_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message_text}
                ]
            }
        )
        groq_response.raise_for_status()
        reply = groq_response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Error in Groq call:", str(e))
        reply = "Sorry, I couldn't process that."

    print(f"Reply: {reply}")

    # Send message using UltraMsg
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": sender,
        "body": reply
    }
    try:
        response = requests.post(ULTRAMSG_URL, data=payload)
        print("UltraMsg Response:", response.status_code, response.text)
    except Exception as e:
        print("Error sending via UltraMsg:", str(e))

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

