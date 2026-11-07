import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")
st.set_page_config(page_title="Dashboard Bike Sharing", page_icon="🚲", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URUTAN_MUSIM = ["Spring", "Summer", "Fall", "Winter"]
URUTAN_CUACA = ["Cerah", "Berkabut/Mendung", "Hujan/Salju Ringan", "Hujan/Salju Lebat"]
URUTAN_WAKTU = ["Dini Hari (00-05)", "Pagi (06-11)", "Siang (12-15)", "Sore (16-20)", "Malam (21-23)"]


@st.cache_data
def load_data():
    hour_df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"), parse_dates=["dteday"])
    day_df = pd.read_csv(os.path.join(BASE_DIR, "day_data.csv"), parse_dates=["dteday"])
    for df in (hour_df, day_df):
        df["season"] = pd.Categorical(df["season"], categories=URUTAN_MUSIM, ordered=True)
        df["weathersit"] = pd.Categorical(df["weathersit"], categories=URUTAN_CUACA, ordered=True)
    hour_df["kategori_waktu"] = pd.Categorical(hour_df["kategori_waktu"], categories=URUTAN_WAKTU, ordered=True)
    return hour_df, day_df


hour_df, day_df = load_data()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.caption("Capital Bikeshare, Washington D.C. (2011-2012)")
    tanggal_min, tanggal_maks = day_df["dteday"].min().date(), day_df["dteday"].max().date()
    rentang = st.date_input("Rentang tanggal", value=(tanggal_min, tanggal_maks),
                            min_value=tanggal_min, max_value=tanggal_maks)
    musim = st.multiselect("Musim", URUTAN_MUSIM, default=URUTAN_MUSIM)

if isinstance(rentang, (tuple, list)) and len(rentang) == 2:
    mulai, akhir = pd.Timestamp(rentang[0]), pd.Timestamp(rentang[1])
else:
    st.info("Pilih tanggal awal dan tanggal akhir pada sidebar.")
    st.stop()

if not musim:
    st.warning("Pilih minimal satu musim pada sidebar.")
    st.stop()

hour_f = hour_df[hour_df["dteday"].between(mulai, akhir) & hour_df["season"].isin(musim)]
day_f = day_df[day_df["dteday"].between(mulai, akhir) & day_df["season"].isin(musim)]

if day_f.empty:
    st.warning("Tidak ada data pada filter yang dipilih.")
    st.stop()

# ---------------- Header & ringkasan ----------------
st.title("Dashboard Analisis Bike Sharing 🚲")
st.write("Dashboard ini menjawab dua pertanyaan bisnis: pola jam penyewaan serta pengaruh musim dan cuaca.")

total = int(day_f["cnt"].sum())
col1, col2, col3 = st.columns(3)
col1.metric("Total penyewaan", f"{total:,}")
col2.metric("Rata-rata penyewaan per hari", f"{day_f['cnt'].mean():,.0f}")
col3.metric("Porsi pengguna casual", f"{day_f['casual'].sum() / total * 100:.1f}%")

# ---------------- Pertanyaan 1 ----------------
st.header("Pertanyaan 1: Jam puncak penyewaan dan komposisi pengguna")
pola_jam = hour_f.groupby(["workingday", "hr"], observed=True)["cnt"].mean().unstack(0)
komposisi = hour_f.groupby("workingday")[["casual", "registered"]].sum()
komposisi = komposisi.div(komposisi.sum(axis=1), axis=0) * 100

warna = {"Hari Kerja": "#1f77b4", "Akhir Pekan/Libur": "#ff7f0e"}
fig, axes = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={"width_ratios": [2, 1]})
for kelompok in pola_jam.columns:
    axes[0].plot(pola_jam.index, pola_jam[kelompok], marker="o", linewidth=2,
                 label=kelompok, color=warna.get(kelompok))
    jam_puncak = int(pola_jam[kelompok].idxmax())
    axes[0].annotate(f"Puncak {jam_puncak}:00", xy=(jam_puncak, pola_jam[kelompok].max()),
                     xytext=(jam_puncak - 4, pola_jam[kelompok].max() * 1.06), fontsize=9,
                     color=warna.get(kelompok), arrowprops=dict(arrowstyle="-", color=warna.get(kelompok)))
axes[0].set_title("Rata-rata Penyewaan per Jam", fontsize=13, fontweight="bold")
axes[0].set_xlabel("Jam")
axes[0].set_ylabel("Rata-rata jumlah penyewaan")
axes[0].set_xticks(range(0, 24))
axes[0].set_ylim(0, pola_jam.max().max() * 1.2)
axes[0].legend(title="Jenis hari", loc="upper left")

komposisi[["registered", "casual"]].plot(kind="bar", stacked=True, ax=axes[1],
                                         color=["#2ca02c", "#d62728"], rot=0)
axes[1].set_title("Komposisi Pengguna", fontsize=13, fontweight="bold")
axes[1].set_xlabel("")
axes[1].set_ylabel("Persentase penyewaan (%)")
axes[1].legend(["Registered", "Casual"], loc="lower right")
for container in axes[1].containers:
    axes[1].bar_label(container, fmt="%.1f%%", label_type="center", color="white", fontsize=10)
plt.tight_layout()
st.pyplot(fig)

if "Hari Kerja" in pola_jam.columns and "Akhir Pekan/Libur" in pola_jam.columns:
    st.info(
        f"Pada hari kerja, penyewaan tertinggi pukul **{int(pola_jam['Hari Kerja'].idxmax())}:00**. "
        f"Pada akhir pekan/libur, puncaknya pukul **{int(pola_jam['Akhir Pekan/Libur'].idxmax())}:00**."
    )

# ---------------- Pertanyaan 2 ----------------
st.header("Pertanyaan 2: Pengaruh musim dan cuaca terhadap penyewaan harian")
rata_musim = day_f.groupby(["yr", "season"], observed=True)["cnt"].mean().unstack(0)
rata_cuaca = day_f.groupby(["yr", "weathersit"], observed=True)["cnt"].mean().unstack(0)

fig, axes = plt.subplots(1, 2, figsize=(15, 5))
rata_musim.plot(kind="bar", ax=axes[0], color=["#9ecae1", "#3182bd"], rot=0)
axes[0].set_title("Rata-rata Penyewaan Harian per Musim", fontsize=13, fontweight="bold")
axes[0].set_xlabel("Musim")
axes[0].set_ylabel("Rata-rata penyewaan per hari")
axes[0].legend(title="Tahun")
rata_cuaca.plot(kind="bar", ax=axes[1], color=["#fdae6b", "#e6550d"], rot=0)
axes[1].set_title("Rata-rata Penyewaan Harian per Kondisi Cuaca", fontsize=13, fontweight="bold")
axes[1].set_xlabel("Kondisi cuaca")
axes[1].set_ylabel("Rata-rata penyewaan per hari")
axes[1].legend(title="Tahun")
for ax in axes:
    for container in ax.containers:
        ax.bar_label(container, fmt="%.0f", fontsize=9)
plt.tight_layout()
st.pyplot(fig)

# ---------------- Analisis lanjutan ----------------
st.header("Analisis Lanjutan: Binning waktu dan suhu")
col_a, col_b = st.columns(2)
waktu = (hour_f.groupby(["kategori_waktu", "workingday"], observed=True)["cnt"]
         .mean().unstack())
fig, ax = plt.subplots(figsize=(7, 4.5))
waktu.plot(kind="bar", ax=ax, color=["#ff7f0e", "#1f77b4"][: len(waktu.columns)], rot=15)
ax.set_title("Rata-rata Penyewaan per Jam menurut Waktu", fontsize=12, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Rata-rata penyewaan per jam")
ax.legend(title="Jenis hari")
plt.tight_layout()
col_a.pyplot(fig)

suhu = day_f.groupby("kategori_suhu", observed=True)["cnt"].mean()
fig, ax = plt.subplots(figsize=(7, 4.5))
sns.barplot(x=suhu.index.astype(str), y=suhu.values, hue=suhu.index.astype(str),
            palette="YlOrRd", legend=False, dodge=False, ax=ax)
ax.set_title("Rata-rata Penyewaan Harian menurut Suhu", fontsize=12, fontweight="bold")
ax.set_xlabel("")
ax.set_ylabel("Rata-rata penyewaan per hari")
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", fontsize=9)
plt.tight_layout()
col_b.pyplot(fig)

st.caption("Sumber data: Bike Sharing Dataset (Capital Bikeshare). Proyek Analisis Data - Dicoding.")
