import streamlit as st
import pickle
import numpy as np
import pandas as pd

# ---------------------------------------------------------
# Page Configuration & Custom CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="교통사고 사망자 예측 & 안전 모니터링",
    page_icon="🚦",
    layout="centered"
)

# 3중 따옴표(triple-quoted string) 시작
st.markdown("""
    <style>
    /* 메인 타이틀 강조 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    
    /* 신호등 전광판 카드 */
    .traffic-box {
        background: linear-gradient(145deg, #18181b, #09090b);
        border: 2px solid #27272a;
        border-radius: 24px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.4);
        margin: 20px 0;
    }
    
    /* 램프 소켓 공통 스타일 */
    .light-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: inline-block;
        margin: 0 12px;
        background-color: #27272a;
        box-shadow: inset 0 4px 8px rgba(0,0,0,0.8);
        transition: all 0.5s ease;
    }
    
    /* 활성화된 램프 애니메이션 */
    .light-green.active {
        background-color: #22c55e;
        box-shadow: 0 0 30px #22c55e, inset 0 -4px 10px rgba(255,255,255,0.4);
        animation: pulse-green 2s infinite;
    }
    .light-yellow.active {
        background-color: #eab308;
        box-shadow: 0 0 30px #eab308, inset 0 -4px 10px rgba(255,255,255,0.4);
        animation: pulse-yellow 2s infinite;
    }
    .light-red.active {
        background-color: #ef4444;
        box-shadow: 0 0 30px #ef4444, inset 0 -4px 10px rgba(255,255,255,0.4);
        animation: pulse-red 1.5s infinite;
    }
    
    @keyframes pulse-red {
        0%, 100% { transform: scale(1); box-shadow: 0 0 30px #ef4444; }
        50% { transform: scale(1.08); box-shadow: 0 0 45px #ef4444; }
    }
    @keyframes pulse-yellow {
        0%, 100% { transform: scale(1); box-shadow: 0 0 30px #eab308; }
        50% { transform: scale(1.05); box-shadow: 0 0 40px #eab308; }
    }
    @keyframes pulse-green {
        0%, 100% { transform: scale(1); box-shadow: 0 0 30px #22c55e; }
        50% { transform: scale(1.03); box-shadow: 0 0 35px #22c55e; }
    }

    /* 어린이 보호구역 수칙 카드 디자인 */
    .school-zone-card {
        border-radius: 16px;
        padding: 24px;
        margin-top: 25px;
        transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True) # 3중 따옴표 정상 종료

# ---------------------------------------------------------
# 1. Model Loading
# ---------------------------------------------------------
@st.cache_resource
def load_orange_model(model_path="traffic_casualty_model.pkcls"):
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"모델 파일('{model_path}') 로드 실패: {e}")
        return None

model = load_orange_model()

# ---------------------------------------------------------
# Header & UI Title
# ---------------------------------------------------------
st.markdown('<div class="main-title">🚦 교통사고 사망자 수 실시간 예측 & 안전 모니터링</div>', unsafe_allow_html=True)
st.write("지역별 사고 조건과 부상자 수치를 슬라이더로 조절하여 **위험도 예측 결과**를 실시간으로 모니터링하세요.")

st.markdown("---")

# --------------------------------
