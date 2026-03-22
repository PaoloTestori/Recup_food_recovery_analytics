import gspread
import numpy as np
from google.oauth2 import service_account
from sklearn.metrics import r2_score
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#importo components
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

#importo utils\filtro_anno.py
spec = importlib.util.spec_from_file_location(
    "Anno",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils', 'filtro_anno.py'))
)
Anno = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Anno)
filtra_df_anno = Anno.filtra_df


st.set_page_config(page_title="Mercati Milano",
                   page_icon="📍",
                   layout="wide")

df = st.session_state["df"].copy()
anni_disponibili = df["ANNO"].unique().astype(int).tolist()
df_Form = st.session_state["df_Form"].copy()
dizionarioVolontari = st.session_state["dizionarioVolontari"].copy()
dizionarioBeneficiari = st.session_state["dizionarioBeneficiari"].copy()
Anno_selezionato = st.session_state["Anno_selezionato"]
#filtri
render_filter_anno(anni_disponibili)
filtroAnno = get_filter_anno()
df = filtra_df_anno(df, filtroAnno)
st.session_state["Anno_selezionato"] = Anno_selezionato

tabconfronti, tabanalisitemporali, tabvolontari = st.tabs(["Andamento Mercati", "Analisi Temporali","Andamento Volontari"])
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

st.sidebar.text("Made with ❤ by Recup")

# Percorso del file JSON del service account
#creds = service_account.Credentials.from_service_account_info(    st.secrets["gcp_service_account"])

# Apertura client
#client = gspread.authorize(creds)
#lettura file mercati 2025
#wbUrl = st.secrets["WEBHOOK_URL_MERCATI2025"]

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
    "BENEDETTO MARCELLO" : 5,
    "PADERNO DUGNANO" : 2
}

#df = pd.read_csv(filepath_or_buffer= wbUrl,header=0,usecols=[0,1,2,3],parse_dates=[0],skiprows=[1],)
#lettura file form google
#df_Form = pd.read_csv(filepath_or_buffer= st.secrets["WEBHOOK_URL_MERCATI_RISPOSTE"],usecols=[0,1,2,3,5,6],parse_dates=[1], skiprows=[0],)

df_Form["Data del Mercato"] = pd.to_datetime(df_Form["Data del Mercato"], dayfirst=True, errors="coerce")
df_form_2025 = df_Form[df_Form["Data del Mercato"].dt.year == 2025]
df_form_2025 = df_form_2025.reset_index(drop=True)
#gestione numero volontari
df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"] = df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"].str.replace(";", ",").str.replace(".", ",").str.replace("-",",").str.replace("/",",").str.replace(" e ",",")
df_form_2025["Numero volontari"] = 0
df_form_2025["Quantə beneficiariə? (inserisci un numero)"] = df_form_2025["Quantə beneficiariə? (inserisci un numero)"].replace("-",0)
#dizionarioVolontari = {}
#dizionarioBeneficiari = {}

#for idx, ben in df_form_2025["Quantə beneficiariə? (inserisci un numero)"].items():
#    if ben is "":
#        continue
#    dizionarioBeneficiari[str.upper(df_form_2025["Nome del Mercato"][idx]) + "_" + (
#        df_form_2025["Data del Mercato"][idx].strftime("%d/%m/%Y"))] = int(df_form_2025["Quantə beneficiariə? (inserisci un numero)"][idx])

#for idx, vol in df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"].items():
#    if vol is "No Data":
#        continue
#    if "," in vol:
#        listaVolontari = str.split(vol,",")
#        listaVolontari = list(filter(None, listaVolontari))
#        numeroVolontari = int(len(listaVolontari))
#        dizionarioVolontari[str.upper(df_form_2025["Nome del Mercato"][idx]) + "_" + (df_form_2025["Data del Mercato"][idx].strftime("%d/%m/%Y"))] = numeroVolontari
#    else:
#        vol = vol.replace(" de "," de_").replace(" di "," di_").replace(" del "," del_").replace(" da "," da_").replace(" dal ","dal_").replace(" lo ","lo_").replace(" la ","la_")
#        listaVolontari = str.split(vol, " ")
#        listaVolontari = list(filter(None, listaVolontari))
#        numeroVolontari = int(len(listaVolontari)/2)
#        dizionarioVolontari[str.upper(df_form_2025["Nome del Mercato"][idx]) + "_" + (df_form_2025["Data del Mercato"][idx].strftime("%d/%m/%Y"))] = numeroVolontari
idx = 0
df["DATA"] = pd.to_datetime(df["DATA"],  format="mixed", dayfirst=True, errors="coerce")
#df["KG"] = df["KG"].str.replace(",", ".",regex=False).astype(float)
df["Numero Volontari"] = 0
for idx, row in df.iterrows():
    df["Numero Volontari"][idx] = dizionarioVolontari[str.upper(df["MERCATO"][idx]) + "_" + df["DATA"][idx].strftime("%d/%m/%Y")]
df["Numero Beneficiari"] = 0
idx = 0
for idx, row in df.iterrows():
    df["Numero Beneficiari"][idx] = dizionarioBeneficiari[str.upper(df["MERCATO"][idx]) + "_" + df["DATA"][idx].strftime("%d/%m/%Y")]

df_media_mercati_2025 = df
df_media_mercati_2025["SETTIMANA"] = df_media_mercati_2025["DATA"].dt.to_period("W").dt.start_time
#df["SETTIMANA"] = df["DATA"] - df["MERCATO"].map(giornate_di_mercato).apply(lambda x: pd.Timedelta(days=x))
df_media_mercati_2025 = (
    (df_media_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby("SETTIMANA")[
        "KG"].mean()).reset_index()
df = df.drop(columns=["SETTIMANA"])
df_std_mercati_2025 = df
df_std_mercati_2025["SETTIMANA"] = df_std_mercati_2025["DATA"].dt.to_period("W").dt.start_time
#df["SETTIMANA"] = df["DATA"] - df["MERCATO"].map(giornate_di_mercato).apply(lambda x: pd.Timedelta(days=x))
df_std_mercati_2025 = (
    (df_std_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby("SETTIMANA")[
        "KG"].std()).reset_index()
df = df.drop(columns=["SETTIMANA"])

df_selection = df

df_volontari_mercato_selezionato = (
    df.groupby(by=["MERCATO", "DATA"])
    .first()[["Numero Volontari"]]
    .reset_index()
    .pivot(index="DATA", columns="MERCATO", values="Numero Volontari")
    .fillna(0)
)
df_beneficiari_mercato_selezionato = (
    df.groupby(by=["MERCATO", "DATA"])
    .first()[["Numero Beneficiari"]]
    .reset_index()
    .pivot(index="DATA", columns="MERCATO", values="Numero Beneficiari")
    .fillna(0)
)
#st.write(df)

with tabconfronti:
    df_grafico_mercato_selezionato = (
        df.drop(columns=["ANNO", "MESE"]).groupby(by=["MERCATO", "DATA"])
        .sum()[["KG"]]
        .reset_index()
        .pivot(index="DATA", columns="MERCATO", values="KG")
        .fillna(0)
    )
    df_grafico_mercato_selezionato = df_grafico_mercato_selezionato.reset_index()
    df_grafico_mercato_selezionato_raggruppato = df_grafico_mercato_selezionato.replace(0, pd.NA)
    df_grafico_mercato_selezionato_raggruppato["SETTIMANA"] = df_grafico_mercato_selezionato_raggruppato["DATA"].dt.to_period("W").dt.start_time
    df_grafico_mercato_selezionato_raggruppato = df_grafico_mercato_selezionato_raggruppato.groupby("SETTIMANA").first().reset_index()
    df_grafico_mercato_selezionato_raggruppato = df_grafico_mercato_selezionato_raggruppato.fillna(0)
    df_grafico_mercato_selezionato_raggruppato_drop = df_grafico_mercato_selezionato_raggruppato.drop(columns=["DATA"])
    with tabconfronti:
        for mercato in df_grafico_mercato_selezionato.columns:
            if mercato != "DATA":
                df_std_mercati_2025 = df_grafico_mercato_selezionato_raggruppato_drop.set_index("SETTIMANA").std(
                    axis=1).reset_index()
                df_media_mercati_2025 = df
                df_media_mercati_2025["SETTIMANA"] = df_media_mercati_2025["DATA"].dt.to_period("W").dt.start_time
                df_media_mercati_2025 = (
                    (df_media_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby(
                        "SETTIMANA")[
                        "KG"].mean()).reset_index()
                df = df.drop(columns=["SETTIMANA"])
                df_std_mercati_2025 = df
                df_std_mercati_2025["SETTIMANA"] = df_std_mercati_2025["DATA"].dt.to_period("W").dt.start_time
                df_std_mercati_2025 = (
                    (df_std_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby(
                        "SETTIMANA")[
                        "KG"].std()).reset_index()
                df = df.drop(columns=["SETTIMANA"])
                #st.title("🍌" + mercato)
                total_df = df.groupby("MERCATO")["KG"].sum().reset_index()
                total_dict = dict(zip(total_df["MERCATO"], total_df["KG"]))
                total =round(float(total_dict[mercato]), 2)
                #st.markdown(f"<p style='font-size:30px'><b>🥦 Nel 2025 a {mercato} abbiamo recuperato ben {total} KG </b></p>", unsafe_allow_html=True)
                fig = go.Figure()
                df_media_mercati_2025["SETTIMANA"] += pd.Timedelta(days=giornate_di_mercato[mercato])
                df_std_mercati_2025["SETTIMANA"] += pd.Timedelta(days=giornate_di_mercato[mercato])
                df_grafico_mercato_selezionato_filtrato = df_grafico_mercato_selezionato[df_grafico_mercato_selezionato["DATA"].dt.weekday == giornate_di_mercato[mercato]]
                media = round(float(df_grafico_mercato_selezionato_filtrato[mercato][df_grafico_mercato_selezionato_filtrato[mercato] != 0].mean()), 2)
                max_mercato = df_grafico_mercato_selezionato_filtrato[mercato].max()
                giorno_max_mercato = (df_grafico_mercato_selezionato_filtrato["DATA"][df_grafico_mercato_selezionato_filtrato[mercato].idxmax()]).date()
                #st.markdown(f"<p style='font-size:20px'><b>🥬 Il giorno in cui abbiamo recuperato di più è stato il {giorno_max_mercato} con {max_mercato} KG</b></p>", unsafe_allow_html=True)
                df_scostamento = df_grafico_mercato_selezionato_filtrato.merge(df_media_mercati_2025[["SETTIMANA", "KG"]], left_on="DATA", right_on="SETTIMANA", how="left")
                df_scostamento["Scostamento"] = ((df_scostamento[mercato]-df_scostamento["KG"])/df_scostamento["KG"])*100
                df_scostamento = df_scostamento.merge(df_std_mercati_2025[["SETTIMANA", "KG"]], left_on="DATA", right_on="SETTIMANA", how="left")
                df_scostamento["Zscore"] = (df_scostamento[mercato]-df_scostamento["KG_x"])/df_scostamento["KG_y"]
                df_std_mercati_2025["Upper"] = (df_media_mercati_2025["KG"] + df_std_mercati_2025["KG"]).fillna(0).interpolate(method="linear")
                df_std_mercati_2025["Lower"] = df_media_mercati_2025["KG"] - df_std_mercati_2025["KG"]

                st.markdown("""
                <style>
                .kpi-card {
                    background: #111;
                    padding: 16px 20px;
                    border-radius: 14px;
                    text-align: center;
                    box-shadow: 0 0 12px rgba(0,0,0,0.4);
                }
                .kpi-title {
                    font-size: 14px;
                    color: #bbbbbb;
                }
                .kpi-value {
                    font-size: 28px;
                    font-weight: 700;
                    color: #00ff9c;
                }
                .header-title {
                    font-size: 42px;
                    font-weight: 700;
                }
                .header-subtitle {
                    font-size: 18px;
                    color: #bbbbbb;
                }
                </style>
                """, unsafe_allow_html=True)
                # ===== HEADER =====
                st.markdown(f"""
                <div style="margin-bottom:20px;">
                  <div class="header-title">📍 {mercato}</div>
                  <div class="header-subtitle">📅 Anno 2025 — Analisi recupero</div>
                </div>
                """, unsafe_allow_html=True)

                # ===== KPI ROW =====
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">🌱 Totale recuperato</div>
                        <div class="kpi-value">{total} kg</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">📈 Giorno record</div>
                        <div class="kpi-value">{giorno_max_mercato}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">🔥 Kg nel giorno record</div>
                        <div class="kpi-value">{max_mercato}</div>
                    </div>
                    """, unsafe_allow_html=True)

                figSubplot = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.08,
                    subplot_titles=("KG recuperati vs Media mercati", "Z-score (scostamento standardizzato)")
                )
                # --- PANNELLO 1 ---
                figSubplot.add_trace(
                    go.Scatter(
                        x=df_grafico_mercato_selezionato_filtrato["DATA"],
                        y=df_grafico_mercato_selezionato_filtrato[mercato],
                        name=f"KG - {mercato}",
                        mode="lines",
                        hovertext=f"KG - {mercato}",
                        hovertemplate="Data: %{x}<br>Kg " + mercato + ": %{y}<extra></extra>"
                    ),
                    row=1, col=1
                )
                figSubplot.add_trace(
                    go.Scatter(
                        x=df_media_mercati_2025["SETTIMANA"],
                        y=df_media_mercati_2025["KG"],
                        name="Media Mercati",
                        mode="lines",
                        hovertext="Media Mercati",
                        hovertemplate="Data: %{x}<br>Kg medi: %{y}<extra></extra>",
                        line=dict(
                            dash="dot"
                        )
                    ),
                    row=1, col=1
                )
                # --- PANNELLO 2 (Z-SCORE) ---
                figSubplot.add_trace(
                    go.Scatter(
                        x=df_scostamento["SETTIMANA_x"],
                        y=df_scostamento["Zscore"],
                        connectgaps=True,
                        mode="lines+markers",
                        name="Z-score",
                        line=dict(color="orange")
                    ),
                    row=2, col=1
                )
                # linee soglia ±2
                figSubplot.add_hline(y=2, line_dash="dash", line_color="red", row=2, col=1)
                figSubplot.add_hline(y=-2, line_dash="dash", line_color="red", row=2, col=1)
                figSubplot.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)
                figSubplot.update_layout(
                    height=700,
                    hovermode="x unified",
                    title="📊 Andamento kg recuperati vs media mercati",
                    template="plotly_dark",
                    title_font_size=18,
                    title_x=0.45,
                    title_xanchor="center"
                )
                figSubplot.update_yaxes(title_text="Kg", row=1, col=1)
                figSubplot.update_yaxes(title_text="Z-score", row=2, col=1)
                figSubplot.update_xaxes(title_text="Data", row=2, col=1)
                st.plotly_chart(figSubplot, use_container_width=True)

    with tabanalisitemporali:
        for mercato in df_grafico_mercato_selezionato.columns:
            if mercato != "DATA" and mercato != "PADERNO DUGNANO":
                fig = go.Figure()
                df_grafico_mercato_selezionato_filtrato = df_grafico_mercato_selezionato[df_grafico_mercato_selezionato["DATA"].dt.weekday == giornate_di_mercato[mercato]]
                df_trend = df_grafico_mercato_selezionato_filtrato[df_grafico_mercato_selezionato_filtrato[mercato] != 0].set_index("DATA").rolling(4).mean().reset_index().dropna()
                df_slope = df_trend.sort_values("DATA")
                x = np.arange(len(df_slope.index))
                y = df_slope[mercato].values
                slope, intercept = np.polyfit(x, y, 1)
                trend = slope*x + intercept
                r2 = round(r2_score(y, trend), 2)
                media = round(float(df_grafico_mercato_selezionato_filtrato[mercato][df_grafico_mercato_selezionato_filtrato[mercato] != 0].mean()), 2)
                st.markdown("""
                <style>
                .kpi-card {
                    background: #111;
                    padding: 16px 20px;
                    border-radius: 14px;
                    text-align: center;
                    box-shadow: 0 0 12px rgba(0,0,0,0.4);
                }
                .kpi-title {
                    font-size: 16px;
                    color: #bbbbbb;
                }
                .kpi-value {
                    font-size: 26px;
                    font-weight: 700;
                    color: #00ff9c;
                }
                .header-title {
                    font-size: 42px;
                    font-weight: 700;
                }
                .header-subtitle {
                    font-size: 18px;
                    color: #bbbbbb;
                }
                </style>
                """, unsafe_allow_html=True)
                # ===== HEADER =====
                st.markdown(f"""
                <div style="margin-bottom:20px;">
                  <div class="header-title">📍 {mercato}</div>
                  <div class="header-subtitle">📅 Analisi andamento medio 2025</div>
                </div>
                """, unsafe_allow_html=True)
                # ===== KPI ROW =====
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">🌱 Media per giornata di mercato</div>
                        <div class="kpi-value">{media} kg</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown("""
                    <div class="kpi-card">
                        <div class="kpi-title">📈 Trend settimanale</div>
                        <div class="kpi-value">+34 kg / settimana</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-title">📊 Affidabilità trend (R²)</div>
                        <div class="kpi-value">{r2}</div>
                    </div>
                    """, unsafe_allow_html=True)

                fig.add_trace(
                    go.Scatter(
                        x=df_trend["DATA"],
                        y=df_trend[mercato],
                        mode="lines",
                        hovertext=f"Media Mobile - {mercato}",
                        name=f"Media Mobile - {mercato}",
                        line=dict(
                            width=2,
                            color="rgb(255,209,102)",
                        ),
                        opacity=1
                    )
                )
                color = " rgb(60,179,113)" if slope > 0 else "rgb(230,57,70)"
                fig.add_trace(
                    go.Scatter(
                        x=df_trend["DATA"],
                        y=trend,
                        mode="lines",
                        hovertext=f"Trend - {mercato}",
                        name=f"Trend - {mercato}",
                        line=dict(
                            dash="dash",
                            width=1,
                            color=color
                        )
                    )
                )
                fig.update_layout(
                    title="📈 Andamento del recupero nel tempo",
                    xaxis=dict(title="DATA"),
                    yaxis=dict(title="KG"),
                    legend=dict(orientation="h", y=-0.3),
                    title_x=0.5,
                    title_xanchor="center",
                    title_font_size=20,  # rimpicciolisce il titolo (prova 16–20)
                )
                color = "rgba(60,179,113,0.9)" if slope > 0 else "rgba(230,57,70,0.9)"
                fig.add_annotation(
                    x=0.02,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text=f"Trend: {slope * 5:+.0f} kg/settimana",
                    showarrow=False,
                    font=dict(size=16, color=color),
                )
                fig.add_annotation(
                    x=0.02,
                    y=0.86,
                    xref="paper",
                    yref="paper",
                    text=f"R² = {r2:.2f}",
                    showarrow=False,
                    font=dict(size=14, color="white"),
                    bgcolor="rgba(0,0,0,0.5)",
                    borderwidth=1
                )
                st.plotly_chart(fig, use_container_width=True)

#grafico con volontari
with tabvolontari:
    for mercato in df_grafico_mercato_selezionato.columns:
        if mercato != "DATA" and mercato != "PADERNO DUGNANO":
            df_grafico_mercato_selezionato_filtrato = df_grafico_mercato_selezionato[df_grafico_mercato_selezionato["DATA"].dt.weekday == giornate_di_mercato[mercato]].reset_index(drop=True)
            df_volontari_mercato_selezionato_filtrato = df_volontari_mercato_selezionato.reset_index()[df_volontari_mercato_selezionato.reset_index()["DATA"].dt.weekday == giornate_di_mercato[mercato]].reset_index(drop=True)
            df_beneficiari_mercato_selezionato_filtrato = df_beneficiari_mercato_selezionato.reset_index()[df_beneficiari_mercato_selezionato.reset_index()["DATA"].dt.weekday == giornate_di_mercato[mercato]].reset_index(drop=True)
            df_volontari_mercato_corrente = pd.merge(
                df_grafico_mercato_selezionato_filtrato[["DATA", mercato]],
                df_volontari_mercato_selezionato[[mercato]],
                left_on="DATA",
                right_index=True,
                how="inner"
            )
            df_beneficiari_mercato_corrente = pd.merge(
                df_grafico_mercato_selezionato_filtrato[["DATA", mercato]],
                df_beneficiari_mercato_selezionato[[mercato]],
                left_on="DATA",
                right_index=True,
                how="inner"
            )
            df_clean = df_volontari_mercato_corrente[(df_volontari_mercato_corrente[mercato + "_x"] > 0) &
                                (df_volontari_mercato_corrente[mercato + "_y"] > 0)]
            corr = round(df_clean[mercato + "_x"].corr(df_clean[mercato + "_y"], method="spearman"), 2)
            media_volontari_mercato_corrente = round(df_clean[mercato + "_y"].mean())
            df_clean = df_beneficiari_mercato_corrente[(df_beneficiari_mercato_corrente[mercato + "_x"] > 0) &
                                (df_beneficiari_mercato_corrente[mercato + "_y"] > 0)]
            media_beneficiari_mercato_corrente = round(df_clean[mercato + "_y"].mean())
            st.markdown("""
            <style>
            .card-info {
                background: linear-gradient(135deg, #111111, #1a1a1a);
                border-radius: 14px;
                padding: 18px 22px;
                margin-bottom: 16px;
                box-shadow: 0 0 18px rgba(100, 200, 255, 0.12);
            }

            .card-info h2 {
                font-size: 42px;
                margin: 0 0 10px 0;
                color: white;
                font-weight: 700;
            }

            .card-info p {
                font-size: 18px;
                margin: 6px 0;
                color: #ddd;
            }
            .card-info span {
                font-weight: 700;
            }
            </style>
            """, unsafe_allow_html=True)
            st.markdown(f"""<div class="card-info">
                <h2>️📍 {mercato}</h2>
                <p>👥 Volontari medi per giornata: <span>{media_volontari_mercato_corrente}</span></p>
                <p>🤝 Beneficiari raggiunti: <span>{media_beneficiari_mercato_corrente}</span></p>
            </div>
            """, unsafe_allow_html=True)
            figVolontariScatter = go.Figure()
            figVolontariScatter.add_trace(
                go.Scatter(
                    x=df_volontari_mercato_corrente["DATA"],
                    y=df_volontari_mercato_corrente[mercato + "_x"],
                    name=f"KG - {mercato}",
                    yaxis="y1",
                    mode="lines",
                    hovertext=f"KG - {mercato}",
                    hovertemplate="Data: %{x}<br>Kg " + mercato + ": %{y}<extra></extra>"
                )
            )
            figVolontariScatter.add_trace(
                go.Scatter(
                    x=df_volontari_mercato_corrente["DATA"],
                    y=df_volontari_mercato_corrente[mercato + "_y"],
                    name=f"Volontari - {mercato}",
                    yaxis="y2",
                    mode="lines",
                    hovertext=f"Volontari - {mercato}",
                    hovertemplate="Data: %{x}<br>Kg " + mercato + ": %{y}<extra></extra>"
                )
            )
            figVolontariScatter.update_layout(
                xaxis=dict(title="Data"),
                yaxis=dict(
                    title="Kg",
                    side="left"
                ),
                title="♻️ Cibo recuperato e partecipazione dei volontari",
                yaxis2=dict(
                    title="Numero Volontari",
                    overlaying="y",
                    side="right"
                ),
                legend=dict(x=0.01, y=0.99),
                title_x=0.5,
                title_xanchor="center",
                title_font_size=20,
            )
            figVolontariScatter.add_annotation(
                x=0.95,
                y=0.99,
                xref="paper",
                yref="paper",
                text=f"Correlazione: {corr}",
                showarrow=False,
                font=dict(size=16, color=color),
            )
            st.plotly_chart(figVolontariScatter, use_container_width=True, theme=None)


