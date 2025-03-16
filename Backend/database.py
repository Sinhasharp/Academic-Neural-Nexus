import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash  # For hashing passwords

DB_NAME = "classroom.db"

# Initialize the database and create required tables
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create the users table (for student login system)
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create the teachers table (for teacher login & registration)
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
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
        ("Vaibhav", "Vaibhav93")  # ✅ Updated Vaibhav's password
    ]

    for user in users:
        # Hashing the passwords before storing them in the database
        hashed_password = generate_password_hash(user[1])
        cursor.execute("INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)", (user[0], hashed_password))

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

# Validate student login credentials
def validate_login(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
    except Exception as e:
        print("Login validation error:", e)
        user = None
    finally:
        conn.close()

    if user and check_password_hash(user[2], password):  # Compare hashed password
        return True
    return False

# Register a new teacher (with hashed password)
def teacher_register(username, email, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        cursor.execute("INSERT INTO teachers (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        return True  # Registration successful
    except sqlite3.IntegrityError:
        print("Error: Username or Email already exists.")
        return False  # Registration failed (duplicate username/email)
    except Exception as e:
        print("Error registering teacher:", e)
        return False
    finally:
        conn.close()

# Validate teacher login credentials
def validate_teacher_login(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers WHERE username = ?", (username,))
        teacher = cursor.fetchone()
    except Exception as e:
        print("Teacher login validation error:", e)
        teacher = None
    finally:
        conn.close()

    if teacher and check_password_hash(teacher[3], password):  # Compare hashed password
        return True
    return False

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
