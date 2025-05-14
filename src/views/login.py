import streamlit as st
from db.client import DBClient
from db.sql import *

db_client = DBClient()

def is_admin(user_login_id):
    admin_ids = ['admin']
    if user_login_id in admin_ids:
        return True
    return False

def check_login(user_login_id):
    return db_client.execute_query(GET_VALID_LOGIN, (user_login_id,))

def show_login():
    st.set_page_config(layout="centered")
    st.title("Login")

    with st.form(key="login_form"):
        user_login_id = st.text_input("User Login ID")
        login_button = st.form_submit_button("Login")

    if login_button:
        valid_login = check_login(user_login_id)
        
        if is_admin(user_login_id):
            st.session_state.logged_in = True
            st.session_state.admin = True
            st.rerun()
        elif len(valid_login) > 0:
            st.session_state.logged_in = True
            st.session_state.admin = False
            st.session_state.instructor_id = int(valid_login.user_id.iloc[0])
            st.session_state.instructor_name = valid_login.user_name.iloc[0]
            st.rerun()
        else:
            st.error("Incorrect User Login ID")