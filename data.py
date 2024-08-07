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
    request = drive_service.files().get_media(fileId=file_id)

    file_buffer = io.BytesIO()

    downloader = MediaIoBaseDownload(file_buffer, request)
    done = False

    progress_bar = st.sidebar.progress(0)
    progress_text = st.sidebar.empty()
    progress_text.text("데이터 불러오는 중...")

    while not done:
        status, done = downloader.next_chunk()
        progress = int(status.progress() * 100)
        progress_bar.progress(progress)
        progress_text.text(f"데이터 불러오는 중...({progress}%)")

    file_buffer.seek(0)
    df = pd.read_csv(file_buffer)

    df['ru_svc_lat_val'] = df['ru_svc_lat_val'].astype(float)
    df['ru_svc_lng_val'] = df['ru_svc_lng_val'].astype(float)

    df_map = df.drop_duplicates(subset=['ru_svc_lat_val', 'ru_svc_lng_val'])

    progress_bar.empty()
    progress_text.empty()
    st.sidebar.success("데이터 로드 완료!")

    return df, df_map
