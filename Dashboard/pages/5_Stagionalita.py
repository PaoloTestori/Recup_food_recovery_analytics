import plotly.express as px
import pandas as pd
import streamlit as st
import importlib.util
import os

BASE = os.path.dirname(__file__)

spec_dl = importlib.util.spec_from_file_location(
    "data_loader", os.path.abspath(os.path.join(BASE, '..', 'components', 'data_loader.py'))
)
data_loader = importlib.util.module_from_spec(spec_dl)
spec_dl.loader.exec_module(data_loader)

spec_st = importlib.util.spec_from_file_location(
    "styles", os.path.abspath(os.path.join(BASE, '..', 'components', 'styles.py'))
)
styles = importlib.util.module_from_spec(spec_st)
spec_st.loader.exec_module(styles)
inietta_css = styles.inietta_css

spec_pal = importlib.util.spec_from_file_location(
    "palette", os.path.abspath(os.path.join(BASE, '..', 'components', 'palette.py'))
)
palette = importlib.util.module_from_spec(spec_pal)
spec_pal.loader.exec_module(palette)
VERDE = palette.VERDE

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Stagionalità", page_icon="📅", layout="wide")
inietta_css()

data = data_loader.load_all()
df = data["df"].copy()

st.markdown("<h1 style='margin-bottom:0;'>📅 Stagionalità</h1>", unsafe_allow_html=True)
st.caption("Pattern mensile del recupero sui mercati di strada (tutti gli anni)")

MESI_BREVI = {1: "Gen", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mag", 6: "Giu",
              7: "Lug", 8: "Ago", 9: "Set", 10: "Ott", 11: "Nov", 12: "Dic"}
ORDINE_BREVI = list(MESI_BREVI.values())

# pivot mese × anno: righe = mese, colonne = anno
pivot = (
    df.groupby(["ANNO", "MESE_NUM"])["KG"].sum()
      .unstack(level=0)
)

# ─── 1. Mediana mensile (robusta all'anno parziale: i NaN restano fuori) ─────
stagionalita = pivot.median(axis=1).reset_index()
stagionalita.columns = ["MESE_NUM", "KG_mediani"]
stagionalita["MESE"] = stagionalita["MESE_NUM"].map(MESI_BREVI)

fig_mediana = px.bar(
    stagionalita,
    x="MESE", y="KG_mediani",
    color_discrete_sequence=[VERDE],
    template="plotly_dark",
)
fig_mediana.update_layout(
    title="Kg recuperati mediani per mese",
    title_font_size=20, title_x=0.5, title_xanchor="center",
    xaxis=dict(title="", categoryorder="array", categoryarray=ORDINE_BREVI),
    yaxis=dict(title="kg mediani"),
    showlegend=False,
    height=420,
)
st.plotly_chart(fig_mediana, use_container_width=True)

pivot_plot = pivot.copy()
pivot_plot.index = pivot_plot.index.map(MESI_BREVI)

fig_heatmap = px.imshow(
    pivot_plot.T,                       # righe = anno, colonne = mese
    labels={"x": "Mese", "y": "Anno", "color": "Kg"},
    color_continuous_scale="Greens",
    aspect="auto",
)
fig_heatmap.update_layout(
    title="Heatmap kg recuperati per anno e mese",
    title_font_size=20, title_x=0.5, title_xanchor="center",
    height=380,
    xaxis=dict(categoryorder="array", categoryarray=ORDINE_BREVI),
    yaxis=dict(autorange="reversed"),
)
st.plotly_chart(fig_heatmap, use_container_width=True)