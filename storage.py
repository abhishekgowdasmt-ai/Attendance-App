import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_ID = "1YHwhD_vIuvuzWl0zGP0mPUEEZoTNFYuzYN2CWBZICSI"

@st.cache_resource
def client():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def sheet(name):
    return client().open_by_key(SPREADSHEET_ID).worksheet(name)

@st.cache_data(ttl=8)
def get_employees():
    ws = sheet("employees")
    df = pd.DataFrame(ws.get_all_records())
    if not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df

@st.cache_data(ttl=8)
def get_attendance():
    ws = sheet("attendance")
    df = pd.DataFrame(ws.get_all_records())
    if not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def clear_cached_data():
    get_employees.clear()
    get_attendance.clear()

def mark_checkin(emp_id, name, location=None, remarks=""):
    ws = sheet("attendance")
    df = get_attendance()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    now_time = pd.Timestamp.now().strftime("%H:%M:%S")

    if not df.empty:
        existing = df[
            (df["employee_id"].astype(str) == str(emp_id)) &
            (df["date"].astype(str) == today)
        ]
        if not existing.empty:
            return "Already checked in"

    next_id = len(df) + 1 if not df.empty else 1

    lat = ""
    lng = ""
    acc = ""
    map_url = ""

    if location and isinstance(location, dict):
        lat = location.get("latitude", "")
        lng = location.get("longitude", "")
        acc = location.get("accuracy", "")
        if lat != "" and lng != "":
            map_url = f"https://maps.google.com/?q={lat},{lng}"

    ws.append_row([
        next_id,
        emp_id,
        name,
        today,
        now_time,
        "",
        remarks,
        lat,
        lng,
        acc,
        map_url,
        "",
        "",
        "",
        ""
    ])

    clear_cached_data()
    return "Checked in"

def mark_checkout(emp_id, location=None):
    ws = sheet("attendance")
    records = ws.get_all_records()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    now_time = pd.Timestamp.now().strftime("%H:%M:%S")

    checkout_lat = ""
    checkout_lng = ""
    checkout_acc = ""
    checkout_map = ""

    if location and isinstance(location, dict):
        checkout_lat = location.get("latitude", "")
        checkout_lng = location.get("longitude", "")
        checkout_acc = location.get("accuracy", "")
        if checkout_lat != "" and checkout_lng != "":
            checkout_map = f"https://maps.google.com/?q={checkout_lat},{checkout_lng}"

    for i, row in enumerate(records, start=2):
        if str(row["employee_id"]) == str(emp_id) and str(row["date"]) == today:
            if str(row.get("check_out", "")).strip():
                return "Already checked out"

            ws.update_cell(i, 6, now_time)
            ws.update_cell(i, 12, checkout_lat)
            ws.update_cell(i, 13, checkout_lng)
            ws.update_cell(i, 14, checkout_acc)
            ws.update_cell(i, 15, checkout_map)

            clear_cached_data()
            return "Checked out"

    return "Check-in first"