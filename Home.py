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
        file.close()

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
    authenticator  = st_authenticator()
    name, authentication_status, username = authenticator.login("main")

    if authentication_status:
        st.session_state.authentication_status = True
        st.success(f"Logged Successfully")
        authenticator.logout('**Logout**', 'main', key='unique_key')
    elif authentication_status is False:
        st.session_state.authentication_status = False
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.session_state.authentication_status = None
        st.warning('Please enter your username and password')
