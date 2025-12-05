# app.py

```python
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    # Transaksi
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            kategori TEXT,
            jumlah REAL,
            keterangan TEXT
        )
    """)

    # Tugas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tugas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT,
            deadline TEXT,
            status TEXT
        )
    """)

    # Catatan
    cur.execute("""
        CREATE TABLE IF NOT EXISTS catatan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT,
            isi TEXT,
            tanggal TEXT
        )
    """)

    # Presensi
    cur.execute("""
        CREATE TABLE IF NOT EXISTS presensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matkul TEXT,
            tanggal TEXT,
            status TEXT
        )
    """)

    # Jadwal Kuliah
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jadwal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matkul TEXT,
            hari TEXT,
            jam TEXT,
            ruangan TEXT
        )
    """)

    conn.commit()
    return conn

conn = init_db()

# ================= HEADER =================
st.set_page_config(page_title="Student Toolkit AKP 7B", page_icon="🎓", layout="wide")
st.title("🎓 Student Master Toolkit — AKP 7B Edition")

menu = st.sidebar.selectbox(
    "Menu Utama",
    [
        "Dashboard",
        "Transaksi Harian",
        "Tugas Kuliah",
        "Catatan Belajar",
        "Jadwal Kuliah",
        "Presensi Mahasiswa",
        "Perhitungan Nilai",
        "Export Data"
    ]
)

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.subheader("📊 Dashboard Lengkap Mahasiswa")
    st.write("Ringkasan keuangan, tugas, presensi, dan catatan.")

    df = pd.read_sql_query("SELECT * FROM transaksi", conn)
    if not df.empty:
        total = df['jumlah'].sum()
        st.metric("Saldo Saat Ini", f"Rp {total:,.0f}")
    else:
        st.info("Belum ada transaksi.")

# ================= TRANSAKSI =================
if menu == "Transaksi Harian":
    st.subheader("💸 Transaksi Harian Mahasiswa AKP 7B")
    tanggal = st.date_input("Tanggal", datetime.now())
    kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
    jumlah = st.number_input("Jumlah (Rp)", step=1000)
    keterangan = st.text_input("Keterangan")

    if st.button("Simpan Transaksi"):
        jml = jumlah if kategori == "Pemasukan" else -jumlah
        conn.execute("INSERT INTO transaksi (tanggal, kategori, jumlah, keterangan) VALUES (?,?,?,?)", (str(tanggal), kategori, jml, keterangan))
        conn.commit()
        st.success("Transaksi berhasil disimpan!")

    st.subheader("Riwayat Transaksi")
    st.dataframe(pd.read_sql_query("SELECT * FROM transaksi", conn))

# ================= TUGAS =================
if menu == "Tugas Kuliah":
    st.subheader("📚 Manajemen Tugas Mahasiswa")
    judul = st.text_input("Judul Tugas")
    deadline = st.date_input("Deadline")
    status = st.selectbox("Status", ["Belum", "Proses", "Selesai"])

    if st.button("Tambah Tugas"):
        conn.execute("INSERT INTO tugas (judul, deadline, status) VALUES (?,?,?)", (judul, str(deadline), status))
        conn.commit()
        st.success("Tugas ditambahkan!")

    st.subheader("Daftar Tugas")
    st.dataframe(pd.read_sql_query("SELECT * FROM tugas", conn))

# ================= CATATAN =================
if menu == "Catatan Belajar":
    st.subheader("📝 Catatan Kuliah & Ringkasan Materi")
    judul = st.text_input("Judul Catatan")
    isi = st.text_area("Isi Catatan (Markdown)")

    if st.button("Simpan Catatan"):
        conn.execute("INSERT INTO catatan (judul, isi, tanggal) VALUES (?,?,?)", (judul, isi, str(datetime.now())))
        conn.commit()
        st.success("Catatan disimpan!")

    st.subheader("Daftar Catatan")
    st.dataframe(pd.read_sql_query("SELECT * FROM catatan", conn))

# ================= JADWAL =================
if menu == "Jadwal Kuliah":
    st.subheader("📅 Jadwal Kuliah AKP 7B")
    matkul = st.text_input("Mata Kuliah")
    hari = st.selectbox("Hari", ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"])
    jam = st.text_input("Jam")
    ruangan = st.text_input("Ruangan")

    if st.button("Tambah Jadwal"):
        conn.execute("INSERT INTO jadwal (matkul, hari, jam, ruangan) VALUES (?,?,?,?)", (matkul, hari, jam, ruangan))
        conn.commit()
        st.success("Jadwal berhasil ditambahkan!")

    st.subheader("Daftar Jadwal")
    st.dataframe(pd.read_sql_query("SELECT * FROM jadwal", conn))

# ================= PRESENSI =================
if menu == "Presensi Mahasiswa":
    st.subheader("📍 Presensi Harian AKP 7B")
    matkul = st.text_input("Mata Kuliah")
    tanggal = st.date_input("Tanggal")
    status = st.selectbox("Status", ["Hadir", "Alpa", "Izin", "Sakit"])

    if st.button("Simpan Presensi"):
        conn.execute("INSERT INTO presensi (matkul, tanggal, status) VALUES (?,?,?)", (matkul, str(tanggal), status))
        conn.commit()
        st.success("Presensi dicatat!")

    st.subheader("Daftar Presensi")
    st.dataframe(pd.read_sql_query("SELECT * FROM presensi", conn))

# ================= NILAI =================
if menu == "Perhitungan Nilai":
    st.subheader("📘 Kalkulator Nilai Mahasiswa")
    uts = st.number_input("Nilai UTS", 0, 100)
    uas = st.number_input("Nilai UAS", 0, 100)
    tugas = st.number_input("Nilai Tugas", 0, 100)
    quiz = st.number_input("Nilai Quiz", 0, 100)

    if st.button("Hitung Nilai Akhir"):
        nilai = (uts * 0.3) + (uas * 0.4) + (tugas * 0.2) + (quiz * 0.1)
        st.success(f"Nilai Akhir Anda: {nilai:.2f}")
``python
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            kategori TEXT,
            jumlah REAL,
            keterangan TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tugas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT,
            deadline TEXT,
            status TEXT
        )
    """)

    conn.commit()
    return conn

conn = init_db()

# ================= HEADER =================
st.set_page_config(page_title="Gen Z Finance App", page_icon="💸", layout="wide")
st.title("💸 Gen Z Money & Task Manager — Menabung & Mencatat Transaksi Harian")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Transaksi", "Tugas", "Export Data"])

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.subheader("📊 Ringkasan Keuangan")

    df = pd.read_sql_query("SELECT * FROM transaksi", conn)

    if df.empty:
        st.info("Belum ada transaksi.")
    else:
        total_pengeluaran = df[df['jumlah'] < 0]['jumlah'].sum()
        total_pemasukan = df[df['jumlah'] > 0]['jumlah'].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.0f}")
        col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}")

        st.bar_chart(df['jumlah'])


# ================= TRANSAKSI =================    
if menu == "Transaksi":
    st.subheader("📝 Tambah Transaksi Harian")

    tanggal = st.date_input("Tanggal", datetime.now())
    kategori = st.selectbox("Kategori", ["Pemasukan", "Pengeluaran"])
    jumlah = st.number_input("Jumlah (Rp)", step=1000)
    keterangan = st.text_input("Keterangan")

    if st.button("Simpan"):
        jml = jumlah if kategori == "Pemasukan" else -jumlah
        conn.execute("INSERT INTO transaksi (tanggal, kategori, jumlah, keterangan) VALUES (?,?,?,?)", 
                     (str(tanggal), kategori, jml, keterangan))
        conn.commit()
        st.success("Transaksi berhasil ditambahkan!")

    st.subheader("📋 Riwayat Transaksi")
    df = pd.read_sql_query("SELECT * FROM transaksi", conn)
    st.dataframe(df)


# ================= TUGAS =================
if menu == "Tugas":
    st.subheader("📚 Task Planner Mahasiswa")

    judul = st.text_input("Judul Tugas")
    deadline = st.date_input("Deadline")
    status = st.selectbox("Status", ["Belum", "Proses", "Selesai"])

    if st.button("Tambah Tugas"):
        conn.execute("INSERT INTO tugas (judul, deadline, status) VALUES (?,?,?)", 
                     (judul, str(deadline), status))
        conn.commit()
        st.success("Tugas ditambahkan!")

    st.subheader("📘 Daftar Tugas")
    df = pd.read_sql_query("SELECT * FROM tugas", conn)
    st.dataframe(df)


# ================= EXPORT =================
if menu == "Export Data":
    st.subheader("💾 Export ke CSV")

    df_transaksi = pd.read_sql_query("SELECT * FROM transaksi", conn)
    df_tugas = pd.read_sql_query("SELECT * FROM tugas", conn)

    st.download_button(
        label="Download Transaksi CSV",
        data=df_transaksi.to_csv(index=False),
        file_name="transaksi.csv",
        mime="text/csv"
    )

    st.download_button(
        label="Download Tugas CSV",
        data=df_tugas.to_csv(index=False),
        file_name="tugas.csv",
        mime="text/csv"
    )
```

# requirements.txt

```
streamlit
pandas
matplotlib
numpy
python-dateutil
pillow
```
