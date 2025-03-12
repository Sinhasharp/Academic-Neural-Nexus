import google.generativeai as genai

# Manually set your Gemini API Key here
API_KEY = "AIzaSyAwkueAB0Bfy-bJtwxDXI2rkgqfySk3xgI"

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Function to call Gemini AI
def generate_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "Error: No response from AI."
    
    except Exception as e:
        return f"Error communicating with Gemini API: {e}"

# Functions for AI feedback
def analyze_emotion(text):
    return generate_gemini_response(f"Analyze the emotional tone of this text: {text}")

def generate_reflection(text):
    return generate_gemini_response(f"Provide metacognitive feedback for this response: {text}")

def create_report(text):
    return generate_gemini_response(f"Generate a parental engagement report based on this feedback: {text}")
