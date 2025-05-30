import streamlit as st
import random

# import openai
import json
import os

# 🔑 OpenAI API 키 설정
# openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# 🥗 식단 후보 데이터
grains = ["퀴노아", "현미밥", "귀리죽"]
proteins = ["연어구이", "두부조림", "닭가슴살"]
vegetables = ["브로콜리", "채소볶음", "시금치나물"]
extras = ["블루베리", "녹차", "아보카도", "무가당 요거트"]


# 🔀 식단 생성 함수
def get_random_meal():
    return {
        "grain": random.choice(grains),
        "protein": random.choice(proteins),
        "vegetable": random.choice(vegetables),
        "extra": random.choice(extras),
    }


# 🤖 GPT 분석 함수
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        raw = response["choices"][0]["message"]["content"]
        return json.loads(raw)
    except Exception as e:
        return {
            "reply": "GPT 분석 실패: " + str(e),
            "timeSlowed": "+0.0h",
            "score": 0,
            "gauge": {"antioxidant": 0, "bloodSugar": 0, "salt": 0},
        }


# 🌐 Streamlit UI
st.set_page_config(page_title="젊밥 🍱", layout="centered")
st.title("🍱 젊어지는 밥상 - 젊밥")
st.caption("늙음을 막는 한 끼 식단, GPT가 분석해드립니다.")

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

    # with st.spinner("GPT가 식단을 분석 중입니다..."):
    #     result = analyze_meal(meal)

    # st.subheader("🧠 GPT 분석 결과")
    # st.metric("⏳ 노화 지연 시간", result["timeSlowed"])
    # st.metric("💯 항노화 점수", f"{result['score']}점")

    # st.markdown("**게이지 분석:**")

    # def draw_gauge(label, value):
    #     bar = "●" * value + "○" * (5 - value)
    #     st.write(f"{label}: {bar}")

    # draw_gauge("항산화", result["gauge"]["antioxidant"])
    # draw_gauge("혈당 부하", result["gauge"]["bloodSugar"])
    # draw_gauge("염분", result["gauge"]["salt"])

    # st.success(result["reply"])

# # 🗣️ 챗봇 영역
# st.divider()
# st.subheader("🤖 GPT에게 궁금한 걸 물어보세요")
# user_input = st.text_input("예: 블루베리가 왜 좋아요?")
# if user_input:
#     with st.spinner("GPT 응답 생성 중..."):
#         chat = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "넌 저속노화 식단 코치야. 짧고 친절하게 대답해.",
#                 },
#                 {"role": "user", "content": user_input},
#             ],
#         )
#         st.chat_message("assistant").write(chat["choices"][0]["message"]["content"])
