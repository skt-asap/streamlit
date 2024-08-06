import pandas as pd
import altair as alt

def create_area_chart(filtered_data_long, selected_cell):
    chart = alt.Chart(filtered_data_long).mark_area().encode(
        x=alt.X('timestamp:T', title='Timestamp'),
        y=alt.Y('Value:Q', title='RB Used'),
        color=alt.Color('RB:N', title='RB Type'),
        tooltip=['timestamp:T', 'RB:N', 'Value:Q']
    ).properties(
        width=800,
        height=400,
        title=f'RB Usage for Cell ID: {selected_cell}'
    ).interactive()

    return chart
