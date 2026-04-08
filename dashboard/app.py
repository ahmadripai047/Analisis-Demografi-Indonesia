"""
Dashboard Analisis Demografi Provinsi Indonesia
Jalankan: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

# ─── Konfigurasi Halaman ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Demografi Indonesia",
    page_icon="🇮🇩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Konstanta ────────────────────────────────────────────────────────────────
PALETTE = {
    "Jawa":         "#2563EB",
    "Sumatera":     "#16A34A",
    "Kalimantan":   "#D97706",
    "Sulawesi":     "#9333EA",
    "Papua/NTT/NTB":"#DC2626",
    "Lainnya":      "#6B7280",
}

JAWA       = {"DKI JAKARTA","JAWA BARAT","JAWA TENGAH","JAWA TIMUR","DI YOGYAKARTA","BANTEN"}
SUMATERA   = {"ACEH","SUMATERA UTARA","SUMATERA BARAT","RIAU","KEPULAUAN RIAU",
               "JAMBI","BENGKULU","SUMATERA SELATAN","KEPULAUAN BANGKA BELITUNG","LAMPUNG"}
KALIMANTAN = {"KALIMANTAN BARAT","KALIMANTAN TENGAH","KALIMANTAN SELATAN",
               "KALIMANTAN TIMUR","KALIMANTAN UTARA"}
SULAWESI   = {"SULAWESI UTARA","GORONTALO","SULAWESI TENGAH","SULAWESI BARAT",
               "SULAWESI SELATAN","SULAWESI TENGGARA"}
PAPUA_NTB  = {"PAPUA","PAPUA BARAT","PAPUA SELATAN","PAPUA TENGAH","PAPUA PEGUNUNGAN",
               "PAPUA BARAT DAYA","NUSA TENGGARA BARAT","NUSA TENGGARA TIMUR"}

# ─── Helpers ─────────────────────────────────────────────────────────────────
def assign_pulau(prov):
    if prov in JAWA:        return "Jawa"
    if prov in SUMATERA:    return "Sumatera"
    if prov in KALIMANTAN:  return "Kalimantan"
    if prov in SULAWESI:    return "Sulawesi"
    if prov in PAPUA_NTB:   return "Papua/NTT/NTB"
    return "Lainnya"

def clean_laju(val):
    if pd.isna(val): return np.nan
    s = str(val).strip()
    if s in ["-", "", "NA", "N/A"]: return np.nan
    s = s.replace(",", ".").split()[0]
    try:    return float(s)
    except: return np.nan

def gini(arr):
    a = np.sort(arr)
    n = len(a)
    return (2 * np.sum(np.arange(1, n+1) * a)) / (n * np.sum(a)) - (n+1)/n

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates(subset="provinsi", keep="first").copy()
    df = df.reset_index(drop=True)

    laju_str_cols = [
        "laju_1971_1980","laju_1980_1990","laju_1990_2000","laju_2000_2010",
        "laju_2010_2016","laju_2010_2017","laju_2010_2018","laju_2010_2019",
        "laju_2010_2020","laju_2020_2021","laju_2020_2022","kepadatan_per_km2_2021"
    ]
    for col in laju_str_cols:
        df[col] = df[col].apply(clean_laju)

    df["provinsi"] = df["provinsi"].str.strip().str.upper()
    df["pulau"]    = df["provinsi"].apply(assign_pulau)
    df["penduduk_juta"] = df["jumlah_penduduk_ribu_2026"] / 1000
    return df

# ─── Load ─────────────────────────────────────────────────────────────────────
import os
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR  = os.path.dirname(BASE_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "data", "processed", "demografi_clean.csv")
RAW_PATH  = os.path.join(ROOT_DIR, "data", "raw", "demografi_provinsi_indonesia_merged.csv")

try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    try:
        df = load_data(RAW_PATH)
    except FileNotFoundError:
        st.error(
            "❌ **File data tidak ditemukan.**\n\n"
            "Pastikan salah satu file berikut ada di repository:\n"
            "- `data/processed/demografi_clean.csv`\n"
            "- `data/raw/demografi_provinsi_indonesia_merged.csv`"
        )
        st.stop()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/9f/Flag_of_Indonesia.svg", width=80)
    st.title("🇮🇩 Filter")
    st.markdown("---")

    pulau_opts = ["Semua"] + sorted(df["pulau"].unique().tolist())
    sel_pulau  = st.multiselect("Gugus Pulau", pulau_opts[1:], default=pulau_opts[1:])
    if not sel_pulau:
        sel_pulau = pulau_opts[1:]

    df_f = df[df["pulau"].isin(sel_pulau)].copy()

    st.markdown("---")
    st.caption("**Sumber data**: BPS Indonesia  \n**Tahun**: 2020–2026  \n**Cakupan**: 38 Provinsi")

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("📊 Dashboard Demografi Provinsi Indonesia")
st.caption("Data BPS Indonesia · Proyeksi 2026 & Indikator SP2020")
st.markdown("---")

# ─── Metrik Utama ─────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total_penduduk = df_f["penduduk_juta"].sum()
median_laju    = df_f["laju_2020_2024"].median()
gini_val       = gini(df_f["jumlah_penduduk_ribu_2026"].values)
median_imr     = df_f["imr_per1000_2020"].median()
n_prov         = len(df_f)

col1.metric("Proyeksi Penduduk 2026", f"{total_penduduk:.1f} juta")
col2.metric("Provinsi Dipilih", str(n_prov))
col3.metric("Median Laju Tumbuh", f"{median_laju:.2f}%/thn")
col4.metric("Gini Distribusi", f"{gini_val:.3f}")
col5.metric("Median IMR 2020", f"{median_imr:.1f} per 1.000")

st.markdown("---")

# ─── Tab Navigasi ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ Distribusi Penduduk",
    "📈 Tren Pertumbuhan",
    "🏥 Indikator Vital",
    "🔬 Analisis Statistik"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DISTRIBUSI PENDUDUK
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns([1.6, 1])

    with c1:
        st.subheader("Penduduk per Provinsi — Proyeksi 2026")
        n_show = st.slider("Tampilkan N provinsi teratas", 5, len(df_f), 15, key="n_bar")
        plot_df = df_f.nlargest(n_show, "penduduk_juta").sort_values("penduduk_juta")
        fig = px.bar(
            plot_df, x="penduduk_juta", y="provinsi",
            color="pulau", color_discrete_map=PALETTE,
            orientation="h", text="penduduk_juta",
            labels={"penduduk_juta": "Penduduk (juta jiwa)", "provinsi": ""},
            height=max(350, n_show * 32)
        )
        fig.update_traces(texttemplate="%{x:.1f} jt", textposition="outside")
        fig.update_layout(margin=dict(l=0,r=60,t=10,b=30), legend_title="Pulau")
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Distribusi per Gugus Pulau")
        pulau_pop = df_f.groupby("pulau")["distribusi_pct_2026"].sum().reset_index()
        fig2 = px.pie(
            pulau_pop, values="distribusi_pct_2026", names="pulau",
            color="pulau", color_discrete_map=PALETTE, hole=0.42,
            height=340
        )
        fig2.update_traces(textinfo="label+percent", textfont_size=11)
        fig2.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig2, width="stretch")

        # Gini
        st.info(f"**Koefisien Gini**: {gini_val:.3f}\n\nKetimpangan distribusi antar provinsi **{'tinggi' if gini_val > 0.5 else 'sedang'}**.\n\n> Interpretasi: 0 = merata sempurna · 1 = sangat timpang")

    # Tabel
    st.subheader("Data Lengkap")
    show_cols = ["provinsi","pulau","penduduk_juta","distribusi_pct_2026","kepadatan_per_km2_2026",
                 "laju_pertumbuhan_pct_2026","rasio_jenis_kelamin_2026"]
    st.dataframe(
        df_f[show_cols].sort_values("penduduk_juta", ascending=False)
        .rename(columns={
            "penduduk_juta": "Penduduk (juta)",
            "distribusi_pct_2026": "Distribusi (%)",
            "kepadatan_per_km2_2026": "Kepadatan/km²",
            "laju_pertumbuhan_pct_2026": "Laju Tumbuh (%)",
            "rasio_jenis_kelamin_2026": "Rasio JK"
        }).reset_index(drop=True),
        width="stretch", height=350
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TREN PERTUMBUHAN
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    periodes = [
        ("1971–80", "laju_1971_1980"), ("1980–90", "laju_1980_1990"),
        ("1990–2000","laju_1990_2000"), ("2000–10", "laju_2000_2010"),
        ("2010–20", "laju_2010_2020"), ("2020–24", "laju_2020_2024"),
    ]
    trend_data = []
    for label, col in periodes:
        vals = df_f[col].dropna()
        if len(vals):
            trend_data.append({
                "periode": label, "median": vals.median(), "mean": vals.mean(),
                "q1": vals.quantile(0.25), "q3": vals.quantile(0.75), "n": len(vals)
            })
    tdf = pd.DataFrame(trend_data)

    c1, c2 = st.columns([1.6, 1])
    with c1:
        st.subheader("Tren Median Laju Pertumbuhan Nasional")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=tdf["periode"], y=tdf["q3"], fill=None, mode="lines",
            line=dict(width=0), showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=tdf["periode"], y=tdf["q1"], fill="tonexty", mode="lines",
            line=dict(width=0), fillcolor="rgba(37,99,235,0.15)", name="IQR"
        ))
        fig.add_trace(go.Scatter(
            x=tdf["periode"], y=tdf["median"], mode="lines+markers",
            line=dict(color="#2563EB", width=3), marker=dict(size=9),
            name="Median"
        ))
        fig.add_trace(go.Scatter(
            x=tdf["periode"], y=tdf["mean"], mode="lines+markers",
            line=dict(color="#DC2626", width=2, dash="dash"), marker=dict(size=7),
            name="Mean"
        ))
        fig.update_layout(
            yaxis_title="Laju Pertumbuhan (% per tahun)",
            yaxis_range=[0.5, 3.8], height=380,
            margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Laju 2020–2024 per Pulau")
        box_df = df_f.dropna(subset=["laju_2020_2024"])
        fig2 = px.box(
            box_df, x="pulau", y="laju_2020_2024", color="pulau",
            color_discrete_map=PALETTE, points="all",
            labels={"laju_2020_2024": "Laju (%)", "pulau": ""},
            height=380
        )
        fig2.add_hline(y=df_f["laju_2020_2024"].median(), line_dash="dot",
                       line_color="red", annotation_text="Median nasional")
        fig2.update_layout(showlegend=False, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig2, width="stretch")

    st.subheader("Ranking Laju Pertumbuhan 2020–2024")
    laju_sorted = df_f.dropna(subset=["laju_2020_2024"]).sort_values("laju_2020_2024", ascending=False)
    fig3 = px.bar(
        laju_sorted, x="laju_2020_2024", y="provinsi",
        color="pulau", color_discrete_map=PALETTE, orientation="h",
        labels={"laju_2020_2024": "Laju Pertumbuhan (% per tahun)", "provinsi": ""},
        height=900
    )
    fig3.update_layout(margin=dict(l=0,r=40,t=10,b=0), legend_title="Pulau")
    st.plotly_chart(fig3, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — INDIKATOR VITAL
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    c1, c2 = st.columns(2)
    vital_df = df_f.dropna(subset=["imr_per1000_2020","tfr_2020"])

    with c1:
        st.subheader("IMR per 1.000 Kelahiran Hidup (2020)")
        imr_s = vital_df.sort_values("imr_per1000_2020", ascending=True)
        fig = px.bar(
            imr_s, x="imr_per1000_2020", y="provinsi", color="pulau",
            color_discrete_map=PALETTE, orientation="h",
            labels={"imr_per1000_2020": "IMR per 1.000", "provinsi": ""},
            height=700
        )
        fig.add_vline(x=imr_s["imr_per1000_2020"].median(), line_dash="dot",
                      line_color="gray", annotation_text="Median")
        fig.update_layout(showlegend=False, margin=dict(l=0,r=40,t=10,b=0))
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("TFR vs IMR — Pola Transisi Demografi")
        fig2 = px.scatter(
            vital_df, x="tfr_2020", y="imr_per1000_2020",
            color="pulau", color_discrete_map=PALETTE,
            size="penduduk_juta", size_max=40,
            hover_name="provinsi",
            labels={"tfr_2020": "TFR (Total Fertility Rate)", "imr_per1000_2020": "IMR per 1.000"},
            trendline="ols", height=400
        )
        fig2.update_layout(margin=dict(l=0,r=0,t=10,b=0), legend_title="Pulau")
        st.plotly_chart(fig2, width="stretch")

        st.subheader("CBR per 1.000 Penduduk per Pulau")
        cbr_df = df_f.dropna(subset=["cbr_per1000_2020"])
        fig3 = px.violin(
            cbr_df, x="pulau", y="cbr_per1000_2020",
            color="pulau", color_discrete_map=PALETTE, box=True, points="all",
            labels={"cbr_per1000_2020": "CBR per 1.000", "pulau": ""},
            height=300
        )
        fig3.update_layout(showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig3, width="stretch")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALISIS STATISTIK
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Matriks Korelasi Spearman")
        corr_cols = [
            "jumlah_penduduk_ribu_2026","kepadatan_per_km2_2026",
            "laju_2020_2024","imr_per1000_2020","cbr_per1000_2020","tfr_2020"
        ]
        corr_labels = ["Penduduk","Kepadatan","Laju 2020-24","IMR","CBR","TFR"]
        corr_matrix = df_f[corr_cols].corr(method="spearman").values
        fig = go.Figure(go.Heatmap(
            z=corr_matrix, x=corr_labels, y=corr_labels,
            colorscale="RdBu", zmin=-1, zmax=1, zmid=0,
            text=np.round(corr_matrix, 2),
            texttemplate="%{text}", textfont={"size": 11},
            hovertemplate="r = %{z:.3f}"
        ))
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Uji-T: Jawa vs Luar Jawa")
        jawa_l = df_f[df_f["pulau"] == "Jawa"]["laju_2020_2024"].dropna()
        luar_l = df_f[df_f["pulau"] != "Jawa"]["laju_2020_2024"].dropna()

        if len(jawa_l) > 1 and len(luar_l) > 1:
            t_stat, t_p = stats.ttest_ind(jawa_l, luar_l, equal_var=False)
            pooled = np.sqrt((jawa_l.std()**2 + luar_l.std()**2) / 2)
            cohens_d = (jawa_l.mean() - luar_l.mean()) / pooled if pooled else 0

            col_a, col_b = st.columns(2)
            col_a.metric("Rata-rata Jawa",  f"{jawa_l.mean():.3f}%")
            col_b.metric("Rata-rata Luar Jawa", f"{luar_l.mean():.3f}%")
            col_a.metric("t-statistic", f"{t_stat:.3f}")
            col_b.metric("p-value", f"{t_p:.4f}")
            col_a.metric("Cohen's d", f"{cohens_d:.3f}")
            col_b.metric("Kesimpulan", "Signifikan ✅" if t_p < 0.05 else "Tidak Signifikan")

            # Violin plot t-test
            vdf = pd.concat([
                jawa_l.rename("laju").to_frame().assign(grup="Jawa"),
                luar_l.rename("laju").to_frame().assign(grup="Luar Jawa")
            ])
            fig_v = px.violin(
                vdf, x="grup", y="laju", color="grup", box=True, points="all",
                color_discrete_map={"Jawa": "#2563EB", "Luar Jawa": "#6B7280"},
                labels={"laju": "Laju Pertumbuhan (%)","grup": ""},
                height=280
            )
            fig_v.update_layout(showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_v, width="stretch")

    st.markdown("---")
    st.subheader("Statistik Deskriptif Extended")
    sel_col = st.selectbox("Pilih variabel:", [
        "penduduk_juta","kepadatan_per_km2_2026","laju_2020_2024",
        "imr_per1000_2020","cbr_per1000_2020","tfr_2020"
    ])
    v = df_f[sel_col].dropna()
    sw_stat, sw_p = stats.shapiro(v) if len(v) >= 3 else (None, None)
    desc_data = {
        "Statistik": ["N","Mean","Median","Std Dev","Min","Max",
                      "CV (%)","Skewness","Kurtosis","Shapiro-Wilk p"],
        "Nilai": [
            str(len(v)), f"{v.mean():.4f}", f"{v.median():.4f}", f"{v.std():.4f}",
            f"{v.min():.4f}", f"{v.max():.4f}",
            f"{v.std()/v.mean()*100:.2f}", f"{stats.skew(v):.4f}",
            f"{stats.kurtosis(v):.4f}", f"{sw_p:.4f}" if sw_p else "—"
        ]
    }
    c1, c2 = st.columns([1, 1.5])
    c1.dataframe(pd.DataFrame(desc_data), width="stretch", hide_index=True)
    with c2:
        fig_hist = px.histogram(
            df_f.dropna(subset=[sel_col]), x=sel_col, color="pulau",
            color_discrete_map=PALETTE, nbins=20, marginal="box",
            labels={sel_col: sel_col},
            height=300
        )
        fig_hist.update_layout(margin=dict(l=0,r=0,t=10,b=0), legend_title="Pulau")
        st.plotly_chart(fig_hist, width="stretch")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📊 Dashboard dibuat dengan Streamlit & Plotly · Data: BPS Indonesia · "
           "Diolah dari `demografi_provinsi_indonesia_merged.csv`")