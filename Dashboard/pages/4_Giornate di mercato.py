import plotly.express as px
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "filters",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'components', 'filters.py'))
)
filters = importlib.util.module_from_spec(spec)
spec.loader.exec_module(filters)
get_filter_anno = filters.get_filter_anno
render_filter_mese = filters.render_filter_mese
get_filter_mese = filters.get_filter_mese
render_filter_data = filters.render_filter_data
get_filter_giorni = filters.get_filter_giorni

spec = importlib.util.spec_from_file_location(
    "Anno",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils', 'filtro_anno.py'))
)
Anno = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Anno)
filtra_df_anno = Anno.filtra_df

spec = importlib.util.spec_from_file_location(
    "Mese",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils', 'filtro_mese.py'))
)
Mese = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Mese)
filtra_df_mese = Mese.filtra_df

spec = importlib.util.spec_from_file_location(
    "Giorno",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils', 'filtro_giorno.py'))
)
Giorno = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Giorno)
filtra_df_giorno = Giorno.filtra_df

spec_dl = importlib.util.spec_from_file_location(
    "data_loader",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'components', 'data_loader.py'))
)
data_loader = importlib.util.module_from_spec(spec_dl)
spec_dl.loader.exec_module(data_loader)
GIORNATE_DI_MERCATO = data_loader.GIORNATE_DI_MERCATO

spec_st = importlib.util.spec_from_file_location(
    "styles",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'components', 'styles.py'))
)
styles = importlib.util.module_from_spec(spec_st)
spec_st.loader.exec_module(styles)
inietta_css = styles.inietta_css


def comprimi_altro(serie_kg, soglia_pct=1.5):
    tot = serie_kg.sum()
    if tot == 0:
        out = serie_kg.reset_index()
        out.columns = ["ITEM", "KG"]
        return out
    pct = serie_kg / tot * 100
    sopra = serie_kg[pct >= soglia_pct]
    resto = serie_kg[pct < soglia_pct].sum()
    out = sopra.reset_index()
    out.columns = ["ITEM", "KG"]
    if resto > 0:
        out = pd.concat([out, pd.DataFrame([{"ITEM": "Altro", "KG": resto}])], ignore_index=True)
    return out


# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Giornate di mercato", page_icon="📅", layout="wide")
inietta_css()

data = data_loader.load_all()
df = data["df"].copy()
dizionarioVolontari = data["dizionarioVolontari"]
dizionarioBeneficiari = data["dizionarioBeneficiari"]
anni_disponibili = df["ANNO"].unique().astype(int).tolist()


mesario = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]

# ─── filtri a cascata anno → mese → giorno ───────────────────────────────────
filtroAnno = get_filter_anno()
df = filtra_df_anno(df, filtroAnno)

render_filter_mese()
filtroMese = get_filter_mese()
df = filtra_df_mese(df, filtroMese)

df["DATA ESTESA"] = df["DATA"].dt.strftime('%d/%m/%Y')
df["DATA"] = df["DATA"].dt.day
date_disponibili = list(dict.fromkeys(df["DATA"].tolist()))
date_selezionate = render_filter_data(date_disponibili)
filtroGiorni = get_filter_giorni()

if not filtroGiorni["DATA"]:
    st.markdown(f"""
    <h1 style='margin-bottom:0;'>📅 {filtroMese["MESE"]} {filtroAnno["ANNO"]}</h1>
    """, unsafe_allow_html=True)
    st.info("📆 Seleziona almeno una data")
    st.stop()

df = filtra_df_giorno(df, filtroGiorni)


st.markdown(f"""
<h1 style='margin-bottom:0;'>📅 {filtroMese["MESE"]} {filtroAnno["ANNO"]}</h1>
""", unsafe_allow_html=True)

tabconfrontomercatigiornate, tabfocusalimentigiornate = st.tabs(["Focus Totali", "Focus Mercati"])

df["DATA"] = pd.to_datetime(df["DATA ESTESA"], dayfirst=True, errors="coerce")

df_selection = df
totali = (
    df_selection.drop(columns=["DATA", "MESE", "ANNO"], errors="ignore")
    .groupby("MERCATO")["KG"].sum()
)

# ═════════════════════════════════════════════════════════════════════════════
if totali.empty:
    st.subheader("Seleziona una data")
else:
    massimo_recupero = round(max(totali.values))
    massimo_mercato = totali.idxmax()
    totale_giorno = round(df_selection["KG"].sum())

    sommavolontari, sommaBeneficiario = 0, 0
    volontari, beneficiari = False, False
    for merc in df_selection["MERCATO"].unique().tolist():
        for giornata in df_selection["DATA ESTESA"].unique().tolist():
            chiave = merc + "_" + giornata
            if chiave in dizionarioVolontari:
                volontari = True
                sommavolontari += dizionarioVolontari[chiave]
            if chiave in dizionarioBeneficiari:
                beneficiari = True
                sommaBeneficiario += dizionarioBeneficiari[chiave]
    if not volontari:
        sommavolontari = "Na"
    if not beneficiari:
        sommaBeneficiario = "Na"

    # ═══════════════════════ TAB 1 — FOCUS TOTALI ═══════════════════════════
    with tabconfrontomercatigiornate:
        col2, col3, col4, col5, col6 = st.columns(5)
        with col2:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🍲</div>
                <div class="kpi-title">Kg recuperati</div>
                <div class="kpi-value">{totale_giorno}</div></div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">👥</div>
                <div class="kpi-title">Volontari totali</div>
                <div class="kpi-value">{sommavolontari}</div></div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🤝</div>
                <div class="kpi-title">Beneficiari totali</div>
                <div class="kpi-value">{sommaBeneficiario}</div></div>""", unsafe_allow_html=True)
        with col5:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🥇</div>
                <div class="kpi-title">Mercato con più recupero</div>
                <div class="kpi-value" style="font-size:1.4rem;">{massimo_mercato}</div></div>""", unsafe_allow_html=True)
        with col6:
            st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🌱</div>
                <div class="kpi-title">Kg recupero massimo singolo mercato</div>
                <div class="kpi-value">{massimo_recupero}</div></div>""", unsafe_allow_html=True)

        # --- bar orizzontale: kg per mercato ---
        df_bar = totali.sort_values().reset_index()
        figBarMercati = px.bar(
            df_bar, x="KG", y="MERCATO", orientation="h",
            text=df_bar["KG"].round(0).astype(int).astype(str) + " kg",
            color_discrete_sequence=["#0083B8"] * len(df_bar),
            template="plotly_white",
        )
        figBarMercati.update_traces(textposition="outside", cliponaxis=False)
        figBarMercati.update_layout(
            title=dict(text="<b>Cibo recuperato per mercato</b>", x=0.02, xanchor="left",
                       font=dict(size=24, family="Inter, Arial, sans-serif", color="#EAEAEA")),
            margin=dict(l=200, r=90, t=80, b=60),
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, title="Kg"),
            yaxis=dict(categoryorder="total ascending", showgrid=False, automargin=True, title=""),
            title_font_size=22, title_x=0.5, title_xanchor="center",
        )
        st.plotly_chart(figBarMercati, use_container_width=True, theme=None)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- TOP alimenti aggregati (senza "Altro": top 20, coda tagliata) ---
        TOP_N = 20
        df_item = (
            df_selection.drop(columns=["DATA", "MESE", "ANNO"], errors="ignore")
            .groupby("ITEM")["KG"].sum()
            .sort_values(ascending=False)
            .head(TOP_N)
            .reset_index()
        )
        figItem = px.bar(
            df_item.sort_values("KG"),
            x="KG", y="ITEM", orientation="h",
            text=df_item.sort_values("KG")["KG"].round(0).astype(int).astype(str) + " kg",
            color_discrete_sequence=["#00b478"] * len(df_item),
            template="plotly_white",
        )
        figItem.update_traces(textposition="outside", cliponaxis=False)
        figItem.update_layout(
            title=dict(text=f"<b>Cosa si è recuperato di più (top {TOP_N})</b>", x=0.3, xanchor="left",
                       font=dict(size=24, family="Inter, Arial, sans-serif", color="#EAEAEA")),
            height=620, margin=dict(l=200, r=90, t=70, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Kg", showgrid=False),
            yaxis=dict(title="", categoryorder="total ascending"),
        )
        st.plotly_chart(figItem, use_container_width=True, theme=None)

    # ═══════════════════════ TAB 2 — FOCUS MERCATI ══════════════════════════
    df_focus = df_selection.copy()

    with tabfocusalimentigiornate:
        mercati_giornata = sorted(df_focus["MERCATO"].unique().tolist())
        if not mercati_giornata:
            st.info("Nessun mercato nella selezione corrente.")
        else:
            merc = st.selectbox("🏘️ Scegli il mercato", mercati_giornata, key="merc_focus")
            tabella = df_focus[df_focus["MERCATO"] == merc].copy().reset_index(drop=True)

            # volontari / beneficiari medi sulla giornata
            n_vol, n_ben, n_giorni = 0, 0, 0
            volontari, beneficiari = False, False
            for giornata in tabella["DATA ESTESA"].unique().tolist():
                n_giorni += 1
                chiave = merc + "_" + giornata
                if chiave in dizionarioVolontari:
                    volontari = True
                    n_vol += dizionarioVolontari[chiave]
                if chiave in dizionarioBeneficiari:
                    beneficiari = True
                    n_ben += dizionarioBeneficiari[chiave]

            totale_merc = round(tabella["KG"].sum())
            n_vol_medio = round(n_vol / n_giorni) if n_giorni else 0
            n_ben_medio = round(n_ben / n_giorni) if n_giorni else 0
            media_cibo_volontario = round(totale_merc / n_vol_medio) if (volontari and n_vol_medio) else "Na"
            if not volontari:
                n_vol_medio = "Na"
                media_cibo_volontario = "Na"
            if not beneficiari:
                n_ben_medio = "Na"

            # aggrega per item e comprimi gli item marginali
            serie = (
                tabella.drop(columns=["DATA", "MESE", "ANNO"], errors="ignore")
                .groupby("ITEM")["KG"].sum().sort_values(ascending=False)
            )
            alimento_top = serie.index[0]
            top = comprimi_altro(serie, soglia_pct=1.5)

            # ===== KPI ROW =====
            col2, col3, col4, col5, col6 = st.columns(5)
            with col2:
                st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🍲</div>
                    <div class="kpi-title">Kg recuperati</div>
                    <div class="kpi-value">{totale_merc}</div></div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">👥</div>
                    <div class="kpi-title">Volontari medi</div>
                    <div class="kpi-value">{n_vol_medio}</div></div>""", unsafe_allow_html=True)
            with col4:
                st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🤝</div>
                    <div class="kpi-title">Beneficiari medi</div>
                    <div class="kpi-value">{n_ben_medio}</div></div>""", unsafe_allow_html=True)
            with col5:
                st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">💪</div>
                    <div class="kpi-title">Kg Medi per volontario</div>
                    <div class="kpi-value">{media_cibo_volontario}</div></div>""", unsafe_allow_html=True)
            with col6:
                st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">🌱</div>
                    <div class="kpi-title">Alimento più recuperato</div>
                    <div class="kpi-value" style="font-size:1.4rem;">{alimento_top}</div></div>""", unsafe_allow_html=True)

            # ===== BAR alimenti: "Altro" grigio e sempre in fondo =====
            tot = top["KG"].sum()
            top["pct"] = top["KG"] / tot * 100

            # ordina per KG, ma forza "Altro" in fondo (in basso sull'asse y)
            senza_altro = top[top["ITEM"] != "Altro"].sort_values("KG")
            altro_row = top[top["ITEM"] == "Altro"]
            top_ord = pd.concat([altro_row, senza_altro], ignore_index=True)

            colori = ["#9aa0a6" if i == "Altro" else "#00b478" for i in top_ord["ITEM"]]

            figItem = px.bar(
                top_ord, x="KG", y="ITEM", orientation="h",
                text=top_ord.apply(lambda r: f"{r['KG']:.0f} kg ({r['pct']:.0f}%)", axis=1),
                template="plotly_white",
            )
            figItem.update_traces(textposition="outside", cliponaxis=False, marker_color=colori)
            figItem.update_layout(
                title=dict(text=f"<b>Composizione · {merc}</b>", x=0.3, xanchor="left",
                           font=dict(size=22, family="Inter, Arial, sans-serif", color="#EAEAEA")),
                height=460, margin=dict(l=140, r=120, t=70, b=40),
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(title="Kg", showgrid=False),
                yaxis=dict(title="", categoryorder="array", categoryarray=top_ord["ITEM"].tolist()),
            )
            st.plotly_chart(figItem, use_container_width=True, theme=None)
            st.divider()