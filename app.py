# ═══════════════════════════════════════════════════════════════════════════════
#  app.py  —  Garlic Order & Delivery Platform
#  IMPORTANT: sys.path MUST be fixed before ANY local import
# ═══════════════════════════════════════════════════════════════════════════════
import sys, os

# Add project root to path — works on local AND Streamlit Cloud
# Streamlit Cloud mounts at /mount/src/<repo_name>/
_ROOT = os.path.dirname(os.path.abspath(__file__))
for _p in [_ROOT, os.path.join(_ROOT, "utils"), os.path.join(_ROOT, "pages")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── NOW it is safe to import streamlit and local modules ──────────────────────
import streamlit as st

st.set_page_config(
    page_title="Garlic Order & Delivery",
    page_icon="🧄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inline CSS (avoids any import for the style module at startup) ────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root{
  --green:#1a7f4b;--green2:#25a862;
  --dark:#0d1f14;--border:#c8e6d4;--text:#1a2e22;--muted:#5a7a65;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--text)}
h1,h2,h3{font-family:'Syne',sans-serif}
.stApp{background:#eef5f0}
header[data-testid="stHeader"]{background:transparent}
.sl{font-family:'Syne',sans-serif;font-weight:700;font-size:.75rem;
  letter-spacing:.8px;text-transform:uppercase;color:var(--green);
  padding-bottom:.4rem;border-bottom:2px solid var(--border);margin-bottom:.8rem}
.map-frame{border-radius:12px;overflow:hidden;border:2px solid var(--border);margin-top:.5rem}
.pill{display:inline-block;font-size:.75rem;padding:3px 12px;border-radius:20px;font-weight:600}
.pill-pend{background:#fff3cd;color:#856404}
.pill-done{background:#d4edda;color:#1a7f4b}
.pill-fail{background:#f8d7da;color:#842029}
.pill-part{background:#cce5ff;color:#004085}
.pill-on{background:#d4edda;color:#1a7f4b}
.pill-off{background:#e2e3e5;color:#383d41}
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea{border-radius:10px !important;border-color:var(--border) !important}
.stButton>button{border-radius:12px !important;font-family:'Syne',sans-serif !important;font-weight:700 !important}
.stButton>button[kind="primary"]{background:var(--green) !important;border:none !important;color:#fff !important}
</style>
""", unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────────────────────
DEFAULTS = {
    "logged_in":     False,
    "user":          None,
    "driver_id":     None,
    "driver_active": True,
    "active_stop":   0,
    "cust_data":     {},
}
for _k, _v in DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── Local imports (safe now that sys.path is fixed) ───────────────────────────
from utils.gsheet import set_driver_status, find_row


# ── Shared helpers ────────────────────────────────────────────────────────────
def map_embed(address: str, height: int = 260) -> str:
    if not address or not address.strip():
        return ""
    enc = address.strip().replace(" ", "+")
    return (f'<div class="map-frame">'
            f'<iframe width="100%" height="{height}" frameborder="0" '
            f'style="border:0;display:block" allowfullscreen '
            f'src="https://maps.google.com/maps?q={enc}&output=embed&z=15">'
            f'</iframe></div>')


def topbar(role_label: str, role_color: str = "#1a7f4b"):
    user = st.session_state.user
    c1, c2, c3 = st.columns([5, 3, 2])
    with c1:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:10px;padding:6px 0">'
            '<span style="font-size:1.6rem">🧄</span>'
            '<span style="font-family:Syne,sans-serif;font-weight:800;'
            'font-size:1.15rem;color:#1a7f4b">Garlic Order & Delivery</span>'
            '</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div style="text-align:center;padding-top:8px">'
            f'<span style="background:{role_color};color:#fff;padding:4px 14px;'
            f'border-radius:20px;font-size:.8rem;font-weight:700">{role_label}</span>'
            f'&nbsp;<code style="font-size:.72rem;color:#5a7a65">{user["uid"]}</code>'
            f'</div>', unsafe_allow_html=True)
    with c3:
        if st.button("🚪 Logout", key="logout_btn"):
            if user["role"] == "delivery Driver":
                dr = find_row("driver_onboard", "Mobile", user["phone"])
                if dr:
                    set_driver_status(dr["Driver ID"], "Offline")
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()
    st.divider()


# ── Page renderers ────────────────────────────────────────────────────────────
def render_login():
    from pages.login_page import show
    show()

def render_admin():
    topbar("🛡️ Admin", "#185fa5")
    from pages.admin.admin_dashboard import (
        show_skus, show_trips, show_assign_drivers,
        show_customers, show_drivers, show_orders, show_log,
    )
    user = st.session_state.user
    tabs = st.tabs(["📦 SKUs","🗺️ Trips","🚚 Assign Drivers",
                    "👤 Customers","🚗 Drivers","📋 Orders","📝 Audit Log"])
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
    from pages.sales.customer_onboard import show as show_onboard
    user = st.session_state.user
    tabs = st.tabs(["➕ New Order","👤 Onboard Customer","📋 My Orders"])
    with tabs[0]: show_order(user)
    with tabs[1]: show_onboard(user)
    with tabs[2]: show_history(user)

def render_delivery():
    topbar("🚚 Delivery Driver · T2", "#854f0b")
    from pages.delivery.route_view     import show as show_route, show_history
    from pages.delivery.driver_onboard import show as show_driver_onboard
    user = st.session_state.user
    tabs = st.tabs(["🗺️ My Route","📝 Driver Onboard","📦 History"])
    with tabs[0]: show_route(user)
    with tabs[1]: show_driver_onboard(user)
    with tabs[2]: show_history(user)


# ── Router ────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        render_login()
        return
    role = st.session_state.user["role"]
    if   role == "admin":            render_admin()
    elif role == "sales executive":  render_sales()
    elif role == "delivery Driver":  render_delivery()
    else:
        st.error(f"Unknown role '{role}' — contact admin.")
        if st.button("Logout"):
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()

main()
