import streamlit as st
import pandas as pd

from db.client import DBClient
from db.sql import *

db_client = DBClient()

def show_admin():
    all_users = db_client.execute_query(GET_ALL_USERS, ())
    all_courses = db_client.execute_query(GET_ALL_COURSES, ())
    all_topics = db_client.execute_query(GET_ALL_TOPICS, ())
    all_entries = db_client.execute_query(GET_ALL_ENTRIES, ())
    all_entries_per_student = db_client.execute_query(GET_ALL_ENTRIES_COUNT_PER_STUDENT, ())

    st.set_page_config(page_title="Admin Dashboard", layout="wide")
    st.sidebar.title("Welcome Admin")
    nav_option = st.sidebar.radio("Navigation", ["Users", "Courses & Enrollment", "Topics", "Entries"])
    logout_button = st.sidebar.button("Logout")
    
    if logout_button:
        st.session_state.logged_in = False
        st.session_state.admin = False
        st.session_state.instructor_id = None
        st.session_state.instructor_name = None
        st.rerun()
            
    if nav_option == "Users":
        st.title("Users")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(all_users))
        with col2:
            st.metric("Registered", (all_users["State"] == 'registered').sum())
        with col3:
            st.metric("Deleted", (all_users["State"] == "deleted").sum())
        
        # Search by username
        search_username = st.text_input("Search by Username", "")
        # Filter by user state
        users_state_filter = st.selectbox("Filter by State", ["All"] + all_users["State"].str.capitalize().dropna().unique().tolist(), key="state_filter")
        
        filtered_users = all_users if users_state_filter == "All" else all_users[all_users["State"].str.capitalize() == users_state_filter]
        
        if search_username:
            searched_user = filtered_users[filtered_users["Username"].str.lower() == search_username.lower()]
            st.dataframe(searched_user)
        else:
            st.dataframe(filtered_users)

    elif nav_option == "Courses & Enrollment":
        # Course
        st.title("Courses")
        st.metric("Total Courses", len(all_courses))

        course_codes = sorted(all_courses["Course Code"].dropna().unique().tolist())
        semesters = sorted(all_courses["Semester"].dropna().unique().tolist())

        # Filter by course code
        course_filter = st.selectbox("Filter by Course Code", ["All"] + course_codes, key="course_filter")
        # Filter by semester
        semester_filter = st.selectbox("Filter by Semester", ["All"] + semesters, key="semester_filter")

        filtered_courses = all_courses

        if course_filter != "All" and semester_filter != "All":
            filtered_courses = all_courses[
                (all_courses["Course Code"] == course_filter) & (all_courses["Semester"] == semester_filter)
            ]
        elif course_filter != "All":
            filtered_courses = all_courses[all_courses["Course Code"] == course_filter]
        elif semester_filter != "All":
            filtered_courses = all_courses[all_courses["Semester"] == semester_filter]

        st.dataframe(filtered_courses)

        # Enrollment by course
        st.title("Enrollment")
        st.subheader(f"Course: {course_filter}") if course_filter != "All" else None

        # Fetch enrolled users by course name
        enrolled_by_course = db_client.execute_query(GET_ENROLLMENT_BY_COURSE, (course_filter,))
        st.dataframe(enrolled_by_course)

    elif nav_option == "Topics":
        st.title("Topics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Topics", len(all_topics))
        with col2:
            st.metric("Active", (all_topics["State"] == 'active').sum())
        with col3:
            st.metric("Unpublished", (all_topics["State"] == 'unpublished').sum())
        with col4:
            st.metric("Deleted", (all_topics["State"] == 'deleted').sum())
        
        # Search by topic author
        search_author = st.text_input("Search by Author", "")
        # Filter by topic state
        topic_state_filter = st.selectbox("Filter by State", ["All"] + all_topics["State"].str.capitalize().dropna().unique().tolist(), key="topic_state_filter")
        # Filter by course name
        topic_course_filter = st.selectbox("Filter by Course Name", ["All"] + all_topics["Course Name"].dropna().unique().tolist(), key="topic_course_filter")

        filtered_topics = all_topics
        
        if topic_state_filter != "All" and topic_course_filter != "All":
            filtered_topics = all_topics[
                (all_topics["State"].str.capitalize() == topic_state_filter) & (all_topics["Course Name"] == topic_course_filter)
            ]
        elif topic_state_filter != "All":
            filtered_topics = all_topics[all_topics["State"].str.capitalize() == topic_state_filter]
        elif topic_course_filter != "All":
            filtered_topics = all_topics[all_topics["Course Name"] == topic_course_filter]
        
        if search_author:
            searched_topic = filtered_topics[filtered_topics["Author"].str.lower() == search_author.lower()]
            st.dataframe(searched_topic)
        else:
            st.dataframe(filtered_topics)

    elif nav_option == "Entries":
        st.title("Entries")
        
        # Filter by topic
        entries_topic_filter = st.selectbox("Filter by Topic", sorted(["All"] + all_entries["Topic Title"].dropna().unique().tolist()), key="entries_topic_filter")
        # Filter by author
        entries_author_filter = st.selectbox("Filter by Entry Author", sorted(["All"] + all_entries["Entry Author"].dropna().unique().tolist()), key="entries_author_filter")
        
        filtered_entries = all_entries
        
        if entries_topic_filter != "All" and entries_author_filter != "All":
            filtered_entries = all_entries[
                (all_entries["Topic Title"] == entries_topic_filter) & (all_entries["Entry Author"] == entries_author_filter)
            ]
        elif entries_topic_filter != "All":
            filtered_entries = all_entries[all_entries["Topic Title"] == entries_topic_filter]
        elif entries_author_filter != "All":
            filtered_entries = all_entries[all_entries["Entry Author"] == entries_author_filter]
        
        st.dataframe(filtered_entries)
        
        # Student Participation
        st.title("Student Participation")
        st.subheader("By Topic")

        topic_entries_count = all_topics[["Title", "# of Active Entries"]].set_index("Title")
        st.bar_chart(topic_entries_count)
        
        st.subheader("By Student")
        st.dataframe(all_entries_per_student)
        


