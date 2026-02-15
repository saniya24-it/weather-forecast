from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
CORS(app)

DB_NAME = "smart_weather.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------- SIGNUP ---------------------------
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
        cursor.execute("""
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        """, (name, email, generate_password_hash(password)))

        conn.commit()
        return jsonify({"success": True})

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email ALREADY exists"})

    finally:
        conn.close()


# --------------------------- LOGIN ---------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()

    conn.close()

    if row:
        db_password = row["password"]
        if check_password_hash(db_password, password):
            return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Invalid email or password"}),  


# --------------------------- TEST ---------------------------
@app.route("/")
def home():
    return "Backend is running!", 200


if __name__ == "__main__":
    print("Backend running at: http://127.0.0.1:5000")
    app.run(debug=True)