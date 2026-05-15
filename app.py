"""
app.py  —  Garlic Order & Delivery Platform
Run with:  streamlit run app.py
"""
import sys
import os

# ── Fix import paths (required for Streamlit Cloud & local) ──────────────────
# Ensures utils/ and pages/ are always importable regardless of working directory
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Garlic Order & Delivery",
    page_icon="🧄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ────────────────────────────────────────────────────
DEFAULTS = {
    "logged_in":     False,
    "user":          None,
    "driver_id":     None,
    "driver_active": True,
    "active_stop":   0,
    "cust_data":     {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Inject global CSS ─────────────────────────────────────────────────────────
from utils.style import inject
inject()


# ── Topbar helper ─────────────────────────────────────────────────────────────
def topbar(role_label: str, role_color: str = "#1a7f4b"):
    user = st.session_state.user
    left, mid, right = st.columns([5, 3, 2])
    with left:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;padding:6px 0">'
            '<span style="font-size:1.6rem">🧄</span>'
            '<span style="font-family:Syne,sans-serif;font-weight:800;'
            'font-size:1.15rem;color:#1a7f4b">Garlic Order & Delivery</span>'
            '</div>', unsafe_allow_html=True)
    with mid:
        st.markdown(
            f'<div style="text-align:center;padding-top:8px">'
            f'<span style="background:{role_color};color:#fff;padding:4px 14px;'
            f'border-radius:20px;font-size:.8rem;font-weight:700">{role_label}</span>'
            f'&nbsp;<code style="font-size:.72rem;color:#5a7a65">{user["uid"]}</code>'
            f'</div>', unsafe_allow_html=True)
    with right:
        if st.button("🚪 Logout", key="logout_btn"):
            if user["role"] == "delivery Driver":
                from utils.gsheet import set_driver_status, find_row
                dr = find_row("driver_onboard", "Mobile", user["phone"])
                if dr:
                    set_driver_status(dr["Driver ID"], "Offline")
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()
    st.divider()


# ── Role renderers ────────────────────────────────────────────────────────────
def render_admin():
    topbar("🛡️ Admin", "#185fa5")
    from pages.admin.admin_dashboard import (
        show_skus, show_trips, show_assign_drivers,
        show_customers, show_drivers, show_orders, show_log,
    )
    user = st.session_state.user
    tabs = st.tabs([
        "📦 SKUs",
        "🗺️ Trips & Routes",
        "🚚 Assign Drivers",
        "👤 Customers",
        "🚗 Drivers",
        "📋 All Orders",
        "📝 Audit Log",
    ])
    with tabs[0]: show_skus(user)
    with tabs[1]: show_trips(user)
    with tabs[2]: show_assign_drivers(user)
    with tabs[3]: show_customers()
    with tabs[4]: show_drivers()
    with tabs[5]: show_orders()
    with tabs[6]: show_log()


def render_sales():
    topbar("🧑‍💼 Sales Executive · T1")
    from pages.sales.order_form       import show as show_order, show_history
    from pages.sales.customer_onboard import show as show_cust_onboard
    user = st.session_state.user
    tabs = st.tabs(["➕ New Order", "👤 Customer Onboard", "📋 My Orders"])
    with tabs[0]: show_order(user)
    with tabs[1]: show_cust_onboard(user)
    with tabs[2]: show_history(user)


def render_delivery():
    topbar("🚚 Delivery Driver · T2", "#854f0b")
    from pages.delivery.route_view      import show as show_route, show_history
    from pages.delivery.driver_onboard  import show as show_driver_onboard
    user = st.session_state.user
    tabs = st.tabs(["🗺️ My Route", "📝 Driver Onboard", "📦 Delivery History"])
    with tabs[0]: show_route(user)
    with tabs[1]: show_driver_onboard(user)
    with tabs[2]: show_history(user)


# ── Main router ───────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        from pages.login_page import show as show_login
        show_login()
        return

    role = st.session_state.user["role"]
    if role == "admin":
        render_admin()
    elif role == "sales executive":
        render_sales()
    elif role == "delivery Driver":
        render_delivery()
    else:
        st.error(f"Unknown role: {role}")
        if st.button("Logout"):
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()


if __name__ == "__main__":
    main()
