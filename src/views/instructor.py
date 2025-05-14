import streamlit as st
import pandas as pd

from db.client import DBClient
from db.sql import *

db_client = DBClient()

def show_instructor():
    instructor_id = st.session_state.instructor_id
    
    all_instructor_courses = db_client.execute_query(GET_ALL_INSTRUCTOR_COURSES, (instructor_id,))
    all_instructor_topics = db_client.execute_query(GET_ALL_INSTRUCTOR_TOPICS, (instructor_id,))
    all_instructor_entries = db_client.execute_query(GET_ALL_INSTRUCTOR_ENTRIES, (instructor_id,))
    all_entries_per_student = db_client.execute_query(GET_COURSE_ENTRIES_COUNT_PER_STUDENT, (instructor_id,))

    st.set_page_config(page_title="Instructor Dashboard", layout="wide")
    st.sidebar.title(f'Welcome {st.session_state.instructor_name}')
    nav_option = st.sidebar.radio("Navigation", ["Courses & Enrollment", "Topics", "Entries"])
    logout_button = st.sidebar.button("Logout")
    
    if logout_button:
        st.session_state.logged_in = False
        st.session_state.admin = False
        st.session_state.instructor_id = None
        st.session_state.instructor_name = None
        st.rerun()

    if nav_option == "Courses & Enrollment":
        # Course
        st.title("Courses")
        st.metric("Total Registered Courses", len(all_instructor_courses))

        course_codes = sorted(all_instructor_courses["Course Code"].dropna().unique().tolist())
        semesters = sorted(all_instructor_courses["Semester"].dropna().unique().tolist())

        # Filter by course code
        course_filter = st.selectbox("Filter by Course Code", course_codes, key="course_filter")
        # Filter by semester
        semester_filter = st.selectbox("Filter by Semester", ["All"] + semesters, key="semester_filter")

        filtered_courses = all_instructor_courses

        if course_filter != "All" and semester_filter != "All":
            filtered_courses = all_instructor_courses[
                (all_instructor_courses["Course Code"] == course_filter) & (all_instructor_courses["Semester"] == semester_filter)
            ]
        elif course_filter != "All":
            filtered_courses = all_instructor_courses[all_instructor_courses["Course Code"] == course_filter]
        elif semester_filter != "All":
            filtered_courses = all_instructor_courses[all_instructor_courses["Semester"] == semester_filter]

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
            st.metric("Total Topics", len(all_instructor_topics))
        with col2:
            st.metric("Active", (all_instructor_topics["State"] == 'active').sum())
        with col3:
            st.metric("Unpublished", (all_instructor_topics["State"] == 'unpublished').sum())
        with col4:
            st.metric("Deleted", (all_instructor_topics["State"] == 'deleted').sum())
        
        # Filter by topic state
        topic_state_filter = st.selectbox("Filter by State", ["All"] + all_instructor_topics["State"].str.capitalize().dropna().unique().tolist(), key="topic_state_filter")
        # Filter by course name
        topic_course_filter = st.selectbox("Filter by Course Name", all_instructor_topics["Course Name"].dropna().unique().tolist(), key="topic_course_filter")

        filtered_topics = all_instructor_topics
        
        if topic_state_filter != "All" and topic_course_filter != "All":
            filtered_topics = all_instructor_topics[
                (all_instructor_topics["State"].str.capitalize() == topic_state_filter) & (all_instructor_topics["Course Name"] == topic_course_filter)
            ]
        elif topic_state_filter != "All":
            filtered_topics = all_instructor_topics[all_instructor_topics["State"].str.capitalize() == topic_state_filter]
        elif topic_course_filter != "All":
            filtered_topics = all_instructor_topics[all_instructor_topics["Course Name"] == topic_course_filter]
        
        st.dataframe(filtered_topics)

    elif nav_option == "Entries":
        st.title("Entries")
        
        # Filter by topic
        entries_topic_filter = st.selectbox("Filter by Topic", sorted(["All"] + all_instructor_entries["Topic Title"].dropna().unique().tolist()), key="entries_topic_filter")
        # Filter by author
        entries_author_filter = st.selectbox("Filter by Entry Author", sorted(["All"] + all_instructor_entries["Entry Author"].dropna().unique().tolist()), key="entries_author_filter")
        
        filtered_entries = all_instructor_entries
        
        if entries_topic_filter != "All" and entries_author_filter != "All":
            filtered_entries = all_instructor_entries[
                (all_instructor_entries["Topic Title"] == entries_topic_filter) & (all_instructor_entries["Entry Author"] == entries_author_filter)
            ]
        elif entries_topic_filter != "All":
            filtered_entries = all_instructor_entries[all_instructor_entries["Topic Title"] == entries_topic_filter]
        elif entries_author_filter != "All":
            filtered_entries = all_instructor_entries[all_instructor_entries["Entry Author"] == entries_author_filter]
        
        st.dataframe(filtered_entries)
        
        # Student Participation
        st.title("Student Participation")
        st.subheader("By Topic")
        topic_entries_count = all_instructor_topics[["Title", "# of Active Entries"]].set_index("Title")
        st.bar_chart(topic_entries_count)
        
        st.subheader("By Student")        
        st.dataframe(all_entries_per_student)
