from flask import Flask, request, jsonify
import os
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Load OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Google Sheets setup
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'path/to/credentials.json'  # Replace with the actual path to your credentials file

def get_google_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open('MidasBot Leads').sheet1  # Replace with your Google Sheet name
    return sheet

@app.route('/')
def home():
    return "MidasBot Backend is Running!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')

    try:
        # Call OpenAI GPT-3.5 API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Midas Cosmetic Surgery Clinic."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )

        bot_reply = response['choices'][0]['message']['content']
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "Sorry, I am having trouble processing your request. Please try again later."}), 500

@app.route('/lead', methods=['POST'])
def capture_lead():
    data = request.json
    name = data.get('name')
    contact = data.get('contact')
    treatment = data.get('treatment')

    if not name or not contact or not treatment:
        return jsonify({"error": "Missing required fields."}), 400

    try:
        sheet = get_google_sheet()
        sheet.append_row([name, contact, treatment])
        return jsonify({"message": "Lead captured successfully."}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to capture lead."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)