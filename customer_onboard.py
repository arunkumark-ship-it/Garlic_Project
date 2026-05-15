import sys as _sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in [_ROOT, _os.path.join(_ROOT,"utils"), _os.path.join(_ROOT,"pages")]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

"""pages/sales/customer_onboard.py  —  Customer onboarding form"""
import streamlit as st
from datetime import date
from utils.gsheet import append_row, get_customer_by_mobile, load_all_customers
from utils.auth import gen_cust_id
from utils.style import map_embed, section

def show(user: dict):
    st.markdown(section("👤 Customer Onboarding"), unsafe_allow_html=True)

    # Search existing first
    st.markdown("#### Search existing customer")
    c1, c2 = st.columns([3, 1])
    with c1:
        search_mobile = st.text_input("Search by mobile number", placeholder="10-digit mobile", key="co_search")
    with c2:
        st.write("")
        st.write("")
        do_search = st.button("🔍 Search", key="co_search_btn")

    if do_search and search_mobile:
        existing = get_customer_by_mobile(search_mobile)
        if existing:
            st.success(f"✅ Customer already onboarded!")
            st.json({
                "CUST-ID":     existing.get("CUST-ID"),
                "Name":        existing.get("Full Name"),
                "Shop":        existing.get("Shop Name"),
                "Mobile":      existing.get("Mobile"),
                "City":        existing.get("City"),
                "Status":      existing.get("Status"),
            })
            return
        else:
            st.info("Not found — fill the form below to onboard.")

    st.divider()
    st.markdown("#### New customer details")

    col1, col2, col3 = st.columns(3)
    with col1:
        full_name = st.text_input("Full name *", key="co_name")
        mobile    = st.text_input("Mobile number *", placeholder="10-digit", key="co_mobile")
    with col2:
        email     = st.text_input("Email ID", placeholder="optional", key="co_email")
        shop_name = st.text_input("Shop name *", key="co_shop")
    with col3:
        city = st.selectbox("City *", ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Hassan", "Tumkur"], key="co_city")
        classification = st.selectbox("Classification", ["A", "B", "C", "Premium", "Wholesale", "Retail"], key="co_cls")

    shop_addr = st.text_input("Shop address (full) *", placeholder="House no, street, landmark, area…", key="co_addr")

    if shop_addr:
        st.markdown(map_embed(shop_addr, height=240), unsafe_allow_html=True)
        st.caption("📍 Verify the pin matches the shop, then submit.")

    st.divider()
    if st.button("✅ Onboard Customer", type="primary", use_container_width=True):
        if not all([full_name, mobile, shop_name, shop_addr]):
            st.error("Fill all required (*) fields.")
            return

        # Duplicate check
        with st.spinner("Checking for duplicates…"):
            existing = get_customer_by_mobile(mobile)
        if existing:
            st.warning(f"⚠️ Mobile already registered. Existing CUST-ID: **{existing['CUST-ID']}**")
            return

        cust_id = gen_cust_id()
        today   = str(date.today())
        row = [
            cust_id, full_name, mobile, email, shop_name,
            shop_addr, city, classification,
            user["uid"], today, "Active",
        ]
        with st.spinner("Saving…"):
            append_row("customer_onboard", row)
            # Bust cache so order form gets fresh list
            load_all_customers.clear()

        st.success(f"✅ Customer onboarded successfully!")
        st.info(f"Permanent Customer ID: **{cust_id}**")
        st.balloons()
