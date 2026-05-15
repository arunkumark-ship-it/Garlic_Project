"""pages/sales/order_form.py  —  Sales order entry (T1)"""
import streamlit as st
from datetime import date, datetime
from utils.gsheet import (
    append_row, load_all_customers, get_active_skus,
    get_customer_by_id, get_customer_by_mobile, read_sheet
)
from utils.auth import gen_order_id
from utils.style import map_embed, section

def show(user: dict):
    # ── Customer lookup ───────────────────────────────────────────────────────
    st.markdown(section("🔍 Customer Lookup"), unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        lookup_id     = st.text_input("Customer ID", placeholder="CUST-XXXXXX", key="ol_id")
    with c2:
        lookup_mobile = st.text_input("OR search by mobile", placeholder="10-digit mobile", key="ol_mob")
    with c3:
        st.write(""); st.write("")
        do_lookup = st.button("Fetch →", key="ol_btn")

    if "cust_data" not in st.session_state:
        st.session_state.cust_data = {}

    if do_lookup:
        with st.spinner("Looking up customer…"):
            cust = None
            if lookup_id:
                cust = get_customer_by_id(lookup_id.strip())
            elif lookup_mobile:
                cust = get_customer_by_mobile(lookup_mobile.strip())
        if cust:
            st.session_state.cust_data = cust
            st.success(f"✅ Found: {cust.get('Full Name')} — {cust.get('Shop Name')}")
        else:
            st.error("❌ Customer not found. Please onboard first.")
            st.session_state.cust_data = {}

    cust = st.session_state.cust_data

    st.divider()

    # ── Order details ─────────────────────────────────────────────────────────
    st.markdown(section("📦 Order Details"), unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        order_id   = st.text_input("Order ID (auto)", value=gen_order_id(), disabled=True, key="f_oid")
        order_date = st.date_input("Order date", value=date.today(), key="f_date")
    with col2:
        city = st.selectbox("City *", ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Hassan", "Tumkur"],
                            index=["Bengaluru","Mysuru","Hubli","Mangaluru","Hassan","Tumkur"].index(
                                cust.get("City","Bengaluru")) if cust.get("City") in
                                ["Bengaluru","Mysuru","Hubli","Mangaluru","Hassan","Tumkur"] else 0,
                            key="f_city")
        ordered_time = st.time_input("Ordered time", value=datetime.now().time(), key="f_time")
    with col3:
        delivery_cutoff = st.time_input("Delivery cut-off", key="f_dcoff")
        shop_open       = st.time_input("Shop opening from", key="f_sopen")

    # ── Customer details (auto-filled, read-only) ─────────────────────────────
    st.markdown(section("👤 Customer Details"), unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    with col4:
        cust_id   = st.text_input("Customer ID", value=cust.get("CUST-ID",""), disabled=True, key="f_cid")
        cust_name = st.text_input("Shop name",   value=cust.get("Shop Name",""),  disabled=True, key="f_cname")
    with col5:
        cust_num  = st.text_input("Mobile",      value=cust.get("Mobile",""),     disabled=True, key="f_cnum")
        cust_cls  = st.text_input("Classification", value=cust.get("Classification",""), disabled=True, key="f_cls")
    with col6:
        se_name   = st.text_input("Sales executive", value=user["name"], disabled=True, key="f_se")
        se_uid    = st.text_input("SE UID",          value=user["uid"],  disabled=True, key="f_seuid")

    # ── SKU ───────────────────────────────────────────────────────────────────
    st.markdown(section("🛒 SKU / Product"), unsafe_allow_html=True)
    skus_df = get_active_skus()
    if skus_df.empty:
        st.warning("⚠️ No active SKUs. Ask admin to add SKUs.")
        return

    sku_options = skus_df["SKU Code"].tolist()
    col7, col8, col9 = st.columns(3)
    with col7:
        selected_sku = st.selectbox("SKU *", sku_options, key="f_sku")
        sku_row = skus_df[skus_df["SKU Code"] == selected_sku].iloc[0]
    with col8:
        price = float(sku_row["Price"])
        wtype = str(sku_row["Weight Type"])
        st.text_input("Unit price (₹) — admin rate", value=f"₹{price:.2f}", disabled=True, key="f_price")
        st.text_input("Weight type", value=wtype, disabled=True, key="f_wtype")
    with col9:
        ordered_qty = st.number_input("Ordered qty *", min_value=0.0, step=0.5, key="f_qty")
        total = price * ordered_qty
        st.text_input("Order total (₹)", value=f"₹{total:.2f}", disabled=True, key="f_total")

    # ── Location ──────────────────────────────────────────────────────────────
    st.markdown(section("📍 Shop Location"), unsafe_allow_html=True)
    addr_default = cust.get("Shop Address", "")
    shop_addr = st.text_input("Shop address *", value=addr_default, key="f_addr")
    if shop_addr:
        st.markdown(map_embed(shop_addr, 240), unsafe_allow_html=True)

    st.divider()

    # ── Submit ────────────────────────────────────────────────────────────────
    if st.button("✅ Submit Order", type="primary", use_container_width=True):
        if not cust:
            st.error("Look up a customer first.")
            return
        if not selected_sku or ordered_qty <= 0:
            st.error("Select SKU and enter quantity.")
            return

        soid = "SO-" + order_id.replace("ORD-","")
        row = [
            order_id, soid, city,
            str(order_date), "",          # ORDER DATE, DELIVERED DATE
            str(ordered_time),
            cust.get("CUST-ID",""), cust.get("Shop Name",""), cust.get("Mobile",""),
            cust.get("Classification",""),
            user["name"], user["uid"],
            selected_sku, wtype, price, ordered_qty, total,
            0, "", "",                     # ReturnQty, Reason, return_updated_role
            "", "",                        # Tripid, Transport
            str(shop_open), "",            # ShopOpeningFrom, ShopReachTime
            str(delivery_cutoff),
            shop_addr,
            "Pending",
            user["uid"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ]
        with st.spinner("Saving order…"):
            append_row("base", row)
        st.success(f"✅ Order submitted! **{order_id}** · Total: **₹{total:,.2f}**")
        st.session_state.cust_data = {}
        st.balloons()

def show_history(user: dict):
    """My orders tab."""
    df = read_sheet("base")
    if df.empty:
        st.info("No orders yet.")
        return
    my = df[df["sales executive Number"].astype(str) == user["uid"]]
    if my.empty:
        st.info("You have not submitted any orders yet.")
        return

    # Stats
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total orders", len(my))
    c2.metric("Pending",   len(my[my["Delivery Status"]=="Pending"]))
    c3.metric("Delivered", len(my[my["Delivery Status"]=="Delivered"]))
    total_val = my["OrderTotal"].apply(lambda x: float(str(x).replace("₹","").replace(",","")) if str(x).strip() else 0).sum()
    c4.metric("Total value", f"₹{total_val:,.0f}")

    st.dataframe(
        my[["Order ID","Customer shop name","SKU","OrderedQty","OrderTotal",
            "ORDER DATE","Delivery Status"]].sort_values("ORDER DATE", ascending=False),
        use_container_width=True, hide_index=True
    )
