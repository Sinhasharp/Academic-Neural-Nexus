from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from gemini_api import analyze_emotion, generate_reflection, create_report
from database import validate_login, validate_teacher_login, teacher_register, save_feedback, get_feedback_history
import re

app = Flask(__name__, template_folder='../frontend')
app.secret_key = "supersecretkey"  # Required for session handling

# Home - Redirect to Login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if validate_login(username, password):  # Student login validation
            session['user'] = username
            session['role'] = 'student'
            return redirect(url_for('student_dashboard'))
        elif validate_teacher_login(username, password):  # Teacher login validation
            session['user'] = username
            session['role'] = 'teacher'
            return redirect(url_for('teacher_dashboard'))
        else:
            flash("Invalid Credentials. Try Again.", "error")  # Flash error message
            return redirect(url_for('login'))

    return render_template('login.html')

# Student Dashboard
@app.route('/student')
def student_dashboard():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student.html')

# Teacher Dashboard
@app.route('/teacher')
def teacher_dashboard():
    if 'user' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher.html')

# Teacher Registration Route
@app.route('/teacher_register', methods=['POST'])
def teacher_register_route():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    # Validate email format
    if not validate_email(email):
        flash("Invalid email format. Please enter a valid email.", "error")
        return redirect(url_for('login'))  # Redirect to login after failed validation

    # Validate password strength
    if not validate_password(password):
        flash("Password must be at least 5 characters long and contain at least one number.", "error")
        return redirect(url_for('login'))  # Redirect to login after failed validation

    # Call the teacher_register function from database.py to save data
    if teacher_register(name, email, password):  
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))  # Redirect to the login page after successful registration
    else:
        flash("Username or email already exists. Try again.", "error")
        return redirect(url_for('login'))  # Redirect to login instead of returning JSON

# Function to validate email format using regex
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Function to validate password (minimum 5 characters and at least one number)
def validate_password(password):
    password_regex = r'^(?=.*\d).{5,}$'  # Ensures at least one number and 5 or more characters
    return re.match(password_regex, password) is not None

# Feedback Page
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_text = request.form.get('studentInput')

        if not student_text.strip():
            return jsonify({"error": "Empty feedback provided."})

        # Save feedback to the database
        save_feedback(session['user'], student_text)

        # AI Analysis Results
        emotion_result = analyze_emotion(student_text)
        reflection_result = generate_reflection(student_text)
        report_result = create_report(student_text)

        return jsonify({
            "student_text": student_text,
            "emotion_result": emotion_result,
            "reflection_result": reflection_result,
            "report_result": report_result
        })

    return render_template('feedback.html')

# API to fetch Chat History (For AJAX requests)
@app.route('/history')
def history():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized access"}), 403  # Return JSON error if not logged in

    # Get feedback history from the database
    feedback_history = get_feedback_history()

    # Return JSON response for frontend
    return jsonify(feedback_history)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
