import gspread
import plotly.express as px
import pandas as pd
from google.oauth2 import service_account
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from sklearn.metrics import r2_score

st.set_page_config(page_title="Homepage",
                   page_icon="🍌",
                   layout="wide")

mesario = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
]

st.markdown("""
<style>
button[data-baseweb="tab"] {
    font-size: 16px;
    padding: 10px 24px;
    border-radius: 10px;
    background-color: #1f1f1f;
    color: #aaa;
}

button[data-baseweb="tab"]:hover {
    background-color: #333;
    color: white;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(90deg,#ff4b4b,#ff914d);
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Percorso del file JSON del service account

#creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])


# Apertura client
#client = gspread.authorize(creds)
#lettura file mercati 2025/2026
wbUrl = st.secrets["WEBHOOK_URL_MERCATI2025"]
wbUrl2026 = st.secrets["WEBHOOK_URL_MERCATI2026"]

st.set_page_config(layout="wide")

df = pd.read_csv(
    filepath_or_buffer= wbUrl,
    header=0,
    usecols=[0,1,2,3],
    parse_dates=[0],
    skiprows=[1],
)
df_2025 = df
df_2026 = pd.read_csv(
    filepath_or_buffer= wbUrl2026,
    header=0,
    usecols=[0,1,2,3,4,5],
    parse_dates=[0],
    skiprows=[1],
)
#lettura file form google
df_Form = pd.read_csv(
    filepath_or_buffer= st.secrets["WEBHOOK_URL_MERCATI_RISPOSTE"],
    usecols=[0,1,2,3,5,6],
    parse_dates=[1],
    skiprows=[0],
)

df = pd.concat([df, df_2026], ignore_index=True)

df["KG"] = (
    df["KG"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)
df["KG"] = pd.to_numeric(df["KG"], errors="coerce")

st.sidebar.text("Made with ❤ by Recup")

st.session_state["df_Form"] = df_Form

dizionarioVolontari = {}
dizionarioBeneficiari = {}
for row2026 in df_2026.iterrows():
    dizionarioVolontari[row2026[1]["MERCATO"] + "_" + row2026[1]["DATA"]] = int(row2026[1]["NUMERO VOLONTARI"])
    dizionarioBeneficiari[row2026[1]["MERCATO"] + "_" + row2026[1]["DATA"]] = int(row2026[1]["NUMERO BENEFICIARI"])

df_Form["Data del Mercato"] = pd.to_datetime(df_Form["Data del Mercato"], dayfirst=True, errors="coerce")
df_form_2025 = df_Form[df_Form["Data del Mercato"].dt.year == 2025]
df_form_2025 = df_form_2025.reset_index(drop=True)
#gestione numero volontari
df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"] = df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"].str.replace(";", ",").str.replace(".", ",").str.replace("-",",").str.replace("/",",").str.replace(" e ",",")
df_form_2025["Numero volontari"] = 0

for idx, vol in df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"].items():
    if vol is "No Data":
        continue
    if "," in vol:
        listaVolontari = str.split(vol,",")
        listaVolontari = list(filter(None, listaVolontari))
        numeroVolontari = int(len(listaVolontari))
        dizionarioVolontari[str.upper(df_form_2025["Nome del Mercato"][idx]) + "_" + (df_form_2025["Data del Mercato"][idx].strftime("%d/%m/%Y"))] = numeroVolontari
    else:
        vol = vol.replace(" de "," de_").replace(" di "," di_").replace(" del "," del_").replace(" da "," da_").replace(" dal ","dal_").replace(" lo ","lo_").replace(" la ","la_")
        listaVolontari = str.split(vol, " ")
        listaVolontari = list(filter(None, listaVolontari))
        numeroVolontari = int(len(listaVolontari)/2)
        dizionarioVolontari[str.upper(df_form_2025["Nome del Mercato"][idx]) + "_" + (df_form_2025["Data del Mercato"][idx].strftime("%d/%m/%Y"))] = numeroVolontari

for idx, ben in df_form_2025["Quantə beneficiariə? (inserisci un numero)"].items():
    if ben is "" or ben is "-":
        continue
    dizionarioBeneficiari[str.upper(df_form_2025["Nome del Mercato"][idx]) + "_" + (
        df_form_2025["Data del Mercato"][idx].strftime("%d/%m/%Y"))] = int(df_form_2025["Quantə beneficiariə? (inserisci un numero)"][idx])

st.session_state["dizionarioVolontari"] = dizionarioVolontari
st.session_state["dizionarioBeneficiari"] = dizionarioBeneficiari
idx = 0
df["DATA"] = pd.to_datetime(df["DATA"],  format="mixed", dayfirst=True, errors="coerce")
#df["KG"] = df["KG"].str.replace(",", ".",regex=False).astype(float)
#df["Numero Volontari"] = 0
for idx, row in df.iterrows():
    df["NUMERO VOLONTARI"][idx] = dizionarioVolontari[str.upper(df["MERCATO"][idx]) + "_" + df["DATA"][idx].strftime("%d/%m/%Y")]
st.session_state["df"] = df

df["ANNO"] = pd.to_datetime(df['DATA'], format='%d-%m-%Y').dt.year
df["MESE"] = df["DATA"].dt.month_name(locale="it_IT")
ordine_mesi = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
]

df["MESE"] = pd.Categorical(df["MESE"], categories=ordine_mesi, ordered=True)
df_grafico_confronto_anni = df.groupby(["ANNO", "MESE"])["KG"].sum().reset_index()
mercati_anni = df.groupby('ANNO')['KG'].sum().reset_index()
mercati_anni["ANNO"] = mercati_anni["ANNO"].astype(str)
totali = mercati_anni.groupby("ANNO")["KG"].sum()

total = round(float(df["KG"].sum()))
#st.markdown(f"## 📅 Anno: 2025")
st.markdown("""
                <style>
                .kpi-card {
                    background: #111;
                    padding: 2px 2px;
                    border-radius: 14px;
                    text-align: center;
                    box-shadow: 0 0 12px rgba(0,0,0,0.4);
                }
                .kpi-title {
                    font-size: 36px;
                    color: #bbbbbb;
                }
                .kpi-value {
                    font-size: 36px;
                    font-weight: 700;
                    color: #00ff9c;
                }
                .kpi-icon {
                    font-size: 36px;
                }
                </style>
                """, unsafe_allow_html=True)
col2 = st.columns(1)


st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-icon">🌱</div>
                        <div class="kpi-title">Cibo recuperato dal 2025</div>
                        <div class="kpi-value">{total} kg</div>
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
grafico_mercati_anni = px.bar(
    mercati_anni,
    x="ANNO",
    y="KG",
    orientation="v",
    color_discrete_sequence=["#0083B8"],
    template="plotly_white"
)
grafico_mercati_anni.update_layout(
    xaxis=dict(title="ANNO"),
    yaxis=dict(title="KG"),
    legend=dict(orientation="h", y=-0.3),
    title="♻️ Recupero negli anni",
    title_font_size=20,
    title_x=0.5,
    title_xanchor="center",
)
grafico_mercati_anni.update_traces(
    width=0.4,
    texttemplate='%{y:.0f} Kg',
    textposition='outside'
)
grafico_mercati_anni.update_layout(
    yaxis=dict(range=[0, mercati_anni["KG"].max() * 1.2]),
    bargap=0.5
)

grafico_confronto_anni = px.line(
    df_grafico_confronto_anni,
    x="MESE",
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
st.plotly_chart(grafico_mercati_anni, use_container_width=True)
st.plotly_chart(grafico_confronto_anni, use_container_width=True)


