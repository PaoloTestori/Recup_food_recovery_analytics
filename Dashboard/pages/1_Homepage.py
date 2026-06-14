import plotly.express as px
import pandas as pd
import streamlit as st
from components.data_loader import load_all, ORDINE_MESI
from components.styles import (inietta_css)
from components.palette import VERDE, ROSSO, BLU, GIALLO, GRIGIO, VERDE_SOFT, ROSSO_SOFT

st.set_page_config(page_title="Homepage",
                   page_icon="🍌",
                   layout="wide")

mesario = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
]

inietta_css()

wbUrl = st.secrets["WEBHOOK_URL_MERCATI2025"]
wbUrl2026 = st.secrets["WEBHOOK_URL_MERCATI2026"]
wbUrl2024 = st.secrets["WEBHOOK_URL_MERCATI2024"]
wbUrl2023 = st.secrets["WEBHOOK_URL_MERCATI2023"]

data = load_all()
df                    = data["df"]
df_Form               = data["df_Form"]
df_2026               = data["df_2026"]
dizionarioVolontari   = data["dizionarioVolontari"]
dizionarioBeneficiari = data["dizionarioBeneficiari"]

st.session_state["df"]                    = df
st.session_state["df_Form"]               = df_Form
st.session_state["dizionarioVolontari"]   = dizionarioVolontari
st.session_state["dizionarioBeneficiari"] = dizionarioBeneficiari

df["ANNO"] = pd.to_datetime(df['DATA'], format='%d-%m-%Y').dt.year
df["MESE"] = df["DATA"].dt.month.map({
    1: "Gennaio", 2: "Febbraio", 3: "Marzo", 4: "Aprile",
    5: "Maggio", 6: "Giugno", 7: "Luglio", 8: "Agosto",
    9: "Settembre", 10: "Ottobre", 11: "Novembre", 12: "Dicembre"
})
ordine_mesi = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
]
df["MESE"] = pd.Categorical(df["MESE"], categories=ordine_mesi, ordered=True)
df["MESE_NUM"] = df["DATA"].dt.month
df = df.sort_values("MESE_NUM")
df_grafico_confronto_anni = df.groupby(["ANNO", "MESE_NUM"])["KG"].sum().reset_index()
mercati_anni = df.groupby('ANNO')['KG'].sum().reset_index()
mercati_anni["ANNO"] = mercati_anni["ANNO"].astype(str)
totali = mercati_anni.groupby("ANNO")["KG"].sum()

total = round(float(df["KG"].sum()))
st.markdown("")
mercati_anni = mercati_anni.sort_values("ANNO")
mercati_anni["pct_change"] = mercati_anni["KG"].pct_change() *100
mercati_anni["pct_label"] = mercati_anni["pct_change"].apply(
    lambda x: f"{x:+.0f}%" if pd.notnull(x) else ""
)
mercati_anni.loc[mercati_anni["ANNO"] == "2026", "pct_label"] = "(parziale)"
mercati_anni["arrow"] = mercati_anni["pct_change"].apply(
    lambda x: "↑" if x > 0 else ("↓" if x < 0 else "")
)

mercati_anni["label"] = (
    mercati_anni["KG"].astype(int).astype(str) + " kg<br>" +
    mercati_anni["arrow"] + " " + mercati_anni["pct_label"]
)
mercati_anni["color"] = mercati_anni["pct_change"].apply(
    lambda x: VERDE if x > 0 else ROSSO
)

inietta_css()

st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-icon">🌱</div>
    <div class="kpi-title">Cibo recuperato dal 2023</div>
    <div class="kpi-value">{total:} kg</div>
</div>
""", unsafe_allow_html=True)

st.markdown("", unsafe_allow_html=True)
grafico_mercati_anni = px.bar(
    mercati_anni,
    x="ANNO",
    y="KG",
    text="label",
    orientation="v",
    color="color",
    color_discrete_map="identity",
    color_discrete_sequence=["#0083B8"],
    template="plotly_white"
)
grafico_mercati_anni.update_layout(
    xaxis=dict(title="ANNO",
               categoryorder="array",
               categoryarray=mercati_anni["ANNO"]
    ),
    yaxis=dict(title="KG"),
    legend=dict(orientation="h", y=-0.3),
    title="♻️ Recupero negli anni",
    title_font_size=20,
    title_x=0.5,
    title_xanchor="center",
)
grafico_mercati_anni.update_traces(
    width=0.4,
    textposition='outside',
    textfont_size=14,
    marker_line_width=2,
    marker_line_color="white"
)
grafico_mercati_anni.update_layout(
    yaxis=dict(range=[0, mercati_anni["KG"].max() * 1.2]),
    bargap=0.5,
    showlegend=False,
    yaxis_title="",
    xaxis_title=""
)

grafico_confronto_anni = px.line(
    df_grafico_confronto_anni,
    x="MESE_NUM",
    y="KG",
    color="ANNO",
    title="Confronto Anni",
    labels={"giorno": "Giorno dell'anno"},
    template="plotly_dark"
)
grafico_confronto_anni.update_layout(
    xaxis=dict(title="MESE"),
    yaxis=dict(title="KG"),
    legend=dict(orientation="h", y=-0.3),
    title="⚖️Confronto Anni",
    title_font_size=20,
    title_x=0.5,
    title_xanchor="center",
)
grafico_confronto_anni.update_xaxes(
    tickmode="array",
    tickvals=list(range(1, 13)),
    ticktext=[
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
        "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
    ]
)
st.plotly_chart(grafico_mercati_anni, use_container_width=True)


