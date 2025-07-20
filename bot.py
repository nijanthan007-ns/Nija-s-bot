import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# UltraMsg details
INSTANCE_ID = "133623"
TOKEN = "shnmtd393b5963kq"

# Hugging Face free model (no key needed)
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

@app.route("/")
def home():
    return "WhatsApp AI Bot is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Incoming:", data)

        if not data or "data" not in data:
            return jsonify({"status": "no data"}), 400

        message_data = data["data"]
        msg_type = message_data.get("type")
        from_number = message_data.get("from")
        text = message_data.get("body", "")

        if msg_type != "chat" or not text:
            print("No text found or unsupported type.")
            return jsonify({"status": "ignored"}), 200

        # Get reply from Hugging Face
        reply = get_bot_reply(text)

        if not reply:
            reply = "Sorry, I couldn't process that."

        # Send reply via UltraMsg
        send_message(from_number, reply)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

def get_bot_reply(user_input):
    try:
        response = requests.post(
            HUGGINGFACE_API_URL,
            headers={"Content-Type": "application/json"},
            json={"inputs": user_input},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

        # Some models return full response as dict
        if isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]

        # Default fallback
        return result[0].get("generated_text", "I'm not sure.")
    except Exception as e:
        print("Error in Hugging Face API:", e)
        return None

def send_message(to_number, message):
    url = f"https://api.ultramsg.com/instance133623/messages/chat"
    payload = {
        "token": TOKEN,
        "to": to_number,
        "body": message,
    }
    response = requests.post(url, data=payload)
    print("UltraMsg Response:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

