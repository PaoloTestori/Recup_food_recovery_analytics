"""
components/data_loader.py
─────────────────────────
Caricamento e parsing centralizzato e CACHED per la dashboard Mercati di strada Recup.

Tutto ciò che prima stava sparso e non-cached in 1_Homepage.py vive ora qui, in
funzioni decorate con @st.cache_data. Così il read_csv da webhook + il parsing
volontari/beneficiari girano UNA volta sola e vengono riusati su ogni pagina e a
ogni cambio di filtro (finché non scade il ttl).

USO nelle pagine:
    from components.data_loader import load_all
    data = load_all()
    df                   = data["df"]                    # df recuperi arricchito
    df_Form              = data["df_Form"]
    dizionarioVolontari  = data["dizionarioVolontari"]
    dizionarioBeneficiari= data["dizionarioBeneficiari"]

(oppure tieni il pattern st.session_state che hai già: vedi guida_modifiche.md)
"""

import pandas as pd
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Costanti condivise (prima erano duplicate in più pagine)
# ─────────────────────────────────────────────────────────────────────────────

ORDINE_MESI = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]

MAPPA_MESI = {i + 1: nome for i, nome in enumerate(ORDINE_MESI)}

# Giorno della settimana (0=lun ... 6=dom) in cui si tiene ciascun mercato.
# Centralizzato qui: prima era ridefinito in 3_Mercati.py e 4_Giornate.py con
# liste DIVERSE (Esterle/Arese presenti in uno e non nell'altro).
GIORNATE_DI_MERCATO = {
    "MOMPIANI": 1,
    "MARTINI": 2,
    "PADERNO DUGNANO": 2,
    "ARESE": 2,
    "TERMOPILI": 4,
    "CATONE": 4,
    "GRAMSCI - SAN DONATO": 4,
    "GRAMSCI": 4,
    "OGLIO": 5,
    "VALVASSORI PERONI": 5,
    "TABACCHI": 5,
    "OSOPPO": 5,
    "PAPINIANO": 5,
    "BENEDETTO MARCELLO": 5,
    "ESTERLE": 5,
}

# Coordinate dei mercati (prima erano dentro 2_Overview.py)
LAT = {
    "BENEDETTO MARCELLO": 45.48194631003896, "CATONE": 45.498572631276076,
    "GRAMSCI - SAN DONATO": 45.41558818510914, "MARTINI": 45.4568377251085,
    "MOMPIANI": 45.43769947440869, "OGLIO": 45.44079962417922,
    "OSOPPO": 45.46856674391473, "PADERNO DUGNANO": 45.56908414624718,
    "PAPINIANO": 45.45809799201643, "TABACCHI": 45.44769247648455,
    "TERMOPILI": 45.49170755334271, "VALVASSORI PERONI": 45.47979583274876,
}
LONG = {
    "BENEDETTO MARCELLO": 9.20908871960476, "CATONE": 9.171843522528558,
    "GRAMSCI - SAN DONATO": 9.265495707447384, "MARTINI": 9.220735241820233,
    "MOMPIANI": 9.222317497412892, "OGLIO": 9.2194775512992,
    "OSOPPO": 9.141949360535436, "PADERNO DUGNANO": 9.15969763897859,
    "PAPINIANO": 9.170071664509393, "TABACCHI": 9.18266244741002,
    "TERMOPILI": 9.220097090233262, "VALVASSORI PERONI": 9.236583212298052,
}


# ─────────────────────────────────────────────────────────────────────────────
# 1. Lettura grezza dei CSV (cached separatamente: ognuno ha il suo ttl)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def _read_recuperi() -> pd.DataFrame:
    """Legge i 4 fogli annuali dei recuperi e li concatena."""
    wbUrl     = st.secrets["WEBHOOK_URL_MERCATI2025"]
    wbUrl2026 = st.secrets["WEBHOOK_URL_MERCATI2026"]
    wbUrl2024 = st.secrets["WEBHOOK_URL_MERCATI2024"]
    wbUrl2023 = st.secrets["WEBHOOK_URL_MERCATI2023"]

    df_2025 = pd.read_csv(wbUrl,     header=0, usecols=[0, 1, 2, 3],
                          parse_dates=[0], skiprows=[1])
    df_2026 = pd.read_csv(wbUrl2026, header=0, usecols=[0, 1, 2, 3, 4, 5],
                          parse_dates=[0], skiprows=[1])
    df_2024 = pd.read_csv(wbUrl2024, header=0, usecols=[0, 1, 2, 3],
                          parse_dates=[0], skiprows=[1])
    df_2023 = pd.read_csv(wbUrl2023, header=0, usecols=[0, 1, 2, 3],
                          parse_dates=[0], skiprows=[1])

    df = pd.concat([df_2023, df_2024, df_2025, df_2026], ignore_index=True)

    # KG: virgola decimale -> punto, poi numerico
    df["KG"] = (
        df["KG"].astype(str).str.replace(",", ".", regex=False)
    )
    df["KG"] = pd.to_numeric(df["KG"], errors="coerce")
    return df, df_2026


@st.cache_data(ttl=600, show_spinner=False)
def _read_form() -> pd.DataFrame:
    """Legge le risposte del form volontari/beneficiari."""
    df_Form = pd.read_csv(
        st.secrets["WEBHOOK_URL_MERCATI_RISPOSTE"],
        usecols=[0, 1, 2, 3, 4, 5, 6],
        parse_dates=[1],
        skiprows=[0],
    )
    return df_Form


# ─────────────────────────────────────────────────────────────────────────────
# 2. Parsing volontari / beneficiari -> dizionari "MERCATO_DD/MM/YYYY" -> numero
# ─────────────────────────────────────────────────────────────────────────────

def _conta_volontari(stringa: str) -> int:
    """
    Conta i volontari da una stringa libera tipo 'Mario Rossi, Anna de_Luca'.
    Logica identica a quella originale ma estratta in funzione testabile.
    """
    if stringa is None or str(stringa).strip() in ("", "No Data"):
        return 0
    vol = str(stringa).replace("+", "")
    if "," in vol:
        lista = list(filter(None, vol.split(",")))
        return len(lista)
    # nessuna virgola: si assume "Nome Cognome Nome Cognome..."
    # le particelle (de/di/del/da/lo/la) vengono "incollate" per non contare doppio
    vol = (vol.replace(" de ", " de_").replace(" di ", " di_")
              .replace(" del ", " del_").replace(" da ", " da_")
              .replace(" dal ", "dal_").replace(" lo ", "lo_")
              .replace(" la ", "la_"))
    lista = list(filter(None, vol.split(" ")))
    return int(len(lista) / 2)


@st.cache_data(ttl=600, show_spinner=False)
def _costruisci_dizionari(df_2026: pd.DataFrame, df_Form: pd.DataFrame):
    """
    Costruisce dizionarioVolontari e dizionarioBeneficiari combinando:
      - il foglio 2026 (che ha già le colonne NUMERO VOLONTARI / NUMERO BENEFICIARI)
      - il form risposte per gli anni 2024-2025
    """
    dizionarioVolontari = {}
    dizionarioBeneficiari = {}

    # --- dal foglio 2026 (colonne strutturate) ---
    for _, r in df_2026.iterrows():
        chiave = f'{r["MERCATO"]}_{r["DATA"]}'
        dizionarioVolontari[chiave] = int(r["NUMERO VOLONTARI"])
        dizionarioBeneficiari[chiave] = int(r["NUMERO BENEFICIARI"])

    # --- dal form risposte (2024-2025, testo libero) ---
    form = df_Form.copy()
    form["Data del Mercato"] = pd.to_datetime(
        form["Data del Mercato"], dayfirst=True, errors="coerce"
    )
    form = form[form["Data del Mercato"].dt.year.isin([2024, 2025])].reset_index(drop=True)

    col_vol = "Inserisci NOME e COGNOME dellə volontariə presenti"
    col_ben = "Quantə beneficiariə? (inserisci un numero)"

    # normalizza i separatori nella colonna volontari
    form[col_vol] = (
        form[col_vol].astype(str)
        .str.replace(";", ",").str.replace(".", ",")
        .str.replace("-", ",").str.replace("/", ",")
        .str.replace(" e ", ",")
    )

    for idx, vol in form[col_vol].items():
        chiave = (form["Nome del Mercato"][idx].upper() + "_"
                  + form["Data del Mercato"][idx].strftime("%d/%m/%Y"))
        dizionarioVolontari[chiave] = _conta_volontari(vol)

    for idx, ben in form[col_ben].items():
        if str(ben).strip() in ("", "-", ".", "Nessuna", "Nessuno", "nessuna", "nessuno"):
            continue
        chiave = (form["Nome del Mercato"][idx].upper() + "_"
                  + form["Data del Mercato"][idx].strftime("%d/%m/%Y"))
        try:
            dizionarioBeneficiari[chiave] = int(ben)
        except (ValueError, TypeError):
            continue

    return dizionarioVolontari, dizionarioBeneficiari


# ─────────────────────────────────────────────────────────────────────────────
# 3. Arricchimento del df recuperi (vettoriale, niente più iterrows + chained assignment)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def _arricchisci_df(df: pd.DataFrame, dizionarioVolontari: dict,
                    dizionarioBeneficiari: dict) -> pd.DataFrame:
    df = df.copy()
    df["DATA"] = pd.to_datetime(df["DATA"], format="mixed", dayfirst=True, errors="coerce")

    # chiave "MERCATO_DD/MM/YYYY" vettoriale
    chiave = (df["MERCATO"].str.upper() + "_"
              + df["DATA"].dt.strftime("%d/%m/%Y"))

    # .map al posto del for idx ... df[col][idx] = ...  (più veloce e niente warning)
    df["NUMERO VOLONTARI"] = chiave.map(dizionarioVolontari).fillna(0).astype(int)
    df["NUMERO BENEFICIARI"] = chiave.map(dizionarioBeneficiari).fillna(0).astype(int)

    # colonne calendario
    df["ANNO"] = df["DATA"].dt.year
    df["MESE_NUM"] = df["DATA"].dt.month
    df["MESE"] = pd.Categorical(
        df["MESE_NUM"].map(MAPPA_MESI), categories=ORDINE_MESI, ordered=True
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4. Entry point unico
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600, show_spinner="Carico i dati dei mercati…")
def load_all() -> dict:
    """
    Carica e prepara TUTTO. Restituisce un dict con:
      df, df_Form, df_2026, dizionarioVolontari, dizionarioBeneficiari
    Chiamala una volta a inizio pagina.
    """
    df_raw, df_2026 = _read_recuperi()
    df_Form = _read_form()
    dizVol, dizBen = _costruisci_dizionari(df_2026, df_Form)
    df = _arricchisci_df(df_raw, dizVol, dizBen)

    return {
        "df": df,
        "df_Form": df_Form,
        "df_2026": df_2026,
        "dizionarioVolontari": dizVol,
        "dizionarioBeneficiari": dizBen,
    }
