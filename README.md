# Social-Engineering-Tool
Social engineering detection tool prototype which helps in detecting phishing attacks
Sure! Here's a refined, professional, and GitHub-optimized version of your `README.md` content for **GUARD MY CLICK** — structured for clarity, impact, and developer appeal:


# 🛡️ GUARD MY CLICK – AI Email Scanner

**GUARD MY CLICK** is a powerful, AI-driven phishing detection system built to proactively protect users from email-based threats. By combining **machine learning** and **fuzzy logic**, this tool performs real-time, automated Gmail inbox scanning to identify and alert users of suspicious or malicious URLs embedded in emails — all with a single click.

---

## 🔍 Key Highlights

### 📬 Automated Inbox Scanning

Seamlessly scans Gmail inboxes for potential phishing threats using ethical, secure access via the Gmail API.

### 🧠 AI-Powered Phishing Detection

Leverages a hybrid ML model to analyze email metadata and embedded URLs, offering real-time threat scoring.

### 🌀 Fuzzy Logic Heuristics

Detects disguised or obfuscated phishing URLs by applying smart, rule-based fuzzy logic evaluation.

### ⚖️ Risk Score Fusion

Combines ML and fuzzy logic scores to produce a comprehensive phishing risk assessment.

### 📊 Visual Threat Intelligence

Interactive radar charts, heatmaps, and visual breakdowns for every URL using Chart.js.

### 🚨 Real-Time Alerts

Receive browser notifications and optional email alerts when phishing activity is detected.

### 📄 One-Click PDF Reports

Generate downloadable summaries of scan results using jsPDF and html2canvas.

### 📱 Responsive Dark UI

Modern, mobile-friendly design built with Bootstrap 5 for a seamless experience across devices.

---

## 🛠 Tech Stack

**Frontend**

* HTML5, CSS3 (Bootstrap 5)
* JavaScript
* Chart.js (visualizations)
* jsPDF + html2canvas (PDF generation)

**Backend**

* Flask (Python Web Framework)
* REST API for email/URL processing
* Gmail API for inbox access

**AI/ML**

* Supervised ML model + Fuzzy Logic heuristics
* URL feature extraction and importance scoring

**Notifications**

* Web Push Notifications
* Email alerts via SMTP (with App Passwords)

---

## 🚀 How It Works

1. Click **"Start Ethical Scan"** on the web app.
2. Gmail API retrieves emails from your inbox.
3. URLs within each email are extracted.
4. Each URL is analyzed using:

   * ML-based phishing probability scoring
   * Fuzzy logic heuristics for obfuscation detection
5. A combined risk score is calculated and visualized.
6. Browser or email alerts are triggered if threats are found.
7. Users can view results in an interactive dashboard or download a PDF report.

---

## ✅ Prerequisites

* Python 3.8+
* pip
* Git
* Google Account (with Gmail access)
* Gmail App Password (if 2FA enabled)

---

## 🔧 Gmail API Setup

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create/select a project → **APIs & Services → Credentials**.
3. Click **Create Credentials → OAuth Client ID**.
4. Choose **Desktop App**, provide a name, and download the `credentials.json`.
5. Place `credentials.json` in the project root.
6. On first run, authenticate Gmail access and `token.json` will be auto-generated.

---

## 📦 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/RA2112701010026/Phishing-Link-Detection-Using-a-Hybrid-ML-Fuzzy-Logic-Model-Integrated-with-Gmail-API.git
cd Phishing-Link-Detection-Using-a-Hybrid-ML-Fuzzy-Logic-Model-Integrated-with-Gmail-API

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate         # macOS/Linux
venv\Scripts\activate            # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following keys:

```ini
SENDER_EMAIL=your_email@gmail.com
RECEIVER_EMAIL=receiver_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

> 💡 Note: If your Gmail uses 2FA, generate an App Password from your Google account settings.

---

## ▶️ Run the Application

```bash
# Ensure the virtual environment is activated
source venv/bin/activate        # or venv\Scripts\activate for Windows

# Start the Flask server
python app.py
```

Then, open your browser and visit:
📍 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 📣 Contribution & Feedback

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.
Feedback and ideas to improve the system’s detection capability are appreciated.

---

## ⭐ Acknowledgements

* Google Gmail API
* Scikit-learn
* Bootstrap & Chart.js
* jsPDF & html2canvas

