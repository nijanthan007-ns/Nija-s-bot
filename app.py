
from flask import Flask, request
import requests

app = Flask(__name__)

ULTRAMSG_INSTANCE_ID = "133623"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"
ULTRAMSG_API_URL = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    try:
        if data.get("event_type") == "message_received":
            message = data["data"]["body"]
            sender = data["data"]["from"]

            # Send to Hugging Face (free endpoint)
            hf_response = requests.post(
                "https://huggingface.co/spaces/mys/phi2-api-demo/feature_extraction",
                headers={"Content-Type": "application/json"},
                json={"inputs": message},
                timeout=20,
            )

            if hf_response.status_code == 200:
                reply = hf_response.text.strip()[:1000]
            else:
                reply = "Sorry, the Hugging Face API returned an error."

            # Send reply via UltraMsg
            payload = {
                "token": ULTRAMSG_TOKEN,
                "to": sender,
                "body": reply,
            }
            resp = requests.post(ULTRAMSG_API_URL, data=payload)
            print("UltraMsg Response:", resp.status_code, resp.text)
    except Exception as e:
        print("Webhook error:", str(e))

    return "OK"
