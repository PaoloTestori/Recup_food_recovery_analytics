from google.oauth2 import service_account
import gspread
import plotly.express as px
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Giornate di mercato",
                   page_icon="📅",
                   layout="wide")

tabconfrontomercatigiornate, tabfocusalimentigiornate = st.tabs(["Focus Totali", "Focus Mercati"])

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

# Percorso del file JSON del service account
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"])

# Apertura client
client = gspread.authorize(creds)
#lettura file mercati 2025
wbUrl = st.secrets["WEBHOOK_URL_MERCATI2025"]

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

emoji_alimenti = {
    "UVA" : "🍇",
}

#df = pd.read_csv(    filepath_or_buffer= wbUrl,    header=0,    usecols=[0,1,2,3],    parse_dates=[0],    skiprows=[1],)
#lettura file form google
#df_Form = pd.read_csv(    filepath_or_buffer= st.secrets["WEBHOOK_URL_MERCATI_RISPOSTE"],    usecols=[0,1,2,3,5,6],    parse_dates=[1],    skiprows=[0],)
df = st.session_state["df"].copy()
df_Form = st.session_state["df_Form"].copy()
dizionarioVolontari = st.session_state["dizionarioVolontari"].copy()

df_Form["Data del Mercato"] = pd.to_datetime(df_Form["Data del Mercato"], dayfirst=True, errors="coerce")
df_form_2025 = df_Form[df_Form["Data del Mercato"].dt.year == 2025]
df_form_2025 = df_form_2025.reset_index(drop=True)
#gestione numero volontari
df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"] = df_form_2025["Inserisci NOME e COGNOME dellə volontariə presenti"].str.replace(";", ",").str.replace(".", ",").str.replace("-",",").str.replace("/",",").str.replace(" e ",",")
df_form_2025["Numero volontari"] = 0
df_form_2025["Quantə beneficiariə? (inserisci un numero)"] = df_form_2025["Quantə beneficiariə? (inserisci un numero)"].replace("-",0)
#dizionarioVolontari = {}
dizionarioBeneficiari = {}

for idx, ben in df_form_2025["Quantə beneficiariə? (inserisci un numero)"].items():
    if ben is "":
        continue
    dizionarioBeneficiari[str.upper(df_form_2025["Nome del Mercato"][idx]) + "_" + (
        df_form_2025["Data del Mercato"][idx].strftime("%d/%m/%Y"))] = int(df_form_2025["Quantə beneficiariə? (inserisci un numero)"][idx])

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
#df["Numero Volontari"] = 0
#for idx, row in df.iterrows():
#    df["Numero Volontari"][idx] = dizionarioVolontari[str.upper(df["MERCATO"][idx]) + "_" + df["DATA"][idx].strftime("%d/%m/%Y")]

#inserimento filtri
st.sidebar.header("Filtri")
st.sidebar.subheader("📅 Filtro date")
opzioni_data = df["DATA"].unique()
selected_year = st.sidebar.selectbox("Anno", "2025")
months = opzioni_data.to_period("M").unique().astype(str)
monthsinword = [
    mesario[int(m.split("-")[1]) - 1]
    for m in months
    if m is not None
]

selected_month = st.sidebar.selectbox("Mese", monthsinword)
year = 2025
month = (monthsinword.index(selected_month)+1)
month_dates = [
    d for d in opzioni_data
    if d is not None and d.year == year and d.month == month
]
default_dates = [
    d for d in st.session_state.get("selected_dates", [])
    if d in month_dates
]

data = st.sidebar.multiselect(
    "Giorno",
    options=month_dates,
    default=month_dates,
    format_func=lambda d: d.strftime("%d"),
    placeholder="Seleziona date..."
)
st.session_state["selected_dates"] = data

if data == month_dates:
    date_selezionate = selected_month
    mese_selezionato = mesario[int((" - ".join(pd.to_datetime(data).strftime("%m"))).split(" - ")[0]) - 1]
    giorno_selezionato = " - ".join(pd.to_datetime(data).strftime("%d"))
else:
    date_selezionate = " - ".join(pd.to_datetime(data).strftime("%d/%m"))

opzioni_mercato = df["MERCATO"].unique()
#seleziona tutti mercati
st.sidebar.markdown("")
st.sidebar.subheader("📍 Filtro mercati")
seleziona_tutti_mercato = st.sidebar.checkbox("Seleziona tutti mercati", value=True)
if seleziona_tutti_mercato:
    mercato = st.sidebar.multiselect(
        "Seleziona Mercato",
        options=opzioni_mercato,
        default=opzioni_mercato
    )
else:
    mercato = st.sidebar.multiselect(
        "Seleziona Mercato",
        options=opzioni_mercato
    )
#seleziona tutti item
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
#df["SETTIMANA"] = df["DATA"] - df["MERCATO"].map(giornate_di_mercato).apply(lambda x: pd.Timedelta(days=x))
df_std_mercati_2025 = (
    (df_std_mercati_2025.groupby(["SETTIMANA", "MERCATO"])["KG"].sum().reset_index()).groupby("SETTIMANA")[
        "KG"].std()).reset_index()
df = df.drop(columns=["SETTIMANA"])

df_selection = df.query("MERCATO == @mercato & DATA == @data")

df_selection_altro = df_selection.copy()
df_selection_altro.loc[df_selection_altro["KG"] < 2, "ITEM"] = "Altro"
df_grafico_mercato_selezionato_alimenti = df_selection_altro.drop(columns=["DATA"])
df_grafico_mercato_selezionato_alimenti = (
    df_grafico_mercato_selezionato_alimenti.groupby(by=["MERCATO", "ITEM"])
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
    sommavolontari = 0
    sommaBeneficiario = 0
    for mercatomercato in df_selection["MERCATO"].unique().tolist():
        for giornatamercato in df_selection["DATA"].unique().tolist():
            giornatamercatostr = giornatamercato.strftime("%d/%m/%Y")
            chiave = mercatomercato + "_" + giornatamercatostr
            if chiave in dizionarioVolontari:
                sommavolontari = sommavolontari + dizionarioVolontari[chiave]
            if chiave in dizionarioBeneficiari:
                sommaBeneficiario = sommaBeneficiario + dizionarioBeneficiari[chiave]
    with tabconfrontomercatigiornate:
        totale_giorno = round(df_selection["KG"].sum(),2)
        if date_selezionate in mesario:
            titolo = "Mese"
        else:
            titolo = "Giorno/i"
        #nuovo
        st.markdown(f"## 📅 {titolo}: {date_selezionate}")
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
                            font-size: 22px;
                            font-weight: 700;
                            color: #00ff9c;
                        }
                        .kpi-icon {
                            font-size: 22px;
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
        #st.markdown("<br><br>", unsafe_allow_html=True)
        df_grafico_mercato_selezionato_alimenti = df_selection_altro.drop(columns=["DATA"])
        df_grafico_mercato_selezionato_alimenti = (
            df_grafico_mercato_selezionato_alimenti.groupby(by=["MERCATO", "ITEM"])
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
            title=f"<b>Cibo raccolto per mercato nel {titolo} {date_selezionate.lower()}</b>", #AGGIUNGERE GIORNO SELEZIONATO
            color_discrete_sequence=["#0083B8"] * len(df_grafico_mercato_selezionato_alimenti),
            template="plotly_white",
            hover_data=["MERCATO", "KG"],
            orientation="h",
        )
        figBarMercati.update_layout(
            title=dict(
                text=f"<b>Cibo recuperato per mercato nel/nei {titolo.lower()} {date_selezionate.lower()}</b>", #AGGIUNGERE GIORNO SELEZIONATO
                x=0.02,
                xanchor="left",
                font=dict(
                    size=24,
                    family="Inter, Arial, sans-serif",
                    color="#EAEAEA"
                )
            ),
            margin=dict(l=200, r=40, t=80, b=60),
           # margin=dict(t=40, l=10, r=10, b=10),
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
                text=f"<b>Composizione del cibo recuperato per mercato nel/nei {titolo.lower()} {date_selezionate.lower()}</b>",  # AGGIUNGERE GIORNO SELEZIONATO
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
        st.markdown(f"## 📅 {header}: {date_selezionate} - 📍Mercato: {merc}")
        tabella_mercato = df_selection_altro[df_selection_altro["MERCATO"] == merc].copy().reset_index(drop=True)
        #st.table(tabella_mercato)
        numero_volontari_mercato_corrente = 0
        numero_beneficiari_mercato_corrente = 0
        numero_giorni_mercato_corrente = 0
        for mercatomercato in tabella_mercato["MERCATO"].unique().tolist():
            for giornatamercato in tabella_mercato["DATA"].unique().tolist():
                numero_giorni_mercato_corrente = numero_giorni_mercato_corrente + 1
                giornatamercatostr = giornatamercato.strftime("%d/%m/%Y")
                chiave = mercatomercato + "_" + giornatamercatostr
                if chiave in dizionarioVolontari:
                    numero_volontari_mercato_corrente = numero_volontari_mercato_corrente + dizionarioVolontari[chiave]
                if chiave in dizionarioBeneficiari:
                    numero_beneficiari_mercato_corrente = numero_beneficiari_mercato_corrente + dizionarioBeneficiari[chiave]
        numero_volontari_mercato_corrente = round(numero_volontari_mercato_corrente/numero_giorni_mercato_corrente)
        numero_beneficiari_mercato_corrente = round(numero_beneficiari_mercato_corrente/numero_giorni_mercato_corrente)
        totale_giorno_mercato_corrente = round(tabella_mercato["KG"].sum(), 1)
        data_mercato_corrente = tabella_mercato["DATA"].iloc[0].strftime("%d/%m/%Y")
        chiave = merc  + "_" + data_mercato_corrente
        tabella_mercato = (tabella_mercato.drop(columns=["DATA"])).groupby("ITEM").sum()[["KG"]].reset_index()
        alimento_pi_recuperato = tabella_mercato["ITEM"].iloc[tabella_mercato["KG"].idxmax()]
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
                    font-size: 22px;
                    font-weight: 700;
                    color: #00ff9c;
                }
                .kpi-icon {
                    font-size: 22px;
                }
                </style>
                """, unsafe_allow_html=True)
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
                         <div class="kpi-title">Volontari</div>
                         <div class="kpi-value">{numero_volontari_mercato_corrente}</div>
                     </div>
                     """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
                     <div class="kpi-card">
                         <div class="kpi-icon">🤝</div>
                         <div class="kpi-title">Beneficiari</div>
                         <div class="kpi-value">{numero_beneficiari_mercato_corrente}</div>
                     </div>
                     """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-icon">💪</div>
                        <div class="kpi-title">Media per volontario</div>
                        <div class="kpi-value">{totale_giorno_mercato_corrente / numero_volontari_mercato_corrente:.1f} kg</div>
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
                # AGGIUNGERE GIORNO SELEZIONATO
                x=0.02,
                xanchor="left",
                font=dict(
                    size=24,
                    family="Inter, Arial, sans-serif",
                    color="#EAEAEA"
                )
            ),
            height=480,  # più piccolo ma leggibile
            margin=dict(t=50, l=20, r=20, b=20),
            template="plotly_white",
            title_font_size=18,
            title_x=0.47,
            title_xanchor="center",
        )
        st.plotly_chart(grafico_mercato_selezionato_alimenti)

        st.divider()

st.sidebar.text("Made with ❤ by Recup")




