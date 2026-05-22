import streamlit as st

from app.auth import current_user_role, require_auth

st.set_page_config(page_title="Beacon Training Matrix", page_icon="🎓", layout="wide")
require_auth()

st.sidebar.title("Beacon Training Matrix")
st.sidebar.write(f"Role: **{current_user_role()}**")

st.title("Welcome")
st.write("Use the sidebar to navigate. Start on **Dashboard** to see what's expiring.")
