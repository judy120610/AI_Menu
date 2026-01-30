import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Test 1: Fish ingredients
ingredients_1 = ["고등어", "무"]
prompt_1 = f"""
You are a professional chef.

**Available Ingredients:** {', '.join(ingredients_1)}
**Dietary Requirements:** 

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

print("Testing with Fish ingredients:", ingredients_1)
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content(prompt_1)
print("Response:", response.text[:200])
try:
    data = json.loads(response.text.replace("```json", "").replace("```", "").strip())
    print("Menus:", data.get("candidates", []))
except:
    print("Failed to parse JSON")

print("\n" + "="*50 + "\n")

# Test 2: Ham/Cheese ingredients
ingredients_2 = ["햄", "치즈"]
prompt_2 = prompt_1.replace(', '.join(ingredients_1), ', '.join(ingredients_2))

print("Testing with Ham/Cheese ingredients:", ingredients_2)
response = model.generate_content(prompt_2)
print("Response:", response.text[:200])
try:
    data = json.loads(response.text.replace("```json", "").replace("```", "").strip())
    print("Menus:", data.get("candidates", []))
except:
    print("Failed to parse JSON")
