import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

ANNI = [2025, 2026]

MESI = [
    "Gennaio", "Febbraio", "Marzo", "Aprile",
    "Maggio", "Giugno", "Luglio", "Agosto",
    "Settembre", "Ottobre", "Novembre", "Dicembre"
]


# 🔹 Init stato globale
def init_filter_anno():
    if "ANNO" not in st.session_state:
        st.session_state["ANNO"] = 2025

def init_filter_mese():
    if "MESE" not in st.session_state:
        st.session_state["MESE"] = "Gennaio"

def init_filter_data():
    if "DATA" not in st.session_state:
        st.session_state["DATA"] = []


# 🔹 Sidebar UI
def render_filter_anno(anni: list):
    init_filter_anno()

    st.sidebar.markdown("## 📅 Filtri")

    anno = st.sidebar.selectbox(
        "Anno",
        anni,
        index=anni.index(st.session_state["ANNO"])
    )

    st.session_state["ANNO"] = anno

def render_filter_mese():
    init_filter_mese()

    mese = st.sidebar.selectbox(
        "Mese",
        MESI,
        index=MESI.index(st.session_state["MESE"])
    )
    st.session_state["MESE"] = mese

def render_filter_data():
    init_filter_data()

    giorni = st.sidebar.multiselect(
        "Giorni",
        list(range(1, 32)),
        default=st.session_state["DATA"]
    )

    # 🔥 aggiorna stato globale
    st.session_state["DATA"] = giorni


# 🔹 Getter pulito
def get_filter_anno():
    return {
        "ANNO": st.session_state["ANNO"],
    }
def get_filter_mese():
    return {
        "MESE": st.session_state["MESE"],
    }
def get_filter_giorni():
    return {
        "DATA": st.session_state["DATA"]
    }

# 🔹 Reset opzionale
#def reset_filters():
    st.session_state["ANNO"] = 2025
    st.session_state["MESE"] = "Gennaio"
    st.session_state["DATA"] = []