# This includes Pagination + Done toggle + Edit + Hide Not Done

import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

# Auth helpers
def login_user(email, password):
    response = requests.post(f"{API_URL}/login", data={"username": email, "password": password})
    return response.json()

def signup_user(email, password):
    response = requests.post(f"{API_URL}/signup", json={"email": email, "password": password})
    return response.json()

def get_tasks(token, skip=0, limit=10):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/tasks?skip={skip}&limit={limit}", headers=headers)
    return response.json()

def create_task(token, title, description, due_date):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": description,
        "due_date": due_date.isoformat()
    }
    response = requests.post(f"{API_URL}/tasks", json=data, headers=headers)
    return response.json()

def delete_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{API_URL}/tasks/{task_id}", headers=headers)
    return response.json()

def update_task(token, task_id, title, description, due_date, done=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": description,
        "due_date": due_date,
    }
    if done is not None:
        data["done"] = done
    response = requests.put(f"{API_URL}/tasks/{task_id}", json=data, headers=headers)
    return response.json()


# Session defaults
if "token" not in st.session_state:
    st.session_state.token = None
if "page" not in st.session_state:
    st.session_state.page = 1
if "editing_task" not in st.session_state:
    st.session_state.editing_task = None

# UI
st.title("📝 To-Do App")
menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

# Sign up
if choice == "Sign Up":
    st.subheader("Create Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        result = signup_user(email, password)
        st.success("Account created! Now log in.")

# Login
elif choice == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        token_data = login_user(email, password)
        if "access_token" in token_data:
            st.session_state.token = token_data["access_token"]
            st.success("Logged in!")
        else:
            st.error("Login failed")

# Task Dashboard
if st.session_state.token:
    st.subheader("📋 Task List")

    limit = 10
    skip = (st.session_state.page - 1) * limit
    tasks = get_tasks(st.session_state.token, skip=skip, limit=limit)

    if not tasks:
        st.info("No tasks available.")
    else:
        for task in tasks:
            col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
            with col1:
                checkbox_key = f"check_{task['id']}"
                is_done = st.checkbox(task["title"], value=task["done"], key=checkbox_key)
                if is_done != task["done"]:
                    update_task(st.session_state.token, task["id"], task["title"], task["description"], task["due_date"], done=is_done)
                    st.rerun()

                st.markdown(f"📅 Due: {task['due_date']}" if task['due_date'] else "")
                if not task["done"]:
                    st.markdown("❌ Not Done")

            with col2:
                if st.button("🗑️", key=f"delete_{task['id']}"):
                    delete_task(st.session_state.token, task["id"])
                    st.rerun()

            with col3:
                if st.button("✏️", key=f"edit_{task['id']}"):
                    st.session_state.editing_task = task["id"]

    # Pagination
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_left:
        if st.session_state.page > 1 and st.button("⏮️ Previous"):
            st.session_state.page -= 1
            st.rerun()
    with col_center:
        st.markdown(f"<center>📄 Page {st.session_state.page}</center>", unsafe_allow_html=True)
    with col_right:
        if len(tasks) == limit and st.button("Next ⏭️"):
            st.session_state.page += 1
            st.rerun()

    # Edit Task Form
    if st.session_state.editing_task:
        task = next((t for t in tasks if t["id"] == st.session_state.editing_task), None)
        if task:
            st.subheader("✏️ Edit Task")
            title = st.text_input("Task Title", value=task["title"])
            description = st.text_area("Task Description", value=task["description"])
            due = datetime.fromisoformat(task["due_date"]) if task["due_date"] else datetime.now()
            date = st.date_input("Due Date", value=due.date())
            time = st.time_input("Due Time", value=due.time())
            due_datetime = datetime.combine(date, time).isoformat()

            if st.button("Update Task"):
                update_task(st.session_state.token, task["id"], title, description, due_datetime)
                st.success("Task updated.")
                st.session_state.editing_task = None
                st.rerun()

    # Add Task
    st.subheader("➕ Add Task")
    title = st.text_input("New Task Title")
    description = st.text_area("New Task Description")
    due_date = st.date_input("Due Date")
    due_time = st.time_input("Due Time")
    due_datetime = datetime.combine(due_date, due_time)

    if st.button("Add Task"):
        if not title.strip():
            st.warning("Task title cannot be empty.")
        else:
            # ✅ Check for duplicates
            existing_titles = [task["title"].strip().lower() for task in tasks]
            if title.strip().lower() in existing_titles:
                st.error("This task already exists!")
            else:
                create_task(st.session_state.token, title.strip(), description.strip(), due_datetime)
                st.success("Task added!")
                st.rerun()

