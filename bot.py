from flask import Flask, request
import requests
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Your credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'data' in data and len(data['data']) > 0:
        message = data['data'][0]
        text = message.get("body", "")
        phone_number = message["from"]

        if text:
            reply = get_openai_response(text)
            send_message(phone_number, reply)

    return "OK", 200

def get_openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-4 if allowed
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def send_message(to, message):
    url = os.getenv("ULTRAMSG_URL")
    token = os.getenv("ULTRAMSG_TOKEN")
    instance_id = os.getenv("ULTRAMSG_INSTANCE_ID")

    payload = {
        "to": to,
        "body": message,
        "priority": 10,
        "referenceId": "openai-whatsapp-bot"
    }

    headers = {
        "Content-Type": "application/json"
    }

    full_url = f"{url}/instance{instance_id}/messages/chat"
    requests.post(full_url, json=payload, headers=headers)

# ⚠️ REMOVE this if using Gunicorn (Render)
# if __name__ == "__main__":
#     app.run(debug=False)
