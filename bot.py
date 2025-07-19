import requests
from flask import Flask, request

# Groq API Key (replace with your actual key securely if needed)
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# UltraMsg Configuration
ULTRAMSG_INSTANCE_ID = "instance133623"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"
ULTRAMSG_API_URL = "https://api.ultramsg.com/instance133623/"

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    if not data or "data" not in data or not data["data"]:
        return "No data", 400

    message = data["data"][0]
    text = message.get("body", "").strip()
    sender = message.get("from")

    if not text or not sender:
        return "Invalid message", 400

    # Get reply from Groq
    reply = get_groq_reply(text)
    print("Reply:", reply)

    # Send reply via WhatsApp
    send_whatsapp_message(sender, reply)
    return "OK", 200

def get_groq_reply(user_input):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7
        }

        res = requests.post(GROQ_API_URL, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("Groq error:", e)
        return "Sorry, I couldn't understand that."

def send_whatsapp_message(to, message):
    try:
        url = f"{ULTRAMSG_API_URL}messages/chat"
        payload = {
            "to": to,
            "body": message,
            "token": ULTRAMSG_TOKEN
        }
        res = requests.post(url, data=payload)
        print("UltraMsg Response:", res.status_code, res.text)
        return res.status_code == 200
    except Exception as e:
        print("UltraMsg Error:", e)
        return False

@app.route("/", methods=["GET"])
def home():
    return "Groq WhatsApp Bot is Live!"

if __name__ == "__main__":
    app.run(debug=False, port=5000)
