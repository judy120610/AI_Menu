import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
# Ensure .env is loaded from the current directory strictly
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def get_gemini_model():
    """Returns the configured Gemini model."""
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not found in environment.")
        return None
    try:
        # Using gemini-flash-latest as an alternative to 2.0-flash
        return genai.GenerativeModel('gemini-flash-latest')
    except Exception as e:
        print(f"Error initializing model: {e}")
        return None

def generate_menu_candidates(ingredients, requirements):
    """
    Generates 10 lunch menu candidates based on ingredients.
    Returns a list of 10 string items.
    """
    model = get_gemini_model()
    if not model:
        print("API Key missing or invalid.")
        return []

    prompt = f"""
    You are a professional chef.
    
    **Available Ingredients:** {', '.join(ingredients)}
    **Dietary Requirements:** {', '.join(requirements)}
    
    **Goal:** Create exactly 10 distinct lunch menu names.

    **CRITICAL INSTRUCTIONS:**
    1. **Ingredient Usage**: You MUST use the provided 'Available Ingredients' as the main components of the dishes. **Do NOT ignore the provided ingredients.** If 'pork' is selected, suggest pork dishes. If 'tofu' is selected, suggest tofu dishes.
    2. **Variety**: Avoid offering the same type of dish multiple times (e.g., do not suggest 3 kimchijjigae variants).
    3. **Cuisine Balance**: Mix Korean, Japanese, Chinese, and Western styles IF possible with the given ingredients.
    4. **Language**: Return ONLY the menu names in Korean.
    5. **Naming**: Just the menu name (e.g., "Kimchi Stew"), no descriptions.

    Return the result ONLY as a valid JSON object with the following structure:
    {{
        "candidates": ["Menu 1", "Menu 2", "Menu 3", ..., "Menu 10"]
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean up potential markdown formatting
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
        
        data = json.loads(text)
        return data.get("candidates", [])
    except Exception as e:
        print(f"Error generating candidates: {e}")
        return []

def generate_recipes(final_plan, ingredients):
    """
    Generates recipes for the selected weekly menu.
    """
    model = get_gemini_model()
    if not model:
        return {day: "API Key verifying... (Mock Recipe: Boil water, add stuff.)" for day in final_plan}

    plan_str = "\n".join([f"{day}: {menu}" for day, menu in final_plan.items()])
    
    prompt = f"""
    You are a professional chef.
    Here is the final weekly lunch plan:
    {plan_str}
    
    Available ingredients: {', '.join(ingredients)}
    
    Please provide a simple recipe for each dish.
    **IMPORTANT: Provide all text (ingredients and instructions) in Korean.**
    
    Format the output as a JSON object where keys are the days (월, 화, 수, 목, 금) and values are the recipe text (including ingredients needed and simple steps).
    
    Example JSON:
    {{
        "월": "**재료**: ...\n**조리법**: 1. ... 2. ...",
        ...
    }}
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
        return json.loads(text)
    except Exception as e:
        print(f"Error generating recipes: {e}")
        return None
