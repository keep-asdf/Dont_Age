import streamlit as st
import random
import json
import google.generativeai as genai

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
    prompt = f"""
    다음은 저속노화를 위한 식단입니다:

    - 주식: {meal['grain']}
    - 단백질: {meal['protein']}
    - 채소: {meal['vegetable']}
    - 간식/음료: {meal['extra']}

    이 식단에 대한 분석을 아래 형식의 JSON으로 반환해주세요:

    {{
    "reply": "이 식단은 어떤 효과가 있는지 한 문장 설명",
    "timeSlowed": "+3.2h",
    "score": 88,
    "gauge": {{
        "antioxidant": 4,
        "bloodSugar": 3,
        "salt": 2
    }}
    }}

    출력은 JSON 형식 문자열만 주시고, 다른 문장은 포함하지 마세요.
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
import streamlit as st

# CSS로 네비게이션 바 스타일링
st.markdown(
    """
<style>
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 60px;
    background-color: #262730;
    display: flex;
    align-items: center;
    padding: 0 20px;
    z-index: 1000;
}

.navbar-brand {
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
    text-decoration: none;
}

.navbar-menu {
    display: flex;
    gap: 20px;
    margin-left: auto;
}

.navbar-item {
    color: white;
    text-decoration: none;
    padding: 5px 10px;
    border-radius: 5px;
}

.navbar-item:hover {
    background-color: #404040;
}

/* 메인 컨텐츠가 네비게이션 바 아래에 오도록 패딩 추가 */
.main {
    padding-top: 80px;
}
</style>
""",
    unsafe_allow_html=True,
)

# 네비게이션 바 HTML
st.markdown(
    """
<div class="navbar">
    <a href="#" class="navbar-brand">🍱 늙지마켓</a>
    <div class="navbar-menu">
        <a href="#" class="navbar-item">홈</a>
        <a href="#" class="navbar-item">식단 추천</a>
        <a href="#" class="navbar-item">식단 분석</a>
        <a href="#" class="navbar-item">설정</a>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# 메인 컨텐츠를 감싸는 div
st.markdown('<div class="main">', unsafe_allow_html=True)

# 여기에 기존 컨텐츠 추가
st.title("🍱 늙지마켓")
st.caption("늙음을 막는 한 끼 식단, AI가 분석해드립니다.")

# 메인 컨텐츠 div 닫기
st.markdown("</div>", unsafe_allow_html=True)


# 🌐 Streamlit UI 구성
st.set_page_config(page_title="젊밥 🍱", layout="centered")
st.title("🍱 젊어지는 밥상 - 젊밥")


# 👉 식단 추천
if st.button("🔁 오늘의 식단 추천받기"):
    meal = get_random_meal()

    st.subheader("🥗 식단 구성")
    st.markdown(
        f"""
    - 🍚 **주식**: {meal['grain']}  
    - 🍗 **단백질**: {meal['protein']}  
    - 🥦 **채소**: {meal['vegetable']}  
    - 🍇 **간식/음료**: {meal['extra']}
    """
    )

    with st.spinner("Gemini가 식단을 분석 중입니다..."):
        result = analyze_meal(meal)

    st.subheader("🧠 분석 결과")
    st.metric("⏳ 노화 지연 시간", result["timeSlowed"])
    st.metric("💯 항노화 점수", f"{result['score']}점")

    st.markdown("**게이지 분석:**")

    def draw_gauge(label, value):
        bar = "●" * value + "○" * (5 - value)
        st.write(f"{label}: {bar}")

    draw_gauge("항산화", result["gauge"]["antioxidant"])
    draw_gauge("혈당 부하", result["gauge"]["bloodSugar"])
    draw_gauge("염분", result["gauge"]["salt"])

    st.success(result["reply"])

# 🗣️ 챗봇 영역
st.divider()
st.subheader("🤖 Gemini에게 궁금한 걸 물어보세요")
user_input = st.text_input("예: 블루베리가 왜 좋아요?")
if user_input:
    with st.spinner("Gemini 응답 생성 중..."):
        model = genai.GenerativeModel("gemini-2.0-flash")
        res = model.generate_content(
            [
                {
                    "role": "user",
                    "parts": [
                        f"넌 저속노화 식단 코치야. 짧고 친절하게 대답해.\n질문: {user_input}"
                    ],
                }
            ]
        )
        st.chat_message("assistant").write(res.text)
