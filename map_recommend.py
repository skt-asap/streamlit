import folium
from folium import CustomIcon, DivIcon

def create_map(dataframe, recommendations):
    # 지도 생성
    m = folium.Map(
        location=[35.1796, 129.0756],
        zoom_start=12,
        control_scale=True,
        tiles='CartoDB positron'
    )

    # 각 위치에 마커 추가
    for idx, row in dataframe.iterrows():
        cell_id = row['enbid_pci']

        # 해당 cell_id의 추천 상태 가져오기
        recommended_cell_state = recommendations.get(cell_id, 'OFF')

        # 상태에 따라 아이콘 색상 선택
        if recommended_cell_state == 'ON':
            color = 'blue'
        else:
            color = 'red'

        custom_icon = DivIcon(
            html=f"""
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="20" height="20">
              <circle cx="10" cy="10" r="5.625" fill="{color}" stroke="#000000" stroke-width="1.25"/>
            </svg>
            """,
            icon_size=(20, 20),
            icon_anchor=(10, 10)
        )

        # Marker 추가 및 팝업 설정
        marker = folium.Marker(
            location=(row['ru_svc_lat_val'], row['ru_svc_lng_val']),
            icon=custom_icon,
            tooltip=f'{cell_id} - {recommended_cell_state}'
        )

        marker.add_to(m)

    return m