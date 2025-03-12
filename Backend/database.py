import sqlite3

DB_NAME = "users.db"

# Function to create the users table and insert initial users
def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Insert default users (only if they don't already exist)
    users = [
        ("Harshil", "Harshil28"),
        ("Sarbojit", "Sarbojit62"),
        ("Suchi", "Suchi64"),
        ("Vaibhav", "Vaibhav92")
    ]

    for user in users:
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", user)

    conn.commit()
    conn.close()

# Function to check login credentials
def validate_login(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()
    return user is not None  # Returns True if user exists, False otherwise

# Initialize database when script runs
if __name__ == "__main__":
    initialize_db()
    print("Database initialized successfully!")
