import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import time

# ------------------------------------------
# 1️⃣  Initialize Firebase Connection
# ------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(r"C:\Users\aniru\Desktop\fogcomputing_project\CLOUD\firebase_config.json")   # same file you used for cloud_upload.py
    firebase_admin.initialize_app(cred, {
        "databaseURL": ""
    })

# ------------------------------------------
# 2️⃣  Streamlit Page Setup
# ------------------------------------------
st.set_page_config(page_title="Fog–Cloud Health Dashboard", layout="wide")
st.title("☁️ Fog–Cloud Smartwatch Health Monitoring Dashboard")

refresh_rate = st.sidebar.slider("⏱️ Auto-refresh interval (seconds)", 5, 60, 10)

# ------------------------------------------
# 3️⃣  Function to fetch data from Firebase
# ------------------------------------------
def get_firebase_data():
    ref = db.reference("/health_data")
    data = ref.get()
    if not data:
        return pd.DataFrame(columns=["timestamp","heart_rate","spo2","stress","activity","status"])
    df = pd.DataFrame(data.values())
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.sort_values("timestamp", ascending=True, inplace=True)
    return df

# ------------------------------------------
# 4️⃣  Live Refresh Loop
# ------------------------------------------
placeholder = st.empty()

while True:
    df = get_firebase_data()
    with placeholder.container():
        if df.empty:
            st.info("Waiting for health data...")
        else:
            # Fill missing columns safely
            for col in ["heart_rate", "spo2", "stress", "activity", "status"]:
                if col not in df.columns:
                    df[col] = None

            latest = df.iloc[-1]

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("❤️ Heart Rate (bpm)", f"{latest.get('heart_rate', '—')}")
            col2.metric("🫁 SpO₂ (%)", f"{latest.get('spo2', '—')}")
            col3.metric("😌 Stress Level", f"{latest.get('stress', '—')}")
            col4.metric("🏃 Activity", f"{latest.get('activity', '—')}")
            status_text = latest.get('status', 'No Data')
            status_color = "🟢" if "Normal" in str(status_text) else "🔴"
            col5.metric("📊 Status", f"{status_color} {status_text}")

            st.markdown("---")
            st.subheader("📈 Heart Rate and SpO₂ Trends")
            st.line_chart(df.set_index("timestamp")[["heart_rate", "spo2"]])

            st.subheader("🧠 Stress and Activity Levels")
            if "stress" in df.columns and "activity" in df.columns:
                st.line_chart(df.set_index("timestamp")[["stress", "activity"]])

            st.subheader("🕒 All Recorded Readings")
            st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)

    time.sleep(refresh_rate)
