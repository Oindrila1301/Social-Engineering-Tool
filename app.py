from flask import Flask, request, render_template, jsonify
from featureExtractor import featureExtraction
from pycaret.classification import load_model, predict_model
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import base64
import re
import os
import json
import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)

# Gmail API Scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Load PyCaret Model
try:
    model = load_model('model/phishingdetection')
    print("✅ Phishing detection model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# --- Fuzzy Logic Setup ---
phishing_prob = ctrl.Antecedent(np.arange(0, 101, 1), 'phishing_prob')
url_length = ctrl.Antecedent(np.arange(0, 500, 1), 'url_length')
final_risk = ctrl.Consequent(np.arange(0, 101, 1), 'final_risk')

phishing_prob['low'] = fuzz.trimf(phishing_prob.universe, [0, 25, 50])
phishing_prob['medium'] = fuzz.trimf(phishing_prob.universe, [40, 60, 80])
phishing_prob['high'] = fuzz.trimf(phishing_prob.universe, [70, 90, 100])

url_length['short'] = fuzz.trimf(url_length.universe, [0, 40, 80])
url_length['medium'] = fuzz.trimf(url_length.universe, [60, 150, 250])
url_length['long'] = fuzz.trimf(url_length.universe, [200, 300, 500])

final_risk['low'] = fuzz.trimf(final_risk.universe, [0, 30, 50])
final_risk['medium'] = fuzz.trimf(final_risk.universe, [40, 60, 80])
final_risk['high'] = fuzz.trimf(final_risk.universe, [70, 90, 100])

rule1 = ctrl.Rule(phishing_prob['low'] & url_length['short'], final_risk['low'])
rule2 = ctrl.Rule(phishing_prob['medium'] & url_length['medium'], final_risk['medium'])
rule3 = ctrl.Rule(phishing_prob['high'] | url_length['long'], final_risk['high'])
rule4 = ctrl.Rule(phishing_prob['low'] & url_length['long'], final_risk['medium'])
rule5 = ctrl.Rule(phishing_prob['medium'] & url_length['short'], final_risk['low'])
rule6 = ctrl.Rule(phishing_prob['high'] & url_length['medium'], final_risk['high'])
rule7 = ctrl.Rule(phishing_prob['medium'] & url_length['long'], final_risk['high'])

risk_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
risk_simulation = ctrl.ControlSystemSimulation(risk_ctrl)

def get_status(score):
    if score < 55:
        return "SAFE"
    elif score < 75:
        return "SUSPICIOUS"
    else:
        return "PHISHING"

def predict(url):
    if model is None:
        return {'error': 'Model not loaded'}

    try:
        data = featureExtraction(url)
        result = predict_model(model, data=data)

        ml_score = round(result['prediction_score'][0] * 100, 2)
        ml_status = get_status(ml_score)
        url_len = min(len(url), 500)

        risk_simulation.input['phishing_prob'] = ml_score
        risk_simulation.input['url_length'] = url_len
        risk_simulation.compute()

        fuzzy_score = round(risk_simulation.output['final_risk'], 2)
        fuzzy_status = get_status(fuzzy_score)

        combined_score = round((ml_score * 0.6) + (fuzzy_score * 0.4), 2)
        combined_status = get_status(combined_score)

        return {
            'URL': url,
            'ML_Prediction_Score': ml_score,
            'ML_Status': ml_status,
            'Fuzzy_Risk_Score': fuzzy_score,
            'Fuzzy_Status': fuzzy_status,
            'Combined_Score': combined_score,
            'Combined_Status': combined_status,
            'Extracted_Features': data.to_dict(orient='records')[0]
        }

    except Exception as e:
        return {'error': f'Prediction failed: {e}', 'URL': url}

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token_file:
            token_data = json.load(token_file)
        if 'refresh_token' not in token_data:
            print("⚠️ Refresh token not found. Re-authentication required.")
            try:
                os.remove('token.json')
            except Exception as e:
                print(f"❌ Couldn't delete token.json: {e}")
                return None
        else:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=8080)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"❌ Gmail authentication failed: {e}")
            return None

    try:
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"❌ Failed to build Gmail service: {e}")
        return None

def extract_links(email_body):
    try:
        soup = BeautifulSoup(email_body, "html.parser")
        return list(set(re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", soup.get_text())))
    except Exception as e:
        print(f"⚠️ Error extracting links: {e}")
        return []

def decode_base64(data):
    try:
        if data:
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"⚠️ Base64 decode error: {e}")
    return ""

def send_email_alert(subject, content):
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        receiver_email = os.getenv("RECEIVER_EMAIL")
        password = os.getenv("EMAIL_PASSWORD")

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(content, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return True
    except Exception as e:
        print(f"❌ Email alert failed: {e}")
        return False

def scan_inbox():
    service = get_gmail_service()
    if not service:
        return [{'error': 'Gmail authentication failed'}]

    try:
        results = service.users().messages().list(userId='me', maxResults=8).execute()
        messages = results.get('messages', [])
    except Exception as e:
        return [{'error': f'Failed to retrieve emails: {e}'}]

    email_results = []

    for msg in messages:
        try:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg_data.get('payload', {})
            headers = payload.get('headers', [])
            parts = payload.get('parts', [])

            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')

            phishing_detected = False
            risky_links = []

            if parts:
                for part in parts:
                    if part.get('mimeType') == 'text/html' and part.get('body'):
                        body = decode_base64(part['body'].get('data', ''))
                        links = extract_links(body)

                        for link in links:
                            result = predict(link)
                            if result.get('Combined_Status') == 'PHISHING':
                                phishing_detected = True
                            risky_links.append(result)

            if phishing_detected:
                alert_subject = f"Phishing Alert: {subject}"
                alert_body = f"Sender: {sender}\nSubject: {subject}\n\nDetected phishing links:\n" + "\n".join(link['URL'] for link in risky_links if link['Combined_Status'] == 'PHISHING')
                send_email_alert(alert_subject, alert_body)

            email_results.append({
                'sender': sender,
                'subject': subject,
                'status': '⚠️ Phishing Detected' if phishing_detected else '✅ Safe',
                'risky_links': risky_links
            })

        except Exception as e:
            print(f"⚠️ Error processing email: {e}")
            email_results.append({
                'sender': 'Unknown',
                'subject': 'Error retrieving email',
                'status': '⚠️ Error',
                'risky_links': []
            })

    return email_results

@app.route("/", methods=["GET", "POST"])
def index():
    email_data = []
    if request.method == "POST":
        email_data = scan_inbox()
    return render_template("index.html", emails=email_data)

@app.route("/scan", methods=["POST"])
def scan():
    email_data = scan_inbox()
    return jsonify(email_data)

@app.route('/about.html')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)