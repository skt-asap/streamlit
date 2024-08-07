import folium
from folium import CustomIcon, DivIcon

def create_map(dataframe):
    m = folium.Map(
        location=[35.1796, 129.0756],
        zoom_start=12,
        control_scale=True,
        tiles='CartoDB positron'
    )

    for idx, row in dataframe.iterrows():
        cell_id = row['enbid_pci']

        color = 'green'
        custom_icon = DivIcon(
            html=f"""
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="20" height="20">
              <circle cx="10" cy="10" r="5.625" fill="{color}" stroke="#000000" stroke-width="1.25"/>
            </svg>
            """,
            icon_size=(20, 20),
            icon_anchor=(10, 10)
        )

        marker = folium.Marker(
            # popup=f'Cell ID: {cell_id}',
            location=(row['ru_svc_lat_val'], row['ru_svc_lng_val']),
            icon=custom_icon,
            tooltip=f'{cell_id}'
        )

        marker.add_to(m)

    return m