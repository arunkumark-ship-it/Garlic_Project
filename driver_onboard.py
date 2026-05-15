"""pages/delivery/driver_onboard.py  —  Driver onboarding"""
import streamlit as st
from datetime import date
from utils.gsheet import append_row, col_exists, find_row
from utils.auth import gen_driver_id
from utils.style import section

def show(user: dict):
    st.markdown(section("🚚 Driver Onboarding", "amber"), unsafe_allow_html=True)

    # Search existing
    st.markdown("#### Check existing driver")
    c1, c2 = st.columns([3,1])
    with c1:
        s_mobile = st.text_input("Search by mobile", placeholder="10-digit", key="do_search")
    with c2:
        st.write(""); st.write("")
        do_search = st.button("🔍 Search", key="do_search_btn")

    if do_search and s_mobile:
        existing = find_row("driver_onboard", "Mobile", s_mobile)
        if existing:
            st.success(f"✅ Already onboarded!")
            # Mask account number
            acct = str(existing.get("Account Number",""))
            masked = ("*" * (len(acct)-4) + acct[-4:]) if len(acct) > 4 else "****"
            st.json({
                "Driver ID":   existing.get("Driver ID"),
                "Name":        existing.get("Full Name"),
                "Mobile":      existing.get("Mobile"),
                "Vehicle":     existing.get("Vehicle Type"),
                "Bank":        existing.get("Bank Name"),
                "Account":     masked,
                "Active":      existing.get("Active Status"),
            })
            return
        else:
            st.info("Not found — fill below to onboard.")

    st.divider()
    st.markdown("#### New driver details")

    col1, col2, col3 = st.columns(3)
    with col1:
        full_name   = st.text_input("Full name *", key="do_name")
        mobile      = st.text_input("Mobile number *", placeholder="10-digit", key="do_mob")
        email       = st.text_input("Email ID", key="do_email")
    with col2:
        vehicle     = st.selectbox("Vehicle type", ["Bike","Auto","Van","Truck","Mini-Truck"], key="do_veh")
        bank_name   = st.text_input("Bank name *", key="do_bank")
        account_no  = st.text_input("Account number *", key="do_acct")
    with col3:
        ifsc        = st.text_input("IFSC code *", key="do_ifsc")
        upi         = st.text_input("UPI ID", placeholder="mobile@upi", key="do_upi")

    st.caption("🔒 Bank details are stored securely and only visible to admin.")
    st.divider()

    if st.button("✅ Onboard Driver", type="primary", use_container_width=True):
        if not all([full_name, mobile, bank_name, account_no, ifsc]):
            st.error("Fill all required (*) fields.")
            return
        with st.spinner("Checking duplicates…"):
            if col_exists("driver_onboard", "Mobile", mobile):
                ex = find_row("driver_onboard", "Mobile", mobile)
                st.warning(f"⚠️ Mobile already registered. Driver ID: **{ex['Driver ID']}**")
                return

        driver_id = gen_driver_id()
        today = str(date.today())
        row = [
            driver_id, full_name, mobile, email, vehicle,
            bank_name, account_no, ifsc, upi,
            today, "Offline", "",
        ]
        with st.spinner("Saving…"):
            append_row("driver_onboard", row)
        st.success("✅ Driver onboarded!")
        st.info(f"Permanent Driver ID: **{driver_id}**")
        st.balloons()
