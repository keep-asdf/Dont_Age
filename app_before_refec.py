import streamlit as st
from datetime import datetime, timedelta
import os
from data_models import get_random_meal
from ai_services import setup_gemini, analyze_meal
from ui_components import get_css_styles, display_meal_analysis

# 🌐 Streamlit UI 구성
st.set_page_config(page_title="젊밥 🍱", layout="centered")

# CSS 스타일 적용
st.markdown(get_css_styles(), unsafe_allow_html=True)

# 타이틀 표시
st.markdown(
    """
    <div style='text-align: center'>
        <h1>🍱 저속노화를 위한 젊어지는 밥상</h1>
        <h1>- 젊밥 -</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# 로고 이미지 중앙 정렬
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image("logo.png", width=400)

# Gemini API 설정
setup_gemini()

# 세션 상태 초기화
if "last_meal_time" not in st.session_state:
    st.session_state.last_meal_time = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "image_generated" not in st.session_state:
    st.session_state.image_generated = False
if "current_meal" not in st.session_state:
    st.session_state.current_meal = None

# 메인 버튼
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    if st.button("🔁 오늘의 젊어지는 식단 추천받기", use_container_width=True):
        current_time = datetime.now()

        if st.session_state.last_meal_time is None or (
            current_time - st.session_state.last_meal_time
        ) > timedelta(seconds=10):
            st.session_state.last_meal_time = current_time
            meal = get_random_meal()

            # 식단 구성 표시
            st.markdown(
                """
                <h2 style='font-size: 2.5em; text-align: left; margin-bottom: 1em;'>🥗 식단 구성</h2>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style='font-size: 1.5em; line-height: 2em;'>
                    <p style='margin-bottom: 1em;'>- 🍚 <strong>주식</strong>: {meal['grain']}</p>
                    <p style='margin-bottom: 1em;'>- 🍗 <strong>단백질</strong>: {meal['protein']}</p>
                    <p style='margin-bottom: 1em;'>- 🥦 <strong>채소</strong>: {meal['vegetable']}</p>
                    <p style='margin-bottom: 1em;'>- 🍇 <strong>간식/음료</strong>: {meal['extra']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # AI 분석 표시
            st.markdown(
                """
                <div style='font-size: 2em; text-align: center; margin: 1em 0;'>
                    <strong>🤖 젊밥 AI</strong>가 식단을 분석 중입니다 
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.spinner(""):
                result = analyze_meal(meal)

            # 분석 결과 표시
            st.markdown(
                """
                <h2 style='font-size: 2.5em; text-align: left; margin: 1em 0;'>🧠 분석 결과</h2>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.metric("⏳ 노화 지연 시간", result["timeSlowed"])
            with col2:
                st.metric("💯 항노화 점수", f"{result['score']}점")

            # 상세 분석 결과 표시
            display_meal_analysis(result)

        else:
            remaining_time = timedelta(minutes=5) - (
                current_time - st.session_state.last_meal_time
            )
            st.warning(
                f"잠시만요! 다음 식단 추천까지 {int(remaining_time.total_seconds())}초 {int(remaining_time.total_seconds() % 60)}초 남았습니다."
            )
