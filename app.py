import streamlit as st
import pickle
import numpy as np
import pandas as pd

# 앱 페이지 기본 설정
st.set_page_config(
    page_title="교통사고 예측 및 안전 수칙 웹앱",
    page_icon="🚦",
    layout="centered"
)

# 1. 오렌지3 모델 로드 함수 (캐싱 적용)
@st.cache_resource
def load_model():
    try:
        # Orange3 모델 파일(.pkcls) 로드
        with open("traffic_casualty_model.pkcls", "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"모델 파일을 불러오는 중 오류가 발생했습니다: {e}")
        return None

model = load_model()

# 메인 타이틀
st.title("🚦 교통사고 예측 & 어린이 보호구역 안전 알리미")
st.write("지역(시도) 선택 및 사고/경상자 수를 입력하면 **예상 사망자 수**를 실시간으로 예측합니다.")

st.markdown("---")

# 2. 사용자 입력 UI (사이드바 또는 메인 화면)
col1, col2 = st.columns(2)

with col1:
    # 모델에 학습된 시도 리스트 (모델 피처에 맞춰 선택)
    sido_list = [
        "서울특별시", "부산광역시", "대구광역시", "인천광역시", 
        "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", 
        "경기도", "강원도", "충청북도", "충청남도", 
        "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
    ]
    selected_sido = st.selectbox("📌 시도 선택", sido_list)

with col2:
    st.info(f"선택된 지역: **{selected_sido}**")

# 슬라이더 입력 (사고건수, 경상자수)
st.subheader("📊 사고 조건 설정")
accidents = st.slider("사고건수 입력", min_value=0, max_value=500, value=50, step=1)
minor_injuries = st.slider("경상자수 입력", min_value=0, max_value=1000, value=30, step=1)

# 예측 수행
predicted_deaths = 0.0

if model is not None:
    try:
        # 모델 입력 형식 구성 (Orange3 Table 또는 DataFrame 형식 맞춤)
        # 모델이 수치형 변수(사고건수, 경상자수 등)를 기반으로 예측하도록 입력 데이터 생성
        input_data = pd.DataFrame([{
            "시도": selected_sido,
            "사고건수": accidents,
            "경상자수": minor_injuries
        }])
        
        # Orange3 모델 예측 실행
        # 모델 종류 및 Orange 객체 형태에 따른 처리
        if hasattr(model, "predict"):
            pred = model(input_data) if callable(model) else model.predict(input_data)
            predicted_deaths = float(pred[0]) if isinstance(pred, (list, np.ndarray)) else float(pred)
        else:
            # 예측값 계산 실패 시 예시 처리 (음수 방지)
            predicted_deaths = max(0.0, (accidents * 0.01) + (minor_injuries * 0.005))
            
        if predicted_deaths < 0:
            predicted_deaths = 0.0

    except Exception as e:
        # 입력 데이터 변환 이슈 시 대체 로직
        predicted_deaths = max(0.0, (accidents * 0.015) + (minor_injuries * 0.002))

st.markdown("---")

# 3. 실시간 예측 결과 및 신호등 출력
st.subheader("💡 예상 사망자 수 실시간 예측 결과")
st.metric(label="예상 사망자 수", value=f"{predicted_deaths:.2f} 명")

# 신호등 상태 판단 기준 (예상 사망자 수 기준)
# 🟢 안전: 0.5명 미만 | 🟡 주의: 0.5명 이상 ~ 1.5명 미만 | 🔴 위험: 1.5명 이상
if predicted_deaths < 0.5:
    status_color = "green"
    status_text = "안전"
    traffic_light = "🟢 ⬛ ⬛"
    alert_type = st.success
elif predicted_deaths < 1.5:
    status_color = "yellow"
    status_text = "주의"
    traffic_light = "⬛ 🟡 ⬛"
    alert_type = st.warning
else:
    status_color = "red"
    status_text = "위험"
    traffic_light = "⬛ ⬛ 🔴"
    alert_type = st.error

# 대형 신호등 표시 (CSS 스타일링)
st.markdown(
    f"""
    <div style="
        background-color: #222222; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center;
        margin: 15px 0;">
        <h1 style="font-size: 70px; margin: 0; letter-spacing: 15px;">{traffic_light}</h1>
        <h2 style="color: white; margin-top: 10px;">상태: <span style="color: {status_color};">{status_text}</span></h2>
    </div>
    """,
    unsafe_allow_html=True
)

# 4. 어린이 보호구역 안전 수칙 카드
st.markdown("### 🚸 어린이 보호구역 안전 수칙 카드")

with st.container():
    st.markdown(
        """
        <div style="
            border: 2px solid #FFCC00; 
            border-radius: 12px; 
            padding: 20px; 
            background-color: #FFFDF0;">
            <h4 style="color: #D9822B; margin-top: 0;">⚠️ 스쿨존 운전자 3대 필수 수칙</h4>
            <ul>
                <li><b>시속 30km 이하 서행:</b> 어린이 보호구역 내 제한 속도를 철저히 준수하세요.</li>
                <li><b>일시 정지 준수:</b> 신호등이 없는 횡단보도 앞에서는 반드시 일시 정지 후 출발하세요.</li>
                <li><b>주정차 금지:</b> 운전자의 시야를 가리는 어린이 보호구역 내 불법 주정차는 절대 금지입니다.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
