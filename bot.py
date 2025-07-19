from flask import Flask, request, jsonify
import requests
import openai
import os

# Load from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
ULTRAMSG_API_URL = os.environ.get("ULTRAMSG_API_URL")
ULTRAMSG_TOKEN = os.environ.get("ULTRAMSG_TOKEN")

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data and 'from' in data:
        phone_number = data['from']
        incoming_msg = data['message']

        # Get AI reply
        reply = chatgpt_response(incoming_msg)

        # Send reply to WhatsApp
        send_whatsapp_message(phone_number, reply)

    return jsonify({"status": "ok"})

def chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "Error: " + str(e)

def send_whatsapp_message(to, message):
    url = f"{ULTRAMSG_API_URL}messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    requests.post(url, data=payload)

if __name__ == '__main__':
    app.run()