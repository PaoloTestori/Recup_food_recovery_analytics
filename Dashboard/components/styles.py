"""
components/styles.py
────────────────────
CSS condiviso per tutte le pagine della dashboard Mercati di strada Recup.
Prima questi blocchi <style> erano copia-incollati identici in ogni pagina
(tab + kpi-card + block-container). Ora vivono qui: ogni pagina chiama
inietta_css() una volta in cima.

USO:
    from components.styles import inietta_css
    inietta_css()
"""

import streamlit as st


def inietta_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=Space+Grotesk:wght@700&family=Outfit:wght@600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=Space+Grotesk:wght@700&display=swap');

    /* ---- Tab ---- */
    button[data-baseweb="tab"]{
        font-size:16px; padding:10px 24px; border-radius:10px;
        background-color:#1f1f1f; color:#aaa;
    }
    button[data-baseweb="tab"]:hover{ background-color:#333; color:white; }
    button[data-baseweb="tab"][aria-selected="true"]{
        background:linear-gradient(90deg,#ff4b4b,#ff914d);
        color:white; font-weight:bold;
    }

    /* ---- KPI card (versione "equilibrata") ---- */
    .kpi-card{
        background:linear-gradient(135deg,#0d1f1a 0%,#0a1a14 100%);
        border:1px solid #1a3a2a;
        padding:1.5rem 2rem;
        border-radius:16px;
        text-align:center;
        max-width:680px;
        margin:1rem auto 0 auto;
        font-family:'DM Sans',sans-serif;
    }
    .kpi-icon{ font-size:1.8rem; line-height:1; margin-bottom:0.4rem; }
    .kpi-title{
        color:#8a9ba8; font-size:1.05rem; letter-spacing:0.12em;
        text-transform:uppercase; margin-bottom:0.5rem; font-weight:400;
        font-family:'DM Sans',sans-serif;
    }
    .kpi-value{
        color:#ffea00; font-size:3rem; font-weight:700; line-height:1;
        font-family:'Space Grotesk',sans-serif;
    }

    /* ---- Layout container ---- */
    .block-container{
        padding-top:1rem !important;
        padding-bottom:0rem !important;
    }
    /* ---- Selectbox mercato ---- */
    .stSelectbox label {
        color: #8a9ba8;
        font-size: 0.9rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-family: 'DM Sans', sans-serif;
        font-weight: 400;
    }
    div[data-baseweb="select"] > div {
        background-color: #0d1f1a;
        border: 1px solid #1a3a2a;
        border-radius: 10px;
        color: #e8f0ec;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 900;
        transition: border-color 0.2s ease;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: #2e7d5b;
    }
    /* tieni l'accent verde anche al focus, invece del rosso di default */
    div[data-baseweb="select"] > div:focus-within {
        border-color: #00ff9c !important;
        box-shadow: 0 0 0 1px #00ff9c !important;
    }
    
    /* ---- Header mercato selezionato ---- */
    .header-title {
        font-size: 34px;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        color: #ffffff;
        display: inline-block;
        padding-bottom: 5px;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #ff4b4b, #ff914d) 1;
        margin-bottom: 18px;
    }
    /* ingrandisci il logo e staccalo dal bordo alto */
    /* logo più grande: selettori multipli + !important per battere gli stili interni */
    section[data-testid="stSidebar"] img[data-testid="stLogo"],
    div[data-testid="stSidebarHeader"] img,
    section[data-testid="stSidebar"] a img {
        height: 84px !important;
        max-height: 84px !important;
        width: auto !important;
        max-width: 100% !important;
        margin: 18px 0 6px 0 !important;
    }
    /* se la versione di Streamlit usa un contenitore header per il logo */
    div[data-testid="stSidebarHeader"] {
        padding-top: 14px;
        padding-bottom: 6px;
    }
    /* etichetta "Naviga" sopra le voci di menu */
    div[data-testid="stSidebarNav"]::before {
        content: "🧭 NAVIGA";
        display: block;
        font-size: 15px;
        font-weight: 800;
        color: #ffffff;
        font-family: 'Outfit', sans-serif; 
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 22px 16px 8px 6px;
    }
    /* il contenitore del Made with va SEMPRE in fondo allo user-content */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(.recup-madewith) {
        order: 99;
    }
    /* attiva il flex sul contenitore dei contenuti sidebar */
    section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] div[data-testid="stVerticalBlock"] {
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stAlert"] p {
    font-size: 1.25rem !important;
    }
    /* ---- menu navigazione in stile Ortomercato ---- */
    /* più aria tra le voci */
    div[data-testid="stSidebarNav"] li {
        margin: 1px 0;
    }
    /* testo più grande e padding da "pillola" */
    div[data-testid="stSidebarNav"] a {
        padding: 2px 24px;
        border-radius: 12px;
    }
    div[data-testid="stSidebarNav"] a span {
        font-size: 17px;
    }
    /* la voce attiva: pillola compatta, non barra a tutta larghezza */
    div[data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(255,255,255,0.10);
        width: fit-content;
    }
    /* hover coerente */
    div[data-testid="stSidebarNav"] a:hover {
        background: rgba(255,255,255,0.06);
    }
    </style>
    """, unsafe_allow_html=True)