import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import data
import map
import js
import chart

# Streamlit 페이지 설정
st.set_page_config(page_title="Dashboard",
                   layout="wide",
                   page_icon="🗺️")

if not st.session_state.get('authentication_status', False):
    st.info('Please Login from the Home page and try again.')
    st.stop()

# 데이터 로드 및 처리
with st.sidebar:
    with st.spinner("데이터 로드 중..."):
        df, df_map = data.load_data()
        st.sidebar.success("데이터 로드 완료!")

# 지도 생성
cell_map = map.create_map(df_map)

# Streamlit 세션 상태 초기화
if 'selected_cell' not in st.session_state:
    st.session_state['selected_cell'] = ""

if 'selected_rbs' not in st.session_state:
    st.session_state['selected_rbs'] = ['RB_800']

# Streamlit 대시보드 함수
def main():
    # 대시보드 제목
    st.markdown("# Dashboard")

    # Folium 지도를 Streamlit에 삽입
    show_map = st.sidebar.checkbox("지도 보기", True)
    if show_map:
        st.markdown("### 🗺️ 부산 PoC 셀 사이트")
        
        folium_static(cell_map)

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

        # 자바스크립트
        js.set_marker_click_template()

    unique_cells = df['enbid_pci'].unique().tolist()

    show_chart = st.sidebar.checkbox("차트 보기", True)
    if show_chart:
        selected_cell = st.selectbox("조회할 셀 ID:", unique_cells, index=unique_cells.index(st.session_state['selected_cell']) if st.session_state['selected_cell'] in unique_cells else 0)
        st.session_state['selected_cell'] = selected_cell

        # 선택한 셀 ID에 대해 데이터프레임 필터링 및 복사
        cell_data = df[df['enbid_pci'] == st.session_state['selected_cell']].copy()

        if not cell_data.empty:
            # 장비 조건에 따라 사용할 수 있는 RB 컬럼 결정
            rb_options = []
            if cell_data['Equip_800'].eq(1).any():
                rb_options.append('RB_800')
            if cell_data['Equip_1800'].eq(1).any():
                rb_options.append('RB_1800')
            if cell_data['Equip_2100'].eq(1).any():
                rb_options.append('RB_2100')
            if cell_data['Equip_2600_10'].eq(1).any():
                rb_options.append('RB_2600_10')
            if cell_data['Equip_2600_20'].eq(1).any():
                rb_options.append('RB_2600_20')

            # 사용 가능한 옵션에 따라 선택한 RB 업데이트
            selected_rbs = st.multiselect("RB 컬럼:", rb_options, default=[rb for rb in st.session_state['selected_rbs'] if rb in rb_options])
            st.session_state['selected_rbs'] = selected_rbs

            # 타임스탬프를 datetime으로 변환
            cell_data['timestamp'] = pd.to_datetime(cell_data['timestamp'])

            # 슬라이더의 날짜 범위 설정을 위해 datetime 객체 사용
            min_date = cell_data['timestamp'].min().to_pydatetime()
            max_date = cell_data['timestamp'].max().to_pydatetime()

            # 날짜 범위를 선택할 수 있는 슬라이더 추가
            start_date, end_date = st.slider(
                "날짜 범위:",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="MM/DD/YY"
            )

            # 선택한 날짜 범위에 따라 데이터 필터링
            filtered_data = cell_data[(cell_data['timestamp'] >= start_date) & (cell_data['timestamp'] <= end_date)]

            # Altair에 적합한 long-form 데이터프레임 생성
            filtered_data_long = pd.melt(
                filtered_data,
                id_vars=['timestamp'],
                value_vars=st.session_state['selected_rbs'],
                var_name='RB',
                value_name='Value'
            )

            # 차트 모듈을 사용하여 영역 차트 생성
            chart_obj = chart.create_area_chart(filtered_data_long, st.session_state['selected_cell'])

            # 차트 표시
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.write("선택한 셀 ID에 대한 데이터가 없습니다.")

if __name__ == "__main__":
    main()
