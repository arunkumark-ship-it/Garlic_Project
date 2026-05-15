"""
app.py  —  Garlic Order & Delivery Platform
Main router. Run with:  streamlit run app.py
"""
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
    "logged_in":    False,
    "user":         None,
    "driver_id":    None,
    "driver_active":True,
    "active_stop":  0,
    "cust_data":    {},
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
    initials = "".join(p[0] for p in user["name"].split())[:2].upper()

    left, mid, right = st.columns([5, 3, 2])
    with left:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding:6px 0">'
            f'<span style="font-size:1.6rem">🧄</span>'
            f'<span style="font-family:Syne,sans-serif;font-weight:800;'
            f'font-size:1.15rem;color:#1a7f4b">Garlic Order & Delivery</span>'
            f'</div>', unsafe_allow_html=True)
    with mid:
        st.markdown(
            f'<div style="text-align:center;padding-top:8px">'
            f'<span class="role-badge" style="background:{role_color};color:#fff;'
            f'padding:4px 14px;border-radius:20px;font-size:.8rem;font-weight:700">'
            f'{role_label}</span>'
            f'&nbsp;<code style="font-size:.72rem;color:#5a7a65">{user["uid"]}</code>'
            f'</div>', unsafe_allow_html=True)
    with right:
        if st.button("🚪 Logout", key="logout_btn"):
            # Set driver offline
            if user["role"] == "delivery Driver":
                from utils.gsheet import set_driver_status, find_row
                dr = find_row("driver_onboard","Mobile",user["phone"])
                if dr:
                    set_driver_status(dr["Driver ID"],"Offline")
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()

    st.divider()


# ── Admin dashboard ───────────────────────────────────────────────────────────
def render_admin():
    topbar("🛡️ Admin", "#185fa5")
    from pages.admin.admin_dashboard import (
        show_skus, show_trips, show_assign_drivers,
        show_customers, show_drivers, show_orders, show_log,
    )
    user = st.session_state.user
    tab_skus, tab_trips, tab_drivers, tab_custs, tab_dd, tab_orders, tab_log = st.tabs([
        "📦 SKUs",
        "🗺️ Trips & Routes",
        "🚚 Assign Drivers",
        "👤 Customers",
        "🚗 Drivers",
        "📋 All Orders",
        "📝 Audit Log",
    ])
    with tab_skus:    show_skus(user)
    with tab_trips:   show_trips(user)
    with tab_drivers: show_assign_drivers(user)
    with tab_custs:   show_customers()
    with tab_dd:      show_drivers()
    with tab_orders:  show_orders()
    with tab_log:     show_log()


# ── Sales executive dashboard ─────────────────────────────────────────────────
def render_sales():
    topbar("🧑‍💼 Sales Executive · T1")
    from pages.sales.order_form      import show as show_order, show_history
    from pages.sales.customer_onboard import show as show_cust_onboard
    user = st.session_state.user

    tab_order, tab_onboard, tab_hist = st.tabs([
        "➕ New Order",
        "👤 Customer Onboard",
        "📋 My Orders",
    ])
    with tab_order:
        show_order(user)
    with tab_onboard:
        show_cust_onboard(user)
    with tab_hist:
        show_history(user)


# ── Delivery driver dashboard ─────────────────────────────────────────────────
def render_delivery():
    topbar("🚚 Delivery Driver · T2", "#854f0b")
    from pages.delivery.route_view     import show as show_route, show_history
    from pages.delivery.driver_onboard import show as show_driver_onboard
    user = st.session_state.user

    tab_route, tab_onboard, tab_hist = st.tabs([
        "🗺️ My Route",
        "📝 Driver Onboard",
        "📦 Delivery History",
    ])
    with tab_route:
        show_route(user)
    with tab_onboard:
        show_driver_onboard(user)
    with tab_hist:
        show_history(user)


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
