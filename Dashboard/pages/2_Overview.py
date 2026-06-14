import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from sklearn.metrics import r2_score
import importlib.util
import os
from components.palette import VERDE, ROSSO, BLU, GIALLO, GRIGIO, VERDE_SOFT, ROSSO_SOFT

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

# coordinate + css condivisi dal loader/styles
spec_dl = importlib.util.spec_from_file_location(
    "data_loader",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'components', 'data_loader.py'))
)
data_loader = importlib.util.module_from_spec(spec_dl)
spec_dl.loader.exec_module(data_loader)
LAT = data_loader.LAT
LONG = data_loader.LONG

spec_st = importlib.util.spec_from_file_location(
    "styles",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'components', 'styles.py'))
)
styles = importlib.util.module_from_spec(spec_st)
spec_st.loader.exec_module(styles)
inietta_css = styles.inietta_css

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide")
inietta_css()

data = data_loader.load_all()
df = data["df"].copy()
dizionarioVolontari = data["dizionarioVolontari"]
dizionarioBeneficiari = data["dizionarioBeneficiari"]
anni_disponibili = df["ANNO"].unique().astype(int).tolist()


# filtri
filtroAnno = get_filter_anno()
df = filtra_df(df, filtroAnno)
Anno_selezionato = str(filtroAnno["ANNO"])
st.session_state["Anno_selezionato"] = Anno_selezionato

st.markdown(f"""
<h1 style='margin-bottom:0;'>📅 Anno {filtroAnno["ANNO"]}</h1>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Mercati", "Andamenti"])

df["DATA"] = pd.to_datetime(df["DATA"], format="mixed", dayfirst=True, errors="coerce")
chiave = df["MERCATO"].str.upper() + "_" + df["DATA"].dt.strftime("%d/%m/%Y")
df["Numero Volontari"] = chiave.map(dizionarioVolontari).fillna(0).astype(int)

# ─── aggregati per mercato ───────────────────────────────────────────────────
mercati_2025 = (
    df.drop(columns=["DATA", "MESE", "ANNO"])
      .groupby("MERCATO").sum()["KG"].reset_index()
)
totali = mercati_2025.groupby("MERCATO")["KG"].sum()
massimo_recupero = round(max(totali.values))
massimo_mercato = totali.idxmax()

mercati_2025["Lat"] = mercati_2025["MERCATO"].map(LAT)
mercati_2025["Long"] = mercati_2025["MERCATO"].map(LONG)

# ═══════════════════════════════ TAB 1 — MERCATI ════════════════════════════
with tab1:
    total = round(float(df["KG"].sum()))
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
                <div class="kpi-value" style="font-size:1.6rem;">{massimo_mercato}</div>
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
        y="MERCATO",
        orientation="h",
        title=f"<b>📊 Recupero Mercati {Anno_selezionato}</b>",
        color_discrete_sequence=[BLU] * len(mercati_2025),
        template="plotly_white",
    )
    grafico_mercati_2025.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(categoryorder="total ascending", tickmode="linear", automargin=True),
        title_font_size=20,
        title_x=0.5,
        title_xanchor="center",
    )
    grafico_mercati_2025.add_trace(go.Scatter(
        x=totali.values,
        y=totali.index,
        mode="text",
        text=[f"{v:.0f} kg" for v in totali.values],
        textposition="middle right",
        showlegend=False,
    ))
    st.plotly_chart(grafico_mercati_2025, use_container_width=True)

# ═══════════════════════════════ TAB 2 — ANDAMENTI ══════════════════════════
with tab2:
    # df settimanale (mantiene la logica originale, ma senza i loop iterrows)
    df_tmp = df.replace(0, pd.NA).copy()
    df_tmp["SETTIMANA"] = df_tmp["DATA"].dt.to_period("W").dt.start_time

    df_somma = df_tmp.drop(columns=["DATA", "MESE", "ANNO"])
    somma_mercati_2025 = (
        df_somma.groupby("SETTIMANA").sum()[["KG"]].reset_index()
    )

    # media e std settimanale tra mercati
    base = df_somma.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()
    df_media_mercati_2025 = base.groupby("SETTIMANA")["KG"].mean().reset_index()
    df_std_mercati_2025 = base.groupby("SETTIMANA")["KG"].std().fillna(0).reset_index()
    df_std_mercati_2025["Upper"] = df_media_mercati_2025["KG"] + df_std_mercati_2025["KG"]
    df_std_mercati_2025["Lower"] = df_media_mercati_2025["KG"] - df_std_mercati_2025["KG"]

    massimo_giorno_kili = round(max(somma_mercati_2025["KG"]), 1)
    massimo_giorno = somma_mercati_2025.loc[
        somma_mercati_2025["KG"].idxmax(), "SETTIMANA"
    ].strftime("%d/%m")

    st.markdown(f"## 📅 Anno: {Anno_selezionato}")
    col2, col3 = st.columns(2)
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">📅</div>
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

    # --- andamento totale ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=somma_mercati_2025["SETTIMANA"],
        y=somma_mercati_2025["KG"],
        name="KG Recuperati",
        mode="lines",
        hovertemplate="Data: %{x}<br>Kg recuperati: %{y}<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(title="DATA"), yaxis=dict(title="KG"),
        legend=dict(orientation="h", y=-0.3),
        title="♻️ Andamento del Recupero Totale",
        title_font_size=20, title_x=0.5, title_xanchor="center",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- andamento medio ± std ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_std_mercati_2025["SETTIMANA"], y=df_std_mercati_2025["Upper"],
        mode="lines", line=dict(color="rgba(0,100,255,0.6)", width=1), showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=df_std_mercati_2025["SETTIMANA"], y=df_std_mercati_2025["Lower"],
        mode="lines", fill="tonexty", fillcolor=BLU,
        line=dict(color="rgba(0,100,255,0.6)", width=1), name="Deviazione std",
    ))
    fig.add_trace(go.Scatter(
        x=df_media_mercati_2025["SETTIMANA"], y=df_media_mercati_2025["KG"],
        name="Media Mercati", mode="lines",
        hovertemplate="Data: %{x}<br>Kg medi: %{y}<extra></extra>",
        line=dict(dash="dot"),
    ))
    fig.update_layout(
        xaxis=dict(title="DATA"), yaxis=dict(title="KG"),
        legend=dict(orientation="h", y=-0.3),
        title="🔄️ Andamento del Recupero Medio",
        title_font_size=20, title_x=0.5, title_xanchor="center",
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- media mobile + trend lineare ---
    fig = go.Figure()
    df_trend = somma_mercati_2025.set_index("SETTIMANA").rolling(4).mean().reset_index().dropna()
    df_slope = df_trend.sort_values("SETTIMANA")
    x = np.arange(len(df_slope.index))
    y = df_slope["KG"].values
    slope, intercept = np.polyfit(x, y, 1)
    trend = slope * x + intercept
    r2 = round(r2_score(y, trend), 2)

    fig.add_trace(go.Scatter(
        x=df_trend["SETTIMANA"], y=df_trend["KG"], mode="lines",
        name="Media Mobile", line=dict(width=2, color="rgb(255,209,102)"), opacity=1,
    ))
    color = "rgb(60,179,113)" if slope > 0 else "rgb(230,57,70)"
    fig.add_trace(go.Scatter(
        x=df_trend["SETTIMANA"], y=trend, mode="lines",
        name="Trend", line=dict(dash="dash", width=1, color=color),
    ))
    fig.update_layout(
        title="📈 Andamento del Recupero nel Tempo",
        xaxis=dict(title="DATA"), yaxis=dict(title="KG"),
        legend=dict(orientation="h", y=-0.3),
        title_x=0.5, title_xanchor="center", title_font_size=20,
    )
    color = "rgba(60,179,113,0.9)" if slope > 0 else "rgba(230,57,70,0.9)"
    fig.add_annotation(
        x=0.02, y=0.95, xref="paper", yref="paper",
        text=f"Trend: {slope * 5:+.0f} kg/settimana",
        showarrow=False, font=dict(size=16, color=color),
    )
    fig.add_annotation(
        x=0.02, y=0.86, xref="paper", yref="paper",
        text=f"R² = {r2:.2f}", showarrow=False,
        font=dict(size=14, color="white"),
        bgcolor="rgba(0,0,0,0.5)", borderwidth=1,
    )
    st.plotly_chart(fig, use_container_width=True)

st.session_state["df_media_mercati_2025"] = df_media_mercati_2025

# ═══════════════════════════ TAB 1 — MAPPA A BOLLE ══════════════════════════
with tab1:
    mappa = px.scatter_map(
        mercati_2025,
        lat="Lat", lon="Long",
        size="KG", color="KG",
        hover_name="MERCATO",
        color_continuous_scale="Reds",
        size_max=70, zoom=11.7,
    )
    mappa.update_layout(
        map_style="carto-darkmatter",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title={"text": "🍌 Mappa dei mercati Recup nella città di Milano",
               "x": 0.5, "xanchor": "center", "yanchor": "top"},
        title_font=dict(size=18),
    )
    st.plotly_chart(mappa, use_container_width=True)