import firebase_admin
from firebase_admin import credentials, db
import json
import time
from datetime import datetime

# Load credentials
cred = credentials.Certificate(r"C:\Users\aniru\Desktop\fogcomputing_project\CLOUD\firebase_config.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": ""
})

def upload_data(data):
    ref = db.reference("/health_data")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ref.push({
        "timestamp": timestamp,
        "heart_rate": data["heart_rate"],
        "spo2": data["spo2"],
        "activity": data["activity"],
        "stress": data["stress"],
        "status": data["status"]
    })
    print(f"✅ Uploaded data at {timestamp}")

