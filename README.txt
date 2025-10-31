🩺 FogHealth

A Hybrid Edge–Fog–Cloud Architecture for Real-Time Health Data Analysis

📘 Overview

This project implements a Fog–Cloud Computing System that connects a smartwatch (Titan) to a local fog node (laptop or smartphone) for real-time health monitoring.
The fog node receives vital signs such as heart rate (HR), SpO₂, and temperature from the smartwatch, performs lightweight machine learning inference locally to detect anomalies, and sends alerts if abnormal conditions are detected.
All processed and raw data are then uploaded to the cloud layer for storage, visualization, and further analytics.

🧠 Key Features

✅ Real-time Data Collection: Stream live data from Titan smartwatch (or use simulated data if unavailable).
✅ Fog Node Intelligence: Local ML model predicts health anomalies with low latency.
✅ Cloud Integration: Syncs all vitals and alerts to the cloud dashboard for long-term analysis.
✅ Alert System: Immediate alert is generated in case of anomalies (high HR, low SpO₂, etc.).
✅ Scalable Architecture: Easily extendable to multiple fog nodes or IoT devices.
✅ Visualization Dashboard: Built using Streamlit to show live data, alerts, and ML predictions.

🏗️ System Architecture
Smartwatch (Edge Device)
        ↓ (BLE/Wi-Fi)
Fog Node (Laptop / Phone)
        ↓ (Local ML Inference)
Cloud Layer (Server / Firebase / AWS)
        ↓
Dashboard & Reports (Streamlit)

🧩 Technologies Used
Layer	Tools & Technologies
Edge (Device)	Titan Smartwatch SDK, Simulated Sensors (Python)
Fog Layer	Python, YAFS (Yet Another Fog Simulator), Scikit-learn, MQTT/SocketIO
Cloud Layer	Firebase / AWS / Google Cloud Storage
Dashboard	Streamlit, Plotly, Pandas
ML Model	Logistic Regression / Random Forest (Anomaly Detection on vitals)


⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/<your-username>/fog-cloud-health-system.git
cd fog-cloud-health-system

2️⃣ Create Virtual Environment
python -m venv .venv
source .venv/bin/activate     # On Linux/Mac
.venv\Scripts\activate        # On Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Simulation (Fog Node)
python main_simulation.py

5️⃣ Run Dashboard
streamlit run dashboard_app.py



🧪 Example Output
✅ ML model loaded successfully.
✅ Starting YAFS simulation with Fog ML Inference …
----------------------------------------
DES     | TOPO  | Src.Mod       | Modules
----------------------------------------
[3.0s] SENSOR → HR=115 | SpO₂=94 | ALERT: HIGH HR DETECTED
[5.0s] SENSOR → HR=78 | SpO₂=98 | NORMAL



🧬 Machine Learning Model

The ML model is trained using historical health data to classify readings as:

🟢 Normal

🔴 Abnormal (Potential Health Risk)

Features include:

Heart Rate

SpO₂

Body Temperature

Time Window Average

The model is trained using Scikit-learn and saved as health_model.pkl.

☁️ Cloud Integration

Data from the fog node is periodically uploaded to a Firebase/Cloud Storage backend for:

Long-term storage

Analytics and visualization

User access via dashboard

Cloud also acts as a backup for missing or corrupted local data.

🧭 Novelty & Uniqueness

✨ Real-time Fog–Cloud Hybrid System using both live smartwatch feed and simulated backup data
✨ On-device ML inference to reduce latency and network dependency
✨ Dual operation mode — Offline (Fog-only) & Online (Fog+Cloud)
✨ Smart data handling — only anomalies are transmitted immediately to the cloud
✨ Streamlit-based live monitoring dashboard

📈 Future Enhancements

Integration with 5G-enabled IoT fog nodes

Enhanced predictive health analytics using LSTM models

Cloud-based API for doctor notifications

Multi-device interoperability (different smartwatch brands)

