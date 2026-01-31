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
                with st.expander("디버깅 정보 (정보 보호를 위해 키는 숨김 처리됨)"):
                    import os
                    env_key = os.getenv("GOOGLE_API_KEY")
                    has_env = bool(env_key)
                    
                    has_secret = False
                    try:
                        if "GOOGLE_API_KEY" in st.secrets:
                            has_secret = True
                    except:
                        pass
                        
                    st.write(f"- 환경변수 설정 여부: {'✅' if has_env else '❌'}")
                    st.write(f"- Streamlit Secrets 설정 여부: {'✅' if has_secret else '❌'}")
                    st.info("Streamlit Cloud를 사용 중이라면, [Add Secrets] 메뉴에서 GOOGLE_API_KEY를 설정해야 합니다.")
                return

            prompt = f"""
            Role: You are a helpful culinary expert.
            
            User's Request: "{requirements}"
            
            Task: Recommend ONE perfect lunch menu based on the user's request.
            Provide the output in Korean.
            
            Format:
            ### 🍱 추천 메뉴: [Menu Name]
            
            **추천 이유**: 
            [Brief explanation (1-2 sentences) why this fits the request]
            
            **팁**: 
            [A small tip for enjoying this dish or a side dish recommendation]
            """
            
            try:
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
