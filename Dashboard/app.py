import streamlit as st
import importlib.util
import os

st.set_page_config(page_title="ReCup Mercati", page_icon="🍌", layout="wide")

BASE = os.path.dirname(__file__)

# ─── logo sopra il menu (meccanismo nativo st.logo) ──────────────────────────
st.logo(
    os.path.join(BASE, "assets", "recup_logo.png"),
    icon_image=os.path.join(BASE, "assets", "recup_icon.png"),
    size="large",
)

# ─── lista anni dal loader cached (per il filtro globale) ────────────────────
spec_dl = importlib.util.spec_from_file_location(
    "data_loader",
    os.path.join(BASE, "components", "data_loader.py")
)
data_loader = importlib.util.module_from_spec(spec_dl)
spec_dl.loader.exec_module(data_loader)

try:
    _data = data_loader.load_all()
    anni_disponibili = sorted(_data["df"]["ANNO"].dropna().unique().astype(int).tolist())
except Exception:
    anni_disponibili = [2025, 2026]

if "ANNO" not in st.session_state:
    st.session_state["ANNO"] = anni_disponibili[-1]

# ─── pagine ──────────────────────────────────────────────────────────────────
pages = [
    st.Page("pages/1_Homepage.py", title="Overview", icon="📊"),
    st.Page("pages/5_Stagionalita.py", title="Stagionalità", icon="🍂"),
    st.Page("pages/2_Overview.py", title="Anni di mercato", icon="📅"),
    st.Page("pages/3_Mercati.py", title="Mercati", icon="🥦"),
    st.Page("pages/4_Giornate di mercato.py", title="Giornate di mercato", icon="☀️"),
]

# ─── sidebar: sotto il menu → sottotitolo + filtro anno + made with ──────────
with st.sidebar:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    /* il logo (st.logo) sta già sopra il menu, nativo.
       qui sotto: sottotitolo, filtro, made with — nell'ordine naturale */
    .recup-sottotitolo {
        font-size: 13px; color: #8a9ba8; font-weight: 500;
        font-family: 'DM Sans', sans-serif; line-height: 1.3;
        margin: 0 0 10px 0;
    }
    .recup-filtro-label {
        font-size: 14px; font-weight: 700; color: #fff;
        font-family: 'DM Sans', sans-serif; text-transform: uppercase;
        letter-spacing: 0.08em; margin: 4px 0 4px 0;
    }
    .recup-madewith {
        font-size: 13px; color: #8a9ba8; font-family: 'DM Sans', sans-serif;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 14px; margin-top: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

pg = st.navigation(pages, position="sidebar", expanded=True)

# il sottotitolo + filtro + made with vanno DOPO la navigation,
# così Streamlit li mette nello user-content sotto il menu
with st.sidebar:
    st.markdown('<div class="recup-filtro-label">📅 Anno</div>', unsafe_allow_html=True)
    st.session_state["ANNO"] = st.selectbox(
        "Anno", anni_disponibili,
        index=anni_disponibili.index(st.session_state["ANNO"]),
        label_visibility="collapsed", key="anno_sidebar",
    )
    st.markdown('<div class="recup-madewith">Made with ❤ by Recup</div>',
                unsafe_allow_html=True)

pg.run()