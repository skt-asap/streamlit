import streamlit as st
from streamlit_folium import folium_static
import pandas as pd
import data
import map
import js
import chart

st.set_page_config(page_title="Dashboard",
                   layout="wide",
                   page_icon="🗺️")

if not st.session_state.get('authentication_status', False):
    st.write("### 🚨 **접근 불가** 🚨")
    st.write("이 페이지를 볼 수 있는 권한이 없습니다.<br>로그인해 주세요.", unsafe_allow_html=True)
    st.stop()

df, df_map = data.load_data()

cell_map = map.create_map(df_map)

if 'selected_cell' not in st.session_state:
    st.session_state['selected_cell'] = "33011_221"

if 'selected_rbs' not in st.session_state:
    st.session_state['selected_rbs'] = ['RB_800', 'RB_1800', 'RB_2100', 'RB_2600_10', 'RB_2600_20']

def main():
    st.markdown("# Dashboard")

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

        # JavaScript
        js.set_marker_click_template()

    unique_cells = df['enbid_pci'].unique().tolist()

    show_chart = st.sidebar.checkbox("차트 보기", True)
    if show_chart:
        def update_selected_cell():
            st.session_state['selected_cell'] = st.session_state['selected_cell_dropdown']

        st.selectbox(
            "조회할 셀 ID:",
            unique_cells,
            index=unique_cells.index(st.session_state['selected_cell']) if st.session_state['selected_cell'] in unique_cells else 0,
            key="selected_cell_dropdown",
            on_change=update_selected_cell
        )

        cell_data = df[df['enbid_pci'] == st.session_state['selected_cell']].copy()

        if not cell_data.empty:
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

            def update_selected_rbs():
                st.session_state['selected_rbs'] = st.session_state['selected_rbs_multiselect']

            st.multiselect(
                "RB 컬럼:",
                rb_options,
                default=[rb for rb in st.session_state['selected_rbs'] if rb in rb_options],
                key="selected_rbs_multiselect",
                on_change=update_selected_rbs
            )

            cell_data['timestamp'] = pd.to_datetime(cell_data['timestamp'])

            min_date = cell_data['timestamp'].min().to_pydatetime()
            max_date = cell_data['timestamp'].max().to_pydatetime()

            start_date, end_date = st.slider(
                "날짜 범위:",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="MM/DD/YY"
            )

            filtered_data = cell_data[(cell_data['timestamp'] >= start_date) & (cell_data['timestamp'] <= end_date)]

            filtered_data_long = pd.melt(
                filtered_data,
                id_vars=['timestamp'],
                value_vars=st.session_state['selected_rbs'],
                var_name='RB',
                value_name='Value'
            )

            chart_obj = chart.create_area_chart(filtered_data_long, st.session_state['selected_cell'])
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.write("선택한 셀 ID에 대한 데이터가 없습니다.")

if __name__ == "__main__":
    main()
