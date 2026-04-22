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
    values = ws.get_all_values()
    if not values:
        return pd.DataFrame()

    headers = [str(h).strip().lower() for h in values[0]]
    rows = values[1:]

    padded_rows = []
    for row in rows:
        row = list(row)
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))
        padded_rows.append(row[:len(headers)])

    df = pd.DataFrame(padded_rows, columns=headers)
    return df

def clear_cached_data():
    get_employees.clear()
    get_attendance.clear()

def _map_url(lat, lng):
    if str(lat).strip() and str(lng).strip():
        return f"https://maps.google.com/?q={lat},{lng}"
    return ""

def mark_checkin(emp_id, name, location=None, remarks=""):
    ws = sheet("attendance")
    df = get_attendance()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    now_time = pd.Timestamp.now().strftime("%H:%M:%S")

    if not df.empty:
        existing = df[
            (df["employee_id"].astype(str).str.strip() == str(emp_id)) &
            (df["date"].astype(str).str.strip() == today)
        ]
        if not existing.empty:
            return "Attendance already marked for today"

    lat = ""
    lng = ""
    acc = ""
    map_url = ""

    if location and isinstance(location, dict):
        lat = location.get("latitude", "") or ""
        lng = location.get("longitude", "") or ""
        acc = location.get("accuracy", "") or ""
        map_url = _map_url(lat, lng)

    next_id = len(df) + 1 if not df.empty else 1

    ws.append_row([
        next_id,         # id
        emp_id,          # employee_id
        name,            # name
        today,           # date
        "Present",       # status
        now_time,        # check_in
        "",              # check_out
        remarks,         # remarks
        lat,             # checkin_lat
        lng,             # checkin_lng
        acc,             # checkin_accuracy
        map_url,         # checkin_map
        "",              # checkout_lat
        "",              # checkout_lng
        "",              # checkout_accuracy
        ""               # checkout_map
    ])

    clear_cached_data()
    return "Checked in"

def mark_absent(emp_id, name, remarks=""):
    ws = sheet("attendance")
    df = get_attendance()

    today = pd.Timestamp.now().strftime("%Y-%m-%d")

    if not df.empty:
        existing = df[
            (df["employee_id"].astype(str).str.strip() == str(emp_id)) &
            (df["date"].astype(str).str.strip() == today)
        ]
        if not existing.empty:
            return "Attendance already marked for today"

    next_id = len(df) + 1 if not df.empty else 1

    ws.append_row([
        next_id,         # id
        emp_id,          # employee_id
        name,            # name
        today,           # date
        "Absent",        # status
        "",              # check_in
        "",              # check_out
        remarks,         # remarks
        "", "", "", "",  # checkin location fields
        "", "", "", ""   # checkout location fields
    ])

    clear_cached_data()
    return "Marked absent"

def mark_checkout(emp_id, location=None):
    ws = sheet("attendance")
    records = ws.get_all_values()

    if not records or len(records) < 2:
        return "Check-in first"

    headers = [str(h).strip().lower() for h in records[0]]
    data_rows = records[1:]

    required_cols = [
        "employee_id", "date", "status", "check_out",
        "checkout_lat", "checkout_lng", "checkout_accuracy", "checkout_map"
    ]

    for col_name in required_cols:
        if col_name not in headers:
            return f"Missing column in attendance sheet: {col_name}"

    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    now_time = pd.Timestamp.now().strftime("%H:%M:%S")

    lat = ""
    lng = ""
    acc = ""
    map_url = ""

    if location and isinstance(location, dict):
        lat = location.get("latitude", "") or ""
        lng = location.get("longitude", "") or ""
        acc = location.get("accuracy", "") or ""
        if str(lat).strip() and str(lng).strip():
            map_url = f"https://maps.google.com/?q={lat},{lng}"

    col = {name: idx + 1 for idx, name in enumerate(headers)}

    for i, row in enumerate(data_rows, start=2):
        row = list(row)
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))

        row_emp_id = str(row[col["employee_id"] - 1]).strip()
        row_date = str(row[col["date"] - 1]).strip()
        row_status = str(row[col["status"] - 1]).strip()
        row_checkout = str(row[col["check_out"] - 1]).strip()

        if row_emp_id == str(emp_id) and row_date == today:
            if row_status == "Absent":
                return "You are marked absent for today"
            if row_checkout:
                return "Already checked out"

            ws.update_cell(i, col["check_out"], now_time)
            ws.update_cell(i, col["checkout_lat"], lat)
            ws.update_cell(i, col["checkout_lng"], lng)
            ws.update_cell(i, col["checkout_accuracy"], acc)
            ws.update_cell(i, col["checkout_map"], map_url)

            clear_cached_data()
            return "Checked out"

    return "Check-in first"