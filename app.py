import streamlit as st
import random
import json
import google.generativeai as genai
from datetime import datetime, timedelta
import os


# 🌐 Streamlit UI 구성
st.set_page_config(page_title="젊밥 🍱", layout="centered")
# st.title("🍱 저속노화를 위한 젊어지는 밥상 - 젊밥")
st.markdown(
    """
<div style='text-align: center'>
    <h1>🍱 저속노화를 위한 젊어지는 밥상</h1>
    <h1>- 젊밥 -</h1>
</div>
""",
    unsafe_allow_html=True,
)

##############
## 기본 셋팅 ##
##############


# 🔑 Gemini API 키 설정
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# 🥗 식단 후보 데이터
grains = ["퀴노아", "현미밥", "귀리죽"]
proteins = ["연어구이", "두부조림", "닭가슴살"]
vegetables = ["브로콜리", "채소볶음", "시금치나물"]
extras = ["블루베리", "녹차", "아보카도", "무가당 요거트"]


def get_random_meal():
    return {
        "grain": random.choice(grains),
        "protein": random.choice(proteins),
        "vegetable": random.choice(vegetables),
        "extra": random.choice(extras),
    }


# 🤖 Gemini 분석 함수
def analyze_meal(meal):
    # prompt = f"""
    # 다음은 저속노화를 위한 식단입니다:

    # - 주식: {meal['grain']}
    # - 단백질: {meal['protein']}
    # - 채소: {meal['vegetable']}
    # - 간식/음료: {meal['extra']}

    # 이 식단에 대한 분석을 아래 형식의 JSON으로 반환해주세요:

    # {{
    # "reply": "이 식단은 어떤 효과가 있는지 한 문장 설명",
    # "timeSlowed": "+3.2h",
    # "score": 88,
    # "gauge": {{
    #     "antioxidant": 4,
    #     "bloodSugar": 3,
    #     "salt": 2
    # }}
    # }}

    # 출력은 JSON 형식 문자열만 주시고, 다른 문장은 포함하지 마세요.
    # """
    prompt = f"""
    다음은 저속노화를 위한 식단입니다:

    - 주식: {meal['grain']}
    - 단백질: {meal['protein']}
    - 채소: {meal['vegetable']}
    - 간식/음료: {meal['extra']}

    이 식단의 영양소를 추정해서 아래 형식의 JSON으로 반환해주세요.
    각 음식의 일반적인 영양가를 고려해서 합리적인 숫자를 추정해주세요.
    예를 들어:
    - 현미밥 1공기: 약 300kcal, 단백질 6g
    - 연어 100g: 약 200kcal, 단백질 20g
    - 브로콜리 100g: 약 30kcal, 단백질 3g
    - 블루베리 100g: 약 50kcal, 단백질 1g

    {{
    "reply": "이 식단은 어떤 효과가 있는지 한 문장 설명",
    "timeSlowed": "+3.2h",
    "score": 88,
    "gauge": {{
        "antioxidant": 4,
        "bloodSugar": 3,
        "salt": 2
    }},
    "nutrition": {{
        "calories": "추정 칼로리 (kcal)",
        "protein": "추정 단백질 (g)",
        "fiber": "추정 식이섬유 (g)",
        "vitamins": ["비타민C", "비타민E"],
        "minerals": ["칼슘", "마그네슘"]
    }},
    "benefits": [
        "항산화 효과",
        "혈당 조절",
        "면역력 강화"
    ],
    "alternatives": [
        {{
            "item": "현미밥",
            "reason": "혈당 지수가 낮아 더 좋은 선택"
        }}
    ]
    }}

    출력은 JSON 형식 문자열만 주시고, 다른 문장은 포함하지 마세요.
    각 영양소의 숫자는 합리적인 범위 내에서 추정해주세요.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # 예외적으로 "```json\n{...}```"로 감싸는 경우도 있어서 처리
        if raw.startswith("```json"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        return json.loads(raw)
    except Exception as e:
        return {
            "reply": "Gemini 분석 실패: " + str(e),
            "timeSlowed": "+0.0h",
            "score": 0,
            "gauge": {"antioxidant": 0, "bloodSugar": 0, "salt": 0},
        }


##############
# CSS 스타일 추가 (페이지 상단에 추가)
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        height: 100px;  /* em 대신 px로 고정 높이 지정 */
        font-size: 5em;  /* 글자 크기만 조절 */
        margin: 0 auto;
        display: block;
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
        line-height: 100px;  /* 버튼 높이와 동일하게 설정 */
    }
    div.stButton > button:hover {
        background-color: #45a049;
        transform: scale(1.2);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 세션 상태 초기화
if "last_meal_time" not in st.session_state:
    st.session_state.last_meal_time = None
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "image_generated" not in st.session_state:
    st.session_state.image_generated = False
if "current_meal" not in st.session_state:
    st.session_state.current_meal = None

# 버튼을 컨테이너로 감싸서 중앙 정렬
# 버튼만 중앙에 배치
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    if st.button("🔁 오늘의 식단 추천받기", use_container_width=True):

        current_time = datetime.now()

        if st.session_state.last_meal_time is None or (
            current_time - st.session_state.last_meal_time
        ) > timedelta(seconds=10):
            st.session_state.last_meal_time = current_time
            meal = get_random_meal()

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

            st.markdown(
                """
                <div style='font-size: 2em; text-align: center; margin: 2em 0;'>
                    <strong>🤖 AI</strong>가 식단을 분석 중입니다...
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.spinner(""):
                result = analyze_meal(meal)

            st.subheader("🧠 분석 결과")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("⏳ 노화 지연 시간", result["timeSlowed"])
            with col2:
                st.metric("💯 항노화 점수", f"{result['score']}점")

            st.markdown("### 📊 건강 지표")

            def draw_gauge(label, value):
                st.progress(
                    value / 5, text=f"{label}: {'●' * value + '○' * (5 - value)}"
                )

            draw_gauge("항산화", result["gauge"]["antioxidant"])
            draw_gauge("혈당 부하", result["gauge"]["bloodSugar"])
            draw_gauge("염분", result["gauge"]["salt"])

            st.markdown("### 🥗 영양소 분석")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("칼로리", f"{result['nutrition']['calories']}")
            with col2:
                st.metric("단백질", f"{result['nutrition']['protein']}")
            with col3:
                st.metric("식이섬유", f"{result['nutrition']['fiber']}")

            st.markdown("#### 💊 주요 영양소")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**비타민**")
                for vitamin in result["nutrition"]["vitamins"]:
                    st.markdown(f"- {vitamin}")
            with col2:
                st.markdown("**미네랄**")
                for mineral in result["nutrition"]["minerals"]:
                    st.markdown(f"- {mineral}")

            st.markdown("### ✨ 건강상 이점")
            for benefit in result["benefits"]:
                st.markdown(f"- {benefit}")

            if result.get("alternatives"):
                st.markdown("### 🔄 대체 추천")
                for alt in result["alternatives"]:
                    st.info(f"**{alt['item']}**: {alt['reason']}")

            st.markdown("### 💡 종합 분석")
            st.success(result["reply"])

        else:
            remaining_time = timedelta(minutes=5) - (
                current_time - st.session_state.last_meal_time
            )
            st.warning(
                f"잠시만요! 다음 식단 추천까지 {int(remaining_time.total_seconds())}초 {int(remaining_time.total_seconds() % 60)}초 남았습니다."
            )


# ---------------------------------------#
# # 👉 식단 추천
# if st.button("🔁 오늘의 식단 추천받기"):
#     meal = get_random_meal()

#     st.subheader("🥗 식단 구성")
#     st.markdown(
#         f"""
#     - 🍚 **주식**: {meal['grain']}
#     - 🍗 **단백질**: {meal['protein']}
#     - 🥦 **채소**: {meal['vegetable']}
#     - 🍇 **간식/음료**: {meal['extra']}
#     """
#     )

#     # st.success(result["reply"])
#     with st.spinner("AI가 식단을 분석 중입니다..."):
#         result = analyze_meal(meal)

#     # 1. 기본 분석 결과
#     st.subheader("🧠 분석 결과")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("⏳ 노화 지연 시간", result["timeSlowed"])
#     with col2:
#         st.metric("💯 항노화 점수", f"{result['score']}점")

#     # 2. 게이지 분석 (시각적 개선)
#     st.markdown("### 📊 건강 지표")

#     def draw_gauge(label, value):
#         # 프로그레스 바로 변경
#         st.progress(value / 5, text=f"{label}: {'●' * value + '○' * (5 - value)}")

#     draw_gauge("항산화", result["gauge"]["antioxidant"])
#     draw_gauge("혈당 부하", result["gauge"]["bloodSugar"])
#     draw_gauge("염분", result["gauge"]["salt"])

#     # 3. 영양소 정보
#     st.markdown("### 🥗 영양소 분석")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("칼로리", f"{result['nutrition']['calories']}kcal")
#     with col2:
#         st.metric("단백질", f"{result['nutrition']['protein']}g")
#     with col3:
#         st.metric("식이섬유", f"{result['nutrition']['fiber']}g")

#     # 4. 비타민과 미네랄
#     st.markdown("#### 💊 주요 영양소")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.markdown("**비타민**")
#         for vitamin in result["nutrition"]["vitamins"]:
#             st.markdown(f"- {vitamin}")
#     with col2:
#         st.markdown("**미네랄**")
#         for mineral in result["nutrition"]["minerals"]:
#             st.markdown(f"- {mineral}")

#     # 5. 건강상 이점
#     st.markdown("### ✨ 건강상 이점")
#     for benefit in result["benefits"]:
#         st.markdown(f"- {benefit}")

#     # 6. 대체 추천
#     if result.get("alternatives"):
#         st.markdown("### 🔄 대체 추천")
#         for alt in result["alternatives"]:
#             st.info(f"**{alt['item']}**: {alt['reason']}")

#     # 7. 종합 분석
#     st.markdown("### 💡 종합 분석")
#     st.success(result["reply"])
# ---------------------------------------#
# # 세션 상태 초기화 (이 부분이 중요!)
# if "last_meal_time" not in st.session_state:
#     st.session_state.last_meal_time = None
# if "question_count" not in st.session_state:
#     st.session_state.question_count = 0

# # 버튼 클릭 처리
# if st.button("🔁 오늘의 식단 추천받기"):
#     current_time = datetime.now()

#     # 첫 클릭이거나 5분이 지났는지 확인
#     if st.session_state.last_meal_time is None or (
#         current_time - st.session_state.last_meal_time
#     ) > timedelta(minutes=5):
#         # 식단 생성 및 표시
#         st.session_state.last_meal_time = current_time
#         meal = get_random_meal()

#         st.subheader("🥗 식단 구성")
#         st.markdown(
#             f"""
#         - 🍚 **주식**: {meal['grain']}
#         - 🍗 **단백질**: {meal['protein']}
#         - 🥦 **채소**: {meal['vegetable']}
#         - 🍇 **간식/음료**: {meal['extra']}
#         """
#         )

#         # Gemini 분석 결과 표시
#         with st.spinner("AI가 식단을 분석 중입니다..."):
#             result = analyze_meal(meal)

#         st.subheader("🧠 AI 분석 결과")
#         st.metric("⏳ 노화 지연 시간", result["timeSlowed"])
#         st.metric("💯 항노화 점수", f"{result['score']}점")

#         st.markdown("**게이지 분석:**")

#         def draw_gauge(label, value):
#             bar = "●" * value + "○" * (5 - value)
#             st.write(f"{label}: {bar}")

#         draw_gauge("항산화", result["gauge"]["antioxidant"])
#         draw_gauge("혈당 부하", result["gauge"]["bloodSugar"])
#         draw_gauge("염분", result["gauge"]["salt"])

#         st.success(result["reply"])

#     else:
#         # 5분이 지나지 않았다면
#         remaining_time = timedelta(minutes=5) - (
#             current_time - st.session_state.last_meal_time
#         )
#         st.warning(
#             f"잠시만요! 다음 식단 추천까지 {int(remaining_time.total_seconds() / 60)}분 {int(remaining_time.total_seconds() % 60)}초 남았습니다."
#         )

# # 현재 상태 표시 (선택사항)
# if st.session_state.last_meal_time:
#     st.sidebar.write(
#         "마지막 식단 추천 시간:", st.session_state.last_meal_time.strftime("%H:%M:%S")
#     )
