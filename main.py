import streamlit as st
import pandas as pd
from utils import generate_menu_candidates, generate_recipes, create_pdf

# Set page config
st.set_page_config(
    page_title="방학 메뉴 추천 서비스",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Premium & Green Aesthetic
st.markdown("""
<style>
    .stButton>button {
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    .stButton>button[kind="secondary"] {
        background-color: #ECFDF5;
        border: 1px solid #10B981;
        color: #065F46;
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: #D1FAE5;
    }
    div[data-testid="stExpander"] {
        background-color: #F8FAFC;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
    }
    h1, h2, h3 {
        color: #064E3B; /* Dark Green Text */
    }
    .ingredient-header {
        color: #059669;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
        display: block;
    }
    .candidate-box {
        padding: 10px;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        margin-bottom: 5px;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# 1. Initialize Session State
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = {
        "생선": ["연어", "오징어", "고등어", "갈치"],
        "고기": ["삼겹살", "차돌박이", "불고기", "닭가슴살"],
        "야채": ["양파", "버섯", "당근", "대파", "감자"],
        "냉동": ["너겟", "만두", "튀김", "돈까스"],
        "기타": ["햄", "치즈", "진미채", "계란", "두부"]
    }
if 'selected_ingredients' not in st.session_state:
    st.session_state.selected_ingredients = set()
if 'custom_reqs' not in st.session_state:
    st.session_state.custom_reqs = ["매운음식 X", "국물 요리 선호", "간단한 조리", "오븐 사용 X"]
if 'selected_reqs' not in st.session_state:
    st.session_state.selected_reqs = set()

# Revised State Variables for New Flow
if 'menu_candidates' not in st.session_state:
    st.session_state.menu_candidates = []  # List of 10 candidates
if 'selected_candidates' not in st.session_state:
    st.session_state.selected_candidates = [] # List of EXACTLY 5 selected items
if 'final_plan' not in st.session_state:
    st.session_state.final_plan = {}
if 'recipes' not in st.session_state:
    st.session_state.recipes = {}

# --- Header ---
st.title("🍳 주간 점심 메뉴 추천 (ver. 2.5)")
# Removed the step description line as requested

tab1, tab2 = st.tabs(["냉장고를 부탁해", "메뉴를 추천해줘"])

with tab1:
    # --- Step 1: Ingredient Selection ---
    st.subheader("1️⃣ 재료 선택")

    # Add Ingredient UI
    with st.expander("➕ 직접 재료 추가하기", expanded=False):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            new_cat = st.selectbox("카테고리", list(st.session_state.ingredients.keys()))
        with c2:
            new_item = st.text_input("재료명 입력")
        with c3:
            if st.button("추가", use_container_width=True):
                if new_item and new_item not in st.session_state.ingredients[new_cat]:
                    st.session_state.ingredients[new_cat].append(new_item)
                    st.rerun()

    # Ingredient Grid
    cols = st.columns(len(st.session_state.ingredients) + 1)
    for i, (category, items) in enumerate(st.session_state.ingredients.items()):
        with cols[i]:
            st.markdown(f"<span class='ingredient-header'>{category}</span>", unsafe_allow_html=True)
            for item in items:
                is_selected = item in st.session_state.selected_ingredients
                btn_type = "primary" if is_selected else "secondary"
                if st.button(item, key=f"ing_{item}", type=btn_type, use_container_width=True):
                    if is_selected:
                        st.session_state.selected_ingredients.remove(item)
                    else:
                        st.session_state.selected_ingredients.add(item)
                    st.rerun()

    # Requirements Column
    with cols[-1]:
        st.markdown("<span class='ingredient-header'>요구사항</span>", unsafe_allow_html=True)
        for req in st.session_state.custom_reqs:
            if st.checkbox(req, key=f"req_{req}"):
                st.session_state.selected_reqs.add(req)
            elif req in st.session_state.selected_reqs:
                st.session_state.selected_reqs.discard(req)
                
        new_req = st.text_input("직접 입력", key="new_req_input", placeholder="예: 저염식", label_visibility="collapsed")
        if st.button("요구사항 추가", key="add_req_btn"):
            if new_req and new_req not in st.session_state.custom_reqs:
                st.session_state.custom_reqs.append(new_req)
                st.rerun()

    st.divider()

    # --- Action: Generate Candidates ---
    c_gen1, c_gen2 = st.columns([1, 4])
    with c_gen1:
        generate_clicked = st.button("🚀 메뉴 10개 추천받기", type="primary", use_container_width=True)

    if generate_clicked:
        if not st.session_state.selected_ingredients:
            st.warning("⚠️ 재료를 최소 하나 이상 선택해주세요!")
        else:
            with st.spinner("👩‍🍳 셰프가 10가지 메뉴를 생각 중입니다..."):
                candidates = generate_menu_candidates(
                    list(st.session_state.selected_ingredients),
                    list(st.session_state.selected_reqs)
                )
                if candidates:
                    st.session_state.menu_candidates = candidates
                    st.session_state.selected_candidates = [] # Reset selection
                    st.session_state.final_plan = {}
                    st.session_state.recipes = {}
                    st.rerun()
                else:
                    st.error("메뉴 생성에 실패했습니다. (API 확인 필요)")

    # --- Step 2: Candidate Selection ---
    if st.session_state.menu_candidates and not st.session_state.recipes:
        st.subheader("2️⃣ 메뉴 후보 10가지 중 5가지를 선택하세요")
        st.write(f"현재 선택된 개수: **{len(st.session_state.selected_candidates)}** / 5")
        
        # 5x2 grid for candidates
        c_cols = st.columns(5)
        
        # We will use checkboxes to select 5
        for i, menu in enumerate(st.session_state.menu_candidates):
            col_idx = i % 5
            with c_cols[col_idx]:
                # Check if currently selected
                is_checked = menu in st.session_state.selected_candidates
                
                # Disable checkbox if 5 are already selected and this one is NOT selected
                disable_checkbox = (len(st.session_state.selected_candidates) >= 5) and (not is_checked)
                
                if st.checkbox(menu, key=f"cand_{i}", value=is_checked, disabled=disable_checkbox):
                    if menu not in st.session_state.selected_candidates:
                        st.session_state.selected_candidates.append(menu)
                        st.rerun()
                else:
                    if menu in st.session_state.selected_candidates:
                        st.session_state.selected_candidates.remove(menu)
                        st.rerun()

        st.divider()
        
        # Confirm Selection Button
        if len(st.session_state.selected_candidates) == 5:
            if st.button("✅ 이 5가지 메뉴로 주간 식단 확정하기", type="primary"):
                days = ["월", "화", "수", "목", "금"]
                # Assign in order
                plan = {}
                for day, menu in zip(days, st.session_state.selected_candidates):
                    plan[day] = menu
                st.session_state.final_plan = plan
                
                with st.spinner("📝 레시피를 작성 중입니다..."):
                    recipes = generate_recipes(
                        st.session_state.final_plan, 
                        list(st.session_state.selected_ingredients)
                    )
                    if recipes:
                        st.session_state.recipes = recipes
                        st.rerun()
        elif len(st.session_state.selected_candidates) > 0:
            st.info("5개를 정확히 선택해야 확정할 수 있습니다.")

    # --- Step 3: Final View & Recipes ---
    if st.session_state.recipes:
        st.success("🎉 이번 주 식단이 완성되었습니다!")
        
        st.subheader("📅 주간 식단표")
        final_df = pd.DataFrame([st.session_state.final_plan])
        st.table(final_df)
        
        st.subheader("👨‍🍳 상세 레시피")
        days = ["월", "화", "수", "목", "금"]
        for day in days:
            menu_name = st.session_state.final_plan.get(day)
            recipe_content = st.session_state.recipes.get(day, "레시피 없음")
            
            with st.expander(f"**{day}요일**: {menu_name}"):
                if isinstance(recipe_content, dict):
                    st.write(recipe_content)
                else:
                    st.markdown(recipe_content)

        c_back, c_down = st.columns([1, 1])
        with c_back:
            if st.button("🔄 처음으로 돌아가기", use_container_width=True):
                st.session_state.menu_candidates = []
                st.session_state.selected_candidates = []
                st.session_state.final_plan = {}
                st.session_state.recipes = {}
                st.rerun()
        
        with c_down:
            pdf_bytes = create_pdf(st.session_state.final_plan, st.session_state.recipes)
            st.download_button(
                label="📄 PDF로 저장하기",
                data=pdf_bytes,
                file_name="weekly_menu.pdf",
                mime="application/pdf",
                use_container_width=True
            )

with tab2:
    st.header("🍽️ 메뉴를 추천해줘")
    
    # Under Construction Image
    import os
    img_path = os.path.join("doc", "under_construction.png")
    if os.path.exists(img_path):
        st.image(img_path, caption="열심히 공사중입니다! 조금만 기다려주세요 🍳", use_container_width=True)
    else:
        st.info("새로운 기능이 곧 추가될 예정입니다.")
