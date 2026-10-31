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


# ─── helper ──────────────────────────────────────────────────────────────────
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


def valore_da_dizionario(dizionario, mercato, giornata):
    """Restituisce il numero per la coppia mercato×giornata, o None se manca/non è valido."""
    v = dizionario.get(f"{mercato}_{giornata}")
    if v is None or pd.isna(v):
        return None
    return v


def somma_da_dizionario(dizionario, mercati, giornate):
    """Somma i valori trovati. Restituisce (totale, quante_giornate_avevano_il_dato)."""
    totale, trovati = 0, 0
    for m in mercati:
        for g in giornate:
            v = valore_da_dizionario(dizionario, m, g)
            if v is not None:
                totale += v
                trovati += 1
    return totale, trovati


def kpi_card(icona, titolo, valore, piccolo=False):
    """Card KPI. Se valore è None mostra 'n.d.' in grigio invece di un numero."""
    if valore is None:
        valore_html = '<div class="kpi-value" style="font-size:1.6rem;color:#8a9ba8;">n.d.</div>'
    else:
        stile = ' style="font-size:1.4rem;"' if piccolo else ""
        valore_html = f'<div class="kpi-value"{stile}>{valore}</div>'
    st.markdown(f"""<div class="kpi-card"><div class="kpi-icon">{icona}</div>
        <div class="kpi-title">{titolo}</div>{valore_html}</div>""", unsafe_allow_html=True)


AVVISO_ND = ("ℹ️ Numero di volontari e beneficiari non disponibile per il periodo "
             "selezionato: le card mostrano **n.d.** (non disponibile).")


# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Giornate di mercato", page_icon="📅", layout="wide")
inietta_css()

data = data_loader.load_all()
df = data["df"].copy()
# .get(..., {}) → se il loader non restituisce i dizionari, si usano dizionari vuoti
dizionarioVolontari = data.get("dizionarioVolontari") or {}
dizionarioBeneficiari = data.get("dizionarioBeneficiari") or {}

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

st.markdown(f"""
<h1 style='margin-bottom:0;'>📅 {filtroMese["MESE"]} {filtroAnno["ANNO"]}</h1>
""", unsafe_allow_html=True)

if not filtroGiorni["DATA"]:
    st.info("📆 Seleziona almeno una data")
    st.stop()

df = filtra_df_giorno(df, filtroGiorni)
df["DATA"] = pd.to_datetime(df["DATA ESTESA"], dayfirst=True, errors="coerce")
df_selection = df

totali = (
    df_selection.drop(columns=["DATA", "MESE", "ANNO"], errors="ignore")
    .groupby("MERCATO")["KG"].sum()
)

if totali.empty:
    st.info("Nessun recupero nelle date selezionate.")
    st.stop()

tabconfrontomercatigiornate, tabfocusalimentigiornate = st.tabs(["Focus Totali", "Focus Mercati"])

massimo_recupero = round(max(totali.values))
massimo_mercato = totali.idxmax()
totale_giorno = round(df_selection["KG"].sum())

mercati_sel = df_selection["MERCATO"].unique().tolist()
giornate_sel = df_selection["DATA ESTESA"].unique().tolist()

vol_tot, vol_trovati = somma_da_dizionario(dizionarioVolontari, mercati_sel, giornate_sel)
ben_tot, ben_trovati = somma_da_dizionario(dizionarioBeneficiari, mercati_sel, giornate_sel)

# None = dato assente → la card mostrerà "n.d."
sommavolontari = int(vol_tot) if vol_trovati else None
sommaBeneficiario = int(ben_tot) if ben_trovati else None

# ═══════════════════════ TAB 1 — FOCUS TOTALI ═══════════════════════════════
with tabconfrontomercatigiornate:
    if sommavolontari is None and sommaBeneficiario is None:
        st.caption(AVVISO_ND)

    col2, col3, col4, col5, col6 = st.columns(5)
    with col2:
        kpi_card("🍲", "Kg recuperati", totale_giorno)
    with col3:
        kpi_card("👥", "Volontari totali", sommavolontari)
    with col4:
        kpi_card("🤝", "Beneficiari totali", sommaBeneficiario)
    with col5:
        kpi_card("🥇", "Mercato con più recupero", massimo_mercato, piccolo=True)
    with col6:
        kpi_card("🌱", "Kg recupero massimo singolo mercato", massimo_recupero)

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

    # --- TOP alimenti aggregati (top 20, coda tagliata) ---
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

# ═══════════════════════ TAB 2 — FOCUS MERCATI ══════════════════════════════
with tabfocusalimentigiornate:
    mercati_giornata = sorted(mercati_sel)
    merc = st.selectbox("🏘️ Scegli il mercato", mercati_giornata, key="merc_focus")
    tabella = df_selection[df_selection["MERCATO"] == merc].copy().reset_index(drop=True)

    totale_merc = round(tabella["KG"].sum())
    kg_per_giorno = tabella.groupby("DATA ESTESA")["KG"].sum()

    # volontari/beneficiari: si contano SOLO le giornate che hanno il dato,
    # così una giornata senza dato non abbassa la media
    vol_per_giorno = {g: valore_da_dizionario(dizionarioVolontari, merc, g) for g in kg_per_giorno.index}
    ben_per_giorno = {g: valore_da_dizionario(dizionarioBeneficiari, merc, g) for g in kg_per_giorno.index}
    giorni_con_vol = [g for g, v in vol_per_giorno.items() if v is not None]
    giorni_con_ben = [g for g, v in ben_per_giorno.items() if v is not None]

    n_vol_medio = round(sum(vol_per_giorno[g] for g in giorni_con_vol) / len(giorni_con_vol)) \
        if giorni_con_vol else None
    n_ben_medio = round(sum(ben_per_giorno[g] for g in giorni_con_ben) / len(giorni_con_ben)) \
        if giorni_con_ben else None

    # kg per volontario: kg delle sole giornate con dato ÷ volontari di quelle giornate
    volontari_somma = sum(vol_per_giorno[g] for g in giorni_con_vol)
    media_cibo_volontario = round(kg_per_giorno[giorni_con_vol].sum() / volontari_somma) \
        if giorni_con_vol and volontari_somma > 0 else None

    if n_vol_medio is None and n_ben_medio is None:
        st.caption(AVVISO_ND)

    # aggrega per item e comprimi gli item marginali
    serie = (
        tabella.drop(columns=["DATA", "MESE", "ANNO"], errors="ignore")
        .groupby("ITEM")["KG"].sum().sort_values(ascending=False)
    )
    alimento_top = serie.index[0] if not serie.empty else None
    top = comprimi_altro(serie, soglia_pct=1.5)

    # ===== KPI ROW =====
    col2, col3, col4, col5, col6 = st.columns(5)
    with col2:
        kpi_card("🍲", "Kg recuperati", totale_merc)
    with col3:
        kpi_card("👥", "Volontari medi", n_vol_medio)
    with col4:
        kpi_card("🤝", "Beneficiari medi", n_ben_medio)
    with col5:
        kpi_card("💪", "Kg medi per volontario", media_cibo_volontario)
    with col6:
        kpi_card("🌱", "Alimento più recuperato", alimento_top, piccolo=True)

    # ===== BAR alimenti: "Altro" grigio e sempre in fondo =====
    if not top.empty:
        tot = top["KG"].sum()
        top["pct"] = top["KG"] / tot * 100

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
