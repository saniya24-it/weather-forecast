import sqlite3

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "smart_weather.db")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# USERS (login + signup)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
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
print("Database initialized successfully!")
