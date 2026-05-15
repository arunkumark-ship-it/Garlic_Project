import sys as _sys, os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in [_ROOT, _os.path.join(_ROOT,"utils"), _os.path.join(_ROOT,"pages")]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

"""pages/admin/admin_dashboard.py  —  Full admin control panel"""
import streamlit as st
import uuid
from datetime import date, datetime
from utils.gsheet import (
    read_sheet, append_row, update_row,
    get_active_drivers, load_trips, write_admin_log,
    load_skus, get_active_skus, load_all_customers
)
from utils.style import section, pill, map_embed

# ── SKU Management ────────────────────────────────────────────────────────────
def show_skus(user: dict):
    st.markdown(section("📦 SKU Master"), unsafe_allow_html=True)
    df = load_skus()

    # Stats
    if not df.empty:
        active_n  = len(df[df["Active"].astype(str).str.lower()=="true"])
        disabled_n = len(df) - active_n
        avg_price = df["Price"].apply(lambda x: float(str(x).replace("₹","").replace(",","") or 0)).mean()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total SKUs",  len(df))
        c2.metric("Active",      active_n)
        c3.metric("Disabled",    disabled_n)
        c4.metric("Avg price",   f"₹{avg_price:,.2f}")

    # Add new SKU
    with st.expander("➕ Onboard new SKU", expanded=False):
        col1,col2,col3 = st.columns(3)
        with col1:
            sk_code  = st.text_input("SKU code *", placeholder="GRLIC-1KG", key="sk_code")
            sk_name  = st.text_input("SKU name *", placeholder="Garlic 1KG Pack", key="sk_name")
        with col2:
            sk_price = st.number_input("Price (₹) *", min_value=0.0, step=1.0, key="sk_price")
            sk_wtype = st.selectbox("Weight type", ["KG","Gram","Box","Piece","Dozen"], key="sk_wt")
        with col3:
            sk_cat   = st.text_input("Category", placeholder="Garlic", key="sk_cat")

        if st.button("Add SKU", type="primary", key="sk_add"):
            if not sk_code or not sk_name or sk_price <= 0:
                st.error("Code, name and price are required.")
            else:
                existing = read_sheet("skus")
                if not existing.empty and sk_code in existing["SKU Code"].values:
                    st.error("SKU code already exists.")
                else:
                    append_row("skus", [
                        sk_code, sk_name, sk_price, sk_wtype,
                        sk_cat or "General", "true",
                        user["uid"], str(date.today()),
                    ])
                    load_skus.clear()
                    write_admin_log(user["uid"],"ADD SKU","SKU",sk_code,"","",sk_name)
                    st.success(f"SKU **{sk_code}** added!")
                    st.rerun()

    # List & edit
    st.markdown("#### All SKUs")
    df = read_sheet("skus")
    if df.empty:
        st.info("No SKUs yet.")
        return

    for idx, row in df.iterrows():
        c1,c2,c3,c4,c5 = st.columns([2,2,1.5,1,1.5])
        c1.markdown(f"**{row['SKU Code']}**")
        c2.write(row["SKU Name"])

        # Inline price edit
        new_price = c3.number_input("Price",value=float(str(row["Price"]).replace("₹","").replace(",","") or 0),
                                    step=1.0, key=f"sk_price_{idx}", label_visibility="collapsed")
        if new_price != float(str(row["Price"]).replace("₹","").replace(",","") or 0):
            if c3.button("💾", key=f"sk_save_{idx}"):
                update_row("skus","SKU Code",row["SKU Code"],{"Price":new_price})
                write_admin_log(user["uid"],"PRICE CHANGE","SKU",row["SKU Code"],row["Price"],new_price)
                load_skus.clear()
                st.rerun()

        is_active = str(row.get("Active","")).lower() == "true"
        c4.markdown(pill("Active","pill-on") if is_active else pill("Off","pill-off"), unsafe_allow_html=True)
        toggle_lbl = "Disable" if is_active else "Enable"
        if c5.button(toggle_lbl, key=f"sk_tog_{idx}"):
            new_status = "false" if is_active else "true"
            update_row("skus","SKU Code",row["SKU Code"],{"Active":new_status})
            write_admin_log(user["uid"],toggle_lbl+" SKU","SKU",row["SKU Code"],"","",
                           "Stock available" if new_status=="true" else "No stock")
            load_skus.clear()
            st.rerun()
        st.divider()

# ── Trip / Route builder ──────────────────────────────────────────────────────
def show_trips(user: dict):
    st.markdown(section("🗺️ Trips & Routes"), unsafe_allow_html=True)

    with st.expander("➕ Create new trip", expanded=False):
        col1,col2,col3 = st.columns(3)
        with col1:
            tr_id   = st.text_input("Trip ID *", placeholder="TRP-001", key="tr_id")
            tr_date = st.date_input("Trip date *", value=date.today(), key="tr_date")
        with col2:
            tr_city = st.selectbox("City", ["Bengaluru","Mysuru","Hubli","Mangaluru"], key="tr_city")
        with col3:
            pass

        # Shop selector
        custs = load_all_customers()
        if not custs.empty:
            shop_options = custs.apply(lambda r: f"{r['CUST-ID']} — {r['Shop Name']} ({r['City']})", axis=1).tolist()
            cust_ids     = custs["CUST-ID"].tolist()
            selected_shops = st.multiselect("Select shops for this trip *", shop_options, key="tr_shops")
            selected_ids   = [cust_ids[shop_options.index(s)] for s in selected_shops]
        else:
            st.warning("No customers onboarded yet.")
            selected_ids = []

        if st.button("Create trip", type="primary", key="tr_create"):
            if not tr_id or not selected_ids:
                st.error("Trip ID and at least one shop required.")
            else:
                trips_df = load_trips()
                if not trips_df.empty and tr_id in trips_df["Trip ID"].values:
                    st.error("Trip ID already exists.")
                else:
                    append_row("trips",[
                        tr_id, str(tr_date), tr_city,
                        ",".join(selected_ids),
                        "","","Assigned",
                        user["uid"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ])
                    write_admin_log(user["uid"],"CREATE TRIP","Trip",tr_id,"","",
                                   f"{len(selected_ids)} shops")
                    st.success(f"Trip **{tr_id}** created with {len(selected_ids)} shops!")
                    st.rerun()

    # Existing trips
    trips_df = load_trips()
    if trips_df.empty:
        st.info("No trips created yet.")
        return
    st.dataframe(trips_df, use_container_width=True, hide_index=True)

# ── Assign drivers ────────────────────────────────────────────────────────────
def show_assign_drivers(user: dict):
    st.markdown(section("🚚 Assign Drivers"), unsafe_allow_html=True)

    # Active drivers panel
    st.markdown("#### 🟢 Active drivers right now")
    active_df = get_active_drivers()
    if active_df.empty:
        st.warning("No drivers are currently active. Drivers go active when they log in.")
    else:
        for _,r in active_df.iterrows():
            c1,c2,c3 = st.columns([2,2,2])
            c1.markdown(f"**{r['Full Name']}**")
            c2.write(f"{r['Driver ID']} · {r['Vehicle Type']}")
            c3.write(f"Active since: {r.get('Last Active','')}")

    st.divider()

    # Assign form — only active drivers
    if active_df.empty:
        st.info("No active drivers to assign.")
        return

    trips_df = load_trips()
    unassigned = trips_df[trips_df["Driver UID"].astype(str).str.strip()==""] if not trips_df.empty else None
    if unassigned is None or unassigned.empty:
        st.info("All trips have drivers assigned, or no trips created yet.")
        return

    col1,col2 = st.columns(2)
    with col1:
        trip_options = unassigned["Trip ID"].tolist()
        sel_trip = st.selectbox("Select trip to assign", trip_options, key="asgn_trip")
        if sel_trip:
            t = unassigned[unassigned["Trip ID"]==sel_trip].iloc[0]
            shops_raw = str(t.get("Shops",""))
            n_shops = len([s for s in shops_raw.split(",") if s.strip()])
            st.caption(f"📦 {n_shops} shops · {t['City']} · {t['Date']}")
    with col2:
        driver_options = active_df.apply(
            lambda r: f"{r['Full Name']} ({r['Driver ID']})", axis=1).tolist()
        driver_ids = active_df["Driver ID"].tolist()
        sel_driver_lbl = st.selectbox("Select active driver", driver_options, key="asgn_driver")
        sel_driver_id  = driver_ids[driver_options.index(sel_driver_lbl)] if sel_driver_lbl else ""
        driver_name    = active_df[active_df["Driver ID"]==sel_driver_id]["Full Name"].values[0] if sel_driver_id else ""

    if st.button("✅ Assign Driver to Trip", type="primary"):
        update_row("trips","Trip ID",sel_trip,{
            "Driver UID":   sel_driver_id,
            "Driver Name":  driver_name,
            "Status":       "Assigned",
        })
        write_admin_log(user["uid"],"ASSIGN DRIVER","Trip",sel_trip,"",sel_driver_id,driver_name)
        st.success(f"**{driver_name}** assigned to **{sel_trip}**!")
        st.rerun()

# ── Customer view ─────────────────────────────────────────────────────────────
def show_customers():
    st.markdown(section("👤 Customer Onboard Data"), unsafe_allow_html=True)
    df = load_all_customers()
    if df.empty:
        st.info("No customers onboarded yet.")
        return
    c1,c2,c3 = st.columns(3)
    c1.metric("Total customers", len(df))
    c2.metric("Active", len(df[df["Status"]=="Active"]))
    cities = df["City"].value_counts().to_dict()
    c3.metric("Cities", len(cities))
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Driver view ───────────────────────────────────────────────────────────────
def show_drivers():
    st.markdown(section("🚚 Driver Onboard Data", "amber"), unsafe_allow_html=True)
    df = read_sheet("driver_onboard")
    if df.empty:
        st.info("No drivers onboarded yet.")
        return
    c1,c2,c3 = st.columns(3)
    c1.metric("Total drivers", len(df))
    c2.metric("Active now", len(df[df["Active Status"]=="Active"]))
    c3.metric("Offline", len(df[df["Active Status"]=="Offline"]))

    # Mask account numbers
    display_df = df.copy()
    if "Account Number" in display_df.columns:
        def mask(v):
            v = str(v)
            return ("*"*(len(v)-4)+v[-4:]) if len(v)>4 else "****"
        display_df["Account Number"] = display_df["Account Number"].apply(mask)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Orders overview ───────────────────────────────────────────────────────────
def show_orders():
    st.markdown(section("📋 All Orders"), unsafe_allow_html=True)
    df = read_sheet("base")
    if df.empty:
        st.info("No orders yet.")
        return
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total",     len(df))
    c2.metric("Pending",   len(df[df["Delivery Status"]=="Pending"]))
    c3.metric("Delivered", len(df[df["Delivery Status"]=="Delivered"]))
    failed = len(df[df["Delivery Status"].isin(["Failed","Partial"])])
    c4.metric("Failed/Partial", failed)
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Admin log ─────────────────────────────────────────────────────────────────
def show_log():
    st.markdown(section("📝 Admin Audit Log", "blue"), unsafe_allow_html=True)
    df = read_sheet("admin_log")
    if df.empty:
        st.info("No admin actions logged yet.")
        return
    st.dataframe(df.sort_values("Timestamp",ascending=False),
                 use_container_width=True, hide_index=True)
