print("Loading chat_history...")
import sqlite3
from datetime import datetime

DB_NAME = "chat_history.db"


def initialize_database():
    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            timestamp TEXT NOT NULL

        )
    """)

    conn.commit()
    conn.close()


def save_message(role, content):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages(role, content, timestamp)
        VALUES (?, ?, ?)
        """,
        (
            role,
            content,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


def load_messages():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "role": row[0],
            "content": row[1]
        }
        for row in rows
    ]


def clear_messages():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM messages")

    conn.commit()

    conn.close()