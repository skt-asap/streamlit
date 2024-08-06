# data_processing.py
import pandas as pd

file_path = '../../Data/Archive 2/ELG_Busan_PoC_per_CA_site_0226_0407.csv'

def load_data():
    # 데이터 로드
    df = pd.read_csv(file_path)

    # 좌표 데이터를 실수로 변환
    df['ru_svc_lat_val'] = df['ru_svc_lat_val'].astype(float)
    df['ru_svc_lng_val'] = df['ru_svc_lng_val'].astype(float)

    # 중복된 위도 및 경도 값 제거
    df_map = df.drop_duplicates(subset=['ru_svc_lat_val', 'ru_svc_lng_val'])

    return df, df_map
