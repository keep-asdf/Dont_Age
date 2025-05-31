import json
import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


def setup_gemini():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


def analyze_meal(meal):
    prompt = f"""
    다음은 저속노화를 위한 식단입니다:

    - 주식: {meal['grain']}
    - 단백질: {meal['protein']}
    - 채소: {meal['vegetable']}
    - 간식/음료: {meal['extra']}

    이 식단의 영양소를 추정해서 아래 형식의 JSON으로 반환해주세요.
    각 음식의 일반적인 영양가를 고려해서 합리적인 숫자를 추정해주세요.

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
        ]
    }}
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```json"):
            raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "reply": f"Gemini 분석 실패: {str(e)}",
            "timeSlowed": "+0.0h",
            "score": 0,
            "gauge": {"antioxidant": 0, "bloodSugar": 0, "salt": 0},
        }


def setup_langchain_gemini():
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=st.secrets["GEMINI_API_KEY"],
            temperature=0.7,
        )
        return llm
    except Exception as e:
        st.error(f"LangChain Gemini 설정 중 오류 발생: {str(e)}")
        return None


def analyze_meal_langchain(meal):
    llm = setup_langchain_gemini()
    if not llm:
        return {
            "reply": "LangChain Gemini 설정 실패",
            "timeSlowed": "+0.0h",
            "score": 0,
            "gauge": {"antioxidant": 0, "bloodSugar": 0, "salt": 0},
        }
    prompt = PromptTemplate(
        input_variables=["grain", "protein", "vegetable", "extra"],
        template="""
        다음은 저속노화를 위한 식단입니다:
        - 주식: {grain}
        - 단백질: {protein}
        - 채소: {vegetable}
        - 간식/음료: {extra}

        이 식단의 영양소를 추정해서 아래 형식의 JSON으로 반환해주세요.
        각 음식의 일반적인 영양가를 고려해서 합리적인 숫자를 추정해주세요.
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
            ]
        }}
        """,
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        result = chain.run(
            grain=meal["grain"],
            protein=meal["protein"],
            vegetable=meal["vegetable"],
            extra=meal["extra"],
        )
        # LangChain 결과가 JSON 문자열이 아닐 수도 있으니 예외 처리
        if result.strip().startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        return json.loads(result)
    except Exception as e:
        return {
            "reply": f"LangChain 분석 실패: {str(e)}",
            "timeSlowed": "+0.0h",
            "score": 0,
            "gauge": {"antioxidant": 0, "bloodSugar": 0, "salt": 0},
        }
