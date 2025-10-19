import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px

# ===========================
# PAGE CONFIG
# ===========================
st.set_page_config(page_title="Centralized Stationery Request", layout="wide")
st.title("🗂️ Centralized Stationery Request & Usage System")

# ===========================
# SIDEBAR: ITEM MASTER UPLOAD
# ===========================
st.sidebar.header("📁 Item Master Management")

uploaded_file = st.sidebar.file_uploader("Upload Item Master (.csv)", type="csv")
if uploaded_file is not None:
    with open("items_master.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Item master has been updated!")
    st.rerun()

# ===========================
# LOAD ITEM MASTER
# ===========================
@st.cache_data
def load_item_master():
    df = pd.read_csv("items_master.csv")
    df.columns = df.columns.str.strip()
    return df

if not os.path.exists("items_master.csv"):
    st.warning("⚠️ No 'items_master.csv' file found. Please upload it first in the sidebar.")
    st.stop()

item_master = load_item_master()

# ===========================
# MAIN MENU
# ===========================
menu = st.sidebar.radio(
    "Select Page:",
    ["📝 Request Items", "📦 Usage Entry", "📊 Data Summary"]
)

# ===========================
# DEPARTMENT LIST
# ===========================
departments = [
    "Administration", "HR & GA", "Finance", "Production",
    "Quality Control", "Warehouse", "Engineering", "Procurement"
]

# ===========================
# PAGE 1: REQUEST ITEMS
# ===========================
if menu == "📝 Request Items":
    st.subheader("🧾 Stationery Request Form")

    # Request info
    col1, col2, col3 = st.columns(3)
    with col1:
        department = st.selectbox("Department", departments)
    with col2:
        requester = st.text_input("Requester Name")
    with col3:
        request_date = st.date_input("Request Date", datetime.date.today())

    remarks = st.text_area("Remarks / Notes (optional)")

    st.divider()

    # Item selection
    item_selected = st.selectbox("Search Item", item_master["Description"].tolist())

    # Get details
    item_data = item_master[item_master["Description"] == item_selected].iloc[0]
    part_number = item_data.get("Part Number", "")
    uom = item_data.get("UOM", "-")

    # Auto-read Unit Price (if exists)
    price_columns = [c for c in item_master.columns if "price" in c.lower()]
    if price_columns:
        unit_price = item_data[price_columns[0]]
    else:
        unit_price = item_data.get("Unit Price", 0)

    quantity = st.number_input("Quantity", min_value=1, step=1)

    st.write(f"**Part Number:** {part_number}")
    st.write(f"**UOM:** {uom}")
    st.write(f"**Unit Price (IDR):** {unit_price:,}")

    if "requests" not in st.session_state:
        st.session_state.requests = []

    if st.button("💾 Save Request"):
        total = quantity * float(unit_price)
        st.session_state.requests.append({
            "Date": request_date.strftime("%Y-%m-%d"),
            "Department": department,
            "Requester": requester,
            "Description": item_selected,
            "Part Number": part_number,
            "UOM": uom,
            "Quantity": quantity,
            "Unit Price (IDR)": unit_price,
            "Total (IDR)": total,
            "Remarks": remarks
        })
        st.success("✅ Request saved successfully!")

# ===========================
# PAGE 2: USAGE ENTRY
# ===========================
elif menu == "📦 Usage Entry":
    st.subheader("📦 Stationery Usage Entry")

    col1, col2 = st.columns(2)
    with col1:
        department = st.selectbox("Department", departments)
    with col2:
        usage_date = st.date_input("Usage Date", datetime.date.today())

    item_selected = st.selectbox("Select Item Used", item_master["Description"].tolist())
    item_data = item_master[item_master["Description"] == item_selected].iloc[0]
    part_number = item_data.get("Part Number", "")
    uom = item_data.get("UOM", "-")

    qty_used = st.number_input("Usage Quantity", min_value=1, step=1)
    used_by = st.text_input("Used By (Name)")
    remarks = st.text_area("Usage Notes / Remarks (optional)")

    if "usage" not in st.session_state:
        st.session_state.usage = []

    if st.button("💾 Save Usage"):
        st.session_state.usage.append({
            "Date": usage_date.strftime("%Y-%m-%d"),
            "Department": department,
            "Used By": used_by,
            "Description": item_selected,
            "Part Number": part_number,
            "UOM": uom,
            "Quantity Used": qty_used,
            "Remarks": remarks
        })
        st.success("✅ Usage record saved successfully!")

# ===========================
# PAGE 3: DATA SUMMARY + CHARTS
# ===========================
elif menu == "📊 Data Summary":
    st.subheader("📊 Stationery Request & Usage Summary")

    tab1, tab2, tab3 = st.tabs(["📝 Requests", "📦 Usage", "📈 Dashboard"])

    # REQUESTS
    with tab1:
        if "requests" in st.session_state and len(st.session_state.requests) > 0:
            df_req = pd.DataFrame(st.session_state.requests)
            st.dataframe(df_req, use_container_width=True)
            total_all = df_req["Total (IDR)"].sum()
            st.write(f"**Total Requested Value: {total_all:,.0f} IDR**")

            csv = df_req.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Requests (CSV)", csv, "requests_summary.csv", "text/csv")
        else:
            st.info("No request data yet.")

    # USAGE
    with tab2:
        if "usage" in st.session_state and len(st.session_state.usage) > 0:
            df_usage = pd.DataFrame(st.session_state.usage)
            st.dataframe(df_usage, use_container_width=True)

            csv2 = df_usage.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Usage (CSV)", csv2, "usage_summary.csv", "text/csv")
        else:
            st.info("No usage data yet.")

    # DASHBOARD
    with tab3:
        st.subheader("📊 Visualization Dashboard")

        if "requests" in st.session_state and len(st.session_state.requests) > 0:
            df_req = pd.DataFrame(st.session_state.requests)

            # Department totals
            dept_summary = df_req.groupby("Department")["Total (IDR)"].sum().reset_index()
            fig1 = px.bar(dept_summary, x="Department", y="Total (IDR)", title="Total Requests by Department")
            st.plotly_chart(fig1, use_container_width=True)

            # Top items
            item_summary = df_req.groupby("Description")["Total (IDR)"].sum().reset_index().sort_values(by="Total (IDR)", ascending=False).head(10)
            fig2 = px.bar(item_summary, x="Description", y="Total (IDR)", title="Top 10 Requested Items")
            st.plotly_chart(fig2, use_container_width=True)

            # Monthly trend
            df_req["Month"] = pd.to_datetime(df_req["Date"]).dt.to_period("M").astype(str)
            month_summary = df_req.groupby("Month")["Total (IDR)"].sum().reset_index()
            fig3 = px.line(month_summary, x="Month", y="Total (IDR)", markers=True, title="Monthly Request Trend")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No data yet to display charts.")

    # RESET
    if st.button("🗑️ Reset All Data"):
        st.session_state.requests = []
        st.session_state.usage = []
        st.success("✅ All data has been cleared!")
