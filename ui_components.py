import streamlit as st


def get_css_styles():
    return """
    <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css\">
    <style>
    html, body, [class*='css']  {
        font-family: 'Pretendard', 'Malgun Gothic', 'Apple SD Gothic Neo', Arial, sans-serif !important;
    }
    .main-title {
        font-size: 2.4em;
        font-weight: 800;
        text-align: center;
        margin-top: 32px;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }
    .sub-title {
        font-size: 1.5em;
        font-weight: 600;
        text-align: center;
        margin-bottom: 24px;
        color: #4CAF50;
    }
    .logo-center {
        display: flex;
        justify-content: center;
        margin-bottom: 24px;
    }
    .section-title {
        font-size: 1.2em;
        font-weight: 700;
        margin-top: 32px;
        margin-bottom: 12px;
        color: #4CAF50;
    }
    .card {
        background: #23272a;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        padding: 1.5em;
        margin-bottom: 2em;
    }
    .main-btn {
        width: 100%;
        height: 80px;
        font-size: 1.5em;
        font-weight: 700;
        border-radius: 10px;
        margin: 0 auto 32px auto;
        display: block;
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        border: none;
        transition: all 0.3s;
        cursor: pointer;
    }
    .main-btn:hover {
        box-shadow: 0 4px 16px rgba(76,175,80,0.15);
        transform: translateY(-2px);
    }
    @media (max-width: 600px) {
        .main-title { font-size: 1.5em; }
        .sub-title { font-size: 1.1em; }
        .main-btn { font-size: 1.1em; height: 60px; }
    }
    </style>
    """


def draw_gauge(label, value):
    st.progress(value / 5, text=f"{label}: {'●' * value + '○' * (5 - value)}")


def display_meal_analysis(result):
    st.markdown("### 📊 건강 지표")
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

    st.markdown("### 💡 종합 분석")
    st.success(result["reply"])
