import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
from dotenv import load_dotenv
from collections import defaultdict
import json
import os

# Importa le funzioni dell'agente
import sys
sys.path.append("/Users/paolotestori/Desktop/Recup/Ortomercato")
from agent import (
    ask, get_summary, get_top_products, get_top_suppliers,
    get_efficiency_by_supplier, get_monthly_trend,
    get_waste_by_product, get_env_impact_by_year,
    get_fruiter_stats, get_working_days_stats,
    get_supplier_by_product
)

#load_dotenv()
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# --- CONFIG ---
st.set_page_config(
    page_title="ReCup Dashboard",
    page_icon="🍌",
    layout="wide"
)

# --- CARICAMENTO DATI ---
@st.cache_data(ttl=3600)
def load_all_data():
    supabase = create_client(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )
    all_data = []
    offset = 0
    while True:
        batch = supabase.table("Donations").select("""
            lotto, kgIn, kgOut, CO2, H2O, cost,
            Items(name),
            Suppliers(name),
            WorkingDays(date)
        """).range(offset, offset + 999).execute()
        if not batch.data:
            break
        all_data.extend(batch.data)
        offset += 1000

    df = pd.json_normalize(all_data).rename(columns={
        "Items.name": "prodotto",
        "Suppliers.name": "fornitore",
        "WorkingDays.date": "data"
    })
    df["data"] = pd.to_datetime(df["data"])
    df["anno"] = df["data"].dt.year
    df["mese"] = df["data"].dt.month
    df["scarto_kg"] = df["kgIn"] - df["kgOut"]
    df["scarto_pct"] = ((df["scarto_kg"] / df["kgIn"]) * 100).round(2)

    mask = (df["kgIn"] < 2) & (df["kgOut"] > 100)
    df.loc[mask, "kgIn"] = df.loc[mask, "kgIn"] * 1000
    df["scarto_kg"] = df["kgIn"] - df["kgOut"]
    df["scarto_pct"] = ((df["scarto_kg"] / df["kgIn"]) * 100).round(2)

    return df

df = load_all_data()

BASE = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE, "assets", "recup_logo.png")
icon_path = os.path.join(BASE, "assets", "recup_icon.png")
if os.path.exists(logo_path):
    st.logo(
        logo_path,
        icon_image=icon_path if os.path.exists(icon_path) else None,
        size="large",
    )

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@700&family=Outfit:wght@600;700;800&display=swap');

    /* logo grande e staccato dal bordo */
    section[data-testid="stSidebar"] img[data-testid="stLogo"],
    div[data-testid="stSidebarHeader"] img,
    section[data-testid="stSidebar"] a img {
        height: 84px !important;
        max-height: 84px !important;
        width: auto !important;
        max-width: 100% !important;
        margin: 18px 0 6px 0 !important;
    }
    div[data-testid="stSidebarHeader"] {
        padding-top: 14px;
        padding-bottom: 6px;
    }

    /* etichette di sezione (NAVIGA / FILTRA PER ANNO) */
    .recup-filtro-label {
        font-size: 15px; font-weight: 800; color: #ffffff;
        font-family: 'Outfit', sans-serif; text-transform: uppercase;
        letter-spacing: 0.08em; margin: 4px 0 4px 0;
    }

    /* radio di navigazione: nasconde i pallini, voci come righe pulite */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        padding: 6px 10px;
        border-radius: 10px;
        margin: 2px 0;
        transition: background 0.15s ease;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.06);
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
        background: rgba(255,255,255,0.10);
        font-weight: 700;
    }

    /* selectbox in stile card scura (come i mercati) */
    div[data-baseweb="select"] > div {
        background-color: #0d1f1a;
        border: 1px solid #1a3a2a;
        border-radius: 10px;
        color: #e8f0ec;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        transition: border-color 0.2s ease;
    }
    div[data-baseweb="select"] > div:hover { border-color: #2e7d5b; }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #2E8B57 !important;
        box-shadow: 0 0 0 1px #2E8B57 !important;
    }

    /* made with in fondo */
    .recup-madewith {
        font-size: 13px; color: #8a9ba8; font-family: 'DM Sans', sans-serif;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 14px; margin-top: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- NAVIGA ---
    st.markdown('<div class="recup-filtro-label">🧭 Naviga</div>', unsafe_allow_html=True)
    pagina = st.radio("Naviga", [
        "📊 Overview",
        "🍂 Stagionalità",
        "🥦 Prodotti",
        "🏭 Fornitori",
        "🌱 Impatto ambientale",
        "🤖 Chat AI"
    ], label_visibility="collapsed")

    st.divider()

    # --- FILTRO ANNO ---
    st.markdown('<div class="recup-filtro-label">📅 Anno</div>', unsafe_allow_html=True)
    anni_disponibili = sorted(df["anno"].unique(), reverse=True)
    anno_filtro = st.selectbox(
        "Filtra per anno",
        ["Tutti"] + [str(a) for a in anni_disponibili],
        label_visibility="collapsed",
    )

    # --- MADE WITH ---
    st.markdown('<div class="recup-madewith">Made with ❤ by Recup</div>',
                unsafe_allow_html=True)

# Applica filtro anno
df_filtered = df if anno_filtro == "Tutti" else df[df["anno"] == int(anno_filtro)]


def fmt(numero):
    """Formatta numeri in italiano: punto per migliaia, virgola per decimali"""
    return f"{numero:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- PAGINE ---
if pagina == "📊 Overview":
    st.title("📊 Overview")

    # Metric box
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Kg donati", fmt(df_filtered['kgOut'].sum()))
    col2.metric("Kg raccolti", fmt(df_filtered['kgIn'].sum()))
    col3.metric("CO2 risparmiata (kg)", fmt(df_filtered['CO2'].sum()))
    col4.metric("Fornitori attivi", df_filtered['fornitore'].nunique())

    st.divider()

    # Volumi per anno
    trend = (df[df["anno"] < 2026].groupby("anno")
             .agg(kg_raccolti=("kgIn", "sum"), kg_donati=("kgOut", "sum"))
             .reset_index())

    fig = go.Figure()
    fig.add_bar(x=trend["anno"], y=trend["kg_raccolti"], name="Kg raccolti", marker_color="#5B9BD5")
    fig.add_bar(x=trend["anno"], y=trend["kg_donati"], name="Kg donati", marker_color="#2E8B57")
    fig.update_layout(barmode="group", title="Kg raccolti vs donati per anno",
                      xaxis_title="Anno", yaxis_title="kg", height=400)
    fig.update_layout(
        separators=".,"  # punto migliaia, virgola decimali
    )
    st.plotly_chart(fig, use_container_width=True)

    # Efficienza per anno

    scarto_anno = (df[df["anno"] < 2026].groupby("anno")
                   .apply(lambda x: round(100 - x["kgOut"].sum() / x["kgIn"].sum() * 100, 1))
                   .reset_index(name="scarto_pct"))
    scarto_anno["anno"] = scarto_anno["anno"].astype(str)
    fig2 = px.line(scarto_anno, x="anno", y="scarto_pct",
                   markers=True, title="Scarto % per anno",
                   color_discrete_sequence=["#E74C3C"])
    fig2.update_layout(yaxis_title="Scarto %", xaxis_title="Anno", height=300)
    fig2.update_xaxes(type="category")
    fig2.add_hline(y=15, line_dash="dash", line_color="gray", annotation_text="Soglia 20%")
    st.plotly_chart(fig2, use_container_width=True)


elif pagina == "🍂 Stagionalità":
    st.title("🍂 Stagionalità")

    # Mediana mensile
    pivot = (df[df["anno"] < 2026]
             .groupby(["anno", "mese"])["kgOut"]
             .sum()
             .unstack(level=0))

    mediana_mensile = pivot.median(axis=1).reset_index()
    mediana_mensile.columns = ["mese", "kg_mediani"]
    nomi_mesi = {1:"Gen",2:"Feb",3:"Mar",4:"Apr",5:"Mag",6:"Giu",
                 7:"Lug",8:"Ago",9:"Set",10:"Ott",11:"Nov",12:"Dic"}
    mediana_mensile["mese_nome"] = mediana_mensile["mese"].map(nomi_mesi)

    fig = px.bar(mediana_mensile, x="mese_nome", y="kg_mediani",
                 title="Kg donati mediani per mese (2021-2025)",
                 color_discrete_sequence=["#2E8B57"])
    fig.update_layout(xaxis_title="", yaxis_title="kg mediani",
                      height=400, separators=".,",
                      xaxis={"categoryorder": "array",
                             "categoryarray": list(nomi_mesi.values())})
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap anno x mese
    st.subheader("Heatmap kg donati per anno e mese")
    pivot_plot = pivot.copy()
    pivot_plot.index = pivot_plot.index.map(nomi_mesi)

    fig2 = px.imshow(pivot_plot.T,
                     labels={"x": "Mese", "y": "Anno", "color": "Kg donati"},
                     color_continuous_scale="Greens",
                     title="Heatmap kg donati")
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

elif pagina == "🥦 Prodotti":
    st.title("🥦 Prodotti")

    col1, col2 = st.columns(2)
    with col1:
        n_prodotti = st.slider("Numero prodotti da mostrare", 5, 30, 15)
    with col2:
        solo_anno = st.checkbox("Usa filtro anno dalla sidebar", value=True)

    df_prod = df_filtered if solo_anno else df

    # Top prodotti per kg
    top_prod = (df_prod.groupby("prodotto")
                .agg(kg_donati=("kgOut", "sum"),
                     kg_raccolti=("kgIn", "sum"),
                     num_lotti=("lotto", "count"))
                .assign(scarto_pct=lambda x: round(100 - x["kg_donati"] / x["kg_raccolti"] * 100, 1))
                .sort_values("kg_donati", ascending=False)
                .head(n_prodotti)
                .reset_index())

    fig = px.bar(top_prod.sort_values("kg_donati"),
                 x="kg_donati", y="prodotto",
                 orientation="h",
                 title=f"Top {n_prodotti} prodotti per kg donati",
                 color="scarto_pct",
                 color_continuous_scale="RdYlGn_r",
                 labels={"kg_donati": "Kg donati", "scarto_pct": "Scarto %"},
                 hover_data=["num_lotti", "scarto_pct"])
    fig.update_layout(height=500, separators=".,",
                      coloraxis_colorbar_title="Scarto %")
    st.plotly_chart(fig, use_container_width=True)

    # Scatter kg vs scarto
    st.subheader("Volume vs Scarto per prodotto")
    scatter_prod = (df_prod[df_prod["fornitore"] != "Sconosciuto"]
                    .groupby("prodotto")
                    .agg(kg_donati=("kgOut", "sum"),
                         num_lotti=("lotto", "count"),
                         kg_raccolti=("kgIn", "sum"))
                    .assign(scarto_pct=lambda x: round(100 - x["kg_donati"] / x["kg_raccolti"] * 100, 1))
                    .reset_index())

    scatter_prod = scatter_prod[scatter_prod["num_lotti"] >= 10]
    scatter_prod = scatter_prod[scatter_prod["scarto_pct"] >= 0]

    fig2 = px.scatter(scatter_prod,
                      x="scarto_pct", y="kg_donati",
                      hover_name="prodotto",
                      size="num_lotti",
                      title="Prodotti: volume vs scarto%",
                      labels={"scarto_pct": "Scarto %", "kg_donati": "Kg donati"},
                      color="scarto_pct",
                      color_continuous_scale="RdYlGn_r")
    fig2.update_layout(height=450, separators=".,")
    st.plotly_chart(fig2, use_container_width=True)

elif pagina == "🏭 Fornitori":
    st.title("🏭 Fornitori")

    st.info("I dati fornitori sono affidabili solo dal 2024 — prima il 75% dei lotti aveva fornitore 'Sconosciuto'.")

    df_forn = df[(df["fornitore"] != "Sconosciuto") & (df["anno"] >= 2024)]

    # Efficienza top 20
    efficienza_forn = (df_forn.groupby("fornitore")
                       .agg(kg_donati=("kgOut", "sum"),
                            kg_raccolti=("kgIn", "sum"),
                            num_lotti=("lotto", "count"),
                            num_prodotti=("prodotto", "nunique"))
                       .assign(efficienza=lambda x: round(x["kg_donati"] / x["kg_raccolti"] * 100, 1))
                       .query("num_lotti >= 20 and efficienza <= 100")
                       .sort_values("kg_donati", ascending=False)
                       .head(20)
                       .reset_index())

    fig = px.bar(efficienza_forn.sort_values("efficienza"),
                 x="efficienza", y="fornitore",
                 orientation="h",
                 title="Top 20 fornitori per volume — efficienza %",
                 color="efficienza",
                 color_continuous_scale="RdYlGn",
                 range_color=[50, 100],
                 labels={"efficienza": "Efficienza %", "kg_donati": "Kg donati"},
                 hover_data=["kg_donati", "num_lotti", "num_prodotti"])
    fig.update_layout(height=550, separators=".,",
                      coloraxis_colorbar_title="Efficienza %")
    fig.add_vline(x=efficienza_forn["efficienza"].mean(),
                  line_dash="dash", line_color="gray",
                  annotation_text=f"Media: {efficienza_forn['efficienza'].mean():.1f}%")
    st.plotly_chart(fig, use_container_width=True)

    # Scatter volume vs efficienza
    st.subheader("Volume vs Efficienza per fornitore")
    fig2 = px.scatter(efficienza_forn,
                      x="efficienza", y="kg_donati",
                      hover_name="fornitore",
                      size="num_lotti",
                      color="efficienza",
                      color_continuous_scale="RdYlGn",
                      range_color=[50, 100],
                      title="Fornitori: volume vs efficienza",
                      labels={"efficienza": "Efficienza %", "kg_donati": "Kg donati"})
    fig2.update_layout(height=450, separators=".,")
    st.plotly_chart(fig2, use_container_width=True)

elif pagina == "🌱 Impatto ambientale":
    st.title("🌱 Impatto ambientale")

    # Metric box
    col1, col2 = st.columns(2)
    col1.metric("CO2 risparmiata totale", f"{fmt(df_filtered['CO2'].sum())} kg")
    col2.metric("H2O risparmiata totale", f"{fmt(df_filtered['H2O'].sum())} litri")

    # Equivalenze comunicative
    st.subheader("In termini pratici...")
    co2_tot = df_filtered["CO2"].sum()
    h2o_tot = df_filtered["H2O"].sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("🌳 Alberi equivalenti", fmt(co2_tot / 22),
                help="Un albero assorbe circa 22 kg di CO2 all'anno")
    col2.metric("🚗 Km in auto evitati", fmt(co2_tot / 0.12),
                help="Un'auto emette circa 120g di CO2 per km")
    col3.metric("🚿 Docce equivalenti", fmt(h2o_tot / 60),
                help="Una doccia usa circa 60 litri di acqua")

    st.divider()

    # CO2 e H2O per anno
    impatto_anno = (df[df["anno"] < 2026].groupby("anno")
                    .agg(CO2=("CO2", "sum"), H2O=("H2O", "sum"))
                    .reset_index())
    impatto_anno["anno"] = impatto_anno["anno"].astype(str)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(impatto_anno, x="anno", y="CO2",
                     title="CO2 risparmiata per anno (kg)",
                     color_discrete_sequence=["#E74C3C"])
        fig.update_layout(height=350, separators=".,",
                          xaxis_title="", yaxis_title="kg CO2")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(impatto_anno, x="anno", y="H2O",
                      title="H2O risparmiata per anno (litri)",
                      color_discrete_sequence=["#3498DB"])
        fig2.update_layout(height=350, separators=".,",
                           xaxis_title="", yaxis_title="litri")
        st.plotly_chart(fig2, use_container_width=True)

    # Trend CO2 cumulativa
    impatto_anno["CO2_cumulativa"] = impatto_anno["CO2"].cumsum()
    fig3 = px.area(impatto_anno, x="anno", y="CO2_cumulativa",
                   title="CO2 risparmiata cumulativa (kg)",
                   color_discrete_sequence=["#E74C3C"])
    fig3.update_layout(height=300, separators=".,",
                       xaxis_title="", yaxis_title="kg CO2 cumulativi")
    fig3.update_xaxes(type="category")
    st.plotly_chart(fig3, use_container_width=True)

elif pagina == "🤖 Chat AI":
    st.title("🤖 Chiedi a ReCup AI")
    st.caption("Fai domande sui dati in linguaggio naturale")

    if "history" not in st.session_state:
        st.session_state.history = []
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostra messaggi precedenti
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input utente
    if prompt := st.chat_input("Es: Quali prodotti hanno più scarto?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Sto analizzando..."):
                risposta, st.session_state.history = ask(prompt, st.session_state.history)
            st.write(risposta)
            st.session_state.messages.append({"role": "assistant", "content": risposta})

    if st.session_state.messages:
        if st.button("🗑️ Cancella conversazione"):
            st.session_state.history = []
            st.session_state.messages = []
            st.rerun()

