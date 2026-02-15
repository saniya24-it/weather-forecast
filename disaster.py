from flask import Flask, jsonify
import requests
import sqlite3
from datetime import datetime

app = Flask(__name__)

API_KEY = "9a7b56b6f5b919658a75bca363637638"

# ------------------ DATABASE ------------------
conn = sqlite3.connect("smart_weather.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS disaster_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district TEXT,
    state TEXT,
    disaster TEXT,
    severity TEXT,
    temperature REAL,
    rainfall REAL,
    wind REAL,
    timestamp TEXT
)
""")
conn.commit()

# ------------------ DISTRICTS ------------------
DISTRICTS = [
    ("Mumbai", "Maharashtra", 19.07, 72.87),
    ("Pune", "Maharashtra", 18.52, 73.85),
    ("Nagpur", "Maharashtra", 21.14, 79.08),
    ("Delhi", "Delhi", 28.61, 77.21),
    ("Lucknow", "Uttar Pradesh", 26.85, 80.95),
    ("Kanpur", "Uttar Pradesh", 26.45, 80.35),
    ("Kolkata", "West Bengal", 22.57, 88.36),
    ("Howrah", "West Bengal", 22.59, 88.31),
    ("Chennai", "Tamil Nadu", 13.08, 80.27),
    ("Madurai", "Tamil Nadu", 9.93, 78.12),
    ("Bengaluru", "Karnataka", 12.97, 77.59),
    ("Mysuru", "Karnataka", 12.30, 76.65),
    ("Hyderabad", "Telangana", 17.38, 78.48),
    ("Warangal", "Telangana", 17.98, 79.60),
    ("Jaipur", "Rajasthan", 26.91, 75.78),
    ("Jodhpur", "Rajasthan", 26.23, 73.02),
    ("Ahmedabad", "Gujarat", 23.02, 72.57),
    ("Surat", "Gujarat", 21.17, 72.83),
    ("Bhopal", "Madhya Pradesh", 23.25, 77.41),
    ("Indore", "Madhya Pradesh", 22.72, 75.85)
]

# ------------------ DISASTER RULE ENGINE ------------------
def detect_disaster(weather):
    alerts = []

    temp = weather["temp"]
    rain = weather["rain"]
    wind = weather["wind"]
    pressure = weather["pressure"]
    visibility = weather["visibility"]

    if temp >= 42:
        alerts.append(("Heatwave", "Severe"))

    if rain >= 50:
        alerts.append(("Flood", "Severe"))

    if wind >= 20:
        alerts.append(("Cyclone / Storm", "High"))

    if visibility <= 1000:
        alerts.append(("Dense Fog", "Moderate"))

    if pressure <= 990:
        alerts.append(("Severe Weather", "Moderate"))

    return alerts

# ------------------ FETCH WEATHER ------------------
def fetch_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    r = requests.get(url).json()

    return {
        "temp": r["main"]["temp"],
        "pressure": r["main"]["pressure"],
        "wind": r["wind"]["speed"],
        "rain": r.get("rain", {}).get("1h", 0),
        "visibility": r.get("visibility", 10000)
    }

# ------------------ ALERT API ------------------
@app.route("/api/alerts")
def get_alerts():
    all_alerts = []

    for district, state, lat, lon in DISTRICTS:
        weather = fetch_weather(lat, lon)
        disasters = detect_disaster(weather)

        for d, severity in disasters:
            alert = {
                "district": district,
                "state": state,
                "lat": lat,
                "lon": lon,
                "disaster": d,
                "severity": severity,
                "time": datetime.now().strftime("%H:%M %d-%m-%Y")
            }

            all_alerts.append(alert)

            cur.execute("""
            INSERT INTO disaster_history 
            (district, state, disaster, severity, temperature, rainfall, wind, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                district, state, d, severity,
                weather["temp"], weather["rain"], weather["wind"],
                datetime.now().isoformat()
            ))
            conn.commit()

    return jsonify(all_alerts)

# ------------------ HISTORY API ------------------
@app.route("/api/history")
def history():
    cur.execute("SELECT district, state, disaster, severity, timestamp FROM disaster_history ORDER BY id DESC LIMIT 50")
    rows = cur.fetchall()

    return jsonify([
        {
            "district": r[0],
            "state": r[1],
            "disaster": r[2],
            "severity": r[3],
            "time": r[4]
        } for r in rows
    ])

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)

