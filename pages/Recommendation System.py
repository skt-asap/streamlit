import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import tensorflow as tf
from streamlit_folium import folium_static
import map_recommend
import data

st.set_page_config(page_title="Frequency Off Recommendation System",
                   layout="wide",
                   page_icon="📡")

if not st.session_state.get('authentication_status', False):
    st.write("### 🚨 **Access Denied** 🚨")
    st.html("You do not have permission to view this page.<br>Please log in.")
    st.stop()

st.title('Cell Off Recommendation System')

date_input = st.date_input('날짜 선택:', datetime(2024, 8, 6))
time_input = st.time_input('시간 선택:', time(0, 0))

timestamp_input = datetime.combine(date_input, time_input)

model_options = ['모델 1: Rule-based']
selected_model = st.selectbox('사용할 모델을 선택하세요:', model_options)

run_button = st.button('Run')

input_data = pd.DataFrame({
    'hour': [timestamp_input.hour],
    'is_weekend': [timestamp_input.weekday() >= 5]
})

def load_and_predict(model_name, input_data, df_map, progress_callback=None):
    recommended_cell_states = {}

    if progress_callback:
        progress_callback(10)

    if model_name == '모델 1: Rule-based':
        for idx, row in df_map.iterrows():
            if timestamp_input.hour < 6 or timestamp_input.hour > 22:
                recommended_cell_states[row['enbid_pci']] = 'OFF'
            else:
                recommended_cell_states[row['enbid_pci']] = 'ON'
            if progress_callback:
                progress_callback(10 + 80 * (idx + 1) // len(df_map))

    return recommended_cell_states

if run_button:

    # with st.sidebar:
    #     with st.spinner('데이터 로딩 중...'):
    #         df, df_map = data.load_data()
    #         st.sidebar.success('데이터 로드 완료')
    df, df_map = data.load_data()

    progress_bar = st.sidebar.progress(0)

    timestamp_input = pd.to_datetime(timestamp_input)

    recommended_cell_states = load_and_predict(
        selected_model,
        input_data,
        df_map,
        progress_callback=progress_bar.progress
    )

    m = map_recommend.create_map(df_map, recommended_cell_states)

    progress_bar.progress(100)
    st.sidebar.success('분석 완료')

    progress_bar.empty()

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
