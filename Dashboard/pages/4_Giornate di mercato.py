from google.oauth2 import service_account
import gspread
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
render_filter_anno = filters.render_filter_anno
get_filter_anno = filters.get_filter_anno
render_filter_mese = filters.render_filter_mese
get_filter_mese = filters.get_filter_mese
render_filter_data = filters.render_filter_data
get_filter_giorni = filters.get_filter_giorni

#importo utils\filtri
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

st.set_page_config(page_title="Giornate di mercato",
                   page_icon="📅",
                   layout="wide")

df = st.session_state["df"].copy()
anni_disponibili = df["ANNO"].unique().astype(int).tolist()
df_Form = st.session_state["df_Form"].copy()
dizionarioVolontari = st.session_state["dizionarioVolontari"].copy()
dizionarioBeneficiari = st.session_state["dizionarioBeneficiari"].copy()

if "anno" not in st.session_state:
    st.session_state["Anno_selezionato"] = 2026
else:
    Anno_selezionato = st.session_state["Anno_selezionato"]
#filtri
render_filter_anno(anni_disponibili)
filtroAnno = get_filter_anno()
df = filtra_df_anno(df, filtroAnno)
render_filter_mese()
filtroMese = get_filter_mese()
filtroGiorni = get_filter_giorni()
df = filtra_df_mese(df, filtroMese)
df["DATA ESTESA"] = df["DATA"].dt.strftime('%d/%m/%Y')
df["DATA"]= df["DATA"].dt.day
date_disponibili = list(dict.fromkeys(df["DATA"].tolist()))
date_selezionate = render_filter_data(date_disponibili)
#st.write(date_selezionate)
filtroGiorni = get_filter_giorni()
df = filtra_df_giorno(df, filtroGiorni)

st.set_page_config(layout="wide")

mesario = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"
]

giornate_di_mercato = {
    "MOMPIANI" : 1,
    "MARTINI" : 2,
    "TERMOPILI" : 4,
    "CATONE" : 4,
    "GRAMSCI - SAN DONATO" : 4,
    "OGLIO" : 5,
    "VALVASSORI PERONI" : 5,
    "TABACCHI" : 5,
    "OSOPPO" : 5,
    "PAPINIANO" : 5,
    "BENEDETTO MARCELLO" : 5
}

st.markdown(f"""
<h1 style='margin-bottom:0;'>📅 {filtroMese["MESE"]} {filtroAnno["ANNO"]}</h1>
""", unsafe_allow_html=True)
tabconfrontomercatigiornate, tabfocusalimentigiornate = st.tabs(["Focus Totali", "Focus Mercati"])

df_Form["Data del Mercato"] = pd.to_datetime(df_Form["Data del Mercato"], dayfirst=True, errors="coerce")
df_form_2025 = df_Form[df_Form["Data del Mercato"].dt.year == 2025]
df_form_2025 = df_form_2025.reset_index(drop=True)

idx = 0
df["DATA"] = pd.to_datetime(df["DATA"],  format="mixed", dayfirst=True, errors="coerce")

item = df["ITEM"].unique()

df_media_mercati_2025 = df
df_media_mercati_2025["SETTIMANA"] = df_media_mercati_2025["DATA"].dt.to_period("W").dt.start_time
#df["SETTIMANA"] = df["DATA"] - df["MERCATO"].map(giornate_di_mercato).apply(lambda x: pd.Timedelta(days=x))
df_media_mercati_2025 = (
    (df_media_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby("SETTIMANA")[
        "KG"].mean()).reset_index()
df = df.drop(columns=["SETTIMANA"])
df_std_mercati_2025 = df
df_std_mercati_2025["SETTIMANA"] = df_std_mercati_2025["DATA"].dt.to_period("W").dt.start_time
df_std_mercati_2025 = (
    (df_std_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby("SETTIMANA")[
        "KG"].std()).reset_index()
df = df.drop(columns=["SETTIMANA"])

df_selection = df
df_selection_altro = df_selection.copy()
df_selection_altro.loc[df_selection_altro["KG"] < 2, "ITEM"] = "Altro"
df_grafico_mercato_selezionato_alimenti = df_selection_altro.drop(columns=["DATA"])
df_grafico_mercato_selezionato_alimenti = (
    df_grafico_mercato_selezionato_alimenti.drop(columns=["MESE", "ANNO"]).groupby(by=["MERCATO", "ITEM"])
    .sum()[["KG"]]
    .reset_index()
    .fillna(0)
)
totali = df_grafico_mercato_selezionato_alimenti.groupby("MERCATO")["KG"].sum()
if totali.empty:
    st.subheader("Seleziona una data")
else:
    massimo_recupero = round(max(totali.values),2)
    massimo_mercato = totali.idxmax()
    numero_giorni = len(df_selection["DATA"].unique())
    volontari = False
    beneficiari = False
    sommavolontari = 0
    sommaBeneficiario = 0
    for mercatomercato in df_selection["MERCATO"].unique().tolist():
        for giornatamercato in df_selection["DATA ESTESA"].unique().tolist():
            chiave = mercatomercato + "_" + giornatamercato
            #st.write(chiave)
            if chiave in dizionarioVolontari:
                volontari = True
                sommavolontari = sommavolontari + dizionarioVolontari[chiave]
            if chiave in dizionarioBeneficiari:
                beneficiari = True
                sommaBeneficiario = sommaBeneficiario + dizionarioBeneficiari[chiave]
    if not volontari:
        sommavolontari = "Na"
    if not beneficiari:
        sommaBeneficiario = "Na"
    totale_giorno = round(df_selection["KG"].sum(),2)

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

    with tabconfrontomercatigiornate:
        st.markdown("""
                        <style>
                   @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=Space+Grotesk:wght@700&display=swap');
                    .kpi-card {
                        background: linear-gradient(135deg, #0d1f1a 0%, #0a1a14 100%);
                        border: 1px solid #1a3a2a;
                        padding: 1.2rem 2rem;
                        border-radius: 16px;
                        text-align: center;
                        max-width: 680px;
                        font-family: 'DM Sans', sans-serif;
                    }
                    .kpi-title {
                        color: #8a9ba8;
                        font-size: 0.9rem;         
                        letter-spacing: 0.1em;
                        text-transform: uppercase;
                        margin-bottom: 0.3rem;
                        font-family: 'DM Sans', sans-serif;
                        font-weight: 400;
                    }
                    .kpi-value {
                        color: #ffea00;
                        font-size: 1.2rem;
                        font-weight: 700;
                        line-height: 1;
                        font-family: 'Space Grotesk', sans-serif;
                    }
                    .kpi-icon {
                        font-size: 2rem;
                        line-height: 1;
                        margin-bottom: 0.3rem;
                    }

                        </style>
                        """, unsafe_allow_html=True)
        col2, col3, col4, col5, col6 = st.columns(5)

        with col2:
            st.markdown(f"""
                            <div class="kpi-card">
                                <div class="kpi-icon">🍲</div>
                                <div class="kpi-title">Kg recuperati</div>
                                <div class="kpi-value">{totale_giorno}</div>
                            </div>
                            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                             <div class="kpi-card">
                                 <div class="kpi-icon">👥</div>
                                 <div class="kpi-title">Volontari totali</div>
                                 <div class="kpi-value">{sommavolontari}</div>
                             </div>
                             """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                             <div class="kpi-card">
                                 <div class="kpi-icon">🤝</div>
                                 <div class="kpi-title">Beneficiari totali</div>
                                 <div class="kpi-value">{sommaBeneficiario}</div>
                             </div>
                             """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
                            <div class="kpi-card">
                                <div class="kpi-icon">🥇</div>
                                <div class="kpi-title">Mercato con più recupero</div>
                                <div class="kpi-value">{massimo_mercato}</div>
                            </div>
                            """, unsafe_allow_html=True)

        with col6:
            st.markdown(f"""
                            <div class="kpi-card">
                                <div class="kpi-icon">🌱</div>
                                <div class="kpi-title">Recupero massimo singolo mercato</div>
                                <div class="kpi-value">{massimo_recupero} kg</div>
                            </div>
                            """, unsafe_allow_html=True)
        df_grafico_mercato_selezionato_alimenti = df_selection_altro.drop(columns=["DATA"])
        df_grafico_mercato_selezionato_alimenti = (
            df_grafico_mercato_selezionato_alimenti.drop(columns=["MESE", "ANNO"]).groupby(by=["MERCATO", "ITEM"])
            .sum()[["KG"]]
            .reset_index()
            .fillna(0)
        )
        df_grafico_mercato_selezionato = df_selection_altro.drop(columns=["DATA"])
        df_grafico_mercato_selezionato = (
            df_grafico_mercato_selezionato_alimenti.groupby(by=["MERCATO"])
            .sum()[["KG"]]
            .reset_index()
            .fillna(0)
        )
        figBarMercati = px.bar(
            df_grafico_mercato_selezionato,
            x="KG",
            y=df_grafico_mercato_selezionato["MERCATO"],
            title=f"<b>Cibo raccolto per mercato</b>",
            color_discrete_sequence=["#0083B8"] * len(df_grafico_mercato_selezionato_alimenti),
            template="plotly_white",
            hover_data=["MERCATO", "KG"],
            orientation="h",
        )
        figBarMercati.update_layout(
            title=dict(
                text=f"<b>Cibo recuperato per mercato</b>",
                x=0.02,
                xanchor="left",
                font=dict(
                    size=24,
                    family="Inter, Arial, sans-serif",
                    color="#EAEAEA"
                )
            ),
            margin=dict(l=200, r=40, t=80, b=60),
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=(dict(showgrid=False)),
            yaxis=dict(
                categoryorder="total ascending",
                #tickmode="linear",
                showgrid=False,
                automargin=False
            ),
        title_font_size = 18,
        title_x = 0.5,
        title_xanchor = "center",
        )
        figBarMercati.add_trace(go.Scatter(
            x=totali.values,
            y=totali.index,
            mode="text",
            text=[f"{v:.0f} kg" for v in totali.values],
            textposition="middle right",
            showlegend=False
        ))
        figBarMercati.update_yaxes(title_standoff=20)
        st.plotly_chart(figBarMercati, use_container_width=True, theme=None)
        palette = [
            "#4C78A8",  # blu,
            "#FFBC79",  # pesca
            "#59A14F",  # verde più profondo
            "#F58518",  # arancio
            "#54A24B",  # verde
            "#E45756",  # rosso soft
            "#72B7B2",  # teal
            "#B279A2",  # viola polveroso
            "#FF9DA6",  # rosa soft
            "#9D755D",  # marrone elegante
            "#BAB0AC",  # grigio caldo
            "#2E91E5",  # blu brillante controllato
        ],
        mercati = df["MERCATO"].unique()
        color_map = dict(zip(mercati, palette))
        st.markdown("<br><br>", unsafe_allow_html=True)
        numero_giorni = len(df_selection["DATA"].unique())
        figTreeAlimenti = px.treemap(
            df_grafico_mercato_selezionato_alimenti,
            path=[px.Constant("ALL"),"MERCATO", "ITEM"],  # gerarchia
            values="KG",
            color="MERCATO",
            #color_discrete_map=color_map,
            title="<b>Composizione del cibo recuperato per mercato (Kg)</b>"
        )
        figTreeAlimenti.update_traces(
            root_color="lightgrey",
            hovertemplate=
                "<b>%{label}</b><br>" +  # ITEM
                "Mercato: %{parent}<br>" +
                "Kg: %{value:.0f}<br>" +
                "Percentuale: %{percentParent:.1%}<br>" +
                "<extra></extra>",
            marker=dict(
                line=dict(width=1, color="rgba(255,255,255,0.15)")
            )
        )
        figTreeAlimenti.update_layout(
            title=dict(
                text=f"<b>Composizione del cibo recuperato per mercato</b>",
                x=0.02,
                xanchor="left",
                font=dict(
                    size=24,
                    family="Inter, Arial, sans-serif",
                    color="#EAEAEA"
                )
            ),
            height=650,
            margin=dict(t=40, l=10, r=10, b=10),
            template="plotly_white",
            title_font_size=18,
            title_x=0.5,
            title_xanchor="center",
        )

        st.plotly_chart(figTreeAlimenti, use_container_width=True, theme=None)

    df_selection_altro = df_selection.copy()
    df_selection_altro.loc[df_selection_altro["KG"] < 1, "ITEM"] = "Altro"

with tabfocusalimentigiornate:
    if date_selezionate in mesario:
        header = "Mese"
    else:
        header = "Giorno/i"
    for merc in df_selection_altro["MERCATO"].unique():
        st.markdown(f"## 📍Mercato: {merc}")
        tabella_mercato = df_selection_altro[df_selection_altro["MERCATO"] == merc].copy().reset_index(drop=True)
        numero_volontari_mercato_corrente = 0
        numero_beneficiari_mercato_corrente = 0
        numero_giorni_mercato_corrente = 0
        volontari = False
        beneficiari = False
        for mercatomercato in tabella_mercato["MERCATO"].unique().tolist():
            for giornatamercato in tabella_mercato["DATA ESTESA"].unique().tolist():
                numero_giorni_mercato_corrente = numero_giorni_mercato_corrente + 1
                chiave = mercatomercato + "_" + giornatamercato
                if chiave in dizionarioVolontari:
                    volontari = True
                    numero_volontari_mercato_corrente = numero_volontari_mercato_corrente + dizionarioVolontari[chiave]
                if chiave in dizionarioBeneficiari:
                    beneficiari = True
                    numero_beneficiari_mercato_corrente = numero_beneficiari_mercato_corrente + dizionarioBeneficiari[chiave]
        numero_volontari_mercato_corrente = round(numero_volontari_mercato_corrente/numero_giorni_mercato_corrente)
        numero_beneficiari_mercato_corrente = round(numero_beneficiari_mercato_corrente/numero_giorni_mercato_corrente)
        totale_giorno_mercato_corrente = round(tabella_mercato["KG"].sum(), 1)
        media_cibo_volontario = round(totale_giorno_mercato_corrente / numero_volontari_mercato_corrente, 1)
        if not volontari:
            numero_volontari_mercato_corrente = "Na"
            media_cibo_volontario = "Na"
        if not beneficiari:
            numero_beneficiari_mercato_corrente = "Na"
            media_cibo_volontario = "Na"
        data_mercato_corrente = tabella_mercato["DATA"].iloc[0].strftime("%d/%m/%Y")
        chiave = merc  + "_" + data_mercato_corrente
        tabella_mercato = (tabella_mercato.drop(columns=["DATA", "MESE", "ANNO"])).groupby("ITEM").sum()[["KG"]].reset_index()
        alimento_pi_recuperato = tabella_mercato["ITEM"].iloc[tabella_mercato["KG"].idxmax()]

        col2, col3, col4, col5, col6 = st.columns(5)

        with col2:
            st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-icon">🍲</div>
                        <div class="kpi-title">Kg recuperati</div>
                        <div class="kpi-value">{totale_giorno_mercato_corrente}</div>
                    </div>
                    """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                     <div class="kpi-card">
                         <div class="kpi-icon">👥</div>
                         <div class="kpi-title">Volontari medi</div>
                         <div class="kpi-value">{numero_volontari_mercato_corrente}</div>
                     </div>
                     """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                     <div class="kpi-card">
                         <div class="kpi-icon">🤝</div>
                         <div class="kpi-title">Beneficiari medi</div>
                         <div class="kpi-value">{numero_beneficiari_mercato_corrente}</div>
                     </div>
                     """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-icon">💪</div>
                        <div class="kpi-title">Media per volontario</div>
                        <div class="kpi-value">{media_cibo_volontario} kg</div>
                    </div>
                    """, unsafe_allow_html=True)

        with col6:
            st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-icon">🌱</div>
                        <div class="kpi-title">Alimento più recuperato</div>
                        <div class="kpi-value">{alimento_pi_recuperato}</div>
                    </div>
                    """, unsafe_allow_html=True)
        grafico_mercato_selezionato_alimenti = go.Figure(
            data=[go.Pie(labels=tabella_mercato["ITEM"], values=tabella_mercato["KG"], hole=0.3)])
        grafico_mercato_selezionato_alimenti.update_layout(
            title=dict(
                text=f"<b>Composizione del cibo recuperato</b>",
                x=0.02,
                xanchor="left",
                font=dict(
                    size=24,
                    family="Inter, Arial, sans-serif",
                    color="#EAEAEA"
                )
            ),
            height=480,
            margin=dict(t=50, l=20, r=20, b=20),
            template="plotly_white",
            title_font_size=18,
            title_x=0.47,
            title_xanchor="center",
        )
        st.plotly_chart(grafico_mercato_selezionato_alimenti)

        st.divider()

st.sidebar.text("Made with ❤ by Recup")




