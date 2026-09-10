import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI

# --- CONFIGURAZIONE PAGINA STREAMLIT ---
st.set_page_config(
    page_title="Sintec S.r.l. - Controllo di Gestione",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STILE TEMA MODERNO SINTEC (RED & DARK ACCENTS) ---
st.markdown(
    """
<style>
    .stApp {
        background-color: #f4f5f7;
        color: #1e1e1e;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Stile Brand SinTec */
    .brand-header {
        background-color: #ffffff;
        padding: 18px 25px;
        border-bottom: 4px solid #d9232a;
        margin-bottom: 20px;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #111111;
        margin: 0;
    }
    .brand-accent {
        color: #d9232a;
    }
    .brand-sub {
        font-size: 0.8rem;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* KPI Cards in stile moderno */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-left: 5px solid #d9232a;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .kpi-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #555555;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #111111;
    }
    .kpi-subtitle {
        font-size: 0.75rem;
        color: #666666;
        margin-top: 4px;
    }
    .kpi-delta-pos {
        color: #16a34a;
        font-weight: 700;
    }
    .kpi-delta-neg {
        color: #d9232a;
        font-weight: 700;
    }

    /* Tab di Navigazione stile Menu Scuro del Sito */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #1e1e1e;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 6px;
        color: #cccccc;
        font-weight: 600;
        border: none;
        padding: 0 14px;
        font-size: 0.82rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #d9232a !important;
        color: #ffffff !important;
    }

    /* Sidebar personalizzata */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #dddddd !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- FUNZIONE STILE RIGHE DI TOTALE ---
def evidenzia_totale(row, col_chiave="Mese"):
    val = str(row[col_chiave]).upper()
    if val in ["TOTALE", "TOTALE FATTURATO", "TOTALE SINTEC (MEDIA GEN-LUG)", "TOTALE YTD (8M)", "TOTALE (GEN-AGO)"]:
        return ['background-color: #dbeafe; font-weight: bold; color: #1e40af'] * len(row)
    elif "PREVISIONALE" in val:
        return ['background-color: #fef08a; font-weight: bold; color: #854d0e'] * len(row)
    return [''] * len(row)

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown(
        "<div style='text-align: center; margin-top: 50px;'><h1 style='color:#111; font-size: 2rem;'>🔒 <span style='color:#d9232a;'>SinTec</span> Accesso Riservato</h1><p style='color: #666;'>Controllo di Gestione Aziendale</p></div>",
        unsafe_allow_html=True,
    )
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        with st.form("login_form"):
            username = st.text_input("Username", key="username")
            password = st.text_input("Password", type="password", key="password")
            submit_button = st.form_submit_button(
                "🚀 Accedi alla Dashboard", use_container_width=True
            )

        if submit_button:
            if username == "sintec" and password == "Sintec2026!":
                st.session_state["authenticated"] = True
                st.success("Accesso effettuato con successo!")
                st.rerun()
            else:
                st.error("Credenziali non valide")
    st.stop()

# --- DATI GENERALI (AGGIORNATI CON FILE UFFICIALE SETTEMBRE 2026 - 8 MESI YTD) ---
df_fat = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Fatturato 2026": [58570.50, 73584.46, 75642.00, 70202.10, 65023.99, 80642.35, 66484.43, 35609.42, 0, 0, 0, 0],
    "Fatturato 2025": [57401.50, 62787.31, 72682.00, 68541.53, 71101.00, 73161.79, 64458.50, 35609.42, 84284.50, 82004.21, 64778.43, 64324.52],
    "Fatturato 2024": [57247.00, 68184.47, 80810.80, 68999.64, 87666.00, 70416.50, 88701.60, 48356.50, 73093.20, 89233.76, 72332.50, 57421.08],
})

# Costi dipendenti 2026 aggiornati da file a-TABELLA RIASSUNTIVA COSTI DIPEND 26.pdf (Gen-Ago 2026)
df_costi = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Costi 2026": [34104.88, 40913.02, 39960.05, 39848.93, 41854.30, 38761.35, 34074.31, 31320.96, 0, 0, 0, 0],
    "Costi 2025": [37513.85, 36318.82, 36075.82, 38017.47, 41233.54, 42640.51, 36236.41, 26967.94, 39929.42, 40450.24, 41594.63, 36510.16],
    "Costi 2024": [30359.58, 34197.57, 43005.65, 40156.84, 43703.97, 44361.46, 32676.33, 36758.37, 42287.59, 40908.77, 36832.46, 46703.16],
})

df_ore_dirette = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Ore Dirette 2026": [1788.0, 2108.5, 2102.5, 2020.5, 2118.5, 2027.0, 1949.0, 1308.0, 0, 0, 0, 0],
    "Ore Dirette 2025": [2017.0, 2087.0, 2317.5, 2155.5, 2251.5, 2221.0, 2084.0, 1308.0, 2454.0, 2355.0, 2134.0, 1641.5],
})

df_ore_indirette = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Ore Indirette 2026": [156.0, 237.0, 327.0, 222.0, 220.5, 134.0, 188.5, 65.0, 0, 0, 0, 0],
    "Ore Indirette 2025": [193.0, 137.0, 81.5, 112.5, 155.5, 126.5, 97.5, 65.0, 163.5, 145.5, 124.5, 171.0],
})

df_media_oraria = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Media Oraria 2026": [30.13, 31.37, 31.13, 31.31, 27.80, 37.32, 31.10, 27.22, 0, 0, 0, 0],
    "Media Oraria 2025": [25.97, 28.23, 30.30, 30.22, 29.54, 31.17, 29.55, 25.94, 32.20, 32.80, 28.68, 35.49],
    "Media Oraria 2024": [25.98, 27.17, 30.29, 27.78, 28.50, 26.28, 30.74, 27.24, 29.82, 31.52, 27.52, 30.05],
})

# --- DATI DIPENDENTI 2026 (AGGIORNATI DA FILE RECENTE - AGOSTO 2026 INCLUSO) ---
df_riassunto_2026 = pd.DataFrame({
    "COGNOME": ["D'ALSAZIA", "BASSISSI", "CASELLI", "LANZI", "GUION", "CAMPANINI", "JOHNSON", "RASENTI", "MAGNO", "SCANO", "PETRO'", "GRANDE", "DEJVI (luglio-sett.)", "TOTALE (GEN-AGO)"],
    "COSTO TOT": [29039.16, 18010.84, 28854.34, 24536.91, 12606.85, 27807.68, 22897.13, 38531.92, 26985.89, 26254.66, 21384.32, 21285.24, 2642.86, 300837.80],
    "ORE TOT": [1222.5, 1186.5, 1017.0, 1166.5, 741.0, 1203.0, 1033.5, 1341.0, 1207.5, 960.0, 1154.5, 709.5, 304.5, 13247.0],
    "COSTO ORARIO": [23.75, 15.18, 28.37, 21.03, 17.01, 23.12, 22.15, 28.73, 22.35, 27.35, 18.52, 30.00, 8.68, 22.71],
})

dati_dipendenti_mensili = {
    "D'ALSAZIA": {"Costo": [3693.39, 3960.66, 3857.07, 3922.04, 3889.52, 4007.63, 2555.03, 3153.82, 0, 0, 0, 0], "Ore": [150.5, 166.5, 172.5, 168.5, 163.0, 168.0, 105.5, 128.0, 0, 0, 0, 0]},
    "BASSISSI": {"Costo": [2169.70, 2337.50, 2361.92, 2332.02, 2406.59, 2407.38, 1520.40, 2475.33, 0, 0, 0, 0], "Ore": [143.5, 160.0, 176.0, 168.0, 158.0, 157.0, 96.0, 128.0, 0, 0, 0, 0]},
    "CASELLI": {"Costo": [3504.50, 3749.44, 4035.38, 4073.36, 3925.75, 3846.69, 2635.19, 3084.03, 0, 0, 0, 0], "Ore": [125.0, 140.0, 151.0, 129.5, 137.5, 141.0, 86.0, 107.0, 0, 0, 0, 0]},
    "LANZI": {"Costo": [2949.79, 3225.64, 3455.40, 3518.32, 3244.59, 3093.37, 2944.15, 2105.65, 0, 0, 0, 0], "Ore": [137.0, 157.5, 175.0, 167.0, 150.5, 144.0, 152.0, 83.5, 0, 0, 0, 0]},
    "GUION": {"Costo": [1296.53, 1452.13, 1912.60, 1518.40, 1779.25, 1801.12, 1680.60, 1166.22, 0, 0, 0, 0], "Ore": [81.5, 96.0, 106.0, 86.5, 101.5, 101.0, 110.0, 58.5, 0, 0, 0, 0]},
    "CAMPANINI": {"Costo": [3430.97, 3447.45, 3523.93, 3480.09, 3647.24, 3701.70, 3549.45, 3026.85, 0, 0, 0, 0], "Ore": [132.0, 137.5, 158.0, 155.5, 157.5, 159.0, 175.5, 128.0, 0, 0, 0, 0]},
    "JOHNSON": {"Costo": [0, 3343.93, 3503.85, 3601.16, 3602.41, 3696.58, 2317.53, 2831.67, 0, 0, 0, 0], "Ore": [0, 144.0, 169.5, 168.0, 160.0, 168.0, 104.0, 120.0, 0, 0, 0, 0]},
    "RASENTI": {"Costo": [4789.75, 5702.35, 4906.62, 4697.05, 6054.25, 4722.98, 4664.75, 2994.17, 0, 0, 0, 0], "Ore": [160.0, 199.0, 193.0, 152.0, 204.0, 179.0, 164.0, 90.0, 0, 0, 0, 0]},
    "MAGNO": {"Costo": [2907.89, 3942.03, 3585.79, 3477.99, 3608.15, 2842.71, 3622.03, 2999.30, 0, 0, 0, 0], "Ore": [134.0, 162.5, 172.5, 156.5, 159.5, 108.0, 184.5, 130.0, 0, 0, 0, 0]},
    "SCANO": {"Costo": [3542.57, 3758.97, 2634.49, 3019.63, 3787.61, 3779.72, 3330.42, 2401.25, 0, 0, 0, 0], "Ore": [143.5, 153.5, 72.0, 104.0, 156.5, 150.0, 101.0, 79.5, 0, 0, 0, 0]},
    "PETRO'": {"Costo": [2663.25, 2580.76, 2737.40, 2869.85, 2878.23, 3139.26, 2229.56, 2286.01, 0, 0, 0, 0], "Ore": [133.5, 121.0, 173.0, 169.0, 147.0, 147.0, 137.0, 127.0, 0, 0, 0, 0]},
    "GRANDE": {"Costo": [3156.54, 3412.16, 3445.60, 3339.02, 3030.71, 1722.21, 1525.20, 1653.80, 0, 0, 0, 0], "Ore": [144.0, 153.0, 170.0, 146.0, 96.5, 0, 0, 0, 0, 0, 0, 0]},
    "DEJVI (luglio-sett.)": {"Costo": [0, 0, 0, 0, 0, 0, 1500.00, 1142.86, 0, 0, 0, 0], "Ore": [0, 0, 0, 0, 0, 0, 176.0, 128.5, 0, 0, 0, 0]}
}

mesi = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]

# --- DATI DETTAGLIATI CLIENTI ---
totale_reale_gen_ago = df_fat["Fatturato 2026"].head(8).sum()

df_clienti_principali = pd.DataFrame({
    "Cliente": [
        "WITTUR SPA", "SIDEL S.P.A.", "ACMI LABELLING SRL (ex SACMI)", "SILVI S.R.L.", 
        "GAMMA MECCANICA S.p.A", "ACMI BEVERAGE SPA (ex SACMI)", "CATTANI SPA", 
        "GEA MECHANICAL EQUIPMENT", "CALF SPA", "REGGIANA RIDUTTORI SRL", 
        "CSF INOX S.P.A.", "DIECI SRL", "ERRESSE Costmec", "JOHN BEAN TECHNOLOGIES", 
        "PRISMA S.P.A.", "I.E. PARK SRL"
    ],
    "Fatturato 2026 (Gen-Ago) (€)": [
        136922.00, 102256.14, 33484.00, 25690.50, 18740.00, 
        17577.00, 15372.00, 12218.00, 9133.00, 5238.00, 
        5175.00, 4603.50, 3273.00, 2640.00, 2227.50, 1860.00
    ],
    "Num Fatture": [19, 29, 6, 6, 6, 2, 7, 5, 3, 1, 3, 2, 1, 2, 2, 1],
})

somma_principali = df_clienti_principali["Fatturato 2026 (Gen-Ago) (€)"].sum()
quota_altri = totale_reale_gen_ago - somma_principali

df_altri = pd.DataFrame([{
    "Cliente": "ALTRI CLIENTI / MINORI",
    "Fatturato 2026 (Gen-Ago) (€)": quota_altri,
    "Num Fatture": 12
}])

df_clienti_2026 = pd.concat([df_clienti_principali, df_altri], ignore_index=True)

dati_clienti_mensili = {
    "WITTUR SPA": {"2026": [19638.0, 19653.0, 27121.5, 20090.5, 18483.0, 31936.0, 0.0, 0.0], "2025": [15561.0, 13911.5, 18000.0, 16500.0, 17800.0, 18200.0, 19500.0, 12000.0], "2024": [12000.0, 14000.0, 17547.0, 16000.0, 17804.5, 16500.0, 23948.5, 10000.0]},
    "SIDEL S.P.A.": {"2026": [10880.5, 12822.0, 16817.5, 16608.1, 19245.0, 20760.0, 5123.04, 0.0], "2025": [9078.0, 13487.31, 11200.0, 12500.0, 14000.0, 11800.0, 12900.0, 8000.0], "2024": [11000.0, 12500.0, 13000.0, 10500.0, 11800.0, 12200.0, 14000.0, 9500.0]},
    "ACMI BEVERAGE SPA (ex SACMI)": {"2026": [6784.0, 10195.0, 10793.0, 6524.0, 6100.0, 0.0, 0.0, 0.0], "2025": [11262.0, 9880.5, 9429.5, 11115.0, 10972.0, 14210.0, 9192.0, 5000.0], "2024": [8140.0, 10092.0, 6986.0, 7968.0, 14381.0, 16875.0, 14487.0, 6000.0]},
    "ACMI LABELLING SRL (ex SACMI)": {"2026": [3284.0, 6134.0, 3624.0, 4770.0, 9586.0, 0.0, 6386.0, 0.0], "2025": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "2024": [5465.0, 5248.0, 4929.0, 4248.0, 0.0, 0.0, 0.0, 0.0]},
    "CATTANI SPA": {"2026": [1918.0, 3290.0, 2674.0, 2996.0, 546.0, 1890.0, 2058.0, 0.0], "2025": [1400.0, 1386.0, 1330.0, 2156.0, 1694.0, 2618.0, 3234.0, 1200.0], "2024": [1512.0, 1148.0, 1946.0, 1428.0, 1848.0, 1022.0, 2170.0, 800.0]},
    "GAMMA MECCANICA S.p.A": {"2026": [1472.0, 480.0, 4868.0, 2832.0, 3264.0, 0.0, 2912.0, 0.0], "2025": [0.0, 2070.0, 4650.0, 1920.0, 0.0, 2280.0, 0.0, 0.0], "2024": [0.0, 0.0, 0.0, 2430.0, 4800.0, 2040.0, 0.0, 0.0]},
    "GEA MECHANICAL EQUIPMENT": {"2026": [0.0, 385.0, 840.0, 3795.0, 3268.0, 0.0, 1965.0, 0.0], "2025": [0.0, 0.0, 0.0, 0.0, 667.0, 0.0, 0.0, 0.0], "2024": [0.0, 0.0, 0.0, 0.0, 0.0, 703.5, 0.0, 0.0]},
    "CSF INOX S.P.A.": {"2026": [0.0, 0.0, 0.0, 0.0, 2295.0, 1680.0, 1200.0, 0.0], "2025": [1920.0, 1920.0, 1920.0, 1440.0, 720.0, 1200.0, 2160.0, 1000.0], "2024": [0.0, 0.0, 1455.0, 1920.0, 1170.0, 0.0, 2160.0, 500.0]},
    "DIECI SRL": {"2026": [0.0, 0.0, 0.0, 0.0, 0.0, 2790.0, 1813.50, 0.0], "2025": [3168.0, 1792.0, 2912.0, 2016.0, 2016.0, 0.0, 0.0, 0.0], "2024": [0.0, 980.0, 0.0, 3332.0, 7588.0, 3180.0, 4140.0, 1200.0]},
    "CALF SPA": {"2026": [4698.0, 4435.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "2025": [6061.0, 5017.0, 6365.5, 6742.5, 5408.5, 6612.0, 5814.5, 2000.0], "2024": [5026.0, 6149.5, 5908.0, 5110.0, 4018.0, 6734.0, 3976.0, 1500.0]},
}

if "cliente_selezionato" not in st.session_state:
    st.session_state["cliente_selezionato"] = "WITTUR SPA"

def layout_grafico_sintec(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1e1e1e", size=10),
        margin=dict(l=10, r=10, t=40, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)"
        ),
        xaxis=dict(tickangle=-45)
    )
    return fig

# --- SIDEBAR ---
st.sidebar.markdown("<h2 style='text-align: center; color: #ffffff;'>⚙️ <span style='color:#d9232a;'>SinTec</span> Menu</h2>", unsafe_allow_html=True)
sezione = st.sidebar.radio(
    "Navigazione Principale",
    ["📈 Dashboard Grafica", "🤖 Assistente IA (Testo e Voce)"]
)

# --- HEADER BRAND SINTEC ---
st.markdown(
    """
    <div class="brand-header">
        <div>
            <div class="brand-title"><span class="brand-accent">ST</span> SinTec</div>
            <div class="brand-sub">Sinergie Tecnologiche - Controllo di Gestione</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

if sezione == "📈 Dashboard Grafica":

    # METRICHE TOP DASHBOARD CON PREVISIONALE 12 MESI (SULLE 8 MENSILITA' AGOSTO INCLUSO)
    tot_f_26 = df_fat["Fatturato 2026"].head(8).sum()
    tot_f_25 = df_fat["Fatturato 2025"].head(8).sum()
    tot_f_25_tot = df_fat["Fatturato 2025"].sum()
    prev_f_26 = (tot_f_26 / 8) * 12
    delta_f = ((tot_f_26 - tot_f_25) / tot_f_25) * 100

    tot_c_26 = df_costi["Costi 2026"].head(8).sum() # € 300.837,80
    tot_c_25 = df_costi["Costi 2025"].head(8).sum() # € 295.004,36
    tot_c_25_tot = df_costi["Costi 2025"].sum()       # € 453.912,92
    prev_c_26 = (tot_c_26 / 8) * 12
    delta_c = ((tot_c_26 - tot_c_25) / tot_c_25) * 100

    mol_26 = tot_f_26 - tot_c_26
    mol_25 = tot_f_25 - tot_c_25
    mol_25_tot = tot_f_25_tot - tot_c_25_tot
    prev_mol_26 = prev_f_26 - prev_c_26
    delta_m = ((mol_26 - mol_25) / mol_25) * 100 if mol_25 != 0 else 0

    class_f = "kpi-delta-pos" if delta_f >= 0 else "kpi-delta-neg"
    class_c = "kpi-delta-neg" if delta_c >= 0 else "kpi-delta-pos"
    class_m = "kpi-delta-pos" if delta_m >= 0 else "kpi-delta-neg"

    col_k1, col_k2, col_k3 = st.columns(3)
    
    col_k1.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Fatturato Gen-Ago 2026</div>
        <div class="kpi-value">€ {tot_f_26:,.2f}</div>
        <div class="kpi-subtitle">Gen-Ago 2025: <b>€ {tot_f_25:,.2f}</b> <span class="{class_f}">({delta_f:+.1f}%)</span></div>
        <div class="kpi-subtitle">Previsionale 12M 2026: <b>€ {prev_f_26:,.2f}</b></div>
        <div class="kpi-subtitle">Totale Anno 2025: <b>€ {tot_f_25_tot:,.2f}</b></div>
    </div>
    ''', unsafe_allow_html=True)

    col_k2.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Costi Personale Gen-Ago 2026</div>
        <div class="kpi-value" style="color:#d9232a;">€ {tot_c_26:,.2f}</div>
        <div class="kpi-subtitle">Gen-Ago 2025: <b>€ {tot_c_25:,.2f}</b> <span class="{class_c}">({delta_c:+.1f}%)</span></div>
        <div class="kpi-subtitle">Previsionale 12M 2026: <b>€ {prev_c_26:,.2f}</b></div>
        <div class="kpi-subtitle">Totale Anno 2025: <b>€ {tot_c_25_tot:,.2f}</b></div>
    </div>
    ''', unsafe_allow_html=True)

    col_k3.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Margine Operativo Gen-Ago 2026</div>
        <div class="kpi-value" style="color:#16a34a;">€ {mol_26:,.2f}</div>
        <div class="kpi-subtitle">Gen-Ago 2025: <b>€ {mol_25:,.2f}</b> <span class="{class_m}">({delta_m:+.1f}%)</span></div>
        <div class="kpi-subtitle">Previsionale 12M 2026: <b>€ {prev_mol_26:,.2f}</b></div>
        <div class="kpi-subtitle">Totale Anno 2025: <b>€ {mol_25_tot:,.2f}</b></div>
    </div>
    ''', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "📊 Confronto Fatturato",
        "👥 Costi Personale",
        "⏱️ Ore Dirette",
        "⚙️ Ore Indirette",
        "💶 Media Oraria",
        "📋 Dettaglio Dipendenti",
        "🍕 Analisi Clienti"
    ])

    # TAB 1: FATTURATO
    with t1:
        st.subheader("📊 Confronto Fatturato Mensile Generale")
        
        f_26_tot_m = df_fat["Fatturato 2026"].sum()
        f_25_tot_m = df_fat["Fatturato 2025"].sum()
        f_24_tot_m = df_fat["Fatturato 2024"].sum()
        f_26_prev_m = (f_26_tot_m / 8) * 12
        
        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        c_f1.markdown(f'<div class="kpi-card"><div class="kpi-title">Fatturato YTD 2026</div><div class="kpi-value">€ {f_26_tot_m:,.2f}</div><div class="kpi-subtitle">Gen-Ago 2026 (8M)</div></div>', unsafe_allow_html=True)
        c_f2.markdown(f'<div class="kpi-card"><div class="kpi-title">Previsionale 12M 2026</div><div class="kpi-value" style="color:#2563eb;">€ {f_26_prev_m:,.2f}</div><div class="kpi-subtitle">Proiezione su 12 Mesi</div></div>', unsafe_allow_html=True)
        c_f3.markdown(f'<div class="kpi-card"><div class="kpi-title">Totale Fatturato 2025</div><div class="kpi-value">€ {f_25_tot_m:,.2f}</div><div class="kpi-subtitle">12 Mesi Completi</div></div>', unsafe_allow_html=True)
        c_f4.markdown(f'<div class="kpi-card"><div class="kpi-title">Totale Fatturato 2024</div><div class="kpi-value">€ {f_24_tot_m:,.2f}</div><div class="kpi-subtitle">12 Mesi Completi</div></div>', unsafe_allow_html=True)

        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=["Fatturato 2026", "Fatturato 2025", "Fatturato 2024"],
            barmode="group",
            title="Andamento Fatturato Mensile (€)",
            color_discrete_sequence=["#d9232a", "#1e1e1e", "#999999"],
            text_auto=",.0f"
        )
        max_val = df_fat[["Fatturato 2026", "Fatturato 2025", "Fatturato 2024"]].max().max()
        fig_f.update_traces(textposition="outside", textfont_size=8)
        fig_f.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_sintec(fig_f), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Fatturato (€)")
        df_fat_tot = pd.concat([
            df_fat,
            pd.DataFrame([{
                "Mese": "TOTALE YTD (8M)",
                "Fatturato 2026": f_26_tot_m,
                "Fatturato 2025": tot_f_25,
                "Fatturato 2024": df_fat["Fatturato 2024"].head(8).sum()
            }]),
            pd.DataFrame([{
                "Mese": "PREVISIONALE 12M 2026",
                "Fatturato 2026": f_26_prev_m,
                "Fatturato 2025": f_25_tot_m,
                "Fatturato 2024": f_24_tot_m
            }])
        ], ignore_index=True)

        st.dataframe(
            df_fat_tot.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                "Fatturato 2026": "€ {:,.2f}",
                "Fatturato 2025": "€ {:,.2f}",
                "Fatturato 2024": "€ {:,.2f}"
            }),
            use_container_width=True
        )

    # TAB 2: COSTI PERSONALE
    with t2:
        st.subheader("👥 Costi Personale Mensili e Dettaglio Singolo Dipendente")
        
        c_26_tot_m = df_costi["Costi 2026"].sum()
        c_25_tot_m = df_costi["Costi 2025"].sum()
        c_24_tot_m = df_costi["Costi 2024"].sum()
        c_26_prev_m = (c_26_tot_m / 8) * 12

        c_c1, c_c2, c_c3, c_c4 = st.columns(4)
        c_c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Costi YTD 2026</div><div class="kpi-value" style="color:#d9232a;">€ {c_26_tot_m:,.2f}</div><div class="kpi-subtitle">Gen-Ago 2026 (8M)</div></div>', unsafe_allow_html=True)
        c_c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Previsionale 12M 2026</div><div class="kpi-value" style="color:#d9232a;">€ {c_26_prev_m:,.2f}</div><div class="kpi-subtitle">Proiezione su 12 Mesi</div></div>', unsafe_allow_html=True)
        c_c3.markdown(f'<div class="kpi-card"><div class="kpi-title">Totale Costi 2025</div><div class="kpi-value">€ {c_25_tot_m:,.2f}</div><div class="kpi-subtitle">12 Mesi Completi</div></div>', unsafe_allow_html=True)
        c_c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Totale Costi 2024</div><div class="kpi-value">€ {c_24_tot_m:,.2f}</div><div class="kpi-subtitle">12 Mesi Completi</div></div>', unsafe_allow_html=True)

        fig_c = px.bar(
            df_costi,
            x="Mese",
            y=["Costi 2026", "Costi 2025", "Costi 2024"],
            barmode="group",
            title="Andamento Costi Personale Complessivi (€)",
            color_discrete_sequence=["#d9232a", "#1e1e1e", "#999999"],
            text_auto=",.0f"
        )
        max_val = df_costi[["Costi 2026", "Costi 2025", "Costi 2024"]].max().max()
        fig_c.update_traces(textposition="outside", textfont_size=8)
        fig_c.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_sintec(fig_c), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Costi Personale (€)")
        df_costi_tot = pd.concat([
            df_costi,
            pd.DataFrame([{
                "Mese": "TOTALE YTD (8M)",
                "Costi 2026": c_26_tot_m,
                "Costi 2025": tot_c_25,
                "Costi 2024": df_costi["Costi 2024"].head(8).sum()
            }]),
            pd.DataFrame([{
                "Mese": "PREVISIONALE 12M 2026",
                "Costi 2026": c_26_prev_m,
                "Costi 2025": c_25_tot_m,
                "Costi 2024": c_24_tot_m
            }])
        ], ignore_index=True)

        st.dataframe(
            df_costi_tot.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                "Costi 2026": "€ {:,.2f}",
                "Costi 2025": "€ {:,.2f}",
                "Costi 2024": "€ {:,.2f}"
            }),
            use_container_width=True
        )

        st.markdown("---")
        st.subheader("🔎 Filtra per Singolo Dipendente nella Scheda Costi")
        dip_scelto_tab2 = st.selectbox("Seleziona Dipendente da Analizzare:", list(dati_dipendenti_mensili.keys()), key="select_dip_tab2")

        df_dip_t2 = pd.DataFrame({
            "Mese": mesi,
            "Costo Totale (€)": dati_dipendenti_mensili[dip_scelto_tab2]["Costo"],
            "Ore Totali": dati_dipendenti_mensili[dip_scelto_tab2]["Ore"]
        })
        df_dip_t2["Costo Orario (€/h)"] = (df_dip_t2["Costo Totale (€)"] / df_dip_t2["Ore Totali"]).fillna(0).round(2)

        tot_c_dip2 = df_dip_t2["Costo Totale (€)"].sum()
        tot_o_dip2 = df_dip_t2["Ore Totali"].sum()
        med_co_dip2 = (tot_c_dip2 / tot_o_dip2) if tot_o_dip2 > 0 else 0
        prev_c_dip2 = (tot_c_dip2 / 8) * 12

        col_dt1, col_dt2 = st.columns([1, 1.2])

        with col_dt1:
            st.markdown(f"#### 📄 Dettaglio Costi e Ore: **{dip_scelto_tab2}**")
            df_dip_tot2 = pd.concat([
                df_dip_t2,
                pd.DataFrame([{
                    "Mese": "TOTALE YTD (8M)",
                    "Costo Totale (€)": tot_c_dip2,
                    "Ore Totali": tot_o_dip2,
                    "Costo Orario (€/h)": med_co_dip2
                }]),
                pd.DataFrame([{
                    "Mese": "PREVISIONALE 12M 2026",
                    "Costo Totale (€)": prev_c_dip2,
                    "Ore Totali": (tot_o_dip2 / 8) * 12,
                    "Costo Orario (€/h)": med_co_dip2
                }])
            ], ignore_index=True)

            st.dataframe(
                df_dip_tot2.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                    "Costo Totale (€)": "€ {:,.2f}",
                    "Ore Totali": "{:,.1f} h",
                    "Costo Orario (€/h)": "€ {:,.2f}"
                }),
                use_container_width=True
            )

        with col_dt2:
            fig_dip2 = px.bar(
                df_dip_t2[df_dip_t2["Ore Totali"] > 0],
                x="Mese",
                y="Costo Totale (€)",
                text_auto=",.0f",
                color_discrete_sequence=["#d9232a"],
                title=f"Andamento Mensile Costi - {dip_scelto_tab2}"
            )
            max_val = df_dip_t2["Costo Totale (€)"].max()
            fig_dip2.update_traces(textposition="outside", textfont_size=8)
            fig_dip2.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
            st.plotly_chart(layout_grafico_sintec(fig_dip2), use_container_width=True)

    # TAB 3: ORE DIRETTE
    with t3:
        st.subheader("⏱️ Ore Dirette Lavorate")
        
        od_26_tot = df_ore_dirette["Ore Dirette 2026"].sum()
        od_25_tot = df_ore_dirette["Ore Dirette 2025"].sum()
        od_26_prev = (od_26_tot / 8) * 12

        c_od1, c_od2, c_od3 = st.columns(3)
        c_od1.markdown(f'<div class="kpi-card"><div class="kpi-title">Ore Dirette YTD 2026</div><div class="kpi-value" style="color:#16a34a;">{od_26_tot:,.1f} h</div><div class="kpi-subtitle">Gen-Ago 2026</div></div>', unsafe_allow_html=True)
        c_od2.markdown(f'<div class="kpi-card"><div class="kpi-title">Previsionale 12M 2026</div><div class="kpi-value" style="color:#16a34a;">{od_26_prev:,.1f} h</div><div class="kpi-subtitle">Proiezione su 12 Mesi</div></div>', unsafe_allow_html=True)
        c_od3.markdown(f'<div class="kpi-card"><div class="kpi-title">Totale Ore Dirette 2025</div><div class="kpi-value">{od_25_tot:,.1f} h</div><div class="kpi-subtitle">12 Mesi Completi</div></div>', unsafe_allow_html=True)

        fig_dir = px.bar(
            df_ore_dirette,
            x="Mese",
            y=["Ore Dirette 2026", "Ore Dirette 2025"],
            barmode="group",
            title="Ore Dirette (h)",
            color_discrete_sequence=["#16a34a", "#86efac"],
            text_auto=",.0f"
        )
        max_val = df_ore_dirette[["Ore Dirette 2026", "Ore Dirette 2025"]].max().max()
        fig_dir.update_traces(textposition="outside", textfont_size=8)
        fig_dir.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_sintec(fig_dir), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Ore Dirette (h)")
        df_ore_dir_tot = pd.concat([
            df_ore_dirette,
            pd.DataFrame([{
                "Mese": "TOTALE YTD (8M)",
                "Ore Dirette 2026": od_26_tot,
                "Ore Dirette 2025": df_ore_dirette["Ore Dirette 2025"].head(8).sum()
            }]),
            pd.DataFrame([{
                "Mese": "PREVISIONALE 12M 2026",
                "Ore Dirette 2026": od_26_prev,
                "Ore Dirette 2025": od_25_tot
            }])
        ], ignore_index=True)

        st.dataframe(
            df_ore_dir_tot.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                "Ore Dirette 2026": "{:,.1f} h",
                "Ore Dirette 2025": "{:,.1f} h"
            }),
            use_container_width=True
        )

    # TAB 4: ORE INDIRETTE
    with t4:
        st.subheader("⚙️ Ore Indirette (Gestione/Struttura)")
        
        oi_26_tot = df_ore_indirette["Ore Indirette 2026"].sum()
        oi_25_tot = df_ore_indirette["Ore Indirette 2025"].sum()
        oi_26_prev = (oi_26_tot / 8) * 12

        c_oi1, c_oi2, c_oi3 = st.columns(3)
        c_oi1.markdown(f'<div class="kpi-card"><div class="kpi-title">Ore Indirette YTD 2026</div><div class="kpi-value" style="color:#d97706;">{oi_26_tot:,.1f} h</div><div class="kpi-subtitle">Gen-Ago 2026</div></div>', unsafe_allow_html=True)
        c_oi2.markdown(f'<div class="kpi-card"><div class="kpi-title">Previsionale 12M 2026</div><div class="kpi-value" style="color:#d97706;">{oi_26_prev:,.1f} h</div><div class="kpi-subtitle">Proiezione su 12 Mesi</div></div>', unsafe_allow_html=True)
        c_oi3.markdown(f'<div class="kpi-card"><div class="kpi-title">Totale Ore Indirette 2025</div><div class="kpi-value">{oi_25_tot:,.1f} h</div><div class="kpi-subtitle">12 Mesi Completi</div></div>', unsafe_allow_html=True)

        fig_ind = px.bar(
            df_ore_indirette,
            x="Mese",
            y=["Ore Indirette 2026", "Ore Indirette 2025"],
            barmode="group",
            title="Ore Indirette (h)",
            color_discrete_sequence=["#d97706", "#fde047"],
            text_auto=",.0f"
        )
        max_val = df_ore_indirette[["Ore Indirette 2026", "Ore Indirette 2025"]].max().max()
        fig_ind.update_traces(textposition="outside", textfont_size=8)
        fig_ind.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_sintec(fig_ind), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Ore Indirette (h)")
        df_ore_ind_tot = pd.concat([
            df_ore_indirette,
            pd.DataFrame([{
                "Mese": "TOTALE YTD (8M)",
                "Ore Indirette 2026": oi_26_tot,
                "Ore Indirette 2025": df_ore_indirette["Ore Indirette 2025"].head(8).sum()
            }]),
            pd.DataFrame([{
                "Mese": "PREVISIONALE 12M 2026",
                "Ore Indirette 2026": oi_26_prev,
                "Ore Indirette 2025": oi_25_tot
            }])
        ], ignore_index=True)

        st.dataframe(
            df_ore_ind_tot.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                "Ore Indirette 2026": "{:,.1f} h",
                "Ore Indirette 2025": "{:,.1f} h"
            }),
            use_container_width=True
        )

    # TAB 5: MEDIA ORARIA
    with t5:
        st.subheader("💶 Media Oraria (Fatturato / Ore Totali)")
        
        mo_26_med = df_media_oraria["Media Oraria 2026"][df_media_oraria["Media Oraria 2026"] > 0].mean()
        mo_25_med = df_media_oraria["Media Oraria 2025"][df_media_oraria["Media Oraria 2025"] > 0].mean()
        mo_24_med = df_media_oraria["Media Oraria 2024"][df_media_oraria["Media Oraria 2024"] > 0].mean()

        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.markdown(f'<div class="kpi-card"><div class="kpi-title">Media Oraria 2026</div><div class="kpi-value" style="color:#9333ea;">€ {mo_26_med:,.2f}/h</div><div class="kpi-subtitle">Media Gen-Ago 2026</div></div>', unsafe_allow_html=True)
        c_m2.markdown(f'<div class="kpi-card"><div class="kpi-title">Media Oraria 2025</div><div class="kpi-value">€ {mo_25_med:,.2f}/h</div><div class="kpi-subtitle">Media Anno 2025</div></div>', unsafe_allow_html=True)
        c_m3.markdown(f'<div class="kpi-card"><div class="kpi-title">Media Oraria 2024</div><div class="kpi-value">€ {mo_24_med:,.2f}/h</div><div class="kpi-subtitle">Media Anno 2024</div></div>', unsafe_allow_html=True)

        fig_media = px.bar(
            df_media_oraria,
            x="Mese",
            y=["Media Oraria 2026", "Media Oraria 2025", "Media Oraria 2024"],
            barmode="group",
            title="Media Oraria (€/h)",
            color_discrete_sequence=["#d9232a", "#1e1e1e", "#999999"],
            text_auto=",.1f"
        )
        max_val = df_media_oraria[["Media Oraria 2026", "Media Oraria 2025", "Media Oraria 2024"]].max().max()
        fig_media.update_traces(textposition="outside", textfont_size=8)
        fig_media.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_sintec(fig_media), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Media Oraria (€/h)")
        df_media_tot = pd.concat([
            df_media_oraria,
            pd.DataFrame([{
                "Mese": "TOTALE MEDIA",
                "Media Oraria 2026": mo_26_med,
                "Media Oraria 2025": mo_25_med,
                "Media Oraria 2024": mo_24_med
            }])
        ], ignore_index=True)

        st.dataframe(
            df_media_tot.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                "Media Oraria 2026": "€ {:,.2f}",
                "Media Oraria 2025": "€ {:,.2f}",
                "Media Oraria 2024": "€ {:,.2f}"
            }),
            use_container_width=True
        )

    # TAB 6: DETTAGLIO DIPENDENTI
    with t6:
        st.subheader("📋 Totale Parziale 2026 (Gen-Ago) - Costi e Ore Personale")
        st.dataframe(
            df_riassunto_2026.style.apply(evidenzia_totale, col_chiave="COGNOME", axis=1).format({
                "COSTO TOT": "€ {:,.2f}",
                "ORE TOT": "{:,.1f}",
                "COSTO ORARIO": "€ {:,.2f}"
            }),
            use_container_width=True,
            height=380
        )

        st.markdown("---")
        st.subheader("🔎 Dettaglio Mensile Dipendente")
        dip_scelto = st.selectbox("Seleziona Dipendente:", list(dati_dipendenti_mensili.keys()), key="select_dip_tab6")

        df_dip = pd.DataFrame({
            "Mese": mesi,
            "Costo Totale (€)": dati_dipendenti_mensili[dip_scelto]["Costo"],
            "Ore Totali": dati_dipendenti_mensili[dip_scelto]["Ore"]
        })
        df_dip["Costo Orario (€/h)"] = (df_dip["Costo Totale (€)"] / df_dip["Ore Totali"]).fillna(0).round(2)

        tot_c_dip = df_dip["Costo Totale (€)"].sum()
        tot_o_dip = df_dip["Ore Totali"].sum()
        med_co_dip = (tot_c_dip / tot_o_dip) if tot_o_dip > 0 else 0
        prev_c_dip = (tot_c_dip / 8) * 12

        c_d1, c_d2, c_d3, c_d4 = st.columns(4)
        c_d1.markdown(f'<div class="kpi-card"><div class="kpi-title">Costo YTD 2026</div><div class="kpi-value">€ {tot_c_dip:,.2f}</div><div class="kpi-subtitle">{dip_scelto} (Gen-Ago)</div></div>', unsafe_allow_html=True)
        c_d2.markdown(f'<div class="kpi-card"><div class="kpi-title">Previsionale 12M</div><div class="kpi-value" style="color:#d9232a;">€ {prev_c_dip:,.2f}</div><div class="kpi-subtitle">Proiezione 2026</div></div>', unsafe_allow_html=True)
        c_d3.markdown(f'<div class="kpi-card"><div class="kpi-title">Ore Totali YTD</div><div class="kpi-value">{tot_o_dip:,.1f} h</div><div class="kpi-subtitle">{dip_scelto} (Gen-Ago)</div></div>', unsafe_allow_html=True)
        c_d4.markdown(f'<div class="kpi-card"><div class="kpi-title">Costo Orario Medio</div><div class="kpi-value">€ {med_co_dip:,.2f}/h</div><div class="kpi-subtitle">{dip_scelto} (Gen-Ago)</div></div>', unsafe_allow_html=True)

        fig_dip = px.bar(
            df_dip[df_dip["Ore Totali"] > 0],
            x="Mese",
            y="Costo Totale (€)",
            text_auto=",.0f",
            color_discrete_sequence=["#d9232a"],
            title=f"Andamento Mensile Costi - {dip_scelto}"
        )
        max_val = df_dip["Costo Totale (€)"].max()
        fig_dip.update_traces(textposition="outside", textfont_size=8)
        fig_dip.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_sintec(fig_dip), use_container_width=True)

        st.markdown(f"#### 📋 Tabella Dati Mensili - {dip_scelto}")
        df_dip_tot = pd.concat([
            df_dip,
            pd.DataFrame([{
                "Mese": "TOTALE YTD (8M)",
                "Costo Totale (€)": tot_c_dip,
                "Ore Totali": tot_o_dip,
                "Costo Orario (€/h)": med_co_dip
            }]),
            pd.DataFrame([{
                "Mese": "PREVISIONALE 12M 2026",
                "Costo Totale (€)": prev_c_dip,
                "Ore Totali": (tot_o_dip / 8) * 12,
                "Costo Orario (€/h)": med_co_dip
            }])
        ], ignore_index=True)

        st.dataframe(
            df_dip_tot.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                "Costo Totale (€)": "€ {:,.2f}",
                "Ore Totali": "{:,.1f} h",
                "Costo Orario (€/h)": "€ {:,.2f}"
            }),
            use_container_width=True
        )

    # TAB 7: ANALISI CLIENTI
    with t7:
        st.subheader("🍕 Analisi e Classifica Fatturato Clienti (Gen-Ago 2026)")

        col_p1, col_p2 = st.columns([1.1, 1])

        with col_p1:
            fig_pie = px.pie(
                df_clienti_2026,
                values="Fatturato 2026 (Gen-Ago) (€)",
                names="Cliente",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
                title="Quota % Fatturato per Cliente"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')

            selected_pie = st.plotly_chart(
                layout_grafico_sintec(fig_pie),
                use_container_width=True,
                on_select="rerun",
                selection_mode="points"
            )

            if selected_pie and "selection" in selected_pie:
                points = selected_pie["selection"].get("points", [])
                if points:
                    cli_cliccato = points[0].get("label")
                    if cli_cliccato in dati_clienti_mensili:
                        st.session_state["cliente_selezionato"] = cli_cliccato

        with col_p2:
            st.markdown("#### 🏆 Tabella Riepilogativa Clienti")
            df_cli_s = df_clienti_2026.sort_values(by="Fatturato 2026 (Gen-Ago) (€)", ascending=False).reset_index(drop=True)
            tot_cli = df_cli_s["Fatturato 2026 (Gen-Ago) (€)"].sum()
            df_cli_s["% Quota"] = (df_cli_s["Fatturato 2026 (Gen-Ago) (€)"] / tot_cli * 100).round(2)

            df_tot_riga = pd.DataFrame([{
                "Cliente": "TOTALE FATTURATO",
                "Fatturato 2026 (Gen-Ago) (€)": tot_cli,
                "Num Fatture": df_cli_s["Num Fatture"].sum(),
                "% Quota": 100.00
            }])
            df_cli_completo = pd.concat([df_cli_s, df_tot_riga], ignore_index=True)

            st.dataframe(
                df_cli_completo.style.apply(evidenzia_totale, col_chiave="Cliente", axis=1).format({
                    "Fatturato 2026 (Gen-Ago) (€)": "€ {:,.2f}",
                    "% Quota": "{:.2f} %"
                }),
                use_container_width=True,
                height=350
            )

        st.markdown("---")
        st.subheader("🔎 Dettaglio Mensile e Storico per Singolo Cliente")

        idx_default = list(dati_clienti_mensili.keys()).index(st.session_state["cliente_selezionato"]) if st.session_state["cliente_selezionato"] in dati_clienti_mensili else 0

        cli_scelto = st.selectbox(
            "Seleziona Cliente da Verificare:",
            list(dati_clienti_mensili.keys()),
            index=idx_default,
            key="select_cli_box"
        )

        st.session_state["cliente_selezionato"] = cli_scelto

        tot_2026 = sum(dati_clienti_mensili[cli_scelto]["2026"])
        tot_2025 = sum(dati_clienti_mensili[cli_scelto]["2025"])
        tot_2024 = sum(dati_clienti_mensili[cli_scelto]["2024"])
        prev_2026_cli = (tot_2026 / 8) * 12

        c_cli1, c_cli2, c_cli3, c_cli4 = st.columns(4)
        c_cli1.markdown(f'<div class="kpi-card"><div class="kpi-title">Fatturato 2026 YTD</div><div class="kpi-value">€ {tot_2026:,.2f}</div><div class="kpi-subtitle">{cli_scelto} (Gen-Ago)</div></div>', unsafe_allow_html=True)
        c_cli2.markdown(f'<div class="kpi-card"><div class="kpi-title">Previsionale 12M 2026</div><div class="kpi-value" style="color:#d9232a;">€ {prev_2026_cli:,.2f}</div><div class="kpi-subtitle">Proiezione su 12 Mesi</div></div>', unsafe_allow_html=True)
        c_cli3.markdown(f'<div class="kpi-card"><div class="kpi-title">Fatturato 2025 YTD</div><div class="kpi-value">€ {tot_2025:,.2f}</div><div class="kpi-subtitle">{cli_scelto} (Gen-Ago)</div></div>', unsafe_allow_html=True)
        c_cli4.markdown(f'<div class="kpi-card"><div class="kpi-title">Fatturato 2024 YTD</div><div class="kpi-value">€ {tot_2024:,.2f}</div><div class="kpi-subtitle">{cli_scelto} (Gen-Ago)</div></div>', unsafe_allow_html=True)

        df_cli_m = pd.DataFrame({
            "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago"],
            "2026 (€)": dati_clienti_mensili[cli_scelto]["2026"],
            "2025 (€)": dati_clienti_mensili[cli_scelto]["2025"],
            "2024 (€)": dati_clienti_mensili[cli_scelto]["2024"],
        })

        df_tot_cliente = pd.DataFrame([{
            "Mese": "TOTALE YTD (8M)",
            "2026 (€)": tot_2026,
            "2025 (€)": tot_2025,
            "2024 (€)": tot_2024
        }])

        df_prev_cliente = pd.DataFrame([{
            "Mese": "PREVISIONALE 12M 2026",
            "2026 (€)": prev_2026_cli,
            "2025 (€)": tot_2025,
            "2024 (€)": tot_2024
        }])

        df_cli_m_tot = pd.concat([df_cli_m, df_tot_cliente, df_prev_cliente], ignore_index=True)

        col_t1, col_t2 = st.columns([1, 1.2])

        with col_t1:
            st.markdown(f"#### 📄 Dettagli & Totale: **{cli_scelto}**")
            st.dataframe(
                df_cli_m_tot.style.apply(evidenzia_totale, col_chiave="Mese", axis=1).format({
                    "2026 (€)": "€ {:,.2f}",
                    "2025 (€)": "€ {:,.2f}",
                    "2024 (€)": "€ {:,.2f}"
                }),
                use_container_width=True
            )

        with col_t2:
            fig_cli_m = px.bar(
                df_cli_m,
                x="Mese",
                y=["2026 (€)", "2025 (€)", "2024 (€)"],
                barmode="group",
                title=f"Confronto Storico Mensile: {cli_scelto}",
                color_discrete_sequence=["#d9232a", "#1e1e1e", "#999999"]
            )
            st.plotly_chart(layout_grafico_sintec(fig_cli_m), use_container_width=True)

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    domanda = st.text_input("Chiedi all'Assistente sui dati o sui clienti (es. Wittur, Sidel, ACMI/SACMI, etc.):")
    if domanda and "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sei l'assistente per il controllo di gestione di Sintec S.r.l. "
                        "Nota importante sui dati: la ragione sociale 'ACMI' (es. ACMI BEVERAGE SPA, ACMI LABELLING SRL) "
                        "negli storici contabili precedenti era registrata come 'SACMI' (SACMI BEVERAGE SPA, SACMI VERONA S.P.A.). "
                        "Considerale come la stessa entità cliente quando analizzi o rispondi."
                    )
                },
                {"role": "user", "content": domanda}
            ]
        )
        st.success(res.choices[0].message.content)