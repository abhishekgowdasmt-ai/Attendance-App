import os
import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation

from auth import authenticate
from storage import get_employees, get_attendance, mark_checkin, mark_checkout, mark_absent

APP_NAME = "Shree Maruthi Travels"
TAGLINE = "On Time, Safe, Reliable"
LOGO_PATH = "logo.jpeg"

ORANGE = "#F5821F"
PURPLE = "#2E1A7D"
BLUE = "#1697E5"
BG = "#F6F8FC"
CARD = "#FFFFFF"
TEXT = "#1F2937"
MUTED = "#6B7280"
BORDER = "#E5E7EB"

st.set_page_config(
    page_title=APP_NAME,
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else "🚖",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state["user"] = None

if "latest_location" not in st.session_state:
    st.session_state["latest_location"] = None


def inject_css():
    st.markdown(f"""
    <style>
    .stApp {{
        background: {BG};
    }}
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 1.5rem;
        max-width: 1400px;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {PURPLE} 0%, #1f3fb7 100%);
        color: white;
    }}
    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}
    .brand-header {{
        background: linear-gradient(135deg, {PURPLE} 0%, #244db9 55%, {BLUE} 100%);
        border-radius: 24px;
        padding: 1.25rem 1.5rem;
        color: white;
        box-shadow: 0 12px 30px rgba(25, 35, 90, 0.18);
        margin-bottom: 1rem;
    }}
    .brand-title {{
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.35rem;
    }}
    .tagline {{
        font-size: 1rem;
        opacity: 0.95;
    }}
    .metric-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 1.1rem 1rem;
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
        text-align: center;
        min-height: 140px;
    }}
    .metric-title {{
        font-size: 1rem;
        color: {MUTED};
        font-weight: 600;
        margin-bottom: 0.65rem;
    }}
    .metric-value {{
        font-size: 2.25rem;
        font-weight: 800;
        color: {TEXT};
    }}
    .section-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 1rem 1rem 0.6rem 1rem;
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
        margin-top: 1rem;
    }}
    .section-title {{
        font-size: 1.55rem;
        font-weight: 800;
        color: {TEXT};
        margin-bottom: 0.5rem;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: white;
        border-radius: 12px 12px 0 0;
        padding: 10px 16px;
        border: 1px solid {BORDER};
    }}
    .stTabs [aria-selected="true"] {{
        color: {ORANGE} !important;
        border-bottom: 3px solid {ORANGE} !important;
    }}
    .stButton > button {{
        border-radius: 14px;
        font-weight: 700;
        border: none;
        height: 3.1rem;
        box-shadow: 0 8px 18px rgba(16, 24, 40, 0.08);
    }}
    .stDownloadButton > button {{
        border-radius: 14px;
        font-weight: 700;
        height: 3rem;
    }}
    div[data-testid="stDataFrame"] {{
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid {BORDER};
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)


def brand_header():
    left, right = st.columns([1, 5])
    with left:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=110)
    with right:
        st.markdown(f"""
        <div class="brand-header">
            <div class="brand-title">
                <span style="color:{ORANGE};">Shree</span>
                <span style="color:white;"> Maruthi Travels</span>
            </div>
            <div class="tagline">{TAGLINE}</div>
        </div>
        """, unsafe_allow_html=True)


def sidebar():
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=155)

        st.markdown(f"""
        <div style="font-size:1.55rem;font-weight:800;line-height:1.2;margin-top:0.4rem;">
            <span style="color:{ORANGE};">Shree</span>
            <span style="color:white;"> Maruthi Travels</span>
        </div>
        <div style="font-size:0.95rem;opacity:0.92;margin-top:0.25rem;">
            {TAGLINE}
        </div>
        """, unsafe_allow_html=True)

        st.write("---")

        current_user = st.session_state.get("user")
        if current_user:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.08);padding:0.9rem;border-radius:18px;border:1px solid rgba(255,255,255,0.12);">
                <div><b>Logged in as:</b> {current_user.get('name', '')}</div>
                <div style="margin-top:6px;"><b>Role:</b> {current_user.get('role', '')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            if st.button("Logout", use_container_width=True):
                st.session_state["user"] = None
                st.session_state["latest_location"] = None
                st.rerun()


def login_page():
    brand_header()
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Employee Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        user = authenticate(username, password)
        if user:
            st.session_state["user"] = dict(user)
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("</div>", unsafe_allow_html=True)


def location_block():
    st.markdown("#### Capture Location")
    loc = streamlit_geolocation()

    if loc and loc.get("latitude") is not None:
        st.session_state["latest_location"] = loc
        st.success("Location captured")
        st.caption(
            f"Lat: {loc.get('latitude')}, Lng: {loc.get('longitude')}, Accuracy: {loc.get('accuracy')}"
        )
    else:
        st.info("Tap the location button and allow GPS access before check-in.")

    return st.session_state.get("latest_location")


def employee_dashboard():
    current_user = st.session_state.get("user")

    if not current_user:
        st.error("Please login again")
        st.stop()

    if not isinstance(current_user, dict):
        st.error("User session is invalid. Please login again.")
        st.stop()

    user_id = str(current_user.get("id", "")).strip()
    user_name = str(current_user.get("name", "")).strip()

    brand_header()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Welcome, {user_name}</div>', unsafe_allow_html=True)

    remarks = st.text_input("Remarks (optional)")
    loc = location_block()

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Check In", use_container_width=True):
            msg = mark_checkin(user_id, user_name, location=loc, remarks=remarks)
            if msg == "Checked in":
                st.success(msg)
            else:
                st.warning(msg)

    with c2:
        if st.button("Check Out", use_container_width=True):
            msg = mark_checkout(user_id, location=loc)
            if msg == "Checked out":
                st.success(msg)
            else:
                st.warning(msg)

    with c3:
        if st.button("Mark Absent", use_container_width=True):
            msg = mark_absent(user_id, user_name, remarks=remarks)
            if msg == "Marked absent":
                st.success(msg)
            else:
                st.warning(msg)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">My Attendance</div>', unsafe_allow_html=True)

    df = get_attendance()
    if not df.empty and "employee_id" in df.columns:
        my_df = df[df["employee_id"].astype(str).str.strip() == user_id].copy()
        st.dataframe(my_df, use_container_width=True, hide_index=True)

        csv = my_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download My Attendance",
            data=csv,
            file_name=f"{user_id}_attendance.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No attendance records yet.")

    st.markdown("</div>", unsafe_allow_html=True)


def admin_dashboard():
    current_user = st.session_state.get("user")
    if not current_user:
        st.error("Please login again")
        st.stop()

    brand_header()

    df = get_attendance()
    emp_df = get_employees()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    today_df = df[df["date"].astype(str).str.strip() == today] if not df.empty else pd.DataFrame()

    total_employees = len(emp_df) if not emp_df.empty else 0
    total_present_today = len(today_df) if not today_df.empty else 0
    total_checked_out = (
        len(today_df[today_df["check_out"].astype(str).str.strip() != ""])
        if not today_df.empty else 0
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Employees</div><div class="metric-value" style="color:{PURPLE};">{total_employees}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Present Today</div><div class="metric-value" style="color:{BLUE};">{total_present_today}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Checked Out</div><div class="metric-value" style="color:{ORANGE};">{total_checked_out}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Admin Dashboard - {current_user.get("name", "")}</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Today's Attendance", "All Employees", "Monthly Report"])

    with tab1:
        if not today_df.empty:
            st.dataframe(today_df, use_container_width=True, hide_index=True)
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

    st.markdown("</div>", unsafe_allow_html=True)


inject_css()

current_user = st.session_state.get("user")
if current_user is None:
    login_page()
else:
    sidebar()
    role = str(current_user.get("role", "")).strip().lower()
    if role == "admin":
        admin_dashboard()
    else:
        employee_dashboard()