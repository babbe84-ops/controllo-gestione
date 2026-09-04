import io
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Sintec S.r.l. - Controllo di Gestione",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- INIEZIONE CSS PER DESIGN RESPONSIVE & MODERNO ---
st.markdown(
    """
<style>
    /* Gradient Background & Fonts */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Card Glassmorphism per KPI e Sezioni */
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.45);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
    }
    .kpi-subtitle {
        font-size: 0.78rem;
        color: #cbd5e1;
        margin-top: 8px;
    }
    .badge-positive {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-info {
        background: rgba(56, 189, 248, 0.2);
        color: #38bdf8;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }

    /* Style dei Tab e Pulsanti */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 8px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        border: none;
        padding: 0 16px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
    }

    /* Ottimizzazione Mobile Responsive */
    @media (max-width: 768px) {
        .kpi-value { font-size: 1.4rem; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 0 8px; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- SCHERMATA DI LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown(
        "<div style='text-align: center; margin-top: 50px;'><h1>🔒 Accesso Riservato</h1><p style='color: #94a3b8;'>Sintec S.r.l. - Controllo di Gestione</p></div>",
        unsafe_allow_html=True,
    )
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        with st.form("login_form"):
            username = st.text_input("Username", key="username")
            password = st.text_input("Password", type="password", key="password")
            submit_button = st.form_submit_button(
                "🚀 Accedi al Dashboard", use_container_width=True
            )

        if submit_button:
            if username == "sintec" and password == "Sintec2026!":
                st.session_state["authenticated"] = True
                st.success("Accesso effettuato con successo!")
                st.rerun()
            else:
                st.error("Credenziali non valide")
    st.stop()

# --- CARICAMENTO DATI FONDAMENTALI ---
df_fat = pd.DataFrame({
    "Mese": [
        "Gen",
        "Feb",
        "Mar",
        "Apr",
        "Mag",
        "Giu",
        "Lug",
        "Ago",
        "Set",
        "Ott",
        "Nov",
        "Dic",
    ],
    "Fatturato 2024": [
        57247.00,
        68184.47,
        80810.80,
        68999.64,
        87666.00,
        70416.50,
        88701.60,
        48356.50,
        73093.20,
        89233.76,
        72332.50,
        57421.08,
    ],
    "Fatturato 2025": [
        57401.50,
        62787.31,
        72682.00,
        68541.53,
        71101.00,
        73161.79,
        64458.50,
        35609.42,
        84284.50,
        82004.21,
        64778.43,
        64324.52,
    ],
    "Fatturato 2026": [
        58570.50,
        73584.46,
        75642.00,
        70202.10,
        65023.99,
        80642.35,
        66484.43,
        0,
        0,
        0,
        0,
        0,
    ],
})

df_costi = pd.DataFrame({
    "Mese": [
        "Gen",
        "Feb",
        "Mar",
        "Apr",
        "Mag",
        "Giu",
        "Lug",
        "Ago",
        "Set",
        "Ott",
        "Nov",
        "Dic",
    ],
    "Costi 2024": [
        30359.58,
        34197.57,
        43005.65,
        40156.84,
        43703.97,
        44361.46,
        32676.33,
        36758.37,
        42287.59,
        40908.77,
        36832.46,
        46703.16,
    ],
    "Costi 2025": [
        32409.91,
        36319.18,
        36075.82,
        38017.47,
        41233.54,
        42390.51,
        36236.41,
        26967.94,
        39929.42,
        40450.24,
        41594.63,
        36510.16,
    ],
    "Costi 2026": [
        34104.88,
        40913.02,
        39960.05,
        39848.93,
        41854.30,
        38761.35,
        32574.31,
        0,
        0,
        0,
        0,
        0,
    ],
})

df_ore_dirette = pd.DataFrame({
    "Mese": [
        "Gen",
        "Feb",
        "Mar",
        "Apr",
        "Mag",
        "Giu",
        "Lug",
        "Ago",
        "Set",
        "Ott",
        "Nov",
        "Dic",
    ],
    "Ore Dirette 2025": [
        2017.0,
        2087.0,
        2317.5,
        2155.5,
        2251.5,
        2221.0,
        2084.0,
        1308.0,
        2454.0,
        2355.0,
        2134.0,
        1641.5,
    ],
    "Ore Dirette 2026": [
        1788.0,
        2108.5,
        2102.5,
        2020.5,
        2118.5,
        2027.0,
        1949.0,
        0,
        0,
        0,
        0,
        0,
    ],
})

df_ore_indirette = pd.DataFrame({
    "Mese": [
        "Gen",
        "Feb",
        "Mar",
        "Apr",
        "Mag",
        "Giu",
        "Lug",
        "Ago",
        "Set",
        "Ott",
        "Nov",
        "Dic",
    ],
    "Ore Indirette 2025": [
        193.0,
        137.0,
        81.5,
        112.5,
        155.5,
        126.5,
        97.5,
        65.0,
        163.5,
        145.5,
        124.5,
        171.0,
    ],
    "Ore Indirette 2026": [
        156.0,
        237.0,
        327.0,
        222.0,
        220.5,
        134.0,
        188.5,
        0,
        0,
        0,
        0,
        0,
    ],
})

df_media_oraria = pd.DataFrame({
    "Mese": [
        "Gen",
        "Feb",
        "Mar",
        "Apr",
        "Mag",
        "Giu",
        "Lug",
        "Ago",
        "Set",
        "Ott",
        "Nov",
        "Dic",
    ],
    "Media Oraria 2024": [
        25.98,
        27.17,
        30.29,
        27.78,
        28.50,
        26.28,
        30.74,
        27.24,
        29.82,
        31.52,
        27.52,
        30.05,
    ],
    "Media Oraria 2025": [
        25.97,
        28.23,
        30.30,
        30.22,
        29.54,
        31.17,
        29.55,
        25.94,
        32.20,
        32.80,
        28.68,
        35.49,
    ],
    "Media Oraria 2026": [
        30.13,
        31.37,
        31.13,
        31.31,
        27.80,
        37.32,
        31.10,
        0,
        0,
        0,
        0,
        0,
    ],
})

df_clienti_2026 = pd.DataFrame({
    "Cliente": [
        "ACMI BEVERAGE SPA",
        "ACMI LABELLING SRL",
        "CALF SPA",
        "CATTANI SPA",
        "CSF INOX S.P.A.",
        "DIECI SRL",
        "ERRESSE Costmec",
        "JOHN BEAN TECHNOLOGIES",
        "GAMMA MECCANICA S.p.A",
        "GEA MECHANICAL EQUIPMENT",
        "REGGIANA RIDUTTORI SRL",
        "PRISMA S.P.A.",
        "I.E. PARK SRL",
        "ALTRI CLIENTI",
    ],
    "Fatturato 2026": [
        17577.00,
        6908.00,
        9133.00,
        13314.00,
        3975.00,
        2790.00,
        3273.00,
        2640.00,
        12916.00,
        9393.00,
        5238.00,
        2227.50,
        1860.00,
        399129.93,
    ],
})

dati_clienti_mensili = {
    "CALF SPA": {
        "2026": [4698.0, 4435.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "2025": [6061.0, 5017.0, 6365.5, 6742.5, 5408.5, 6612.0, 5814.5],
        "2024": [5026.0, 6149.5, 5908.0, 5110.0, 4018.0, 6734.0, 3976.0],
    },
    "CATTANI SPA": {
        "2026": [1918.0, 3290.0, 2674.0, 2996.0, 546.0, 1890.0, 2058.0],
        "2025": [1400.0, 1386.0, 1330.0, 2156.0, 1694.0, 2618.0, 3234.0],
        "2024": [1512.0, 1148.0, 1946.0, 1428.0, 1848.0, 1022.0, 2170.0],
    },
    "GAMMA MECCANICA S.p.A": {
        "2026": [1472.0, 480.0, 4868.0, 2832.0, 3264.0, 0.0, 2912.0],
        "2025": [0.0, 2070.0, 4650.0, 1920.0, 0.0, 2280.0, 0.0],
        "2024": [0.0, 0.0, 0.0, 2430.0, 4800.0, 2040.0, 0.0],
    },
    "CSF INOX S.P.A.": {
        "2026": [0.0, 0.0, 0.0, 0.0, 2295.0, 1680.0, 1200.0],
        "2025": [1920.0, 1920.0, 1920.0, 1440.0, 720.0, 1200.0, 2160.0],
        "2024": [0.0, 0.0, 1455.0, 1920.0, 1170.0, 0.0, 2160.0],
    },
    "ACMI BEVERAGE SPA": {
        "2026": [6784.0, 0.0, 10793.0, 0.0, 0.0, 0.0, 0.0],
        "2025": [11262.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "2024": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    },
}

df_riassunto_2026 = pd.DataFrame({
    "COGNOME": [
        "D'ALSAZIA",
        "BASSISSI",
        "CASELLI",
        "LANZI",
        "GUION",
        "CAMPANINI",
        "JOHNSON",
        "RASENTI",
        "MAGNO",
        "SCANO",
        "PETRO'",
        "GRANDE",
        "DEJVI (luglio-sett.)",
        "TOTALE SINTEC (MEDIA GEN-LUG)",
    ],
    "COSTO TOT": [
        25885.34,
        15535.51,
        25770.31,
        22431.26,
        11440.63,
        24780.83,
        20065.46,
        35537.75,
        23986.59,
        23853.41,
        19098.31,
        19631.44,
        2642.86,
        270659.70,
    ],
    "ORE TOT": [
        1222.5,
        1186.5,
        1017.0,
        1166.5,
        741.0,
        1203.0,
        1033.5,
        1341.0,
        1207.5,
        960.0,
        1154.5,
        709.5,
        304.5,
        13247.0,
    ],
    "COSTO ORARIO": [
        21.17,
        13.09,
        25.34,
        19.23,
        15.44,
        20.60,
        19.42,
        26.50,
        19.86,
        24.85,
        16.54,
        27.67,
        8.68,
        20.43,
    ],
})

dati_dipendenti_mensili = {
    "D'ALSAZIA": {
        "Costo": [
            3693.39,
            3960.66,
            3857.07,
            3922.04,
            3889.52,
            4007.63,
            2555.03,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [150.5, 166.5, 172.5, 168.5, 163.0, 168.0, 105.5, 0, 0, 0, 0, 0],
    },
    "BASSISSI": {
        "Costo": [
            2169.70,
            2337.50,
            2361.92,
            2332.02,
            2406.59,
            2407.38,
            1520.40,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [143.5, 160.0, 176.0, 168.0, 158.0, 157.0, 96.0, 0, 0, 0, 0, 0],
    },
    "CASELLI": {
        "Costo": [
            3504.50,
            3749.44,
            4035.38,
            4073.36,
            3925.75,
            3846.69,
            2635.19,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [125.0, 140.0, 151.0, 129.5, 137.5, 141.0, 86.0, 0, 0, 0, 0, 0],
    },
    "LANZI": {
        "Costo": [
            2949.79,
            3225.64,
            3455.40,
            3518.32,
            3244.59,
            3093.37,
            2944.15,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [137.0, 157.5, 175.0, 167.0, 150.5, 144.0, 152.0, 0, 0, 0, 0, 0],
    },
    "GUION": {
        "Costo": [
            1296.53,
            1452.13,
            1912.60,
            1518.40,
            1779.25,
            1801.12,
            1680.60,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [81.5, 96.0, 106.0, 86.5, 101.5, 101.0, 110.0, 0, 0, 0, 0, 0],
    },
    "CAMPANINI": {
        "Costo": [
            3430.97,
            3447.45,
            3523.93,
            3480.09,
            3647.24,
            3701.70,
            3549.45,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [132.0, 137.5, 158.0, 155.5, 157.5, 159.0, 175.5, 0, 0, 0, 0, 0],
    },
    "RASENTI": {
        "Costo": [
            4789.75,
            5702.35,
            4906.62,
            4697.05,
            6054.25,
            4722.98,
            4664.75,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [160.0, 199.0, 193.0, 152.0, 204.0, 179.0, 164.0, 0, 0, 0, 0, 0],
    },
    "SCANO": {
        "Costo": [
            3542.57,
            3758.97,
            2634.49,
            3019.63,
            3787.61,
            3779.72,
            3330.42,
            0,
            0,
            0,
            0,
            0,
        ],
        "Ore": [143.5, 153.5, 72.0, 104.0, 156.5, 150.0, 101.0, 0, 0, 0, 0, 0],
    },
}

mesi = [
    "Gen",
    "Feb",
    "Mar",
    "Apr",
    "Mag",
    "Giu",
    "Lug",
    "Ago",
    "Set",
    "Ott",
    "Nov",
    "Dic",
]

# --- SIDEBAR E NAVIGAZIONE ---
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #38bdf8;'>⚙️ Sintec App</h2>",
    unsafe_allow_html=True,
)
sezione = st.sidebar.radio(
    "Navigazione Principale",
    ["📈 Dashboard Grafica", "🤖 Assistente IA (Testo e Voce)"],
)

st.sidebar.markdown("---")
st.sidebar.link_button(
    "📓 Apri Google Notebook",
    "https://notebook.google.com/notebook/e4078841-d0c1-4aed-8a70-1ee190c51016",
    use_container_width=True,
)

# HELPER PER GRAFICI CON DESIGN DARK UNIFORME
def layout_grafico_scuro(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#f8fafc"),
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


if sezione == "📈 Dashboard Grafica":
    st.sidebar.subheader("🎛️ Filtri e Caricamento Dati")
    anno_selezionato = st.sidebar.selectbox(
        "Seleziona Anno Analisi", [2026, 2024]
    )

    file_upload = st.sidebar.file_uploader(
        "📁 Carica File Excel (.xlsx)", type=["xlsx"]
    )
    if file_upload:
        st.sidebar.success("File caricato correttamente!")

    label_anno = (
        "2026 (Parziale Gen–Lug)"
        if anno_selezionato == 2026
        else str(anno_selezionato)
    )

    st.markdown(
        f"## 📊 Risultati **{label_anno}** vs **2025** (Anno Riferimento)"
    )

    # --- CALCOLI METRICHE E PREVISIONALI ---
    tot_f_sel = df_fat[f"Fatturato {anno_selezionato}"].sum()
    tot_c_sel = df_costi[f"Costi {anno_selezionato}"].sum()
    mol_sel = tot_f_sel - tot_c_sel

    mesi_consolidati = 7 if anno_selezionato == 2026 else 12
    prev_f_sel = (tot_f_sel / mesi_consolidati) * 12
    prev_c_sel = (tot_c_sel / mesi_consolidati) * 12
    prev_mol_sel = prev_f_sel - prev_c_sel

    tot_f_2025_tot = df_fat["Fatturato 2025"].sum()
    tot_f_2025_parz = df_fat["Fatturato 2025"].iloc[:7].sum()

    tot_c_2025_tot = df_costi["Costi 2025"].sum()
    tot_c_2025_parz = df_costi["Costi 2025"].iloc[:7].sum()

    mol_2025_tot = tot_f_2025_tot - tot_c_2025_tot
    mol_2025_parz = tot_f_2025_parz - tot_c_2025_parz

    # --- CARD KPI CUSTOM RESPONSIVE ---
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

    with col_kpi1:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">Fatturato Totale {label_anno}</div>
            <div class="kpi-value">€ {tot_f_sel:,.2f}</div>
            <div style="margin-top:8px;">
                <span class="badge-positive">🔮 Previsionale 12M: € {prev_f_sel:,.2f}</span>
            </div>
            <div class="kpi-subtitle">📌 2025 Gen-Lug: € {tot_f_2025_parz:,.2f} | Tot 2025: € {tot_f_2025_tot:,.2f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_kpi2:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">Costi Totali Personale</div>
            <div class="kpi-value" style="color: #f43f5e;">€ {tot_c_sel:,.2f}</div>
            <div style="margin-top:8px;">
                <span class="badge-info">🔮 Previsionale 12M: € {prev_c_sel:,.2f}</span>
            </div>
            <div class="kpi-subtitle">📌 2025 Gen-Lug: € {tot_c_2025_parz:,.2f} | Tot 2025: € {tot_c_2025_tot:,.2f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col_kpi3:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">Margine Operativo</div>
            <div class="kpi-value" style="color: #10b981;">€ {mol_sel:,.2f}</div>
            <div style="margin-top:8px;">
                <span class="badge-positive">🔮 Previsionale 12M: € {prev_mol_sel:,.2f}</span>
            </div>
            <div class="kpi-subtitle">📌 2025 Gen-Lug: € {mol_2025_parz:,.2f} | Tot 2025: € {mol_2025_tot:,.2f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABBED INTERFACE CON ICONE ---
    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "📊 Fatturato",
        "👥 Costi Personale",
        "⏱️ Ore Dirette",
        "⚙️ Ore Indirette",
        "💶 Media Oraria",
        "📋 Dipendenti",
        "🍕 Analisi Clienti",
    ])

    with t1:
        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=[f"Fatturato {anno_selezionato}", "Fatturato 2025"],
            barmode="group",
            title=f"Confronto Fatturato Mensile: {label_anno} vs 2025",
            labels={"value": "Euro (€)", "variable": "Anno"},
            color_discrete_sequence=["#38bdf8", "#818cf8"],
            text_auto=",.0f",
        )
        fig_f.update_traces(textposition="outside")
        st.plotly_chart(
            layout_grafico_scuro(fig_f), use_container_width=True
        )

    with t2:
        fig_c = px.bar(
            df_costi,
            x="Mese",
            y=[f"Costi {anno_selezionato}", "Costi 2025"],
            barmode="group",
            title=f"Confronto Costi Personale Mensili: {label_anno} vs 2025",
            labels={"value": "Euro (€)", "variable": "Anno"},
            color_discrete_sequence=["#f43f5e", "#fb7185"],
            text_auto=",.0f",
        )
        fig_c.update_traces(textposition="outside")
        st.plotly_chart(
            layout_grafico_scuro(fig_c), use_container_width=True
        )

    with t3:
        tot_dir_26 = df_ore_dirette["Ore Dirette 2026"].sum()
        tot_dir_25_parz = df_ore_dirette["Ore Dirette 2025"].iloc[:7].sum()
        tot_dir_25_tot = df_ore_dirette["Ore Dirette 2025"].sum()
        prev_dir_26 = (
            (tot_dir_26 / mesi_consolidati) * 12
            if anno_selezionato == 2026
            else tot_dir_26
        )

        st.caption(
            f"🔮 **Previsione 12M 2026:** {prev_dir_26:,.1f} h | 📌 **Gen-Lug 2025:** {tot_dir_25_parz:,.1f} h | **Consuntivo 2025:** {tot_dir_25_tot:,.1f} h"
        )
        fig_dir = px.bar(
            df_ore_dirette,
            x="Mese",
            y=["Ore Dirette 2026", "Ore Dirette 2025"],
            barmode="group",
            title=f"Confronto Ore Dirette: {label_anno} vs 2025",
            color_discrete_sequence=["#34d399", "#059669"],
            text_auto=",.1f",
        )
        fig_dir.update_traces(textposition="outside")
        st.plotly_chart(
            layout_grafico_scuro(fig_dir), use_container_width=True
        )

    with t4:
        tot_ind_26 = df_ore_indirette["Ore Indirette 2026"].sum()
        tot_ind_25_parz = df_ore_indirette["Ore Indirette 2025"].iloc[:7].sum()
        tot_ind_25_tot = df_ore_indirette["Ore Indirette 2025"].sum()
        prev_ind_26 = (
            (tot_ind_26 / mesi_consolidati) * 12
            if anno_selezionato == 2026
            else tot_ind_26
        )

        st.caption(
            f"🔮 **Previsione 12M 2026:** {prev_ind_26:,.1f} h | 📌 **Gen-Lug 2025:** {tot_ind_25_parz:,.1f} h | **Consuntivo 2025:** {tot_ind_25_tot:,.1f} h"
        )
        fig_ind = px.bar(
            df_ore_indirette,
            x="Mese",
            y=["Ore Indirette 2026", "Ore Indirette 2025"],
            barmode="group",
            title=f"Confronto Ore Indirette: {label_anno} vs 2025",
            color_discrete_sequence=["#fbbf24", "#d97706"],
            text_auto=",.1f",
        )
        fig_ind.update_traces(textposition="outside")
        st.plotly_chart(
            layout_grafico_scuro(fig_ind), use_container_width=True
        )

    with t5:
        st.caption(
            "📌 **Gen–Lug 2026:** € 31.42/h | **Gen–Lug 2025:** € 29.23/h | **Consuntivo 2025 Totale:** € 30.12/h"
        )
        fig_media = px.bar(
            df_media_oraria,
            x="Mese",
            y=[
                f"Media Oraria {anno_selezionato}",
                "Media Oraria 2025",
                "Media Oraria 2024",
            ],
            barmode="group",
            title="Confronto Media Oraria Fatturato (€/h)",
            color_discrete_sequence=["#a855f7", "#c084fc", "#e9d5ff"],
            text_auto=",.2f",
        )
        fig_media.update_traces(textposition="outside")
        st.plotly_chart(
            layout_grafico_scuro(fig_media), use_container_width=True
        )

    with t6:
        st.subheader("📊 Totale Parziale 2026 - Costi e Ore Personale")

        def style_totale(row):
            if "TOTALE SINTEC" in str(row["COGNOME"]):
                return [
                    "background-color: rgba(59, 130, 246, 0.2); font-weight: bold; color: #60a5fa"
                ] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_riassunto_2026.style.apply(style_totale, axis=1).format({
                "COSTO TOT": "€ {:,.2f}",
                "ORE TOT": "{:,.1f}",
                "COSTO ORARIO": "€ {:,.2f}",
            }),
            use_container_width=True,
            height=450,
        )

        st.markdown("---")
        st.subheader("🔎 Dettaglio Mensile Dipendente")
        dip_scelto = st.selectbox(
            "Seleziona Dipendente:", list(dati_dipendenti_mensili.keys())
        )

        df_dip = pd.DataFrame({
            "Mese": mesi,
            "Costo Totale (€)": dati_dipendenti_mensili[dip_scelto]["Costo"],
            "Ore Totali": dati_dipendenti_mensili[dip_scelto]["Ore"],
        })
        df_dip["Costo Orario (€/h)"] = (
            df_dip["Costo Totale (€)"] / df_dip["Ore Totali"]
        ).fillna(0).round(2)

        st.dataframe(
            df_dip.style.format({
                "Costo Totale (€)": "€ {:,.2f}",
                "Ore Totali": "{:,.1f} h",
                "Costo Orario (€/h)": "€ {:,.2f}",
            }),
            use_container_width=True,
        )

        fig_dip = px.bar(
            df_dip[df_dip["Ore Totali"] > 0],
            x="Mese",
            y="Costo Totale (€)",
            text_auto=",.0f",
            color_discrete_sequence=["#38bdf8"],
            title=f"Andamento Mensile Costi - {dip_scelto}",
        )
        fig_dip.update_traces(textposition="outside")
        st.plotly_chart(
            layout_grafico_scuro(fig_dip), use_container_width=True
        )

    with t7:
        st.subheader("🍕 Quota Fatturato per Cliente")

        col_p1, col_p2 = st.columns([1.1, 1])

        with col_p1:
            fig_pie = px.pie(
                df_clienti_2026,
                values="Fatturato 2026",
                names="Cliente",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_pie.update_traces(
                textposition="inside", textinfo="percent+label"
            )
            st.plotly_chart(
                layout_grafico_scuro(fig_pie), use_container_width=True
            )

        with col_p2:
            st.markdown("#### 🏆 Graduatoria Clienti (2026 Gen–Lug)")
            df_cli_s = df_clienti_2026.sort_values(
                by="Fatturato 2026", ascending=False
            ).reset_index(drop=True)
            tot_cli = df_cli_s["Fatturato 2026"].sum()
            df_cli_s["% Quota"] = (
                df_cli_s["Fatturato 2026"] / tot_cli * 100
            ).round(2)

            st.dataframe(
                df_cli_s.style.format({
                    "Fatturato 2026": "€ {:,.2f}",
                    "% Quota": "{:.2f} %",
                }),
                use_container_width=True,
                height=380,
            )

        st.markdown("---")
        st.subheader("🔎 Storico Mensile del Singolo Cliente")
        cli_scelto = st.selectbox(
            "Seleziona Cliente:", list(dati_clienti_mensili.keys())
        )

        df_cli_m = pd.DataFrame({
            "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug"],
            "2026 (€)": dati_clienti_mensili[cli_scelto]["2026"],
            "2025 (€)": dati_clienti_mensili[cli_scelto]["2025"],
            "2024 (€)": dati_clienti_mensili[cli_scelto]["2024"],
        })

        st.dataframe(
            df_cli_m.style.format({
                "2026 (€)": "€ {:,.2f}",
                "2025 (€)": "€ {:,.2f}",
                "2024 (€)": "€ {:,.2f}",
            }),
            use_container_width=True,
        )

        fig_cli_m = px.bar(
            df_cli_m,
            x="Mese",
            y=["2026 (€)", "2025 (€)", "2024 (€)"],
            barmode="group",
            title=f"Storico Mensile: {cli_scelto}",
            color_discrete_sequence=["#38bdf8", "#818cf8", "#c084fc"],
            text_auto=",.0f",
        )
        fig_cli_m.update_traces(textposition="outside")
        st.plotly_chart(
            layout_grafico_scuro(fig_cli_m), use_container_width=True
        )

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    st.subheader("🤖 Assistente Virtuale Smart")
    st.write(
        "Poni qualsiasi domanda in formato testo o vocale sui dati gestionali Sintec."
    )

    col_a1, col_a2 = st.columns([3, 1])
    with col_a1:
        domanda = st.text_input(
            "Chiedi all'Assistente:",
            placeholder="Es. Qual è il previsionale del fatturato 2026 a 12 mesi?",
        )
    with col_a2:
        st.write("🎙️ Input Vocale:")
        audio = mic_recorder(
            start_prompt="Inizia", stop_prompt="Invia", key="rec", format="wav"
        )

    if domanda:
        st.markdown("---")
        st.markdown("### 💡 Risposta:")

        if "OPENAI_API_KEY" in st.secrets:
            try:
                prompt_sistema = """
                Sei l'assistente di Controllo di Gestione di Sintec S.r.l.
                Dati aziendali essenziali:
                - Fatturato 2026 Gen-Lug: € 490.149,83 | Previsionale 12M: € 840.256,85 | Consuntivo 2025: € 801.134,71
                - Costi Personale 2026 Gen-Lug: € 268.016,84 | Previsionale 12M: € 459.457,44 | Consuntivo 2025: € 453.488,81
                - Margine 2026 Gen-Lug: € 222.132,99 | Previsionale 12M: € 380.799,41 | Consuntivo 2025: € 347.645,90
                - Media Oraria 2026 Gen-Lug: € 31,42/h | Consuntivo 2025: € 30,12/h
                """
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": domanda},
                    ],
                )
                st.success(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Errore API OpenAI: {e}")