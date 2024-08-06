import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Google Drive 및 Sheets API 인증
scope = [
    "https://www.googleapis.com/auth/drive.readonly"
]
credentials = Credentials.from_service_account_info(st.secrets["google"], scopes=scope)
file_id = st.secrets["drive"]["file_id"]

drive_service = build('drive', 'v3', credentials=credentials)

@st.cache_data(show_spinner=False)
def load_data():
    """
    Google Drive에서 CSV 파일을 다운로드하여 pandas DataFrame으로 로드합니다.
    다운로드 진행 상황을 Streamlit의 사이드바에 프로그레스 바로 표시합니다.
    """
    # 파일 다운로드 요청
    request = drive_service.files().get_media(fileId=file_id)

    # 파일 다운로드 버퍼 생성
    file_buffer = io.BytesIO()

    # 파일 다운로드 수행
    downloader = MediaIoBaseDownload(file_buffer, request)
    done = False

    # Streamlit sidebar에 프로그레스 바 생성
    progress_bar = st.sidebar.progress(0)
    progress_text = st.sidebar.empty()  # 프로그레스 상태 텍스트
    progress_text.text("데이터 불러오는 중...")

    # 다운로드 진행상황 업데이트
    while not done:
        status, done = downloader.next_chunk()
        progress = int(status.progress() * 100)
        progress_bar.progress(progress)  # 프로그레스 바 업데이트
        progress_text.text(f"데이터 불러오는 중...({progress}%)")

    # 버퍼를 데이터프레임으로 읽기
    file_buffer.seek(0)  # 버퍼의 시작 위치로 이동
    df = pd.read_csv(file_buffer)

    # 좌표 데이터를 실수로 변환
    df['ru_svc_lat_val'] = df['ru_svc_lat_val'].astype(float)
    df['ru_svc_lng_val'] = df['ru_svc_lng_val'].astype(float)

    # 중복된 위도 및 경도 값 제거
    df_map = df.drop_duplicates(subset=['ru_svc_lat_val', 'ru_svc_lng_val'])

    progress_bar.empty()  # 프로그레스 바 제거
    progress_text.empty()
    st.sidebar.success("데이터 로드 완료!")

    return df, df_map
