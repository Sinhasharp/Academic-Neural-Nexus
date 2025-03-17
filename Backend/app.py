from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from gemini_api import analyze_emotion, generate_reflection, create_report
from database import (
    validate_login, validate_teacher_login, teacher_register, save_feedback, get_feedback_history,
    get_student_metrics, update_student_metrics, save_note, get_all_notes
)
import re
import io

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
            flash("Invalid Credentials. Try Again.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

# Student Dashboard
@app.route('/student')
def student_dashboard():
    if 'user' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    username = session['user']
    metrics = get_student_metrics(username)
    return render_template('student.html', gpa=metrics['gpa'], sgpa=metrics['sgpa'], attendance=metrics['attendance'])

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
    if not validate_email(email):
        flash("Invalid email format. Please enter a valid email.", "error")
        return redirect(url_for('login'))
    if not validate_password(password):
        flash("Password must be at least 5 characters long and contain at least one number.", "error")
        return redirect(url_for('login'))
    if teacher_register(name, email, password):
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    else:
        flash("Username or email already exists. Try again.", "error")
        return redirect(url_for('login'))

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_password(password):
    password_regex = r'^(?=.*\d).{5,}$'
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
        save_feedback(session['user'], student_text)
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

# API to fetch Chat History
@app.route('/history')
def history():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized access"}), 403
    feedback_history = get_feedback_history()
    return jsonify(feedback_history)

# Route for editing student metrics (Accessible by teacher)
@app.route('/edit_student_metrics', methods=['GET', 'POST'])
def edit_student_metrics():
    if 'user' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    if request.method == 'POST':
        student_username = request.form.get('student_username')
        gpa = request.form.get('gpa')
        sgpa = request.form.get('sgpa')
        attendance = request.form.get('attendance')
        try:
            gpa_val = float(gpa)
            sgpa_val = float(sgpa)
            attendance_val = int(attendance)
        except ValueError:
            flash("Invalid GPA or Attendance value.", "error")
            return redirect(url_for('edit_student_metrics'))
        if update_student_metrics(student_username, gpa_val, sgpa_val, attendance_val):
            flash("Student metrics updated successfully!", "success")
        else:
            flash("Error updating student metrics.", "error")
        return redirect(url_for('edit_student_metrics'))
    return render_template('edit_student_metrics.html')

# Route to render the file upload page (for teacher)
@app.route('/notes_upload', methods=['GET'])
def notes_upload_page():
    if 'user' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('notes_upload.html')

# New route: Upload note (for teacher file uploads)
@app.route('/upload_note', methods=['POST'])
def upload_note():
    if 'user' not in session or session.get('role') != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 403
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    allowed_extensions = ['pdf', 'doc', 'docx', 'txt', 'md']
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed_extensions:
        return jsonify({'error': 'File type not allowed'}), 400
    try:
        file_data = file.read()
        teacher_username = session['user']
        save_note(teacher_username, file.filename, file_data, file.content_type)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New route: Render notes arrangement page (accessible to all logged-in users)
@app.route('/notes_arrangement', methods=['GET'])
def notes_arrangement():
    if 'user' not in session:
        return redirect(url_for('login'))
    notes = get_all_notes()  # This function fetches all uploaded notes from the DB
    return render_template('notes_arrangement.html', notes=notes)


# New route: Download note by id
@app.route('/download_note/<int:note_id>')
def download_note(note_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT file_name, file_data, file_type FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            file_name, file_data, file_type = row
            # Ensure file_data is not empty and is in binary format
            return send_file(io.BytesIO(file_data),
                             download_name=file_name,
                             mimetype=file_type,
                             as_attachment=True)
        else:
            flash("Note not found.", "error")
            return redirect(url_for('notes_arrangement'))
    except Exception as e:
        flash("Error downloading note: " + str(e), "error")
        return redirect(url_for('notes_arrangement'))
# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
