import sqlite3
from datetime import datetime

def create_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            joined_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            file_unique_id TEXT,
            file_size INTEGER,
            width INTEGER,
            height INTEGER,
            uploaded_at TEXT
        )
    ''')

    conn.commit()
    conn.close()

def save_user(user):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, joined_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        user.id,
        user.username,
        user.first_name,
        user.last_name,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def save_image(user_id, photo):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO images (user_id, file_id, file_unique_id, file_size, width, height, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        photo.file_id,
        photo.file_unique_id,
        photo.file_size,
        photo.width,
        photo.height,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
