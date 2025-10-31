import sys, os, random, joblib, sklearn
import numpy as np
sys.path.append(os.path.abspath("YAFS/src"))
import csv
from datetime import datetime
import os

from collections import deque
from yafs.core import Sim
from yafs.topology import Topology
from yafs.application import Application
from yafs.distribution import deterministic_distribution
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "CLOUD")))
from cloud_upload import upload_data
from alert_system import send_alert_email


import warnings
warnings.filterwarnings("ignore", message="X does not have valid feature names")

vital_buffer = deque(maxlen=10)  # store last 10 readings

def log_result_to_csv(result_dict, filename="data/fog_results.csv"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    header = ["timestamp", "HR", "SpO2", "stress", "activity", "status"]

    result_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if f.tell() == 0:  # write header only once
            writer.writeheader()
        writer.writerow(result_dict)


# ----------------------------------------------------
# 1️⃣ Define Topology
# ----------------------------------------------------
topo = Topology()
topology_json = {
    "entity": [
        {"id": 0, "model": "CLOUD", "IPT": 4000, "RAM": 8000},
        {"id": 1, "model": "FOG",   "IPT": 1500, "RAM": 2000},
        {"id": 2, "model": "SENSOR"}
    ],
    "link": [
        {"s": 0, "d": 1, "BW": 1000, "PR": 2},
        {"s": 1, "d": 2, "BW": 1000, "PR": 1}
    ]
}
topo.load(topology_json)


# ----------------------------------------------------
# 2️⃣ Define Application
# ----------------------------------------------------
app = Application("FogHealthApp")
app.set_modules([
    {"Sensor":  {"Type": Application.TYPE_SOURCE, "RAM": 64, "IPT": 100}},
    {"FogNode": {"Type": Application.TYPE_MODULE, "RAM": 512, "IPT": 500}},
    {"Cloud":   {"Type": Application.TYPE_SINK,   "RAM": 1024, "IPT": 2000}}
])
app.add_service_module("Sensor", "FogNode",
                       {"name": "VitalsData", "Bytes": 2000, "Type": Application.TYPE_SOURCE})
app.add_service_module("FogNode", "Cloud",
                       {"name": "ProcessedData", "Bytes": 500, "Type": Application.TYPE_SINK})


# ----------------------------------------------------
# 3️⃣ Create Simulator
# ----------------------------------------------------
sim = Sim(topo)

# ----------------------------------------------------
# 4️⃣ Load ML Model (only once)
# ----------------------------------------------------
try:
    model_path = os.path.join("models", "fog_model_final.joblib")
    model_bundle = joblib.load(r"C:\Users\aniru\Desktop\fogcomputing_project\models\fog_model_final.joblib")
    scaler = model_bundle["scaler"]
    clf = model_bundle["clf"]
    iso = model_bundle["iso"]
    print("✅ ML model loaded successfully.")
except Exception as e:
    print("⚠️ Could not load ML model:", e)
    clf = None
    scaler = None
    iso = None


# ----------------------------------------------------
# 5️⃣ Define Event Logic with ML Inference
# ----------------------------------------------------
def sensor_process(env):
    """Sensor sends exactly 10 readings at 3s intervals."""
    reading_count = 0
    while reading_count < 10:
        yield env.timeout(3)
        hr = random.randint(55, 160)
        spo2 = random.randint(88, 100)
        stress = random.randint(1, 10)
        activity = random.randint(0, 100)
        reading_count += 1
        print(f"[{env.now:.1f}s] SENSOR → Reading {reading_count}/10 | HR={hr} | SpO₂={spo2} | Stress={stress} | Activity={activity}")
        vital_buffer.append([hr, spo2, stress, activity])

    # After collecting 10 readings, run ML inference once
    sim.env.process(fog_process(env))


# test_data = [
#     [82, 97, 4, 48],
#     [90, 96, 3, 60],
#     [85, 98, 4, 55],
#     [88, 97, 5, 52],
#     [93, 96, 4, 50],
#     [87, 98, 3, 58],
#     [91, 97, 4, 53],
#     [89, 95, 5, 47],
#     [84, 97, 4, 61],
#     [88, 96, 3, 56],
# ]

# def sensor_process(env):
#     """Sensor sends exactly 10 fixed normal readings."""
#     for i, (hr, spo2, stress, activity) in enumerate(test_data, start=1):
#         yield env.timeout(3)
#         print(f"[{env.now:.1f}s] SENSOR → Reading {i}/10 | HR={hr} | SpO₂={spo2} | Stress={stress} | Activity={activity}")
#         vital_buffer.append([hr, spo2, stress, activity])

#     # After collecting 10 readings, run ML inference once
#     sim.env.process(fog_process(env))


def fog_process(env):
    """Runs ML inference after collecting 10 readings."""
    yield env.timeout(1)

    if clf is None or scaler is None:
        print("⚠️ ML model not loaded. Skipping inference.")
        return

    try:
        if len(vital_buffer) == vital_buffer.maxlen:
            window_data = np.array(vital_buffer)
            scaled = scaler.transform(window_data)
            window_mean = scaled.mean(axis=0).reshape(1, -1)
            pred_class = clf.predict(window_mean)[0]


            # Optional isolation forest check
            iso_flag = iso.predict([scaled.mean(axis=0)])[0]

            alert = (pred_class == 1) or (iso_flag == -1)
            status = "⚠️ ANOMALY DETECTED" if alert else "Normal"
        else:
            status = f"Not enough data ({len(vital_buffer)}/{vital_buffer.maxlen})"

    except Exception as e:
        status = f"Error: {e}"

    # Use last reading for HR/SpO₂ logging
    last_hr, last_spo2, last_stress, last_activity = vital_buffer[-1]

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "HR": last_hr,
        "SpO2": last_spo2,
        "stress": last_stress,
        "activity": last_activity,
        "status": status
    }


    # Upload once to Firebase
    data_packet = {
        "heart_rate": last_hr,
        "spo2": last_spo2,
        "stress": last_stress,
        "activity": last_activity,
        "status": status
    }

    try:
        upload_data(data_packet)
        print(f"☁️ Uploaded to Firebase → {status}")
    except Exception as e:
        print(f"⚠️ Cloud upload failed: {e}")

    # --- Trigger alert if anomaly detected ---
    if "ANOMALY" in status:
        try:
            alert_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "heart_rate": last_hr,
                "spo2": last_spo2,
                "stress": last_stress,
                "activity": last_activity,
                "status": status
            }
            send_alert_email(alert_data)
        except Exception as e:
            print(f"⚠️ Failed to trigger alert: {e}")

    # Optionally, stop simulation after 10 readings
    # sim.env.exit()  # comment out if you want to continue


# Register the main processes
sim.env.process(sensor_process(sim.env))

# ----------------------------------------------------
# 6️⃣ Run Simulation
# ----------------------------------------------------
print("✅ Starting YAFS simulation with Fog ML Inference …")
sim.run(35)
print("✅ Simulation complete.")
