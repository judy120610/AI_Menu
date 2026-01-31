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

import streamlit as st

import streamlit as st

def get_api_key():
    """Try to get API key from environment variables or streamlit secrets."""
    # 1. Try environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return api_key
    
    # 2. Try Streamlit secrets
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except (FileNotFoundError, Exception):
        pass
    
    return None

def get_gemini_model():
    """Returns the configured Gemini model."""
    api_key = get_api_key()
    
    if not api_key:
        st.error("🚫 API 키를 찾을 수 없습니다. (.env 또는 Secrets 설정을 확인하세요)")
        return None
        
    try:
        genai.configure(api_key=api_key)
        # Using gemini-flash-latest as an alternative to 2.0-flash
        return genai.GenerativeModel('gemini-2.5-flash')
    except Exception as e:
        st.error(f"🚫 모델 초기화 중 오류가 발생했습니다: {e}")
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
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf(plan, recipes):
    """
    Generates a PDF file with the weekly menu and recipes.
    Returns bytes.
    """
    buffer = io.BytesIO()
    
    # helper to register font
    font_name = 'MalgunGothic'
    try:
        # Try standard Windows path first
        pdfmetrics.registerFont(TTFont(font_name, 'malgun.ttf'))
    except:
        try:
            # Try absolute path
            pdfmetrics.registerFont(TTFont(font_name, 'C:/Windows/Fonts/malgun.ttf'))
        except:
            print("Korean font not found. Fallback to standard font (Korean may not show).")
            font_name = 'Helvetica' # Fallback

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    # Create a custom style for the header and body using the registered font
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        spaceAfter=20
    )
    
    if font_name != 'Helvetica':
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            leading=14 # line spacing
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            spaceAfter=10,
            spaceBefore=10
        )
    else:
        body_style = styles['Normal']
        heading_style = styles['Heading2']

    # Title
    story.append(Paragraph("주간 점심 메뉴 및 레시피", title_style))
    story.append(Spacer(1, 12))
    
    # Content
    days = ["월", "화", "수", "목", "금"]
    for day in days:
        menu_name = plan.get(day, "메뉴 없음")
        recipe_content = recipes.get(day, "레시피 없음")
        
        # Day Header
        story.append(Paragraph(f"{day}요일: {menu_name}", heading_style))
        
        # Recipe Body
        # If recipe_content is dict, convert to string (though current implementation returns string usually, prompt asks for string in JSON)
        # But previous prompt example showed JSON structure for recipe text.
        # Let's handle string with newlines.
        if isinstance(recipe_content, dict):
            # Fallback if it parses as dict
            text = str(recipe_content)
        else:
            text = str(recipe_content)
            
        # Replace newlines with <br/> for Paragraph
        formatted_text = text.replace('\n', '<br/>')
        
        story.append(Paragraph(formatted_text, body_style))
        story.append(Spacer(1, 12))
        story.append(Spacer(1, 12)) # Extra space between days

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
