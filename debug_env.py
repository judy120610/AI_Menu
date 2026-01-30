
import os
from dotenv import load_dotenv
import google.generativeai as genai

print("--- Debugging Environment ---")
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("Model initialized successfully (client-side).")
        response = model.generate_content("Hello, can you hear me?")
        print(f"Generation Test Success: {response.text}")
    except Exception as e:
        print(f"Error during generation: {e}")
else:
    print("API Key NOT found.")
