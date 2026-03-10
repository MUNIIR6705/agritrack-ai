import google.generativeai as genai
from django.conf import settings

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_symptoms(symptoms, species):
    # Updated to Google's current active model name
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"As a veterinary expert, analyze these symptoms for a {species}: {symptoms}. Provide a possible diagnosis and recommended first-aid steps."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to AI: {str(e)}"