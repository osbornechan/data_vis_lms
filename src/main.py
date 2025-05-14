import streamlit as st
from views.admin import show_admin
from views.login import show_login
from views.instructor import show_instructor

from db.client import DBClient
from db.sql import *

db_client = DBClient()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.admin = False
    st.session_state.instructor_id = None
    st.session_state.instructor_name = None
    
if st.session_state.logged_in and st.session_state.admin:
    show_admin()
elif st.session_state.logged_in:
    show_instructor()
else:    
    show_login()
