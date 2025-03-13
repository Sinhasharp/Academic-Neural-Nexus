import sqlite3

DB_NAME = "classroom.db"

# Initialize the database and create required tables
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create the users table (for login system)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create the feedback table (for student feedback)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    # Insert default login credentials (if not exists)
    users = [
        ("Harshil", "Harshil28"),
        ("Sarbojit", "Sarbojit62"),
        ("Suchi", "Suchi64"),
        ("Vaibhav", "Vaibhav92")  # Fixed Vaibhav's password
    ]

    for user in users:
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", user)

    conn.commit()
    conn.close()

# Save a new message in the feedback history
def save_feedback(sender, message):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (sender, message) VALUES (?, ?)", (sender, message))
        conn.commit()
    except Exception as e:
        print("Database Error:", e)
    finally:
        conn.close()

# Retrieve the last 10 messages from feedback history
def get_feedback_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT sender, message FROM feedback ORDER BY id DESC LIMIT 10")
        history = [{"sender": row[0], "message": row[1]} for row in cursor.fetchall()]
    except Exception as e:
        print("Error fetching feedback history:", e)
        history = []
    finally:
        conn.close()
    
    return history

# Validate login credentials
def validate_login(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
    except Exception as e:
        print("Login validation error:", e)
        user = None
    finally:
        conn.close()
    
    return user is not None  # Returns True if user exists, False otherwise

# Function to clear feedback history (for testing/reset)
def clear_feedback_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedback")  # Clears all feedback records
        conn.commit()
        print("Feedback history cleared successfully.")
    except Exception as e:
        print("Error clearing feedback history:", e)
    finally:
        conn.close()

# Run this once to initialize the database
init_db()
