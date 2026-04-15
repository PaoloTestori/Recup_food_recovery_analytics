import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from sklearn.metrics import r2_score
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

spec = importlib.util.spec_from_file_location(
    "Anno",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils', 'filtro_anno.py'))
)
Anno = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Anno)
filtra_df = Anno.filtra_df
st.set_page_config(layout="wide")
df = st.session_state["df"].copy()
anni_disponibili = df["ANNO"].unique().astype(int).tolist()
df_Form = st.session_state["df_Form"].copy()
dizionarioVolontari = st.session_state["dizionarioVolontari"].copy()
#filtri
render_filter_anno(anni_disponibili)
filtroAnno = get_filter_anno()
df = filtra_df(df, filtroAnno)
Anno_selezionato = str(filtroAnno["ANNO"])
st.session_state["Anno_selezionato"] = Anno_selezionato
st.markdown(f"""
<h1 style='margin-bottom:0;'>📅 Anno {filtroAnno["ANNO"]}</h1>
""", unsafe_allow_html=True)

st.sidebar.text("Made with ❤ by Recup")
tab1, tab2 = st.tabs(["Mercati", "Andamenti"])


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


df_Form["Data del Mercato"] = pd.to_datetime(df_Form["Data del Mercato"], dayfirst=True, errors="coerce")
df_form_2025 = df_Form[df_Form["Data del Mercato"].dt.year == 2025]
df_form_2025 = df_form_2025.reset_index(drop=True)
df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"] = df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"].str.replace(";", ",").str.replace(".", ",").str.replace("-",",").str.replace("/",",").str.replace(" e ",",")
df_form_2025["Numero volontari"] = 0

idx = 0
df["DATA"] = pd.to_datetime(df["DATA"],  format="mixed", dayfirst=True, errors="coerce")
df["Numero Volontari"] = 0

for idx, row in df.iterrows():
    chiave = str.upper(df["MERCATO"][idx]) + "_" + df["DATA"][idx].strftime("%d/%m/%Y")
    if chiave in dizionarioVolontari:
        df["Numero Volontari"][idx] = dizionarioVolontari[str.upper(df["MERCATO"][idx]) + "_" + df["DATA"][idx].strftime("%d/%m/%Y")]
    else:
        df["Numero Volontari"][idx] = 0

mercati_2025 = df.drop(columns=["DATA", "MESE", "ANNO"]).groupby("MERCATO").sum()["KG"].reset_index()
grafico_mercati_2025=go.Figure(data=[go.Pie(labels=mercati_2025["MERCATO"],values=mercati_2025["KG"],hole=0.3)])
totali = mercati_2025.groupby("MERCATO")["KG"].sum()
massimo_recupero = round(max(totali.values))
massimo_mercato = totali.idxmax()

with tab1:
    total = round(float(df["KG"].sum()))
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
                        font-size: 1rem;         
                        letter-spacing: 0.1em;
                        text-transform: uppercase;
                        margin-bottom: 0.3rem;
                        font-family: 'DM Sans', sans-serif;
                        font-weight: 400;

                    }
                    .kpi-value {
                        color: #ffea00;
                        font-size: 1.5rem;
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
    col2, col3, col4 = st.columns(3)

    with col2:
        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-icon">🌱</div>
                            <div class="kpi-title">Totale recuperato nel {Anno_selezionato}</div>
                            <div class="kpi-value">{total} kg</div>
                        </div>
                        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-icon">🏆</div>
                            <div class="kpi-title">Mercato con più recupero</div>
                            <div class="kpi-value">{massimo_mercato}</div>
                        </div>
                        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-icon">🥕</div>
                            <div class="kpi-title">Recupero massimo singolo mercato</div>
                            <div class="kpi-value">{massimo_recupero} kg</div>
                        </div>
                        """, unsafe_allow_html=True)
    grafico_mercati_2025 = px.bar(
        mercati_2025,
        x="KG",
        y=mercati_2025["MERCATO"][mercati_2025["MERCATO"].index],
        orientation="h",
        title=f"<b>📊 Recupero Mercati {Anno_selezionato}</b>",
        color_discrete_sequence=["#0083B8"] * len(mercati_2025),
        template="plotly_white"
    )
    grafico_mercati_2025.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False)),
        yaxis=dict(
            categoryorder="total ascending",
            tickmode="linear",
            automargin=True
        ),
    title_font_size = 20,
    title_x = 0.5,
    title_xanchor = "center",
    )
    grafico_mercati_2025.add_trace(go.Scatter(
        x=totali.values,
        y=totali.index,
        mode="text",
        text=[f"{v:.0f} kg" for v in totali.values],
        textposition="middle right",
        showlegend=False
    ))
    st.plotly_chart(grafico_mercati_2025)

with tab2:
    df = df.replace(0, pd.NA)
    df_raggruppato = df
    df_raggruppato["SETTIMANA"] = df_raggruppato[
        "DATA"].dt.to_period("W").dt.start_time
    df_raggruppato = df_raggruppato.groupby(
        "SETTIMANA").first().reset_index()
    df_raggruppato = df_raggruppato.apply(
        lambda col: col.astype(col.cat.categories.dtype) if hasattr(col, 'cat') else col
    )
    df_raggruppato = df_raggruppato.fillna(0)
    df_raggruppato = df_raggruppato.drop(columns=["DATA", "MESE", "ANNO"])
    df["Settimana"] = 1
    df["mese"] = ""
    idx = 0
    for idx, recupero in df.iterrows():
        df["Settimana"][idx] = recupero["DATA"].isocalendar().week
        df["mese"][idx] = recupero["DATA"].strftime("%B")
    df_somma_mercati_2025 = df.drop(columns=["DATA", "MESE", "ANNO"])
    somma_mercati_2025 = (df_somma_mercati_2025.groupby(by=["SETTIMANA"]).sum())[["KG"]].reset_index()
    fig = go.Figure()
    df_media_mercati_2025 = ((df_somma_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby("SETTIMANA")["KG"].mean()).reset_index()
    df_std_mercati_2025 = ((df_somma_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby("SETTIMANA")["KG"].std()).fillna(0).reset_index()
    df_std_mercati_2025["Upper"] = df_media_mercati_2025["KG"] + df_std_mercati_2025["KG"]
    df_std_mercati_2025["Lower"] = df_media_mercati_2025["KG"] - df_std_mercati_2025["KG"]
    massimo_giorno_kili = round(max(somma_mercati_2025["KG"]), 1)
    massimo_giorno = (somma_mercati_2025.loc[somma_mercati_2025['KG'].idxmax(), 'SETTIMANA']).strftime('%d/%m')
    st.markdown(f"## 📅 Anno: {Anno_selezionato}")

    col2, col3 = st.columns(2)

    with col2:
        st.markdown(f"""
                            <div class="kpi-card">
                                <div class="kpi-icon">📅 </div>
                                <div class="kpi-title">Settimana record</div>
                                <div class="kpi-value">{massimo_giorno}/{Anno_selezionato}</div>
                            </div>
                            """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
                            <div class="kpi-card">
                                <div class="kpi-icon">🥇</div>
                                <div class="kpi-title">Massimo recupero settimanale</div>
                                <div class="kpi-value">{massimo_giorno_kili} kg</div>
                            </div>
                            """, unsafe_allow_html=True)

    fig.add_trace(
        go.Scatter(
            x=somma_mercati_2025["SETTIMANA"],
            y=somma_mercati_2025["KG"],
            name="KG Recuperati",
            mode="lines",
            hovertext=f"KG - Recuperati",
            hovertemplate="Data: %{x}<br>Kg recuperati: %{y}<extra></extra>"
        )
    )
    fig.update_layout(
        xaxis=dict(title="DATA"),
        yaxis=dict(title="KG"),
        legend=dict(orientation="h", y=-0.3),
        title="♻️ Andamento del Recupero Totale",
        title_font_size=20,
        title_x=0.5,
        title_xanchor="center",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_std_mercati_2025["SETTIMANA"],
        y=df_std_mercati_2025["Upper"],
        mode="lines",
        line=dict(color="rgba(0,100,255,0.6)", width=1),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=df_std_mercati_2025["SETTIMANA"],
        y=df_std_mercati_2025["Lower"],
        mode="lines",
        fill="tonexty",  # riempie fino alla trace sopra
        fillcolor="rgba(0,100,255,0.35)",  # azzurro trasparente
        line=dict(color="rgba(0,100,255,0.6)", width=1),
        name="Deviazione std"
    ))
    fig.add_trace(
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
        )
    )
    fig.update_layout(
        xaxis=dict(title="DATA"),
        yaxis=dict(title="KG"),
        legend=dict(orientation="h", y=-0.3),
        title = "🔄️ Andamento del Recupero Medio",
        title_font_size = 20,
        title_x = 0.5,
        title_xanchor = "center",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = go.Figure()
    df_trend = somma_mercati_2025.set_index(
        "SETTIMANA").rolling(4).mean().reset_index().dropna()
    df_slope = df_trend.sort_values("SETTIMANA")
    x = np.arange(len(df_slope.index))
    y = df_slope["KG"].values
    slope, intercept = np.polyfit(x, y, 1)
    trend = slope * x + intercept
    r2 = round(r2_score(y, trend), 2)
    media = round(float(somma_mercati_2025.mean()["KG"]),2)
    fig.add_trace(
        go.Scatter(
            x=df_trend["SETTIMANA"],
            y=df_trend["KG"],
            mode="lines",
            hovertext=f"Media Mobile",
            name=f"Media Mobile",
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
            x=df_trend["SETTIMANA"],
            y=trend,
            mode="lines",
            hovertext=f"Trend",
            name=f"Trend",
            line=dict(
                dash="dash",
                width=1,
                color=color
            )
        )
    )
    fig.update_layout(
        title="📈 Andamento del Recupero nel Tempo",
        xaxis=dict(title="DATA"),
        yaxis=dict(title="KG"),
        legend=dict(orientation="h", y=-0.3),
        title_x=0.5,
        title_xanchor="center",
        title_font_size=20,
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

st.session_state["df_media_mercati_2025"] = df_media_mercati_2025

with tab1:
    st.write(mercati_2025)
    mercati_2025["Lat"] = [45.48194631003896, 45.498572631276076, 45.41558818510914, 45.4568377251085, 45.43769947440869, 45.44079962417922, 45.46856674391473, 45.56908414624718, 45.45809799201643, 45.44769247648455 , 45.49170755334271, 45.47979583274876]
    mercati_2025["Long"] = [9.20908871960476, 9.171843522528558, 9.265495707447384, 9.220735241820233, 9.222317497412892, 9.2194775512992, 9.141949360535436, 9.15969763897859, 9.170071664509393, 9.18266244741002, 9.220097090233262, 9.236583212298052]
    mercati_2025_bubble = mercati_2025
    mercati_2025_bubble["DATA"] = somma_mercati_2025["SETTIMANA"]
    mercati_2025_bubble_map = px.scatter_map(
        mercati_2025_bubble,
        lat="Lat",
        lon="Long",
        size="KG",
        color="KG",
        hover_name="MERCATO",
        color_continuous_scale="Reds",
        #animation_frame="DATA",
        size_max=70,
        zoom=11.7,
    )
    mercati_2025_bubble_map.update_layout(
        map_style="carto-darkmatter",
        margin={"r":0, "t":0, "l":0, "b":0},
        title={
            "text": "🍌 Mappa dei mercati Recup nella città di Milano",
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top"
        },
        title_font=dict(size=18),
    )

    st.plotly_chart(mercati_2025_bubble_map, width="stretch")

