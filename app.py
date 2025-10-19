import streamlit as st
import pandas as pd
import os

# ===========================
# KONFIGURASI AWAL
# ===========================
st.set_page_config(page_title="Centralized Stationery Request", layout="wide")
st.title("🗂️ Centralized Stationery Request & Usage System")

# ===========================
# SIDEBAR UPLOAD FILE
# ===========================
st.sidebar.header("📁 Item Master Management")

uploaded_file = st.sidebar.file_uploader("Upload Item Master (.csv)", type="csv")
if uploaded_file is not None:
    with open("items_master.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Item master berhasil diperbarui!")
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
    st.warning("⚠️ Belum ada file *items_master.csv*. Upload dulu di sidebar.")
    st.stop()

item_master = load_item_master()

# ===========================
# PILIHAN MENU
# ===========================
menu = st.sidebar.radio("Pilih Halaman:", ["📦 Request Barang", "🧾 Rekap Data", "📊 Pemakaian Barang"])

# ===========================
# HALAMAN REQUEST BARANG
# ===========================
if menu == "📦 Request Barang":
    st.subheader("📝 Form Request Barang")

    # Pilih barang
    item_selected = st.selectbox("Cari Barang", item_master["Description"].tolist())

    # Ambil data terkait
    item_data = item_master[item_master["Description"] == item_selected].iloc[0]
    part_number = item_data["Part Number"]
    uom = item_data.get("UOM", "-")
    unit_price = item_data.get("Unit Price", 0)

    jumlah = st.number_input("Jumlah", min_value=1, step=1)

    st.write(f"**Part Number:** {part_number}")
    st.write(f"**UOM:** {uom}")
    st.write(f"**Unit Price:** {unit_price:,}")

    # Simpan ke session state
    if "rekap" not in st.session_state:
        st.session_state.rekap = []

    if st.button("💾 Simpan Request"):
        total = jumlah * unit_price
        st.session_state.rekap.append({
            "Description": item_selected,
            "Part Number": part_number,
            "UOM": uom,
            "Jumlah": jumlah,
            "Unit Price": unit_price,
            "Total": total
        })
        st.success("✅ Request berhasil disimpan!")

# ===========================
# HALAMAN PEMAKAIAN
# ===========================
elif menu == "📊 Pemakaian Barang":
    st.subheader("📦 Form Pemakaian Barang (Usage)")

    # Pilih barang yang sudah ada
    item_selected = st.selectbox("Pilih Barang yang Dipakai", item_master["Description"].tolist())

    item_data = item_master[item_master["Description"] == item_selected].iloc[0]
    part_number = item_data["Part Number"]
    uom = item_data.get("UOM", "-")

    jumlah_pakai = st.number_input("Jumlah Pemakaian", min_value=1, step=1)
    nama_pengguna = st.text_input("Nama Pengguna / Departemen")

    if "usage" not in st.session_state:
        st.session_state.usage = []

    if st.button("💾 Simpan Pemakaian"):
        st.session_state.usage.append({
            "Description": item_selected,
            "Part Number": part_number,
            "UOM": uom,
            "Jumlah": jumlah_pakai,
            "Pengguna": nama_pengguna
        })
        st.success("✅ Data pemakaian berhasil disimpan!")

# ===========================
# HALAMAN REKAP DATA
# ===========================
elif menu == "🧾 Rekap Data":
    st.subheader("📊 Rekapitulasi Request & Pemakaian Barang")

    tab1, tab2 = st.tabs(["📦 Request", "📊 Pemakaian"])

    with tab1:
        if "rekap" in st.session_state and len(st.session_state.rekap) > 0:
            df_request = pd.DataFrame(st.session_state.rekap)
            st.dataframe(df_request, use_container_width=True)
            total_sum = df_request["Total"].sum()
            st.write(f"**Total Keseluruhan: {total_sum:,.0f}**")

            csv = df_request.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Rekap Request (CSV)", csv, "rekap_request.csv", "text/csv")
        else:
            st.info("Belum ada data request.")

    with tab2:
        if "usage" in st.session_state and len(st.session_state.usage) > 0:
            df_usage = pd.DataFrame(st.session_state.usage)
            st.dataframe(df_usage, use_container_width=True)

            csv = df_usage.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Rekap Pemakaian (CSV)", csv, "rekap_usage.csv", "text/csv")
        else:
            st.info("Belum ada data pemakaian.")

    if st.button("🗑️ Reset Semua Data"):
        st.session_state.rekap = []
        st.session_state.usage = []
        st.success("✅ Semua data berhasil dihapus!")
