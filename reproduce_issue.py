
import os
from dotenv import load_dotenv
import google.generativeai as genai

print("--- Reproduction Test ---")
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY is not set in environment.")
else:
    print(f"API Key found: {api_key[:4]}... (length: {len(api_key)})")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("Model initialized: gemini-1.5-flash")
        
        ingredients = ["고등어", "무"]
        prompt = f"Create a menu with these ingredients: {ingredients}"
        
        print("Attempting generation...")
        response = model.generate_content(prompt)
        print("Generation successful.")
        print("Response text snippet:", response.text[:50])
        
    except Exception as e:
        print(f"EXCEPTION during generation: {e}")
