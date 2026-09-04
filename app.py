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

# --- STILE TEMA CHIARO E RESPONSIVE MOBILE ---
st.markdown(
    """
<style>
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0f172a;
    }
    .kpi-subtitle {
        font-size: 0.75rem;
        color: #475569;
        margin-top: 4px;
    }
    .kpi-delta-pos {
        color: #16a34a;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .kpi-delta-neg {
        color: #e11d48;
        font-weight: 700;
        font-size: 0.75rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f1f5f9;
        padding: 4px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        overflow-x: auto;
        white-space: nowrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 6px;
        color: #475569;
        font-weight: 600;
        border: none;
        padding: 0 12px;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }

    @media (max-width: 768px) {
        .kpi-card {
            padding: 12px;
            margin-bottom: 8px;
        }
        .kpi-title {
            font-size: 0.7rem;
        }
        .kpi-value {
            font-size: 1.2rem;
        }
        .kpi-subtitle {
            font-size: 0.7rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0 8px;
            font-size: 0.75rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- FUNZIONE STILE RIGHE DI TOTALE ---
def evidenzia_totale(row, col_chiave="Mese"):
    if str(row[col_chiave]).upper() in ["TOTALE", "TOTALE FATTURATO", "TOTALE SINTEC (MEDIA GEN-LUG)"]:
        return ['background-color: #dbeafe; font-weight: bold; color: #1e40af'] * len(row)
    return [''] * len(row)

# --- LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown(
        "<div style='text-align: center; margin-top: 30px;'><h1 style='color:#0f172a; font-size: 1.8rem;'>🔒 Accesso Riservato</h1><p style='color: #64748b;'>Sintec S.r.l. - Controllo di Gestione</p></div>",
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

# --- DATI GENERALI (ORDINATI: 2026, 2025, 2024) ---
df_fat = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Fatturato 2026": [58570.50, 73584.46, 75642.00, 70202.10, 65023.99, 80642.35, 66484.43, 0, 0, 0, 0, 0],
    "Fatturato 2025": [57401.50, 62787.31, 72682.00, 68541.53, 71101.00, 73161.79, 64458.50, 35609.42, 84284.50, 82004.21, 64778.43, 64324.52],
    "Fatturato 2024": [57247.00, 68184.47, 80810.80, 68999.64, 87666.00, 70416.50, 88701.60, 48356.50, 73093.20, 89233.76, 72332.50, 57421.08],
})

df_costi = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Costi 2026": [34104.88, 40913.02, 39960.05, 39848.93, 41854.30, 38761.35, 32574.31, 0, 0, 0, 0, 0],
    "Costi 2025": [32409.91, 36319.18, 36075.82, 38017.47, 41233.54, 42390.51, 36236.41, 26967.94, 39929.42, 40450.24, 41594.63, 36510.16],
    "Costi 2024": [30359.58, 34197.57, 43005.65, 40156.84, 43703.97, 44361.46, 32676.33, 36758.37, 42287.59, 40908.77, 36832.46, 46703.16],
})

df_ore_dirette = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Ore Dirette 2026": [1788.0, 2108.5, 2102.5, 2020.5, 2118.5, 2027.0, 1949.0, 0, 0, 0, 0, 0],
    "Ore Dirette 2025": [2017.0, 2087.0, 2317.5, 2155.5, 2251.5, 2221.0, 2084.0, 1308.0, 2454.0, 2355.0, 2134.0, 1641.5],
})

df_ore_indirette = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Ore Indirette 2026": [156.0, 237.0, 327.0, 222.0, 220.5, 134.0, 188.5, 0, 0, 0, 0, 0],
    "Ore Indirette 2025": [193.0, 137.0, 81.5, 112.5, 155.5, 126.5, 97.5, 65.0, 163.5, 145.5, 124.5, 171.0],
})

df_media_oraria = pd.DataFrame({
    "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "Media Oraria 2026": [30.13, 31.37, 31.13, 31.31, 27.80, 37.32, 31.10, 0, 0, 0, 0, 0],
    "Media Oraria 2025": [25.97, 28.23, 30.30, 30.22, 29.54, 31.17, 29.55, 25.94, 32.20, 32.80, 28.68, 35.49],
    "Media Oraria 2024": [25.98, 27.17, 30.29, 27.78, 28.50, 26.28, 30.74, 27.24, 29.82, 31.52, 27.52, 30.05],
})

# --- DATI DIPENDENTI 2026 ---
df_riassunto_2026 = pd.DataFrame({
    "COGNOME": ["D'ALSAZIA", "BASSISSI", "CASELLI", "LANZI", "GUION", "CAMPANINI", "JOHNSON", "RASENTI", "MAGNO", "SCANO", "PETRO'", "GRANDE", "DEJVI (luglio-sett.)", "TOTALE SINTEC (MEDIA GEN-LUG)"],
    "COSTO TOT": [25885.34, 15535.51, 25770.31, 22431.26, 11440.63, 24780.83, 20065.46, 35537.75, 23986.59, 23853.41, 19098.31, 19631.44, 2642.86, 270659.70],
    "ORE TOT": [1222.5, 1186.5, 1017.0, 1166.5, 741.0, 1203.0, 1033.5, 1341.0, 1207.5, 960.0, 1154.5, 709.5, 304.5, 13247.0],
    "COSTO ORARIO": [21.17, 13.09, 25.34, 19.23, 15.44, 20.60, 19.42, 26.50, 19.86, 24.85, 16.54, 27.67, 8.68, 20.43],
})

dati_dipendenti_mensili = {
    "D'ALSAZIA": {"Costo": [3693.39, 3960.66, 3857.07, 3922.04, 3889.52, 4007.63, 2555.03, 0, 0, 0, 0, 0], "Ore": [150.5, 166.5, 172.5, 168.5, 163.0, 168.0, 105.5, 0, 0, 0, 0, 0]},
    "BASSISSI": {"Costo": [2169.70, 2337.50, 2361.92, 2332.02, 2406.59, 2407.38, 1520.40, 0, 0, 0, 0, 0], "Ore": [143.5, 160.0, 176.0, 168.0, 158.0, 157.0, 96.0, 0, 0, 0, 0, 0]},
    "CASELLI": {"Costo": [3504.50, 3749.44, 4035.38, 4073.36, 3925.75, 3846.69, 2635.19, 0, 0, 0, 0, 0], "Ore": [125.0, 140.0, 151.0, 129.5, 137.5, 141.0, 86.0, 0, 0, 0, 0, 0]},
    "LANZI": {"Costo": [2949.79, 3225.64, 3455.40, 3518.32, 3244.59, 3093.37, 2944.15, 0, 0, 0, 0, 0], "Ore": [137.0, 157.5, 175.0, 167.0, 150.5, 144.0, 152.0, 0, 0, 0, 0, 0]},
}

mesi = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]

# --- DATI DETTAGLIATI CLIENTI ---
totale_reale_gen_lug = df_fat["Fatturato 2026"].sum()

df_clienti_principali = pd.DataFrame({
    "Cliente": [
        "WITTUR SPA", "SIDEL S.P.A.", "ACMI LABELLING SRL (ex SACMI)", "SILVI S.R.L.", 
        "GAMMA MECCANICA S.p.A", "ACMI BEVERAGE SPA (ex SACMI)", "CATTANI SPA", 
        "GEA MECHANICAL EQUIPMENT", "CALF SPA", "REGGIANA RIDUTTORI SRL", 
        "CSF INOX S.P.A.", "DIECI SRL", "ERRESSE Costmec", "JOHN BEAN TECHNOLOGIES", 
        "PRISMA S.P.A.", "I.E. PARK SRL"
    ],
    "Fatturato 2026 (Gen-Lug) (€)": [
        136922.00, 102256.14, 33484.00, 25690.50, 18740.00, 
        17577.00, 15372.00, 12218.00, 9133.00, 5238.00, 
        5175.00, 4603.50, 3273.00, 2640.00, 2227.50, 1860.00
    ],
    "Num Fatture": [19, 29, 6, 6, 6, 2, 7, 5, 3, 1, 3, 2, 1, 2, 2, 1],
})

somma_principali = df_clienti_principali["Fatturato 2026 (Gen-Lug) (€)"].sum()
quota_altri = totale_reale_gen_lug - somma_principali

df_altri = pd.DataFrame([{
    "Cliente": "ALTRI CLIENTI / MINORI",
    "Fatturato 2026 (Gen-Lug) (€)": quota_altri,
    "Num Fatture": 12
}])

df_clienti_2026 = pd.concat([df_clienti_principali, df_altri], ignore_index=True)

dati_clienti_mensili = {
    "WITTUR SPA": {"2026": [19638.0, 19653.0, 27121.5, 20090.5, 18483.0, 31936.0, 0.0], "2025": [15561.0, 13911.5, 18000.0, 16500.0, 17800.0, 18200.0, 19500.0], "2024": [12000.0, 14000.0, 17547.0, 16000.0, 17804.5, 16500.0, 23948.5]},
    "SIDEL S.P.A.": {"2026": [10880.5, 12822.0, 16817.5, 16608.1, 19245.0, 20760.0, 5123.04], "2025": [9078.0, 13487.31, 11200.0, 12500.0, 14000.0, 11800.0, 12900.0], "2024": [11000.0, 12500.0, 13000.0, 10500.0, 11800.0, 12200.0, 14000.0]},
    "ACMI BEVERAGE SPA (ex SACMI)": {"2026": [6784.0, 10195.0, 10793.0, 6524.0, 6100.0, 0.0, 0.0], "2025": [11262.0, 9880.5, 9429.5, 11115.0, 10972.0, 14210.0, 9192.0], "2024": [8140.0, 10092.0, 6986.0, 7968.0, 14381.0, 16875.0, 14487.0]},
    "ACMI LABELLING SRL (ex SACMI)": {"2026": [3284.0, 6134.0, 3624.0, 4770.0, 9586.0, 0.0, 6386.0], "2025": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "2024": [5465.0, 5248.0, 4929.0, 4248.0, 0.0, 0.0, 0.0]},
    "CATTANI SPA": {"2026": [1918.0, 3290.0, 2674.0, 2996.0, 546.0, 1890.0, 2058.0], "2025": [1400.0, 1386.0, 1330.0, 2156.0, 1694.0, 2618.0, 3234.0], "2024": [1512.0, 1148.0, 1946.0, 1428.0, 1848.0, 1022.0, 2170.0]},
    "GAMMA MECCANICA S.p.A": {"2026": [1472.0, 480.0, 4868.0, 2832.0, 3264.0, 0.0, 2912.0], "2025": [0.0, 2070.0, 4650.0, 1920.0, 0.0, 2280.0, 0.0], "2024": [0.0, 0.0, 0.0, 2430.0, 4800.0, 2040.0, 0.0]},
    "GEA MECHANICAL EQUIPMENT": {"2026": [0.0, 385.0, 840.0, 3795.0, 3268.0, 0.0, 1965.0], "2025": [0.0, 0.0, 0.0, 0.0, 667.0, 0.0, 0.0], "2024": [0.0, 0.0, 0.0, 0.0, 0.0, 703.5, 0.0]},
    "CSF INOX S.P.A.": {"2026": [0.0, 0.0, 0.0, 0.0, 2295.0, 1680.0, 1200.0], "2025": [1920.0, 1920.0, 1920.0, 1440.0, 720.0, 1200.0, 2160.0], "2024": [0.0, 0.0, 1455.0, 1920.0, 1170.0, 0.0, 2160.0]},
    "DIECI SRL": {"2026": [0.0, 0.0, 0.0, 0.0, 0.0, 2790.0, 1813.50], "2025": [3168.0, 1792.0, 2912.0, 2016.0, 2016.0, 0.0, 0.0], "2024": [0.0, 980.0, 0.0, 3332.0, 7588.0, 3180.0, 4140.0]},
    "CALF SPA": {"2026": [4698.0, 4435.0, 0.0, 0.0, 0.0, 0.0, 0.0], "2025": [6061.0, 5017.0, 6365.5, 6742.5, 5408.5, 6612.0, 5814.5], "2024": [5026.0, 6149.5, 5908.0, 5110.0, 4018.0, 6734.0, 3976.0]},
}

if "cliente_selezionato" not in st.session_state:
    st.session_state["cliente_selezionato"] = "WITTUR SPA"

def layout_grafico_chiaro(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#0f172a", size=10),
        margin=dict(l=10, r=10, t=50, b=30),
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
st.sidebar.markdown("<h2 style='text-align: center; color: #1e3a8a;'>⚙️ Sintec App</h2>", unsafe_allow_html=True)
sezione = st.sidebar.radio(
    "Navigazione Principale",
    ["📈 Dashboard Grafica", "🤖 Assistente IA (Testo e Voce)"]
)

st.sidebar.markdown("---")
st.sidebar.link_button(
    "📓 Apri Google Notebook",
    "https://notebook.google.com/notebook/e4078841-d0c1-4aed-8a70-1ee190c51016",
    use_container_width=True
)

if sezione == "📈 Dashboard Grafica":
    st.markdown("## 📊 Controllo di Gestione - **Sintec S.r.l.**")

    # METRICHE TOP DASHBOARD
    tot_f_26 = df_fat["Fatturato 2026"].head(7).sum()
    tot_f_25 = df_fat["Fatturato 2025"].head(7).sum()
    tot_f_25_tot = df_fat["Fatturato 2025"].sum()
    delta_f = ((tot_f_26 - tot_f_25) / tot_f_25) * 100

    tot_c_26 = df_costi["Costi 2026"].head(7).sum()
    tot_c_25 = df_costi["Costi 2025"].head(7).sum()
    tot_c_25_tot = df_costi["Costi 2025"].sum()
    delta_c = ((tot_c_26 - tot_c_25) / tot_c_25) * 100

    mol_26 = tot_f_26 - tot_c_26
    mol_25 = tot_f_25 - tot_c_25
    mol_25_tot = tot_f_25_tot - tot_c_25_tot
    delta_m = ((mol_26 - mol_25) / mol_25) * 100 if mol_25 != 0 else 0

    class_f = "kpi-delta-pos" if delta_f >= 0 else "kpi-delta-neg"
    class_c = "kpi-delta-neg" if delta_c >= 0 else "kpi-delta-pos"
    class_m = "kpi-delta-pos" if delta_m >= 0 else "kpi-delta-neg"

    col_k1, col_k2, col_k3 = st.columns(3)
    
    col_k1.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Fatturato Gen-Lug 2026</div>
        <div class="kpi-value">€ {tot_f_26:,.2f}</div>
        <div class="kpi-subtitle">Gen-Lug 2025: <b>€ {tot_f_25:,.2f}</b> <span class="{class_f}">({delta_f:+.1f}%)</span></div>
        <div class="kpi-subtitle">Totale Anno 2025: <b>€ {tot_f_25_tot:,.2f}</b></div>
    </div>
    ''', unsafe_allow_html=True)

    col_k2.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Costi Personale Gen-Lug 2026</div>
        <div class="kpi-value" style="color:#e11d48;">€ {tot_c_26:,.2f}</div>
        <div class="kpi-subtitle">Gen-Lug 2025: <b>€ {tot_c_25:,.2f}</b> <span class="{class_c}">({delta_c:+.1f}%)</span></div>
        <div class="kpi-subtitle">Totale Anno 2025: <b>€ {tot_c_25_tot:,.2f}</b></div>
    </div>
    ''', unsafe_allow_html=True)

    col_k3.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Margine Operativo Gen-Lug 2026</div>
        <div class="kpi-value" style="color:#16a34a;">€ {mol_26:,.2f}</div>
        <div class="kpi-subtitle">Gen-Lug 2025: <b>€ {mol_25:,.2f}</b> <span class="{class_m}">({delta_m:+.1f}%)</span></div>
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
        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=["Fatturato 2026", "Fatturato 2025", "Fatturato 2024"],
            barmode="group",
            title="Andamento Fatturato Mensile (€)",
            color_discrete_sequence=["#2563eb", "#60a5fa", "#93c5fd"],
            text_auto=",.0f"
        )
        max_val = df_fat[["Fatturato 2026", "Fatturato 2025", "Fatturato 2024"]].max().max()
        fig_f.update_traces(textposition="outside", textfont_size=8)
        fig_f.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_chiaro(fig_f), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Fatturato (€)")
        df_fat_tot = pd.concat([
            df_fat,
            pd.DataFrame([{
                "Mese": "TOTALE",
                "Fatturato 2026": df_fat["Fatturato 2026"].sum(),
                "Fatturato 2025": df_fat["Fatturato 2025"].sum(),
                "Fatturato 2024": df_fat["Fatturato 2024"].sum()
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
        st.subheader("👥 Costi Personale Mensili")
        fig_c = px.bar(
            df_costi,
            x="Mese",
            y=["Costi 2026", "Costi 2025", "Costi 2024"],
            barmode="group",
            title="Andamento Costi Personale (€)",
            color_discrete_sequence=["#e11d48", "#f43f5e", "#fda4af"],
            text_auto=",.0f"
        )
        max_val = df_costi[["Costi 2026", "Costi 2025", "Costi 2024"]].max().max()
        fig_c.update_traces(textposition="outside", textfont_size=8)
        fig_c.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_chiaro(fig_c), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Costi Personale (€)")
        df_costi_tot = pd.concat([
            df_costi,
            pd.DataFrame([{
                "Mese": "TOTALE",
                "Costi 2026": df_costi["Costi 2026"].sum(),
                "Costi 2025": df_costi["Costi 2025"].sum(),
                "Costi 2024": df_costi["Costi 2024"].sum()
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

    # TAB 3: ORE DIRETTE
    with t3:
        st.subheader("⏱️ Ore Dirette Lavorate")
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
        st.plotly_chart(layout_grafico_chiaro(fig_dir), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Ore Dirette (h)")
        df_ore_dir_tot = pd.concat([
            df_ore_dirette,
            pd.DataFrame([{
                "Mese": "TOTALE",
                "Ore Dirette 2026": df_ore_dirette["Ore Dirette 2026"].sum(),
                "Ore Dirette 2025": df_ore_dirette["Ore Dirette 2025"].sum()
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
        st.plotly_chart(layout_grafico_chiaro(fig_ind), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Ore Indirette (h)")
        df_ore_ind_tot = pd.concat([
            df_ore_indirette,
            pd.DataFrame([{
                "Mese": "TOTALE",
                "Ore Indirette 2026": df_ore_indirette["Ore Indirette 2026"].sum(),
                "Ore Indirette 2025": df_ore_indirette["Ore Indirette 2025"].sum()
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
        fig_media = px.bar(
            df_media_oraria,
            x="Mese",
            y=["Media Oraria 2026", "Media Oraria 2025", "Media Oraria 2024"],
            barmode="group",
            title="Media Oraria (€/h)",
            color_discrete_sequence=["#9333ea", "#c084fc", "#e9d5ff"],
            text_auto=",.1f"
        )
        max_val = df_media_oraria[["Media Oraria 2026", "Media Oraria 2025", "Media Oraria 2024"]].max().max()
        fig_media.update_traces(textposition="outside", textfont_size=8)
        fig_media.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_chiaro(fig_media), use_container_width=True)

        st.markdown("#### 📋 Tabella Dati Media Oraria (€/h)")
        df_media_tot = pd.concat([
            df_media_oraria,
            pd.DataFrame([{
                "Mese": "TOTALE",
                "Media Oraria 2026": df_media_oraria["Media Oraria 2026"][df_media_oraria["Media Oraria 2026"] > 0].mean(),
                "Media Oraria 2025": df_media_oraria["Media Oraria 2025"][df_media_oraria["Media Oraria 2025"] > 0].mean(),
                "Media Oraria 2024": df_media_oraria["Media Oraria 2024"][df_media_oraria["Media Oraria 2024"] > 0].mean()
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
        st.subheader("📋 Totale Parziale 2026 - Costi e Ore Personale")
        st.dataframe(
            df_riassunto_2026.style.apply(evidenzia_totale, col_chiave="COGNOME", axis=1).format({
                "COSTO TOT": "€ {:,.2f}",
                "ORE TOT": "{:,.1f}",
                "COSTO ORARIO": "€ {:,.2f}"
            }),
            use_container_width=True,
            height=350
        )

        st.markdown("---")
        st.subheader("🔎 Dettaglio Mensile Dipendente")
        dip_scelto = st.selectbox("Seleziona Dipendente:", list(dati_dipendenti_mensili.keys()))

        df_dip = pd.DataFrame({
            "Mese": mesi,
            "Costo Totale (€)": dati_dipendenti_mensili[dip_scelto]["Costo"],
            "Ore Totali": dati_dipendenti_mensili[dip_scelto]["Ore"]
        })
        df_dip["Costo Orario (€/h)"] = (df_dip["Costo Totale (€)"] / df_dip["Ore Totali"]).fillna(0).round(2)

        fig_dip = px.bar(
            df_dip[df_dip["Ore Totali"] > 0],
            x="Mese",
            y="Costo Totale (€)",
            text_auto=",.0f",
            color_discrete_sequence=["#2563eb"],
            title=f"Andamento Mensile Costi - {dip_scelto}"
        )
        max_val = df_dip["Costo Totale (€)"].max()
        fig_dip.update_traces(textposition="outside", textfont_size=8)
        fig_dip.update_layout(yaxis=dict(range=[0, max_val * 1.30]))
        st.plotly_chart(layout_grafico_chiaro(fig_dip), use_container_width=True)

        st.markdown(f"#### 📋 Tabella Dati Mensili - {dip_scelto}")
        tot_c_dip = df_dip["Costo Totale (€)"].sum()
        tot_o_dip = df_dip["Ore Totali"].sum()
        med_co_dip = (tot_c_dip / tot_o_dip) if tot_o_dip > 0 else 0

        df_dip_tot = pd.concat([
            df_dip,
            pd.DataFrame([{
                "Mese": "TOTALE",
                "Costo Totale (€)": tot_c_dip,
                "Ore Totali": tot_o_dip,
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
        st.subheader("🍕 Analisi e Classifica Fatturato Clienti (Gen-Lug 2026)")

        col_p1, col_p2 = st.columns([1.1, 1])

        with col_p1:
            fig_pie = px.pie(
                df_clienti_2026,
                values="Fatturato 2026 (Gen-Lug) (€)",
                names="Cliente",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
                title="Quota % Fatturato per Cliente"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')

            selected_pie = st.plotly_chart(
                layout_grafico_chiaro(fig_pie),
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
            df_cli_s = df_clienti_2026.sort_values(by="Fatturato 2026 (Gen-Lug) (€)", ascending=False).reset_index(drop=True)
            tot_cli = df_cli_s["Fatturato 2026 (Gen-Lug) (€)"].sum()
            df_cli_s["% Quota"] = (df_cli_s["Fatturato 2026 (Gen-Lug) (€)"] / tot_cli * 100).round(2)

            df_tot_riga = pd.DataFrame([{
                "Cliente": "TOTALE FATTURATO",
                "Fatturato 2026 (Gen-Lug) (€)": tot_cli,
                "Num Fatture": df_cli_s["Num Fatture"].sum(),
                "% Quota": 100.00
            }])
            df_cli_completo = pd.concat([df_cli_s, df_tot_riga], ignore_index=True)

            st.dataframe(
                df_cli_completo.style.apply(evidenzia_totale, col_chiave="Cliente", axis=1).format({
                    "Fatturato 2026 (Gen-Lug) (€)": "€ {:,.2f}",
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

        df_cli_m = pd.DataFrame({
            "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug"],
            "2026 (€)": dati_clienti_mensili[cli_scelto]["2026"],
            "2025 (€)": dati_clienti_mensili[cli_scelto]["2025"],
            "2024 (€)": dati_clienti_mensili[cli_scelto]["2024"],
        })

        tot_2026 = sum(dati_clienti_mensili[cli_scelto]["2026"])
        tot_2025 = sum(dati_clienti_mensili[cli_scelto]["2025"])
        tot_2024 = sum(dati_clienti_mensili[cli_scelto]["2024"])

        df_tot_cliente = pd.DataFrame([{
            "Mese": "TOTALE",
            "2026 (€)": tot_2026,
            "2025 (€)": tot_2025,
            "2024 (€)": tot_2024
        }])

        df_cli_m_tot = pd.concat([df_cli_m, df_tot_cliente], ignore_index=True)

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
                color_discrete_sequence=["#2563eb", "#60a5fa", "#93c5fd"]
            )
            st.plotly_chart(layout_grafico_chiaro(fig_cli_m), use_container_width=True)

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    st.subheader("🤖 Assistente IA Gestionale")
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