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
    return generate_gemini_response(f"Act as a supportive and empathetic AI for students by offering tailored mental health guidance, constructive feedback on academic work, wellness strategies, and resource recommendations. Recognize and respond to various emotions expressed through text messages while respecting cultural nuances. Provide clear, respectful communication in both person and online settings, ensuring privacy and confidentiality. Offer support in crises with timely assistance and understanding of boundaries. Use a supportive tone to encourage self-compassion and long-term academic success, staying informed about available resources and best practices for student well-being. Also keep the responses short and precise unless asked otherwise.: {text}")

def generate_reflection(text):
    return generate_gemini_response(f"Provide metacognitive feedback for this response: {text}")

def create_report(text):
    return generate_gemini_response(f"Generate a parental engagement report based on this feedback: {text}")
