import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
# Manually set your API key
API_KEY = "AIzaSyAwkueAB0Bfy-bJtwxDXI2rkgqfySk3xgI"


# Configure Gemini API
genai.configure(api_key=API_KEY)

def analyze_emotion(text):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(f"Analyze the emotional tone of this text and help the user overcome it. The steps should be very concise and precise. And also make sure that the user's requirements are fixed: {text}")
        return response.text.strip()
    except Exception as e:
        return f"Error analyzing emotion: {e}"

def generate_reflection(text):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(f"Provide metacognitive feedback for this response: {text}")
        return response.text.strip()
    except Exception as e:
        return f"Error generating reflection: {e}"

def create_report(text):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(f"Generate a parental engagement report based on this feedback: {text}")
        return response.text.strip()
    except Exception as e:
        return f"Error generating report: {e}"
