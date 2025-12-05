import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta
import plotly.express as px

# ---------------------------
# Inisialisasi session state
# ---------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "transactions" not in st.session_state:
    st.session_state.transactions = []  # list of dicts: tanggal, jenis, jumlah, kategori, catatan, user

if "savings" not in st.session_state:
    st.session_state.savings = []

if "categories" not in st.session_state:
    st.session_state.categories = ["Makanan", "Transportasi", "Kuliah", "Belanja", "Hiburan", "Lainnya"]

if "wishlist" not in st.session_state:
    st.session_state.wishlist = []  # list of dicts: item, price, note, user

if "debts" not in st.session_state:
    st.session_state.debts = []  # list of dicts: name, amount, type (utang/piutang), note, user

if "budget" not in st.session_state:
    # store budgets as {'type':'daily'/'weekly'/'monthly', 'amount':..., 'user':...}
    st.session_state.budget = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------------------------
# Simple CSS for Dark Mode
# ---------------------------
def set_theme(dark: bool):
    if dark:
        st.markdown(
            """
            <style>
            .stApp { background-color: #0f1724; color: #e6eef8; }
            .css-1d391kg { color: #e6eef8; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("", unsafe_allow_html=True)

set_theme(st.session_state.dark_mode)

# ---------------------------
# Authentication (simple)
# ---------------------------
st.sidebar.title("👩‍💻 Akun")
if st.session_state.user is None:
    user_choice = st.sidebar.radio("Login sebagai", ["May", "Lili", "Tamu"])
    if st.sidebar.button("Masuk"):
        st.session_state.user = user_choice
        st.sidebar.success(f"Masuk sebagai {user_choice}")
else:
    st.sidebar.info(f"Login: {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()

# theme toggle
st.sidebar.markdown("---")
if st.sidebar.checkbox("Dark mode", value=st.session_state.dark_mode):
    st.session_state.dark_mode = True
    set_theme(True)
else:
    st.session_state.dark_mode = False
    set_theme(False)

# ---------------------------
# Sidebar Main Menu
# ---------------------------
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Menu Utama",
    [
        "🏠 Dashboard",
        "➕ Pemasukan",
        "➖ Pengeluaran Harian",
        "📂 Riwayat Transaksi",
        "📊 Grafik & Laporan",
        "💰 Tabungan",
        "📥 Import / Export",
        "⚙️ Kelola Kategori",
        "🎯 Anggaran (Budget)",
        "🛍️ Wishlist",
        "💸 Hutang / Piutang",
        "👤 Profil"
    ],
)

# ---------------------------
# Helpers
# ---------------------------
def add_transaction(user, jenis, jumlah, kategori, catatan, tanggal=None):
    if tanggal is None:
        tanggal = datetime.now().isoformat()
    st.session_state.transactions.append({
        "tanggal": tanggal,
        "jenis": jenis,
        "jumlah": float(jumlah),
        "kategori": kategori,
        "catatan": catatan,
        "user": user
    })

def filter_by_user(df, user):
    if user in (None, "Tamu"):
        return df
    return df[df["user"] == user]

def export_excel_bytes(df_dict):
    # df_dict: {"sheetname": df}
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for name, df in df_dict.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return output.getvalue()

# ---------------------------
# Pages
# ---------------------------

# 1) Dashboard
if menu == "🏠 Dashboard":
    st.title("📊 Dashboard — AKP 7B")
    st.write("Ringkasan cepat untuk pemasukan, pengeluaran, saldo, dan kategori.")

    df = pd.DataFrame(st.session_state.transactions)
    df_user = filter_by_user(df, st.session_state.user)

    if df_user.empty:
        st.info("Belum ada transaksi. Coba tambah pemasukan atau pengeluaran.")
    else:
        pemasukan = df_user[df_user["jenis"] == "Pemasukan"]["jumlah"].sum()
        pengeluaran = df_user[df_user["jenis"] == "Pengeluaran"]["jumlah"].sum()
        saldo = pemasukan - pengeluaran

        c1, c2, c3 = st.columns(3)
        c1.metric("Pemasukan", f"Rp {pemasukan:,.0f}")
        c2.metric("Pengeluaran", f"Rp {pengeluaran:,.0f}")
        c3.metric("Saldo", f"Rp {saldo:,.0f}")

        # Pie by category (pengeluaran only)
        pemakaian = df_user[df_user["jenis"] == "Pengeluaran"]
        if not pemakaian.empty:
            fig = px.pie(pemakaian, names="kategori", values="jumlah", title="Proporsi Pengeluaran per Kategori")
            st.plotly_chart(fig, use_container_width=True)

# 2) Pemasukan
elif menu == "➕ Pemasukan":
    st.title("➕ Tambah Pemasukan")
    if st.session_state.user is None:
        st.warning("Silakan login terlebih dahulu agar transaksi tersimpan per user.")
    jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=5000.0, format="%f")
    catatan = st.text_input("Catatan (opsional)")
    if st.button("Simpan Pemasukan"):
        add_transaction(st.session_state.user or "Tamu", "Pemasukan", jumlah, "Pemasukan", catatan)
        st.success("Pemasukan tersimpan!")

# 3) Pengeluaran Harian
elif menu == "➖ Pengeluaran Harian":
    st.title("➖ Catat Pengeluaran Harian")
    if st.session_state.user is None:
        st.warning("Login supaya data disimpan per akun.")
    jumlah = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, format="%f")
    kategori = st.selectbox("Kategori", st.session_state.categories)
    catatan = st.text_input("Keterangan (mis. Makan siang, kopi, print)")
    if st.button("Simpan Pengeluaran"):
        add_transaction(st.session_state.user or "Tamu", "Pengeluaran", jumlah, kategori, catatan)
        st.success("Pengeluaran berhasil dicatat!")

# 4) Riwayat Transaksi
elif menu == "📂 Riwayat Transaksi":
    st.title("📂 Riwayat Transaksi")
    df = pd.DataFrame(st.session_state.transactions)
    if df.empty:
        st.info("Belum ada transaksi.")
    else:
        df = filter_by_user(df, st.session_state.user)
        st.dataframe(df.sort_values("tanggal", ascending=False))
        # quick filters
        sel_cat = st.multiselect("Filter kategori", options=st.session_state.categories, default=st.session_state.categories)
        sel_type = st.multiselect("Tipe", options=df["jenis"].unique().tolist() if not df.empty else ["Pemasukan","Pengeluaran"], default=["Pemasukan","Pengeluaran"])
        if not df.empty:
            dff = df[df["kategori"].isin(sel_cat) & df["jenis"].isin(sel_type)]
            st.dataframe(dff.sort_values("tanggal", ascending=False))

# 5) Grafik & Laporan
elif menu == "📊 Grafik & Laporan":
    st.title("📊 Grafik & Laporan")
    df = pd.DataFrame(st.session_state.transactions)
    df = filter_by_user(df, st.session_state.user)
    if df.empty:
        st.info("Belum ada data.")
    else:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        df["bulan"] = df["tanggal"].dt.to_period("M").astype(str)
        monthly = df.groupby(["bulan","jenis"])["jumlah"].sum().reset_index()
        st.subheader("Pendapatan & Pengeluaran Per Bulan")
        st.dataframe(monthly)
        fig = px.line(monthly, x="bulan", y="jumlah", color="jenis", markers=True, title="Tren Bulanan")
        st.plotly_chart(fig, use_container_width=True)

# 6) Tabungan
elif menu == "💰 Tabungan":
    st.title("💰 Tabungan")
    target = st.number_input("Target Tabungan (Rp)", min_value=0.0, step=10000.0)
    setor = st.number_input("Setor Sekarang (Rp)", min_value=0.0, step=1000.0)
    if st.button("Setor"):
        st.session_state.savings.append({"user": st.session_state.user or "Tamu", "tanggal": datetime.now().isoformat(), "jumlah": float(setor)})
        st.success("Tersetor!")
    df = pd.DataFrame(st.session_state.savings)
    if not df.empty:
        df_user = df[df["user"] == (st.session_state.user or "Tamu")]
        total = df_user["jumlah"].sum()
        st.metric("Total Tabungan", f"Rp {total:,.0f}")
        st.dataframe(df_user.sort_values("tanggal", ascending=False))

# 7) Import / Export
elif menu == "📥 Import / Export":
    st.title("📥 Import & Export Data")
    st.subheader("Export")
    df_all = pd.DataFrame(st.session_state.transactions)
    if not df_all.empty:
        df_user = filter_by_user(df_all, st.session_state.user)
        csv = df_user.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV (Transactions)", data=csv, file_name="transactions.csv", mime="text/csv")
        # Excel
        xlsx_bytes = export_excel_bytes({"transactions": df_user})
        st.download_button("Download Excel (Transactions)", data=xlsx_bytes, file_name="transactions.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Belum ada data untuk diexport.")

    st.subheader("Import")
    uploaded = st.file_uploader("Upload CSV/Excel berisi transaksi (kolom: tanggal,jenis,jumlah,kategori,catatan,user)", type=["csv","xlsx"], accept_multiple_files=False)
    if uploaded is not None:
        try:
            if uploaded.type == "text/csv" or uploaded.name.lower().endswith(".csv"):
                df_in = pd.read_csv(uploaded)
            else:
                df_in = pd.read_excel(uploaded)
            # validate and append
            for _, r in df_in.iterrows():
                # require minimal columns
                if set(["tanggal","jenis","jumlah","kategori"]).issubset(r.index):
                    st.session_state.transactions.append({
                        "tanggal": str(r.get("tanggal")),
                        "jenis": r.get("jenis"),
                        "jumlah": float(r.get("jumlah")),
                        "kategori": r.get("kategori"),
                        "catatan": r.get("catatan", ""),
                        "user": r.get("user", st.session_state.user or "Tamu")
                    })
            st.success("Import selesai!")
        except Exception as e:
            st.error(f"Gagal import: {e}")

# 8) Kelola Kategori
elif menu == "⚙️ Kelola Kategori":
    st.title("⚙️ Kelola Kategori")
    st.write("Tambah / hapus kategori agar sesuai kebutuhanmu.")
    with st.form("cat_form", clear_on_submit=True):
        newc = st.text_input("Kategori baru")
        if st.form_submit_button("Tambah"):
            if newc and newc not in st.session_state.categories:
                st.session_state.categories.append(newc)
                st.success("Kategori ditambahkan")
            else:
                st.warning("Kategori kosong atau sudah ada.")
    st.write(st.session_state.categories)
    # hapus sederhana
    to_del = st.multiselect("Pilih kategori untuk hapus", options=st.session_state.categories)
    if to_del and st.button("Hapus kategori"):
        st.session_state.categories = [c for c in st.session_state.categories if c not in to_del]
        st.success("Kategori dihapus")

# 9) Anggaran / Budget
elif menu == "🎯 Anggaran (Budget)":
    st.title("🎯 Atur Anggaran")
    st.write("Atur limit harian/mingguan/bulanan. Aplikasi akan memberi peringatan jika terlampaui.")
    typ = st.selectbox("Tipe Anggaran", ["daily","weekly","monthly"])
    amt = st.number_input("Jumlah (Rp)", min_value=0.0)
    if st.button("Simpan Anggaran"):
        st.session_state.budget.append({"type": typ, "amount": float(amt), "user": st.session_state.user or "Tamu"})
        st.success("Anggaran tersimpan!")

    # check and notify
    df = pd.DataFrame(st.session_state.transactions)
    if not df.empty:
        df = filter_by_user(df, st.session_state.user)
        now = datetime.now()
        for b in st.session_state.budget:
            if b["user"] != (st.session_state.user or "Tamu"):
                continue
            if b["type"] == "daily":
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif b["type"] == "weekly":
                start = now - timedelta(days=now.weekday())  # monday
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            df["tanggal_dt"] = pd.to_datetime(df["tanggal"])
            spent = df[(df["jenis"]=="Pengeluaran") & (df["tanggal_dt"] >= start)]["jumlah"].sum()
            if spent > b["amount"]:
                st.error(f"⚠️ Kamu telah melebihi anggaran {b['type']} (Rp {b['amount']:,.0f}). Pengeluaran: Rp {spent:,.0f}")

# 10) Wishlist
elif menu == "🛍️ Wishlist":
    st.title("🛍️ Wishlist — Barang yang ingin dibeli")
    item = st.text_input("Nama Barang")
    price = st.number_input("Perkiraan Harga (Rp)", min_value=0.0)
    note = st.text_input("Catatan (opsional)")
    if st.button("Tambah ke Wishlist"):
        st.session_state.wishlist.append({"item": item, "price": float(price), "note": note, "user": st.session_state.user or "Tamu"})
        st.success("Ditambahkan ke wishlist!")
    df = pd.DataFrame(st.session_state.wishlist)
    if not df.empty:
        st.dataframe(filter_by_user(df, st.session_state.user))

# 11) Hutang / Piutang
elif menu == "💸 Hutang / Piutang":
    st.title("💸 Hutang & Piutang")
    name = st.text_input("Nama orang")
    amount = st.number_input("Jumlah (Rp)", min_value=0.0)
    tp = st.selectbox("Tipe", ["Utang Saya (Saya berutang)", "Piutang Saya (Orang berutang)"])
    note = st.text_input("Catatan")
    if st.button("Simpan"):
        st.session_state.debts.append({"name": name, "amount": float(amount), "type": tp, "note": note, "user": st.session_state.user or "Tamu"})
        st.success("Catatan hutang/piutang tersimpan!")
    df = pd.DataFrame(st.session_state.debts)
    if not df.empty:
        st.dataframe(filter_by_user(df, st.session_state.user))

# 12) Profil
elif menu == "👤 Profil":
    st.title("👤 Profil Pengguna")
    st.write(f"User: **{st.session_state.user or 'Tamu'}**")
    st.write("Aplikasi ini dibuat untuk membantu mahasiswa AKP 7B (May & Lili) mengelola keuangan harian, tabungan, wishlist, dan hutang/piutang.")
    st.markdown("---")
    st.write("Tips singkat:")
    st.write("- Catat semua transaksi kecil (kopi, print, makan) supaya laporan akurat.")
    st.write("- Gunakan anggaran harian jika ingin kontrol pengeluaran.")

