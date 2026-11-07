# Proyek Analisis Data: Bike Sharing Dataset 🚲

Proyek akhir kelas analisis data (Dicoding). Menganalisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011-2012) dan menyajikannya dalam dashboard Streamlit.

## Pertanyaan Bisnis
1. Pada jam berapa penyewaan sepeda mencapai puncak pada hari kerja dibandingkan akhir pekan/libur sepanjang 2012, dan berapa persentase pengguna *casual* dibandingkan *registered*?
2. Bagaimana pengaruh musim dan kondisi cuaca terhadap rata-rata penyewaan harian pada 2011 dibandingkan 2012, dan kondisi cuaca mana yang menurunkan penyewaan paling besar?

## Struktur Direktori
```
submission
├───dashboard
| ├───main_data.csv    # data per jam yang sudah dibersihkan
| ├───day_data.csv     # data harian yang sudah dibersihkan
| └───dashboard.py
├───data
| ├───day.csv
| └───hour.csv
├───notebook.ipynb
├───README.md
└───requirements.txt
```

## Setup Environment
Disarankan memakai virtual environment.

```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Menjalankan Dashboard
Jalankan dari folder `submission`:

```
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka di `http://localhost:8501`.

## Menjalankan Ulang Notebook
Buka `notebook.ipynb` dari folder `submission` (agar path `data/day.csv` terbaca), lalu jalankan semua sel. Sel terakhir akan menghasilkan ulang `dashboard/main_data.csv` dan `dashboard/day_data.csv`.
