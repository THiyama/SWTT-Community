import streamlit as st

from utils.utils import display_team_id_sidebar, get_session

session = get_session()
display_team_id_sidebar()

st.markdown("in develop...")
