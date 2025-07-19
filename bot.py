from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp AI Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        
        # UltraMsg format
        messages = data.get("data", {}).get("messages", [])
        if not messages:
            return jsonify({"status": "ignored – no message"}), 200

        message = messages[0]
        sender = message.get("from")
        text = message.get("text", {}).get("body")

        if not sender or not text:
            return jsonify({"status": "ignored – incomplete message"}), 200

        # Send to OpenAI
        reply = get_openai_reply(text)

        # Send reply to WhatsApp
        send_whatsapp_message(sender, reply)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


def get_openai_reply(user_msg):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_msg}]
    }
    response = requests.post(url, json=payload, headers=headers)
    reply = response.json()["choices"][0]["message"]["content"]
    return reply.strip()


def send_whatsapp_message(to, text):
    url = "https://api.ultramsg.com/instance133623/"
    token = "shnmtd393b5963kq"
    payload = {
        "to": to,
        "body": text
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
