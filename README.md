# 📊 Analisis Demografi Provinsi Indonesia
👉 [Klik di sini untuk melihat Dashboard](https://demografi-indonesia-analytifai.streamlit.app/)

> Proyek portofolio analisis data kependudukan berbasis data resmi BPS Indonesia,  
> mencakup data cleaning, eksplorasi statistik, visualisasi, dan dashboard interaktif.

---

## Latar Belakang

Indonesia adalah negara keempat terpenduduk di dunia dengan 287 juta jiwa (proyeksi 2026).
Memahami pola distribusi, tren pertumbuhan, dan indikator vital kependudukan sangat krusial
untuk perencanaan pembangunan. Proyek ini menganalisis data demografi 38 provinsi Indonesia
dari Sensus Penduduk 2020 (SP2020) dan proyeksi BPS 2026.

---

## Pertanyaan Penelitian

1. Bagaimana distribusi penduduk antar provinsi dan seberapa timpang?
2. Apakah laju pertumbuhan penduduk memiliki tren menurun?
3. Apakah provinsi Jawa dan Luar Jawa memiliki laju pertumbuhan yang berbeda secara signifikan?
4. Bagaimana disparitas indikator kesehatan (IMR, TFR, CBR) antar wilayah?
5. Variabel demografis mana yang paling berkorelasi satu sama lain?

---

## Temuan Utama

- **Koefisien Gini distribusi penduduk: 0.602** → ketimpangan tinggi
- **55,4% penduduk** terkonsentrasi di Pulau Jawa (6 dari 38 provinsi)
- Laju pertumbuhan nasional **melambat** dari ~2,67%/thn (1971–80) → 1,37%/thn (2020–24)
- Uji-t menunjukkan **Luar Jawa tumbuh lebih cepat** dari Jawa (p < 0.001, Cohen's d = -1.73)
- IMR Papua (38,2) hampir **4× lebih tinggi** dari DKI Jakarta (10,4) — disparitas sangat besar
- Korelasi TFR–CBR sangat kuat (r = 0,96 Spearman), konsisten dengan teori transisi demografi

---

## Struktur Proyek

```
demografi-indonesia/
├── data/
│   ├── raw/           ← Data asli dari BPS 
│   └── processed/     ← Data hasil cleaning
├── notebooks/
│   ├── 01_cleaning.ipynb       ← Data wrangling & standarisasi
│   ├── 02_eda.ipynb            ← Statistik deskriptif & uji hipotesis
│   └── 03_visualisasi.ipynb   ← 6 visualisasi
├── dashboard/
│   └── app.py         ← Dashboard Streamlit
├── output/
│   └── figures/       ← Grafik hasil analisis (.png)
├── README.md
└── requirements.txt
```

---

## Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan notebook secara berurutan
```bash
jupyter notebook
# Buka dan jalankan: 01_cleaning.ipynb → 02_eda.ipynb → 03_visualisasi.ipynb
```

### 3. Jalankan dashboard Streamlit
```bash
cd dashboard
streamlit run app.py
```
Dashboard akan terbuka di browser: `http://localhost:8501`

---

## Metodologi

| Tahap | Metode |
|-------|--------|
| Data cleaning | Deduplikasi, konversi tipe, standardisasi nama provinsi |
| Statistik deskriptif | Mean, median, CV, skewness, kurtosis, Shapiro-Wilk |
| Analisis ketimpangan | Koefisien Gini distribusi penduduk |
| Uji hipotesis | Independent t-test + Levene test (varians) + Cohen's d |
| Korelasi | Spearman (robust untuk distribusi skewed) |
| Visualisasi | Matplotlib/Seaborn (notebooks) + Plotly (dashboard) |

---

## Sumber Data

- **BPS Indonesia** — [bps.go.id](https://bps.go.id)
- Sensus Penduduk 2020 (SP2020)
- Proyeksi Penduduk Indonesia 2020–2035
- Statistik Indonesia 2024

---

## Tech Stack

`Python 3.10` · `pandas` · `numpy` · `scipy` · `matplotlib` · `seaborn` · `plotly` · `streamlit`
