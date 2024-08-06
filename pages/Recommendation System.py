import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import tensorflow as tf
from streamlit_folium import folium_static
import map_recommend
import data

# 페이지 설정
st.set_page_config(page_title="Frequency Off Recommendation System",
                   layout="wide",
                   page_icon="📡")

if not st.session_state.get('authentication_status', False):
    st.info('Please Login from the Home page and try again.')
    st.stop()

# Streamlit 인터페이스 설정
st.title('Cell Off Recommendation System')

# 날짜 입력
date_input = st.date_input('날짜 선택:', datetime(2024, 8, 6))
# 시간 입력
time_input = st.time_input('시간 선택:', time(0, 0))

# 선택한 날짜와 시간을 하나의 datetime 객체로 결합
timestamp_input = datetime.combine(date_input, time_input)

# 모델 선택
model_options = ['모델 1: Rule-based', '모델 2: Autoencoder', '모델 3: K-means Clustering']
selected_model = st.selectbox('사용할 모델을 선택하세요:', model_options)

# Run 버튼
run_button = st.button('Run')

# 가상의 입력 데이터 예시
# 실제 환경에서는 데이터 프레임에서 가져오는 방식으로 구현
input_data = pd.DataFrame({
    'hour': [timestamp_input.hour],
    'is_weekend': [timestamp_input.weekday() >= 5]
    # 추가적인 입력 특성들
})

# 모델 불러오기 및 예측
def load_and_predict(model_name, input_data, df_map, progress_callback=None):
    recommended_cell_states = {}
    
    if progress_callback:
        progress_callback(10)  # 초기 진행 상태
    
    # 각 모델에 맞는 가상 로직
    if model_name == '모델 1: Rule-based':
        # Rule-based 로직
        for idx, row in df_map.iterrows():
            if timestamp_input.hour < 6 or timestamp_input.hour > 22:
                recommended_cell_states[row['enbid_pci']] = 'OFF'
            else:
                recommended_cell_states[row['enbid_pci']] = 'ON'
            if progress_callback:
                progress_callback(10 + 80 * (idx + 1) // len(df_map))  # 진행 상태 업데이트

    elif model_name == '모델 2: Autoencoder':
        # Autoencoder 모델 불러오기
        model = tf.keras.models.load_model('autoencoder_model.h5')
        
        # 입력 데이터 전처리 (예시)
        input_array = df_map[['hour', 'is_weekend']].values  # 필요한 입력 특성 사용
        
        # 모델 예측
        reconstruction = model.predict(input_array)
        reconstruction_error = np.mean(np.square(input_array - reconstruction), axis=1)
        
        if progress_callback:
            progress_callback(60)  # 중간 진행 상태

        # 이상치 탐지 기준 설정 (예시)
        threshold = 0.5  # 예제 임계값
        for idx, row in df_map.iterrows():
            if reconstruction_error[idx] > threshold:
                recommended_cell_states[row['enbid_pci']] = 'OFF'
            else:
                recommended_cell_states[row['enbid_pci']] = 'ON'
            if progress_callback:
                progress_callback(60 + 30 * (idx + 1) // len(df_map))  # 진행 상태 업데이트

    elif model_name == '모델 3: K-means Clustering':
        # K-means 모델 불러오기
        model = tf.keras.models.load_model('kmeans_model.h5')
        
        # 입력 데이터 전처리 (예시)
        input_array = df_map[['hour', 'is_weekend']].values  # 필요한 입력 특성 사용
        
        # 모델 예측
        clusters = model.predict(input_array)
        
        if progress_callback:
            progress_callback(60)  # 중간 진행 상태

        # 클러스터 결과 기반 On/Off 결정 (예시)
        for idx, row in df_map.iterrows():
            if clusters[idx] == 0:
                recommended_cell_states[row['enbid_pci']] = 'OFF'
            else:
                recommended_cell_states[row['enbid_pci']] = 'ON'
            if progress_callback:
                progress_callback(60 + 30 * (idx + 1) // len(df_map))  # 진행 상태 업데이트
    
    return recommended_cell_states

if run_button:
    
    with st.sidebar:
        with st.spinner('데이터 로딩 중...'):
            df, df_map = data.load_data()
            st.sidebar.success('데이터 로드 완료')

    # 프로그래스 바 생성
    progress_bar = st.sidebar.progress(0)

    # 입력값 변환
    timestamp_input = pd.to_datetime(timestamp_input)

    # 모델 실행하여 추천 결과 얻기
    recommended_cell_states = load_and_predict(
        selected_model,
        input_data,
        df_map,
        progress_callback=progress_bar.progress  # 프로그래스 바 업데이트 함수 전달
    )

    # 지도 생성 및 표시
    m = map_recommend.create_map(df_map, recommended_cell_states)

    # 최종 프로그래스 바 업데이트
    progress_bar.progress(100)
    st.sidebar.success('분석 완료')

    # 프로그래스 바 제거
    progress_bar.empty()

    # Folium 지도 표시
    folium_static(m)

    st.write("""
    <style>
    iframe {
        max-width: 2000px;
        width: 100%;
        height: 600px;
        border-radius: 10px;
        border: 1px solid #d3d3d3;
    }
    </style>
    """, unsafe_allow_html=True)
