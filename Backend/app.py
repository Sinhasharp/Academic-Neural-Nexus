from flask import Flask, render_template, request, jsonify
from gemini_api import analyze_emotion, generate_reflection, create_report

app = Flask(__name__, template_folder='../frontend')

@app.route('/')
def home():
    return render_template('feedback.html')

@app.route('/feedback', methods=['POST'])
def feedback():
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

if __name__ == '__main__':
    app.run(debug=True)
