import numpy as np
from sklearn.metrics import r2_score
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

spec = importlib.util.spec_from_file_location(
    "Anno",
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils', 'filtro_anno.py'))
)
Anno = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Anno)
filtra_df_anno = Anno.filtra_df

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

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Mercati Milano", page_icon="📍", layout="wide")
inietta_css()

data = data_loader.load_all()
df = data["df"].copy()
dizionarioVolontari = data["dizionarioVolontari"]
dizionarioBeneficiari = data["dizionarioBeneficiari"]
anni_disponibili = df["ANNO"].unique().astype(int).tolist()


# filtro anno
filtroAnno = get_filter_anno()
df = filtra_df_anno(df, filtroAnno)
Anno_selezionato = str(filtroAnno["ANNO"])

st.markdown(f"""
<h1 style='margin-bottom:0;'>📅 Anno {filtroAnno["ANNO"]}</h1>
""", unsafe_allow_html=True)

df["DATA"] = pd.to_datetime(df["DATA"], format="mixed", dayfirst=True, errors="coerce")
chiave = df["MERCATO"].str.upper() + "_" + df["DATA"].dt.strftime("%d/%m/%Y")
df["Numero Volontari"] = chiave.map(dizionarioVolontari).fillna(0).astype(int)
df["Numero Beneficiari"] = chiave.map(dizionarioBeneficiari).fillna(0).astype(int)

df_pivot = (
    df.drop(columns=["ANNO", "MESE"], errors="ignore")
      .groupby(by=["MERCATO", "DATA"]).sum(numeric_only=True)[["KG"]]
      .reset_index()
      .pivot(index="DATA", columns="MERCATO", values="KG")
      .fillna(0)
      .reset_index()
)

base_sett = df.copy()
base_sett["SETTIMANA"] = base_sett["DATA"].dt.to_period("W").dt.start_time
base_sett = base_sett.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()
df_media_mercati = base_sett.groupby("SETTIMANA")["KG"].mean().reset_index()
df_std_mercati = base_sett.groupby("SETTIMANA")["KG"].std().fillna(0).reset_index()

mercati_disponibili = sorted([c for c in df_pivot.columns if c != "DATA"])

# ═════════════════════════════════════════════════════════════════════════════
mercato = st.selectbox("🏘️ Scegli il mercato", mercati_disponibili)

giorno_mercato = GIORNATE_DI_MERCATO.get(mercato, 5)

df_mercato = df_pivot[df_pivot["DATA"].dt.weekday == giorno_mercato]
serie = df_mercato[mercato]
serie_nonzero = serie[serie != 0]
total = round(float(df[df["MERCATO"] == mercato]["KG"].sum()), 2)
tabconfronti, tabanalisitemporali = st.tabs(["Andamento Mercati", "Analisi Temporali"])



# ═══════════════════════════════ TAB 1 — ANDAMENTO ══════════════════════════
with tabconfronti:

    if len(serie_nonzero) == 0:
        st.info(f"Nessun dato disponibile per **{mercato}** nell'anno selezionato.")
    else:
        max_mercato = serie.max()
        giorno_max = df_mercato["DATA"][serie.idxmax()].date().strftime("%d/%m/%Y")

        # scostamento % medio del mercato rispetto alla media mercati
        df_scost = df_mercato.copy()
        df_scost["SETTIMANA"] = df_scost["DATA"].dt.to_period("W").dt.start_time
        df_scost = df_scost.merge(
            df_media_mercati, on="SETTIMANA", how="left", suffixes=("", "_media")
        )

        # serie del mercato = df_scost[mercato]; media mercati = df_scost["KG"]
        mask = df_scost[mercato] != 0  # solo i giorni in cui il mercato c'è stato
        with np.errstate(divide="ignore", invalid="ignore"):
            scost_pct = ((df_scost[mercato] - df_scost["KG"]) / df_scost["KG"]) * 100
        scost_pct = scost_pct[mask].replace([np.inf, -np.inf], np.nan).dropna()
        scost_medio = round(float(scost_pct.mean()), 0) if not scost_pct.empty else 0

        # ===== HEADER =====
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
                <div class="kpi-value" style="font-size:1.8rem;">{giorno_max}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🔥 Kg nel giorno record</div>
                <div class="kpi-value">{max_mercato}</div>
            </div>
            """, unsafe_allow_html=True)

        # allinea la media al giorno del mercato
        media_shift = df_media_mercati.copy()
        media_shift["SETTIMANA"] = media_shift["SETTIMANA"] + pd.Timedelta(days=giorno_mercato)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_mercato["DATA"], y=serie,
            name=f"KG - {mercato}", mode="lines",
            hovertemplate="Data: %{x}<br>Kg " + mercato + ": %{y}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=media_shift["SETTIMANA"], y=media_shift["KG"],
            name="Media Mercati", mode="lines", line=dict(dash="dot"),
            hovertemplate="Data: %{x}<br>Kg medi: %{y}<extra></extra>",
        ))
        fig.update_layout(
            height=480,
            hovermode="x unified",
            title="📊 Andamento kg recuperati vs media mercati",
            template="plotly_dark",
            xaxis=dict(title="Data"), yaxis=dict(title="Kg"),
            legend=dict(orientation="h", y=-0.3),
            title_font_size=18, title_x=0.45, title_xanchor="center",
        )
        col_scost = "rgba(60,179,113,0.9)" if scost_medio >= 0 else "rgba(230,57,70,0.9)"
        fig.add_annotation(
            x=0.02, y=0.95, xref="paper", yref="paper",
            text=f"Scostamento medio dalla media mercati: {scost_medio:+.0f}%",
            showarrow=False, font=dict(size=15, color=col_scost),
        )
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════ TAB 2 — ANALISI TEMPORALI ══════════════════
with tabanalisitemporali:
    if len(serie_nonzero) < 4:
        st.info(f"Dati insufficienti per calcolare un trend affidabile per **{mercato}**.")
    else:
        df_trend = (
            df_mercato[df_mercato[mercato] != 0]
            .set_index("DATA").rolling(4).mean().reset_index().dropna()
        )
        df_slope = df_trend.sort_values("DATA")
        x = np.arange(len(df_slope.index))
        y = df_slope[mercato].values
        slope, intercept = np.polyfit(x, y, 1)
        trend = slope * x + intercept
        r2 = round(r2_score(y, trend), 2)
        media = round(float(serie_nonzero.mean()), 2)

        # ===== HEADER =====


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
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📈 Trend settimanale</div>
                <div class="kpi-value">{slope * 5:+.0f} kg / sett.</div>
            </div>
            """, unsafe_allow_html=True)  # BUG FIX: era hardcoded +34
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📊 Affidabilità trend (R²)</div>
                <div class="kpi-value">{r2}</div>
            </div>
            """, unsafe_allow_html=True)

        # ===== GRAFICO media mobile + trend =====
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trend["DATA"], y=df_trend[mercato], mode="lines",
            name=f"Media Mobile - {mercato}",
            line=dict(width=2, color="rgb(255,209,102)"), opacity=1,
        ))
        color = "rgb(60,179,113)" if slope > 0 else "rgb(230,57,70)"
        fig.add_trace(go.Scatter(
            x=df_trend["DATA"], y=trend, mode="lines",
            name=f"Trend - {mercato}",
            line=dict(dash="dash", width=1, color=color),
        ))
        fig.update_layout(
            title="📈 Andamento del recupero nel tempo",
            xaxis=dict(title="DATA"), yaxis=dict(title="KG"),
            legend=dict(orientation="h", y=-0.3),
            title_x=0.5, title_xanchor="center", title_font_size=20,
        )
        col_ann = "rgba(60,179,113,0.9)" if slope > 0 else "rgba(230,57,70,0.9)"
        fig.add_annotation(
            x=0.02, y=0.95, xref="paper", yref="paper",
            text=f"Trend: {slope * 5:+.0f} kg/settimana",
            showarrow=False, font=dict(size=16, color=col_ann),
        )
        fig.add_annotation(
            x=0.02, y=0.86, xref="paper", yref="paper",
            text=f"R² = {r2:.2f}", showarrow=False,
            font=dict(size=14, color="white"),
            bgcolor="rgba(0,0,0,0.5)", borderwidth=1,
        )
        st.plotly_chart(fig, use_container_width=True)