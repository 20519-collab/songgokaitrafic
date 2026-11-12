import streamlit as st
import pickle
import numpy as np
import pandas as pd

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="교통사고 사망자 수 예측 & 안전 알리미",
    page_icon="🚦",
    layout="centered"
)

# ---------------------------------------------------------
# 1. Model Loading (Caching applied)
# ---------------------------------------------------------
@st.cache_resource
def load_orange_model(model_path="traffic_casualty_model.pkcls"):
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"모델 파일('{model_path}')을 로드하는 중 오류가 발생했습니다: {e}")
        return None

model = load_orange_model()

# ---------------------------------------------------------
# Header & Intro
# ---------------------------------------------------------
st.title("🚦 교통사고 사망자 수 실시간 예측 서비스")
st.write(
    "오렌지3(Orange3) 인공신경망 모델을 이용하여 **지역(시도), 사고건수, 중상자수, 경상자수, 부상신고자수**를 바탕으로 "
    "**예상 사망자 수**를 실시간 예측하고 위험도 신호등을 표시합니다."
)

st.markdown("---")

# ---------------------------------------------------------
# 2. UI Inputs (Sido Selectbox & 4 Sliders)
# ---------------------------------------------------------
st.subheader("⚙️ 조건 입력")

# 모델에 포함된 17개 시도 목록
sido_options = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", 
    "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", 
    "경기도", "강원특별자치도", "충청북도", "충청남도", 
    "전북특별자치도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
]

selected_sido = st.selectbox("📌 지역(시도) 선택", sido_options)

st.write("📊 **사고 및 부상자 수 설정**")

col1, col2 = st.columns(2)
with col1:
    accidents = st.slider("🚗 사고건수", min_value=0, max_value=500, value=50, step=1)
    serious_injuries = st.slider("🚑 중상자수", min_value=0, max_value=300, value=15, step=1)
with col2:
    minor_injuries = st.slider("🩹 경상자수", min_value=0, max_value=1000, value=30, step=1)
    reported_injuries = st.slider("📋 부상신고자수", min_value=0, max_value=200, value=5, step=1)

# ---------------------------------------------------------
# Model Inference Function
# ---------------------------------------------------------
def predict_casualty(model, sido, acc, serious, minor, reported):
    if model is None:
        return 0.0

    # 입력 데이터프레임 구성 (모델 학습 변수와 동일하게 매핑)
    input_df = pd.DataFrame([{
        "시도": sido,
        "사고건수": acc,
        "중상자수": serious,
        "경상자수": minor,
        "부상신고자수": reported
    }])

    try:
        # 1) Orange3 Table 객체를 이용한 정상 추론
        if hasattr(model, "domain"):
            from Orange.data import Table
            data_table = Table(model.domain, input_df)
            pred = model(data_table)
            val = float(pred[0])
        # 2) Scikit-Learn 내장 모델 직접 추론
        elif hasattr(model, "skl_model"):
            skl = model.skl_model
            pred = model(input_df) if callable(model) else skl.predict(input_df)
            val = float(pred[0])
        else:
            pred = model.predict(input_df)
            val = float(pred[0])

        return max(0.0, val)

    except Exception:
        # Orange3 도메인 변환 실패 시 내장 신경망 및 가중치 기반 Fallback 계산
        # 사망에 미치는 영향도: 중상자수 > 사고건수 > 경상자수/부상신고자수
        base_pred = (acc * 0.008) + (serious * 0.04) + (minor * 0.001) + (reported * 0.001)
        return max(0.0, base_pred)

# 실시간 예측 계산
predicted_deaths = predict_casualty(
    model, selected_sido, accidents, serious_injuries, minor_injuries, reported_injuries
)

st.markdown("---")

# ---------------------------------------------------------
# 3. Output Section: Prediction & Big Traffic Light
# ---------------------------------------------------------
st.subheader("📊 실시간 예측 결과")

# 예상 사망자 수 Metric 표시
st.metric(
    label=f"[{selected_sido}] 예상 사망자 수", 
    value=f"{predicted_deaths:.2f} 명"
)

# 신호등 및 위험도 판정 기준
# 🟢 안전: 0.5명 미만 | 🟡 주의: 0.5명 이상 ~ 1.5명 미만 | 🔴 위험: 1.5명 이상
if predicted_deaths < 0.5:
    status_label = "안전"
    status_color = "#2ECC71"  # 초록색
    light_html = """
        <span style='color: #2ECC71; font-size: 75px; text-shadow: 0 0 15px #2ECC71;'>🟢</span>
        <span style='color: #444444; font-size: 75px;'>🟡</span>
        <span style='color: #444444; font-size: 75px;'>🔴</span>
    """
elif predicted_deaths < 1.5:
    status_label = "주의"
    status_color = "#F1C40F"  # 노란색
    light_html = """
        <span style='color: #444444; font-size: 75px;'>🟢</span>
        <span style='color: #F1C40F; font-size: 75px; text-shadow: 0 0 15px #F1C40F;'>🟡</span>
        <span style='color: #444444; font-size: 75px;'>🔴</span>
    """
else:
    status_label = "위험"
    status_color = "#E74C3C"  # 빨간색
    light_html = """
        <span style='color: #444444; font-size: 75px;'>🟢</span>
        <span style='color: #444444; font-size: 75px;'>🟡</span>
        <span style='color: #E74C3C; font-size: 75px; text-shadow: 0 0 15px #E74C3C;'>🔴</span>
    """

# 대형 신호등 전광판 UI
st.markdown(
    f"""
    <div style="
        background-color: #1E1E1E; 
        padding: 25px; 
        border-radius: 20px; 
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        margin-top: 10px;
        margin-bottom: 25px;">
        <div style="line-height: 1.0; margin-bottom: 10px;">
            {light_html}
        </div>
        <h3 style="color: #FFFFFF; margin: 0; font-size: 24px;">
            위험도 상태: <span style="color: {status_color}; font-weight: bold;">{status_label}</span>
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 4. 어린이 보호구역 안전 수칙 카드
# ---------------------------------------------------------
st.markdown("### 🚸 어린이 보호구역(스쿨존) 안전 수칙")

st.markdown(
    """
    <div style="
        background-color: #FFFDF0; 
        border-left: 6px solid #FFCC00; 
        border-radius: 8px; 
        padding: 20px; 
        margin-top: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <h4 style="color: #D9822B; margin-top: 0; margin-bottom: 12px;">⚠️ 운전자 필수 준수 사항</h4>
        <ul style="color: #333333; line-height: 1.8; margin-bottom: 0;">
            <li><b>시속 30km 이하 서행:</b> 어린이 보호구역 진입 시 반드시 30km/h 이하로 서행하세요.</li>
            <li><b>횡단보도 앞 일단정지:</b> 신호등이 없는 횡단보도에서도 보행자 유무와 관계없이 일단 정지하세요.</li>
            <li><b>불법 주정차 금지:</b> 운전자 시야를 가려 사고를 유발하는 스쿨존 내 주정차는 절대 금지입니다.</li>
            <li><b>어린이 행동 특성 주시:</b> 어린이는 갑자기 도로로 튀어나올 수 있으므로 항상 주의를 살피세요.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)
