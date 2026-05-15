import sys as _sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in [_ROOT, _os.path.join(_ROOT,"utils"), _os.path.join(_ROOT,"pages")]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

"""utils/auth.py  —  Auth, UID generation, password hashing"""
import hashlib, uuid
from datetime import datetime
import streamlit as st
from utils.gsheet import (append_row, find_row, col_exists,
                           read_sheet, update_row)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def gen_uid(role: str) -> str:
    prefix = {"admin": "ADMIN", "sales executive": "SE", "delivery Driver": "DD"}.get(role, "USR")
    return f"{prefix}-{uuid.uuid4().hex[:6].upper()}"

def gen_cust_id() -> str:
    return f"CUST-{uuid.uuid4().hex[:6].upper()}"

def gen_driver_id() -> str:
    return f"DD-{uuid.uuid4().hex[:6].upper()}"

def gen_order_id() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    rand_part = uuid.uuid4().hex[:4].upper()
    return f"ORD-{date_part}-{rand_part}"

def register_user(name: str, phone: str, role: str, password: str):
    """Register a login user. Returns (uid, error_str)."""
    if col_exists("user_registry", "Phone", phone):
        existing = find_row("user_registry", "Phone", phone)
        return None, f"Phone already registered (UID: {existing['UID']})."
    uid = gen_uid(role)
    pw_hash = hash_pw(password)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [uid, name, phone, role, pw_hash, ts, "Active"]
    append_row("user_registry", row)
    # Also write to role-specific sheet
    role_key = "sales_exec" if role == "sales executive" else "delivery_driver"
    if role in ("sales executive", "delivery Driver"):
        append_row(role_key, [uid, name, phone, role, pw_hash, ts])
    return uid, None

def login_user(phone: str, password: str):
    """Returns (user_dict, error_str)."""
    user = find_row("user_registry", "Phone", phone)
    if not user:
        return None, "Phone number not found."
    if user.get("Password Hash") != hash_pw(password):
        return None, "Incorrect password."
    if str(user.get("Status", "")).lower() != "active":
        return None, "Account is inactive. Contact admin."
    return {
        "uid":  user["UID"],
        "name": user["Full Name"],
        "role": user["Role"],
        "phone": user["Phone"],
    }, None

def check_login():
    """Returns True if user is logged in, else redirects handled by caller."""
    return st.session_state.get("logged_in", False)
