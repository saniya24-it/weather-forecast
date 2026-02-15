from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==========================================================
#  DB PATH (IMPORTANT – always correct file)
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "smart_weather.db")

def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
#  DATABASE INITIALIZATION
# ==========================================================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # FEEDBACK
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        message TEXT,
        rating INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # EVENT REGISTRATION
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_registration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        event TEXT,
        date TEXT
    )
    """)

    # DONATION HISTORY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        amount REAL,
        payment_id TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # WEATHER SEARCH HISTORY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        city TEXT,
        temperature TEXT,
        description TEXT,
        searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # DISASTER HISTORY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disaster_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        location TEXT,
        severity TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ==========================================================
#  SIGNUP
# ==========================================================
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400
    
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                       (name, email, generate_password_hash(password)))
        conn.commit()
        return jsonify({"success": True})
    except:
        return jsonify({"success": False, "message": "Email already exists"})
    finally:

        conn.close()


# ==========================================================
#  LOGIN
# ==========================================================
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()

    if row and check_password_hash(row[0], password):
        return jsonify({"success": True}), 200

    # ❗ FIX: Return status 401 so frontend can detect failure
    return jsonify({"success": False, "message": "Invalid credentials"}), 401
# ==========================================================
#  SAVE WEATHER SEARCH HISTORY
# ==========================================================
@app.route("/api/save-weather", methods=["POST"])
def save_weather():
    data = request.json
    email = data.get("email")
    city = data.get("city")
    temperature = data.get("temperature")
    description = data.get("description")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO weather_history (email, city, temperature, description) VALUES (?, ?, ?, ?)",
                   (email, city, temperature, description))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==========================================================
#  EVENT REGISTRATION
# ==========================================================
@app.route("/api/event/register", methods=["POST"])
def event_register():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO event_registration (name, email, phone, event, date)
        VALUES (?, ?, ?, ?, ?)
    """, (data["name"], data["email"], data["phone"], data["event"], data["date"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==========================================================
#  FEEDBACK
# ==========================================================
@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.json
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (name, email, message, rating)
        VALUES (?, ?, ?, ?)
    """, (data["name"], data["email"], data["message"], data["rating"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==========================================================
#  DONATION (Razorpay placeholder)
# ==========================================================
@app.route("/api/donate", methods=["POST"])
def donation():
    data = request.json
    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO donations (name, email, amount, payment_id, status)
        VALUES (?, ?, ?, ?, ?)
    """, (data["name"], data["email"], data["amount"], data["payment_id"], data["status"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==========================================================
#  DISASTER HISTORY
# ==========================================================
@app.route("/api/disaster/add", methods=["POST"])
def add_disaster():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO disaster_history (title, location, severity, time)
        VALUES (?, ?, ?, ?)
    """, (data["title"], data["location"], data["severity"], data["time"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# ==========================================================
#  SERVER START
# ==========================================================
if __name__ == "__main__":
    print(f"🚀 Backend running at: http://127.0.0.1:5000")
    print(f"📁 Database Path: {DB_PATH}")
    app.run(debug=True)