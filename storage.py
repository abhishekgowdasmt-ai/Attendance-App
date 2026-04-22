import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SPREADSHEET_NAME = "attendance_db"

def client():
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=SCOPES
    )
    return gspread.authorize(creds)

def sheet(name):
    return client().open(SPREADSHEET_NAME).worksheet(name)

def get_employees():
    ws = sheet("employees")
    df = pd.DataFrame(ws.get_all_records())
    if not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def get_attendance():
    ws = sheet("attendance")
    df = pd.DataFrame(ws.get_all_records())
    if not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def mark_checkin(emp_id, name):
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

    ws.append_row([
        next_id,
        emp_id,
        name,
        today,
        now_time,
        "",
        ""
    ])
    return "Checked in"

def mark_checkout(emp_id):
    ws = sheet("attendance")
    records = ws.get_all_records()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    now_time = pd.Timestamp.now().strftime("%H:%M:%S")

    for i, row in enumerate(records, start=2):
        if str(row["employee_id"]) == str(emp_id) and str(row["date"]) == today:
            if str(row["check_out"]).strip():
                return "Already checked out"

            ws.update_cell(i, 6, now_time)
            return "Checked out"

    return "Check-in first"