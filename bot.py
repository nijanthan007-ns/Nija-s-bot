import requests
from flask import Flask, request

# 🔐 Groq API Key (replace with your real one)
GROQ_API_KEY = "gsk_YOUR_GROQ_API_KEY_HERE"  # <-- Replace this

# 🌐 Groq API URL
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 📲 UltraMsg Configuration
ULTRAMSG_INSTANCE_ID = "instance133623"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"
ULTRAMSG_API_URL = f"https://api.ultramsg.com/instance133623/"

# 🚀 Flask app
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Incoming:", data)

    if not data or "data" not in data or not data["data"]:
        return "⚠️ Invalid payload", 400

    message = data["data"][0]
    text = message.get("body", "").strip()
    sender = message.get("from")

    if not text or not sender:
        return "⚠️ Missing sender or message text", 400

    # 🧠 Get AI response
    reply = get_groq_reply(text)
    print("🤖 Reply:", reply)

    # 📤 Send WhatsApp reply
    sent = send_whatsapp_message(sender, reply)
    return "✅ OK" if sent else "❌ Failed", 200

def get_groq_reply(user_input):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",  # You can also try llama3-70b-8192 if needed
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print("❌ Groq error:", e)
        return "Sorry, I couldn't process that."

def send_whatsapp_message(to, message):
    try:
        url = f"{ULTRAMSG_API_URL}messages/chat"
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": to,
            "body": message
        }
        response = requests.post(url, data=payload)
        print("📤 UltraMsg Response:", response.status_code, response.text)
        return response.status_code == 200
    except Exception as e:
        print("❌ UltraMsg Error:", e)
        return False

@app.route("/", methods=["GET"])
def home():
    return "✅ Groq WhatsApp Bot is Running!"

if __name__ == "__main__":
    app.run(debug=False, port=5000)

