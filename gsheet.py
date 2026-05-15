"""
utils/gsheet.py  —  All Google Sheets helpers
Reads credentials.json from project root (local dev).
Falls back to st.secrets for Streamlit Cloud deploy.
"""
import os, uuid
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_NAME = "Garlic_Order & Delivery Project"

SHEET = {
    "base":             "Base",
    "customer_onboard": "Customer Onboard Data",
    "driver_onboard":   "Driver Onboard Data",
    "sales_exec":       "sales executive",
    "delivery_driver":  "delivery Driver",
    "user_registry":    "UserRegistry",
    "admin_log":        "Admin Log",
    "skus":             "SKU Master",
    "trips":            "Trips",
}

HEADERS = {
    "base": [
        "Order ID","SOID","City","ORDER DATE","DELIVERED DATE","ORDERED TIME",
        "CustomerId","Customer shop name","Customer Number","Customer_Classification",
        "sales executive","sales executive Number","SKU","WeightType","Price",
        "OrderedQty","OrderTotal","ReturnQty","Reason","return_updated_role",
        "Tripid","Transport","ShopOpeningFrom","ShopReachTime","DeliveryCutOff",
        "Shop Location","Delivery Status","EnteredBy_UID","Timestamp",
    ],
    "customer_onboard": [
        "CUST-ID","Full Name","Mobile","Email","Shop Name","Shop Address",
        "City","Classification","Onboarded By","Onboard Date","Status",
    ],
    "driver_onboard": [
        "Driver ID","Full Name","Mobile","Email","Vehicle Type",
        "Bank Name","Account Number","IFSC Code","UPI ID",
        "Onboard Date","Active Status","Last Active",
    ],
    "user_registry": [
        "UID","Full Name","Phone","Role","Password Hash","Created At","Status",
    ],
    "sales_exec":     ["UID","Full Name","Phone","Role","Password Hash","Created At"],
    "delivery_driver":["UID","Full Name","Phone","Role","Password Hash","Created At"],
    "admin_log": [
        "Log ID","Timestamp","Admin UID","Action Type",
        "Entity","Entity ID","Old Value","New Value","Notes",
    ],
    "skus": [
        "SKU Code","SKU Name","Price","Weight Type",
        "Category","Active","Created By","Created At",
    ],
    "trips": [
        "Trip ID","Date","City","Shops","Driver UID",
        "Driver Name","Status","Created By","Created At",
    ],
}

# ── Auth client ───────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")
    if os.path.exists(creds_path):
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES)
    return gspread.authorize(creds)

def open_sp():
    client = get_client()
    try:
        return client.open(SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        return client.create(SPREADSHEET_NAME)

def get_ws(key: str):
    sp = open_sp()
    name = SHEET[key]
    try:
        ws = sp.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = sp.add_worksheet(title=name, rows=2000, cols=40)
        if key in HEADERS:
            ws.append_row(HEADERS[key])
    return ws

# ── Core CRUD ─────────────────────────────────────────────────────────────────
def read_sheet(key: str) -> pd.DataFrame:
    try:
        ws = get_ws(key)
        rows = ws.get_all_records()
        return pd.DataFrame(rows) if rows else pd.DataFrame(columns=HEADERS.get(key, []))
    except Exception as e:
        st.error(f"Sheet read error ({key}): {e}")
        return pd.DataFrame(columns=HEADERS.get(key, []))

def append_row(key: str, row: list):
    ws = get_ws(key)
    ws.append_row(row, value_input_option="USER_ENTERED")

def update_row(key: str, id_col: str, id_val: str, updates: dict) -> bool:
    ws = get_ws(key)
    headers = ws.row_values(1)
    for i, row in enumerate(ws.get_all_records(), start=2):
        if str(row.get(id_col, "")).strip() == str(id_val).strip():
            for col, val in updates.items():
                if col in headers:
                    ws.update_cell(i, headers.index(col) + 1, val)
            return True
    return False

def find_row(key: str, col: str, val: str):
    df = read_sheet(key)
    if df.empty or col not in df.columns:
        return None
    m = df[df[col].astype(str).str.strip() == str(val).strip()]
    return m.iloc[0].to_dict() if not m.empty else None

def col_exists(key: str, col: str, val: str) -> bool:
    return find_row(key, col, val) is not None

# ── Customer ──────────────────────────────────────────────────────────────────
def get_customer_by_id(cust_id: str):
    return find_row("customer_onboard", "CUST-ID", cust_id)

def get_customer_by_mobile(mobile: str):
    return find_row("customer_onboard", "Mobile", mobile)

@st.cache_data(ttl=120)
def load_all_customers() -> pd.DataFrame:
    return read_sheet("customer_onboard")

# ── SKU ───────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_skus() -> pd.DataFrame:
    return read_sheet("skus")

def get_active_skus() -> pd.DataFrame:
    df = load_skus()
    if df.empty: return df
    return df[df["Active"].astype(str).str.lower() == "true"]

# ── Driver ────────────────────────────────────────────────────────────────────
def set_driver_status(driver_id: str, status: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_row("driver_onboard", "Driver ID", driver_id,
               {"Active Status": status, "Last Active": ts})

def get_active_drivers() -> pd.DataFrame:
    df = read_sheet("driver_onboard")
    if df.empty: return df
    return df[df["Active Status"].astype(str).str.lower() == "active"]

# ── Trip ──────────────────────────────────────────────────────────────────────
def load_trips() -> pd.DataFrame:
    return read_sheet("trips")

def get_driver_trip(driver_uid: str):
    df = load_trips()
    if df.empty: return None
    m = df[(df["Driver UID"].astype(str) == driver_uid) &
           (df["Status"].astype(str).str.lower().isin(["assigned","in progress"]))]
    return m.iloc[0].to_dict() if not m.empty else None

# ── Admin log ─────────────────────────────────────────────────────────────────
def write_admin_log(admin_uid, action, entity, entity_id, old="", new="", notes=""):
    log_id = "LOG-" + uuid.uuid4().hex[:6].upper()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    append_row("admin_log", [log_id, ts, admin_uid, action, entity, str(entity_id),
                              str(old), str(new), notes])
