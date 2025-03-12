import os
from dotenv import load_dotenv  # Ensure .env loads properly
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from gemini_api import analyze_emotion, generate_reflection, create_report
from database import validate_login

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

        if validate_login(username, password):
            session['user'] = username
            return redirect(url_for('student_dashboard'))
        else:
            return "Invalid Credentials. Try Again."

    return render_template('login.html')

# Student Dashboard
@app.route('/student')
def student_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('student.html')

# Feedback Page
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        student_text = request.form.get('studentInput')

        if not student_text:
            return jsonify({"error": "Empty feedback provided."})

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

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
