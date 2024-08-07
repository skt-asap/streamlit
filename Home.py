import streamlit as st
from streamlit.logger import get_logger
import streamlit_authenticator as stauth
import yaml

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="SKT AI Fellowship Team ASAP",
        page_icon="📡",
        layout="wide"
    )

    st.write("# SKT AI Fellowship Team ASAP 👋")

def st_authenticator():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=stauth.SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    return authenticator

if __name__ == "__main__":
    run()
    authenticator = st_authenticator()

    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
        st.session_state['username'] = None

    name, authentication_status, username = authenticator.login("main", "Login")

    if authentication_status:
        st.session_state['authentication_status'] = True
        st.session_state['username'] = username
        st.success(f"{name}님, 환영합니다!")
        authenticator.logout('Logout', 'main', key='unique_key')

    elif authentication_status is False:
        st.session_state['authentication_status'] = False
        st.error('아이디/비밀번호가 잘못되었습니다.')

    elif authentication_status is None:
        st.session_state['authentication_status'] = None
        st.warning('아이디와 비밀번호를 입력해주세요.')

