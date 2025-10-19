import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Centralized Stationery Request", layout="wide")

# Load data item master
@st.cache_data
def load_data():
    df = pd.read_csv("items_master.csv")
    df.columns = df.columns.str.strip()
    return df

# Cek file items_master.csv
if not os.path.exists("items_master.csv"):
    st.error("❌ File items_master.csv belum diunggah ke repository.")
else:
    master = load_data()

    st.title("📦 Centralized Stationery Request System")
    st.write("Gunakan form di bawah untuk mengajukan permintaan stationery dan otomatis merekap datanya.")

    with st.form("request_form"):
        col1, col2 = st.columns(2)

        with col1:
            dept = st.selectbox("Departemen", ["QA", "Production", "HRGA", "Finance", "PPIC", "R&D", "Engineering", "Warehouse"])
            requester = st.text_input("Nama PIC")

        with col2:
            tanggal = st.date_input("Tanggal Permintaan")
            remark = st.text_area("Keterangan (opsional)")

        st.subheader("🧾 Pilih Barang")
        selected_item = st.selectbox("Cari Barang", master["Description"].sort_values().unique())

        # Ambil data otomatis dari item master
        selected_row = master.loc[master["Description"] == selected_item].iloc[0]
        part_no = selected_row["Part Number"]
        uom = selected_row.get("UOM", "")
        price = selected_row.get("Unit Price", 0)

        qty = st.number_input("Jumlah", min_value=1, step=1)

        st.write(f"**Part Number:** {part_no}")
        st.write(f"**UOM:** {uom}")
        st.write(f"**Unit Price:** {price:,}")

        submitted = st.form_submit_button("💾 Simpan Request")

    if submitted:
        total = price * qty if isinstance(price, (int, float)) else ""
        new_row = {
            "Tanggal": tanggal,
            "Departemen": dept,
            "PIC": requester,
            "Part Number": part_no,
            "Deskripsi": selected_item,
            "UOM": uom,
            "Jumlah": qty,
            "Harga Satuan": price,
            "Total Harga": total,
            "Keterangan": remark
        }

        rekap_file = "rekap_request.csv"
        if os.path.exists(rekap_file):
            rekap = pd.read_csv(rekap_file)
        else:
            rekap = pd.DataFrame(columns=new_row.keys())

        rekap = pd.concat([rekap, pd.DataFrame([new_row])], ignore_index=True)
        rekap.to_csv(rekap_file, index=False)

        st.success("✅ Permintaan berhasil disimpan!")
        st.dataframe(rekap.tail(10), use_container_width=True)

# Tombol untuk hapus rekap (reset data)
if st.button("🗑 Reset Rekap Data"):
    if os.path.exists("rekap_request.csv"):
        os.remove("rekap_request.csv")
        st.warning("File rekap_request.csv berhasil dihapus.")
    else:
        st.info("Belum ada file rekap_request.csv.")
