import streamlit as st
from utils import get_gemini_model

def run_menu_recommender():
    st.header("🍽️ 메뉴를 부탁해")
    st.markdown("먹고 싶은 메뉴의 특징이나 상황을 알려주세요. 딱 맞는 메뉴를 추천해드릴게요!")

    # User input
    requirements = st.text_area(
        "요구사항을 입력하세요", 
        placeholder="예) 매운 국물 요리가 땡겨요, 다이어트 중이라 가벼운 거 없을까요?, 어제 치킨 먹어서 닭은 싫어요",
        height=100
    )

    if st.button("✨ 메뉴 추천받기", type="primary"):
        if not requirements:
            st.warning("⚠️ 요구사항을 입력해주세요!")
            return

        with st.spinner("AI가 셰프가 고민 중입니다... 🍳"):
            model = get_gemini_model()
            if not model:
                st.error("API 설정을 확인해주세요. (API Key Missing)")
                return

            prompt = f"""
            Role: You are a helpful culinary expert.
            
            User's Request: "{requirements}"
            
            Task: Recommend exactly 10 distinct lunch menus based on the user's request.
            Provide the output in Korean.
            
            Format:
            Return ONLY a valid JSON object with the following structure:
            {{
                "recommendations": [
                    {{
                        "menu": "Menu Name 1",
                        "reason": "Brief reason for recommendation",
                        "tip": "Short tip"
                    }},
                    ...
                ]
            }}
            """
            
            try:
                response = model.generate_content(prompt)
                import json
                
                text = response.text
                # Clean up potential markdown formatting
                if text.startswith("```"):
                    text = text.split("\n", 1)[1]
                    if text.endswith("```"):
                        text = text.rsplit("\n", 1)[0]
                
                data = json.loads(text)
                items = data.get("recommendations", [])
                
                st.markdown("---")
                st.subheader("🍱 추천 메뉴 10선")
                
                if items:
                    for i, item in enumerate(items, 1):
                        with st.expander(f"{i}. {item['menu']}"):
                            st.write(f"**이유**: {item['reason']}")
                            st.write(f"**팁**: {item['tip']}")
                else:
                    st.warning("메뉴를 추천받지 못했습니다.")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
