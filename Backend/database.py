import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash  # For hashing passwords

DB_NAME = "classroom.db"

# Initialize the database and create required tables
def init_db():
    try:
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

        # Create the student_metrics table for storing GPA and Attendance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_metrics (
                username TEXT PRIMARY KEY,
                gpa REAL,
                sgpa REAL,
                attendance INTEGER
            )
        ''')

        # Create the notes table for uploaded documents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_username TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_data BLOB NOT NULL,
                file_type TEXT,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert default login credentials (if not exists)
        users = [
            ("Harshil", "Harshil28"),
            ("Sarbojit", "Sarbojit62"),
            ("Suchi", "Suchi64"),
            ("Vaibhav", "Vaibhav93"),
            ("GDG", "GDG2025")  
        ]

        for user in users:
            # Hash the password before storing it in the database
            hashed_password = generate_password_hash(user[1])
            cursor.execute("INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)", (user[0], hashed_password))

        conn.commit()
    except Exception as e:
        print("Error during database initialization:", e)
    finally:
        conn.close()

# Save a new message in the feedback history
def save_feedback(sender, message):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (sender, message) VALUES (?, ?)", (sender, message))
        conn.commit()
    except Exception as e:
        print("Database Error in save_feedback:", e)
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

    if user and check_password_hash(user[2], password):  # user[2] holds the hashed password
        return True
    return False

# Register a new teacher (with hashed password)
def teacher_register(username, email, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO teachers (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print("Error: Username or Email already exists.")
        return False
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

    if teacher and check_password_hash(teacher[3], password):  # teacher[3] holds the hashed password
        return True
    return False

# Function to clear feedback history (for testing/reset)
def clear_feedback_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedback")
        conn.commit()
        print("Feedback history cleared successfully.")
    except Exception as e:
        print("Error clearing feedback history:", e)
    finally:
        conn.close()

# Get student metrics (GPA and attendance) for a given student
def get_student_metrics(username):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT gpa, sgpa, attendance FROM student_metrics WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return {"gpa": row[0], "sgpa": row[1], "attendance": row[2]}
        else:
            return {"gpa": 0.0, "sgpa": 0.0, "attendance": 0}
    except Exception as e:
        print("Error fetching student metrics:", e)
        return {"gpa": 0.0, "sgpa": 0.0, "attendance": 0}
    finally:
        conn.close()

# Update student metrics (GPA and attendance) for a given student
def update_student_metrics(username, gpa, sgpa, attendance):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_metrics WHERE username = ?", (username,))
        if cursor.fetchone():
            cursor.execute("UPDATE student_metrics SET gpa = ?, sgpa = ?, attendance = ? WHERE username = ?", (gpa, sgpa, attendance, username))
        else:
            cursor.execute("INSERT INTO student_metrics (username, gpa, sgpa, attendance) VALUES (?, ?, ?, ?)", (username, gpa, sgpa, attendance))
        conn.commit()
        return True
    except Exception as e:
        print("Error updating student metrics:", e)
        return False
    finally:
        conn.close()

# Save an uploaded note (document) into the database
def save_note(teacher_username, file_name, file_data, file_type):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (teacher_username, file_name, file_data, file_type) VALUES (?, ?, ?, ?)",
            (teacher_username, file_name, file_data, file_type)
        )
        conn.commit()
    except Exception as e:
        print("Error saving note:", e)
        raise e
    finally:
        conn.close()

# Retrieve all notes (for student download view)
def get_all_notes():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, teacher_username, file_name, upload_time FROM notes ORDER BY upload_time DESC")
        notes = [{"id": row[0], "teacher_username": row[1], "file_name": row[2], "upload_time": row[3]} for row in cursor.fetchall()]
    except Exception as e:
        print("Error fetching notes:", e)
        notes = []
    finally:
        conn.close()
    return notes

# Run this once to initialize the database
init_db()
