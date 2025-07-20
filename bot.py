from flask import Flask, request
import requests

app = Flask(__name__)

# UltraMsg credentials
INSTANCE_ID = "133623"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"

# Hugging Face API URL (public and working)
HF_MODEL_URL = "https://hf.space/embed/mrm8488/t5-base-finetuned-question-generation-ap/+/api/predict"

def send_whatsapp_message(to, message):
    url = f"https://api.ultramsg.com/instance133623/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    try:
        response = requests.post(url, data=payload)
        print("UltraMsg Response:", response.status_code, response.text)
    except Exception as e:
        print("Error sending message:", str(e))

def ask_huggingface(prompt):
    try:
        res = requests.post(HF_MODEL_URL, json={"data": [prompt]}, timeout=30)
        res.raise_for_status()
        response = res.json()
        answer = response["data"][0]
        return answer.strip()
    except Exception as e:
        print("Error calling Hugging Face API:", str(e))
        return "Sorry, I couldn't process that."

@app.route("/")
def home():
    return "WhatsApp bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)
    try:
        if data["event_type"] == "message_received":
            msg_data = data["data"]
            sender = msg_data["from"]
            msg = msg_data["body"]

            # Ask HF
            reply = ask_huggingface(msg)
            send_whatsapp_message(sender, reply)
    except Exception as e:
        print("Webhook Error:", str(e))
    return "ok", 200

if __name__ == "__main__":
    app.run(debug=True)
