from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_NAME = "smart_weather.db"   # Use ONE database for all modules

# -------------------- CREATE TABLE IF NOT EXISTS --------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            event TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------- EVENT REGISTRATION API --------------------
@app.route("/api/event/register", methods=["POST"])
def register_event():
    try:
        data = request.json

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        event = data.get("event")
        date = data.get("date")

        # VALIDATION
        if not name or not email or not event or not date:
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        if phone and (not phone.isdigit() or len(phone) != 10):
            return jsonify({"success": False, "message": "Phone must be 10 digits"}), 400

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO event_registration (name, email, phone, event, date)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, phone, event, date))

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Event registered successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    print("🚀 Event Backend running at: http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
