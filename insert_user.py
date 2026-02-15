from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash
import sqlite3

app = Flask(__name__)
from flask_cors import CORS

CORS(app, resources={r"/*": {"origins": "*"}})


DB_NAME = "smart_weather.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

import random
import time

# ============================
# SIMPLE IN-MEMORY OTP STORAGE
# ============================
otp_storage = {}  
# Example structure:
# otp_storage[email] = {"otp": "123456", "expires": 1710000000}

# ============================
# SEND OTP
# ============================
@app.route("/api/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    # Check if user exists
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Store OTP in memory with 5-minute expiry
    otp_storage[email] = {
        "otp": otp,
        "expires": time.time() + 300  # 5 minutes
    }

    print("OTP for", email, "=", otp)  # For testing; remove in production

    return jsonify({"message": "OTP sent to email"}), 200


# ============================
# VERIFY OTP + RESET PASSWORD
# ============================
@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("newPassword")

    if not email or not otp or not new_password:
        return jsonify({"message": "Missing required fields"}), 400

    # Check if OTP exists
    if email not in otp_storage:
        return jsonify({"message": "OTP not generated"}), 400

    record = otp_storage[email]

    # Check OTP expiration
    if time.time() > record["expires"]:
        del otp_storage[email]
        return jsonify({"message": "OTP expired"}), 400

    # Check OTP match
    if record["otp"] != otp:
        return jsonify({"message": "Invalid OTP"}), 400

    # OTP is correct → update password
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (generate_password_hash(new_password), email)
    )
    conn.commit()
    conn.close()

    # Remove OTP after success
    del otp_storage[email]

    return jsonify({"message": "Password updated successfully"}), 200



if __name__ == "__main__":
    print("🚀 Backend running on http://192.168.1.7:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
