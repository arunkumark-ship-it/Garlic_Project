"""pages/login_page.py  —  Login + Register"""
import streamlit as st
from utils.auth import login_user, register_user, gen_uid
from utils.style import inject

def show():
    inject()
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;margin-top:2.5rem;margin-bottom:1rem">
      <div style="width:70px;height:70px;border-radius:18px;background:#1a7f4b;
                  display:flex;align-items:center;justify-content:center;
                  font-size:36px;margin-bottom:12px;box-shadow:0 8px 24px rgba(26,127,75,.35)">🧄</div>
      <h1 style="font-size:1.8rem;color:#0d1f14;margin:0">Garlic Order & Delivery</h1>
      <p style="color:#5a7a65;font-size:.95rem;margin-top:4px">Field Operations Platform</p>
    </div>""", unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        tab_login, tab_reg = st.tabs(["🔐  Login", "📝  Register"])

        # ── LOGIN ─────────────────────────────────────────────────────────────
        with tab_login:
            phone    = st.text_input("Phone number", placeholder="Registered phone", key="lg_ph")
            password = st.text_input("Password", type="password", key="lg_pw")
            if st.button("Login →", type="primary", use_container_width=True):
                if not phone or not password:
                    st.error("Enter phone and password.")
                else:
                    with st.spinner("Verifying…"):
                        user, err = login_user(phone, password)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user      = user
                        # Auto-set driver active status on login
                        if user["role"] == "delivery Driver":
                            from utils.gsheet import set_driver_status, find_row
                            dr = find_row("driver_onboard", "Mobile", user["phone"])
                            if dr:
                                set_driver_status(dr["Driver ID"], "Active")
                                st.session_state.driver_id = dr["Driver ID"]
                        st.rerun()

        # ── REGISTER ──────────────────────────────────────────────────────────
        with tab_reg:
            r_name  = st.text_input("Full name", key="rg_name")
            r_phone = st.text_input("Phone number", key="rg_phone")
            r_role  = st.selectbox("Role", ["sales executive", "delivery Driver", "admin"], key="rg_role")
            r_pw    = st.text_input("Password", type="password", key="rg_pw")
            r_pw2   = st.text_input("Confirm password", type="password", key="rg_pw2")

            if st.button("Create account →", type="primary", use_container_width=True):
                if not all([r_name, r_phone, r_pw, r_pw2]):
                    st.error("Fill in all fields.")
                elif r_pw != r_pw2:
                    st.error("Passwords do not match.")
                elif len(r_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account…"):
                        uid, err = register_user(r_name, r_phone, r_role, r_pw)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.success(f"✅ Account created!")
                        st.info(f"Your permanent UID: **{uid}**  — save this, it never changes.")
