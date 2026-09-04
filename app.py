import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# --- CONFIGURAZIONE PAGINA STREAMLIT ---
st.set_page_config(
    page_title="Sintec S.r.l. - Controllo di Gestione",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- INIEZIONE CSS PER TEMA CHIARO E GRAFICA PULITA ---
st.markdown(
    """
<style>
    /* Sfondo Globale Chiaro */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Card KPI in stile Light Mode */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
    }
    .kpi-subtitle {
        font-size: 0.8rem;
        color: #475569;
        margin-top: 8px;
    }
    .badge-positive {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .badge-info {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.75rem;
    }

    /* Stile Tab Moderni */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 6px;
        color: #475569;
        font-weight: 600;
        border: none;
        padding: 0 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
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
        "<div style='text-align: center; margin-top: 50px;'><h1 style='color:#0f172a;'>🔒 Accesso Riservato</h1><p style='color: #64748b;'>Sintec S.r.l. - Controllo di Gestione</p></div>",
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

# --- DATI FATTURATO E COSTI ---
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

# --- DATI CLIENTI AGGIORNATI DAI REPORT DEL NOTEBOOK ---
df_clienti_2026 = pd.DataFrame({
    "Cliente": [
        "WITTUR SPA",
        "SIDEL S.P.A.",
        "ACMI LABELLING SRL",
        "SILVI S.R.L.",
        "ACMI BEVERAGE SPA",
        "GAMMA MECCANICA S.p.A",
        "CATTANI SPA",
        "GEA MECHANICAL EQUIPMENT",
        "CALF SPA",
        "REGGIANA RIDUTTORI SRL",
        "CSF INOX S.P.A.",
        "WIPRO FERRETTO",
        "DIECI SRL",
        "ERRESSE Costmec",
        "JOHN BEAN TECHNOLOGIES",
        "STV DI SALATI G. & C.",
        "PRISMA S.P.A.",
        "I.E. PARK SRL",
        "ALTRI CLIENTI / MINORI",
    ],
    "Fatturato 2026 Gen-Giu (€)": [
        136922.00,
        102256.14,
        33484.00,
        25690.50,
        17577.00,
        15828.00,
        13314.00,
        10253.00,
        9133.00,
        5238.00,
        3975.00,
        4880.00,
        2790.00,
        3273.00,
        2640.00,
        2410.00,
        2227.50,
        1860.00,
        28884.26,
    ],
    "Num Fatture": [
        19,
        29,
        6,
        6,
        2,
        5,
        6,
        4,
        3,
        1,
        2,
        3,
        1,
        1,
        2,
        3,
        2,
        1,
        10,
    ],
})

dati_clienti_mensili = {
    "WITTUR SPA": {
        "2026": [19638.0, 19653.0, 27121.5, 20090.5, 18483.0, 31936.0, 0.0],
        "2025": [
            15561.0,
            13911.5,
            18000.0,
            16500.0,
            17800.0,
            18200.0,
            19500.0,
        ],
        "2024": [
            12000.0,
            14000.0,
            17547.0,
            16000.0,
            17804.5,
            16500.0,
            23948.5,
        ],
    },
    "SIDEL S.P.A.": {
        "2026": [10880.5, 12822.0, 16817.5, 16608.1, 19245.0, 20760.0, 0.0],
        "2025": [
            9078.0,
            13487.31,
            11200.0,
            12500.0,
            14000.0,
            11800.0,
            12900.0,
        ],
        "2024": [
            11000.0,
            12500.0,
            13000.0,
            10500.0,
            11800.0,
            12200.0,
            14000.0,
        ],
    },
    "ACMI LABELLING SRL": {
        "2026": [3284.0, 0.0, 3624.0, 4770.0, 0.0, 21806.0, 0.0],
        "2025": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "2024": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    },
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

# --- HELPER LAYOUT GRAFICI ---
def layout_grafico_chiaro(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#0f172a"),
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


# --- SIDEBAR E NAVIGAZIONE ---
st.sidebar.markdown(
    "<h2 style='text-align: center; color: #1e3a8a;'>⚙️ Sintec App</h2>",
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

if sezione == "📈 Dashboard Grafica":
    st.sidebar.subheader("🎛️ Filtri e Caricamento Dati")
    anno_selezionato = st.sidebar.selectbox(
        "Seleziona Anno Analisi", [2026, 2024]
    )

    label_anno = (
        "2026 (Parziale Gen–Lug)"
        if anno_selezionato == 2026
        else str(anno_selezionato)
    )
    st.markdown(
        f"## 📊 Risultati **{label_anno}** vs **2025** (Anno Riferimento)"
    )

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

    # --- KPI CARDS ---
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.markdown(
            f"""
        <div class="kpi-card">
            <div class="kpi-title">Fatturato Totale {label_anno}</div>
            <div class="kpi-value">€ {tot_f_sel:,.2f}</div>
            <div style="margin-top:8px;"><span class="badge-positive">🔮 Previsionale 12M: € {prev_f_sel:,.2f}</span></div>
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
            <div class="kpi-value" style="color: #e11d48;">€ {tot_c_sel:,.2f}</div>
            <div style="margin-top:8px;"><span class="badge-info">🔮 Previsionale 12M: € {prev_c_sel:,.2f}</span></div>
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
            <div class="kpi-value" style="color: #16a34a;">€ {mol_sel:,.2f}</div>
            <div style="margin-top:8px;"><span class="badge-positive">🔮 Previsionale 12M: € {prev_mol_sel:,.2f}</span></div>
            <div class="kpi-subtitle">📌 2025 Gen-Lug: € {mol_2025_parz:,.2f} | Tot 2025: € {mol_2025_tot:,.2f}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- TAB ---
    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "📊 Fatturato",
        "👥 Costi Personale",
        "⏱️ Ore Dirette",
        "⚙️ Ore Indirette",
        "💶 Media Oraria",
        "📋 Dipendenti",
        "🍕 Analisi Clienti (Wittur & altri)",
    ])

    with t1:
        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=[f"Fatturato {anno_selezionato}", "Fatturato 2025"],
            barmode="group",
            title=f"Confronto Fatturato Mensile: {label_anno} vs 2025",
            color_discrete_sequence=["#2563eb", "#93c5fd"],
            text_auto=",.0f",
        )
        st.plotly_chart(
            layout_grafico_chiaro(fig_f), use_container_width=True
        )

    with t2:
        fig_c = px.bar(
            df_costi,
            x="Mese",
            y=[f"Costi {anno_selezionato}", "Costi 2025"],
            barmode="group",
            title=f"Confronto Costi Personale Mensili: {label_anno} vs 2025",
            color_discrete_sequence=["#e11d48", "#fda4af"],
            text_auto=",.0f",
        )
        st.plotly_chart(
            layout_grafico_chiaro(fig_c), use_container_width=True
        )

    with t3:
        fig_dir = px.bar(
            df_ore_dirette,
            x="Mese",
            y=["Ore Dirette 2026", "Ore Dirette 2025"],
            barmode="group",
            title=f"Confronto Ore Dirette: {label_anno} vs 2025",
            color_discrete_sequence=["#16a34a", "#86efac"],
            text_auto=",.1f",
        )
        st.plotly_chart(
            layout_grafico_chiaro(fig_dir), use_container_width=True
        )

    with t4:
        fig_ind = px.bar(
            df_ore_indirette,
            x="Mese",
            y=["Ore Indirette 2026", "Ore Indirette 2025"],
            barmode="group",
            title=f"Confronto Ore Indirette: {label_anno} vs 2025",
            color_discrete_sequence=["#d97706", "#fde047"],
            text_auto=",.1f",
        )
        st.plotly_chart(
            layout_grafico_chiaro(fig_ind), use_container_width=True
        )

    with t5:
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
            color_discrete_sequence=["#9333ea", "#c084fc", "#e9d5ff"],
            text_auto=",.2f",
        )
        st.plotly_chart(
            layout_grafico_chiaro(fig_media), use_container_width=True
        )

    with t6:
        st.subheader("📊 Totale Parziale 2026 - Costi e Ore Personale")
        st.dataframe(
            df_riassunto_2026.style.format({
                "COSTO TOT": "€ {:,.2f}",
                "ORE TOT": "{:,.1f}",
                "COSTO ORARIO": "€ {:,.2f}",
            }),
            use_container_width=True,
            height=400,
        )

    with t7:
        st.subheader("🍕 Analisi Dettagliata Clienti e Fatture Emesse (2026)")
        st.info(
            "💡 **Wittur SPA** è il primo cliente aziendale per volume d'affari nel 2026 (€ 136.922,00 su 19 fatture nel semestre)."
        )

        col_p1, col_p2 = st.columns([1.1, 1])
        with col_p1:
            fig_pie = px.pie(
                df_clienti_2026,
                values="Fatturato 2026 Gen-Giu (€)",
                names="Cliente",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
                title="Ripartizione Fatturato per Cliente (Gen-Giu 2026)",
            )
            fig_pie.update_traces(
                textposition="inside", textinfo="percent+label"
            )
            st.plotly_chart(
                layout_grafico_chiaro(fig_pie), use_container_width=True
            )

        with col_p2:
            st.markdown("#### 🏆 Classifica Completa Clienti (Gen-Giu 2026)")
            df_cli_s = df_clienti_2026.sort_values(
                by="Fatturato 2026 Gen-Giu (€)", ascending=False
            ).reset_index(drop=True)
            tot_cli = df_cli_s["Fatturato 2026 Gen-Giu (€)"].sum()
            df_cli_s["% Quota"] = (
                df_cli_s["Fatturato 2026 Gen-Giu (€)"] / tot_cli * 100
            ).round(2)

            st.dataframe(
                df_cli_s.style.format({
                    "Fatturato 2026 Gen-Giu (€)": "€ {:,.2f}",
                    "% Quota": "{:.2f} %",
                }),
                use_container_width=True,
                height=380,
            )

        st.markdown("---")
        st.subheader("🔎 Storico Mensile Cliente Singolo")
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
            title=f"Andamento Mensile Fatturato: {cli_scelto}",
            color_discrete_sequence=["#2563eb", "#60a5fa", "#93c5fd"],
            text_auto=",.0f",
        )
        st.plotly_chart(
            layout_grafico_chiaro(fig_cli_m), use_container_width=True
        )

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    st.subheader("🤖 Assistente IA Gestionale")
    domanda = st.text_input(
        "Fai una domanda sui dati di fatturato, Wittur o costi:"
    )
    if domanda and "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Sei l'assistente per il controllo di gestione di Sintec S.r.l.",
                },
                {"role": "user", "content": domanda},
            ],
        )
        st.success(res.choices[0].message.content)