import streamlit as st
import pandas as pd
from auth import authenticate
from storage import get_employees, get_attendance, mark_checkin, mark_checkout

st.set_page_config(page_title="Attendance System", page_icon="✅", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

def login_page():
    st.title("Attendance System")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = authenticate(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid username or password")

def employee_dashboard():
    user = st.session_state.user
    st.title(f"Welcome, {user['name']}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Check In", use_container_width=True):
            msg = mark_checkin(user["id"], user["name"])
            if msg == "Checked in":
                st.success(msg)
            else:
                st.warning(msg)

    with col2:
        if st.button("Check Out", use_container_width=True):
            msg = mark_checkout(user["id"])
            if msg == "Checked out":
                st.success(msg)
            else:
                st.warning(msg)

    st.divider()
    st.subheader("My Attendance")

    df = get_attendance()
    if not df.empty:
        my_df = df[df["employee_id"].astype(str) == str(user["id"])].copy()
        st.dataframe(my_df, use_container_width=True)

        csv = my_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download My Attendance",
            data=csv,
            file_name=f"{user['id']}_attendance.csv",
            mime="text/csv",
        )
    else:
        st.info("No attendance records yet.")

def admin_dashboard():
    user = st.session_state.user
    st.title(f"Admin Dashboard - {user['name']}")

    tab1, tab2, tab3 = st.tabs(["Today's Attendance", "All Employees", "Monthly Report"])

    with tab1:
        df = get_attendance()
        if not df.empty:
            today = pd.Timestamp.now().strftime("%Y-%m-%d")
            today_df = df[df["date"].astype(str) == today]
            st.dataframe(today_df, use_container_width=True)

            csv = today_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Today's Attendance CSV",
                data=csv,
                file_name=f"attendance_{today}.csv",
                mime="text/csv",
            )
        else:
            st.info("No attendance records yet.")

    with tab2:
        emp_df = get_employees()
        if not emp_df.empty:
            st.dataframe(emp_df, use_container_width=True)
        else:
            st.info("No employees found.")

    with tab3:
        df = get_attendance()
        if not df.empty:
            month = st.selectbox(
                "Select Month",
                sorted(df["date"].astype(str).str[:7].unique(), reverse=True)
            )
            month_df = df[df["date"].astype(str).str.startswith(month)]
            st.dataframe(month_df, use_container_width=True)

            csv = month_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Monthly Report",
                data=csv,
                file_name=f"attendance_{month}.csv",
                mime="text/csv",
            )
        else:
            st.info("No attendance records yet.")

def sidebar():
    with st.sidebar:
        st.write("### Menu")
        if st.session_state.user:
            st.write(f"Logged in as: **{st.session_state.user['name']}**")
            st.write(f"Role: **{st.session_state.user['role']}**")
            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.rerun()

if st.session_state.user is None:
    login_page()
else:
    sidebar()
    role = str(st.session_state.user["role"]).strip().lower()
    if role == "admin":
        admin_dashboard()
    else:
        employee_dashboard()