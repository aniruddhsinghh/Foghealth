import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail setup (use an App Password if 2FA is enabled)
SENDER_EMAIL = ""
APP_PASSWORD = ""  # generate from your Google Account
RECEIVER_EMAIL = ""

def send_alert_email(data):
    """
    Sends an email alert with sensor readings and timestamp.
    """
    subject = f"⚠️ Health Alert Detected at {data['timestamp']}"
    
    body = (
        f"🚨 Anomaly Detected in Smartwatch Data\n\n"
        f"Timestamp: {data['timestamp']}\n"
        f"Heart Rate: {data['heart_rate']} bpm\n"
        f"SpO₂: {data['spo2']} %\n"
        f"Stress Level: {data['stress']}\n"
        f"Activity Level: {data['activity']}\n"
        f"Status: {data['status']}\n\n"
        f"Please check the patient’s vitals immediately."
    )

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print(f"📨 Alert email sent successfully to {RECEIVER_EMAIL}")
    except Exception as e:
        print(f"⚠️ Failed to send alert email: {e}")
