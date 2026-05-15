"""pages/delivery/route_view.py  —  Driver route execution (T2)"""
import streamlit as st
from datetime import date, datetime
from utils.gsheet import (
    get_driver_trip, load_trips, read_sheet, find_row,
    update_row, set_driver_status, append_row
)
from utils.style import map_embed, section, pill

def show(user: dict):
    driver_id = st.session_state.get("driver_id", "")

    # Active status toggle
    col_status, col_refresh = st.columns([4,1])
    with col_status:
        is_active = st.session_state.get("driver_active", True)
        toggle_label = "🟢 Active — visible to admin" if is_active else "⚫ Offline"
        if st.button(toggle_label, key="active_toggle"):
            is_active = not is_active
            st.session_state.driver_active = is_active
            status = "Active" if is_active else "Offline"
            if driver_id:
                set_driver_status(driver_id, status)
            st.rerun()
    with col_refresh:
        if st.button("🔄", key="route_refresh", help="Refresh route"):
            st.rerun()

    if not is_active:
        st.warning("You are offline. Toggle Active to receive trips.")
        return

    # Find assigned trip
    trip = get_driver_trip(user["uid"])
    if not trip:
        st.info("📋 No trip assigned yet. Contact admin to assign a route.")
        return

    # Parse shops
    shops_raw = str(trip.get("Shops",""))
    shop_ids  = [s.strip() for s in shops_raw.split(",") if s.strip()]

    st.markdown(section(f"🗺️ Trip: {trip['Trip ID']} — {trip['City']} · {trip['Date']}", "amber"),
                unsafe_allow_html=True)
    st.markdown(f"**{len(shop_ids)} stops assigned** — complete each in order to unlock the next.",
                unsafe_allow_html=True)

    # Load all orders for this trip
    orders_df = read_sheet("base")
    trip_orders = {}
    if not orders_df.empty:
        t_rows = orders_df[orders_df["Tripid"].astype(str) == str(trip["Trip ID"])]
        for _, r in t_rows.iterrows():
            trip_orders[str(r["CustomerId"])] = r.to_dict()

    # Trip start
    if str(trip.get("Status","")).lower() == "assigned":
        st.info("Trip not started yet.")
        if st.button("▶️ Start Trip", type="primary"):
            update_row("trips","Trip ID", trip["Trip ID"], {"Status":"In Progress"})
            st.rerun()
        return

    # Active stop index
    if "active_stop" not in st.session_state:
        st.session_state.active_stop = 0

    active_idx = st.session_state.active_stop

    # Count done stops
    done_stops = 0
    for sid in shop_ids:
        o = trip_orders.get(sid)
        if o and str(o.get("Delivery Status","")) not in ("Pending",""):
            done_stops += 1
    if done_stops > active_idx:
        active_idx = done_stops
        st.session_state.active_stop = active_idx

    # Render each stop
    for i, sid in enumerate(shop_ids):
        shop = find_row("customer_onboard","CUST-ID", sid)
        order = trip_orders.get(sid)
        is_done   = order and str(order.get("Delivery Status","")) not in ("Pending","")
        is_active = (i == active_idx) and not is_done
        is_locked = i > active_idx and not is_done

        status_txt = order.get("Delivery Status","Pending") if order else "No order"
        pill_cls = ("pill-done" if is_done else "pill-pend" if is_active else "pill-offline")

        with st.container():
            left, right = st.columns([10,2])
            with left:
                icon = "✅" if is_done else ("📍" if is_active else "🔒")
                st.markdown(f"**{icon} Stop {i+1}** — {shop.get('Shop Name','') if shop else sid}")
                if shop:
                    st.caption(f"{shop.get('Shop Address','')} · Opens: {shop.get('Shop Address','')}")
                if order:
                    st.caption(f"SKU: {order.get('SKU','')} · Qty: {order.get('OrderedQty','')} · ₹{order.get('OrderTotal','')}")
            with right:
                st.markdown(pill(status_txt, pill_cls), unsafe_allow_html=True)

        if is_active and not is_locked:
            # Show map
            addr = shop.get("Shop Address","") if shop else ""
            if addr:
                st.markdown(map_embed(addr, 200), unsafe_allow_html=True)

            # Delivery form
            with st.form(key=f"del_form_{i}"):
                st.markdown("##### Delivery update")
                d1, d2, d3 = st.columns(3)
                with d1:
                    reach_time  = st.time_input("Shop reach time *", value=datetime.now().time())
                    del_date    = st.date_input("Delivered date", value=date.today())
                with d2:
                    del_status  = st.selectbox("Delivery status *",
                                               ["Delivered","Partial","Failed","Rescheduled"])
                with d3:
                    return_qty  = st.number_input("Return qty", min_value=0.0, step=0.5)
                    return_rsn  = st.text_input("Return reason")

                notes = st.text_input("Notes (optional)")
                submitted = st.form_submit_button("✅ Submit & Unlock Next Stop",
                                                   type="primary", use_container_width=True)

            if submitted:
                if order:
                    update_row("base","Order ID", order["Order ID"], {
                        "Delivery Status":    del_status,
                        "ShopReachTime":      str(reach_time),
                        "DELIVERED DATE":     str(del_date),
                        "ReturnQty":          return_qty,
                        "Reason":             return_rsn,
                        "return_updated_role":"delivery Driver",
                    })
                st.session_state.active_stop = i + 1
                st.success(f"✅ Stop {i+1} marked {del_status}. Next stop unlocked!")
                st.rerun()

        st.divider()

    # All done
    if active_idx >= len(shop_ids):
        st.success("🎉 All stops completed! Trip finished.")
        update_row("trips","Trip ID", trip["Trip ID"], {"Status":"Completed"})

def show_history(user: dict):
    df = read_sheet("base")
    if df.empty:
        st.info("No delivery history.")
        return
    my = df[df["return_updated_role"].astype(str) == "delivery Driver"]
    my = my[my["Delivery Status"] != "Pending"]
    if my.empty:
        st.info("No completed deliveries yet.")
        return
    st.dataframe(
        my[["Order ID","Customer shop name","SKU","OrderedQty",
            "Delivery Status","DELIVERED DATE","ReturnQty","Reason"]].sort_values(
            "DELIVERED DATE", ascending=False),
        use_container_width=True, hide_index=True
    )
