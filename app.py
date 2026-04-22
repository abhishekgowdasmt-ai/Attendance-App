import os
import streamlit as st
import pandas as pd
from auth import authenticate
from storage import get_employees, get_attendance, mark_checkin, mark_checkout

APP_NAME = "Shree Maruthi Travels"
TAGLINE = "On Time, Safe, Reliable"
LOGO_PATH = "logo.png"

st.set_page_config(
    page_title=APP_NAME,
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🚖",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None

def load_branding():
    st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .brand-card {
            background: linear-gradient(135deg, #1e88e5 0%, #2e1a7d 100%);
            padding: 1.25rem 1.5rem;
            border-radius: 18px;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.12);
        }
        .brand-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .brand-subtitle {
            font-size: 1rem;
            opacity: 0.9;
        }
        .section-card {
            background: white;
            padding: 1rem 1rem 0.5rem 1rem;
            border-radius: 16px;
            box-shadow: 0 8px 18px rgba(0,0,0,0.06);
            margin-bottom: 1rem;
        }
        .stButton > button {
            border-radius: 12px;
            font-weight: 600;
            height: 3rem;
        }
        .metric-box {
            background: white;
            border-radius: 16px;
            padding: 1rem;
            box-shadow: 0 8px 18px rgba(0,0,0,0.06);
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

def brand_header():
    col1, col2 = st.columns([1, 5])
    with col1:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=110)
    with col2:
        st.markdown(f"""
        <div class="brand-card">
            <div class="brand-title">{APP_NAME}</div>
            <div class="brand-subtitle">{TAGLINE}</div>
        </div>
        """, unsafe_allow_html=True)

def login_page():
    brand_header()
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Employee Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = authenticate(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown('</div>', unsafe_allow_html=True)

def employee_dashboard():
    user = st.session_state.user
    brand_header()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"Welcome, {user['name']}")

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

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("My Attendance")

    df = get_attendance()
    if not df.empty:
        my_df = df[df["employee_id"].astype(str) == str(user["id"])].copy()
        st.dataframe(my_df, use_container_width=True, hide_index=True)

        csv = my_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download My Attendance",
            data=csv,
            file_name=f"{user['id']}_attendance.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No attendance records yet.")
    st.markdown('</div>', unsafe_allow_html=True)

def admin_dashboard():
    user = st.session_state.user
    brand_header()

    df = get_attendance()
    emp_df = get_employees()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    today_df = df[df["date"].astype(str) == today] if not df.empty else pd.DataFrame()

    total_employees = len(emp_df) if not emp_df.empty else 0
    total_present_today = len(today_df) if not today_df.empty else 0
    total_checked_out = (
        len(today_df[today_df["check_out"].astype(str).str.strip() != ""])
        if not today_df.empty else 0
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-box"><h4>Total Employees</h4><h2>{total_employees}</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-box"><h4>Present Today</h4><h2>{total_present_today}</h2></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-box"><h4>Checked Out</h4><h2>{total_checked_out}</h2></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f"Admin Dashboard - {user['name']}")

    tab1, tab2, tab3 = st.tabs(["Today's Attendance", "All Employees", "Monthly Report"])

    with tab1:
        if not today_df.empty:
            st.dataframe(today_df, use_container_width=True, hide_index=True)
            csv = today_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Today's Attendance CSV",
                data=csv,
                file_name=f"attendance_{today}.csv",
                mime="text/csv"
            )
        else:
            st.info("No attendance records yet.")

    with tab2:
        if not emp_df.empty:
            st.dataframe(emp_df, use_container_width=True, hide_index=True)
        else:
            st.info("No employees found.")

    with tab3:
        if not df.empty:
            month_options = sorted(df["date"].astype(str).str[:7].unique(), reverse=True)
            month = st.selectbox("Select Month", month_options)
            month_df = df[df["date"].astype(str).str.startswith(month)]
            st.dataframe(month_df, use_container_width=True, hide_index=True)

            csv = month_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Monthly Report",
                data=csv,
                file_name=f"attendance_{month}.csv",
                mime="text/csv"
            )
        else:
            st.info("No attendance records yet.")

    st.markdown('</div>', unsafe_allow_html=True)

def sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=160)

        st.markdown(f"### {APP_NAME}")
        st.caption(TAGLINE)
        st.write("---")

        if st.session_state.user:
            st.write(f"**Logged in as:** {st.session_state.user['name']}")
            st.write(f"**Role:** {st.session_state.user['role']}")

            if st.button("Logout", use_container_width=True):
                st.session_state.user = None
                st.rerun()

load_branding()

if st.session_state.user is None:
    login_page()
else:
    sidebar()
    role = str(st.session_state.user["role"]).strip().lower()
    if role == "admin":
        admin_dashboard()
    else:
        employee_dashboard()