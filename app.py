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

# --- STILE TEMA CHIARO E PULITO ---
st.markdown(
    """
<style>
    /* Sfondo Globale Chiaro e Font */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Card KPI in stile Light */
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .kpi-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
    }
    .kpi-subtitle {
        font-size: 0.78rem;
        color: #475569;
        margin-top: 6px;
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

    /* Stile dei Tab */
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

# --- LOGIN ---
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

# --- DATI GENERALI AMMINISTRATIVI (AGGIORNATI A LUGLIO 2026) ---
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

# --- DATI DETTAGLIATI CLIENTI ---
df_clienti_2026 = pd.DataFrame({
    "Cliente": [
        "WITTUR SPA",
        "SIDEL S.P.A.",
        "ACMI LABELLING SRL",
        "SILVI S.R.L.",
        "CATTANI SPA",
        "GAMMA MECCANICA S.p.A",
        "ACMI BEVERAGE SPA",
        "GEA MECHANICAL EQUIPMENT",
        "CALF SPA",
        "REGGIANA RIDUTTORI SRL",
        "CSF INOX S.P.A.",
        "DIECI SRL",
        "ERRESSE Costmec",
        "JOHN BEAN TECHNOLOGIES",
        "PRISMA S.P.A.",
        "I.E. PARK SRL",
        "ALTRI CLIENTI / MINORI",
    ],
    "Fatturato 2026 (Gen-Lug) (€)": [
        136922.00,
        102256.14,
        33484.00,
        25690.50,
        15372.00,
        18740.00,
        17577.00,
        12218.00,
        9133.00,
        5238.00,
        5175.00,
        4603.50,
        3273.00,
        2640.00,
        2227.50,
        1860.00,
        87540.19,
    ],
    "Num Fatture": [
        19,
        29,
        6,
        6,
        7,
        6,
        2,
        5,
        3,
        1,
        3,
        2,
        1,
        2,
        2,
        1,
        12,
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
    "GEA MECHANICAL EQUIPMENT": {
        "2026": [0.0, 385.0, 840.0, 3795.0, 3268.0, 0.0, 1965.0],
        "2025": [0.0, 0.0, 0.0, 0.0, 667.0, 0.0, 0.0],
        "2024": [0.0, 0.0, 0.0, 0.0, 0.0, 703.5, 0.0],
    },
    "CSF INOX S.P.A.": {
        "2026": [0.0, 0.0, 0.0, 0.0, 2295.0, 1680.0, 1200.0],
        "2025": [1920.0, 1920.0, 1920.0, 1440.0, 720.0, 1200.0, 2160.0],
        "2024": [0.0, 0.0, 1455.0, 1920.0, 1170.0, 0.0, 2160.0],
    },
    "DIECI SRL": {
        "2026": [0.0, 0.0, 0.0, 0.0, 0.0, 2790.0, 1813.50],
        "2025": [3168.0, 1792.0, 2912.0, 2016.0, 2016.0, 0.0, 0.0],
        "2024": [0.0, 980.0, 0.0, 3332.0, 7588.0, 3180.0, 4140.0],
    },
    "CALF SPA": {
        "2026": [4698.0, 4435.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "2025": [6061.0, 5017.0, 6365.5, 6742.5, 5408.5, 6612.0, 5814.5],
        "2024": [5026.0, 6149.5, 5908.0, 5110.0, 4018.0, 6734.0, 3976.0],
    },
}

if "cliente_selezionato" not in st.session_state:
    st.session_state["cliente_selezionato"] = "WITTUR SPA"


def layout_grafico_chiaro(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#0f172a"),
        margin=dict(l=20, r=20, t=40, b=20),
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


# --- SIDEBAR ---
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
    st.markdown("## 📊 Controllo di Gestione - **Sintec S.r.l.**")

    t1, t2, t3, t4, t5 = st.tabs([
        "🍕 Analisi Clienti",
        "📊 Fatturato",
        "👥 Costi Personale",
        "⏱️ Ore Dirette/Indirette",
        "💶 Media Oraria",
    ])

    with t1:
        st.subheader("🍕 Analisi e Classifica Fatturato Clienti (Gen-Lug 2026)")

        col_p1, col_p2 = st.columns([1.1, 1])

        with col_p1:
            fig_pie = px.pie(
                df_clienti_2026,
                values="Fatturato 2026 (Gen-Lug) (€)",
                names="Cliente",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3,
                title="Quota % Fatturato per Cliente (Clicca per selezionare)",
            )
            fig_pie.update_traces(
                textposition="inside", textinfo="percent+label"
            )
            fig_pie.update_layout(
                legend_itemclick=False, legend_itemdoubleclick=False
            )

            selected_pie = st.plotly_chart(
                layout_grafico_chiaro(fig_pie),
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
            )

            if selected_pie and "selection" in selected_pie:
                points = selected_pie["selection"].get("points", [])
                if points:
                    cli_cliccato = points[0].get("label")
                    if cli_cliccato in dati_clienti_mensili:
                        st.session_state["cliente_selezionato"] = cli_cliccato

        with col_p2:
            st.markdown("#### 🏆 Tabella Riepilogativa Clienti")
            df_cli_s = df_clienti_2026.sort_values(
                by="Fatturato 2026 (Gen-Lug) (€)", ascending=False
            ).reset_index(drop=True)
            tot_cli = df_cli_s["Fatturato 2026 (Gen-Lug) (€)"].sum()
            df_cli_s["% Quota"] = (
                df_cli_s["Fatturato 2026 (Gen-Lug) (€)"] / tot_cli * 100
            ).round(2)

            df_tot_riga = pd.DataFrame([{
                "Cliente": "TOTALE FATTURATO",
                "Fatturato 2026 (Gen-Lug) (€)": tot_cli,
                "Num Fatture": df_cli_s["Num Fatture"].sum(),
                "% Quota": 100.0,
            }])
            df_cli_completo = pd.concat(
                [df_cli_s, df_tot_riga], ignore_index=True
            )

            def style_totale_gen(row):
                if row["Cliente"] == "TOTALE FATTURATO":
                    return [
                        "background-color: #dbeafe; font-weight: bold; color: #1e40af"
                    ] * len(row)
                return [""] * len(row)

            st.dataframe(
                df_cli_completo.style.apply(style_totale_gen, axis=1).format({
                    "Fatturato 2026 (Gen-Lug) (€)": "€ {:,.2f}",
                    "% Quota": "{:.2f} %",
                }),
                use_container_width=True,
                height=380,
            )

        st.markdown("---")
        st.subheader("🔎 Dettaglio Mensile e Storico per Singolo Cliente")

        idx_default = (
            list(dati_clienti_mensili.keys()).index(
                st.session_state["cliente_selezionato"]
            )
            if st.session_state["cliente_selezionato"]
            in dati_clienti_mensili
            else 0
        )

        cli_scelto = st.selectbox(
            "Seleziona Cliente da Verificare:",
            list(dati_clienti_mensili.keys()),
            index=idx_default,
            key="select_cli_box",
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
            "2024 (€)": tot_2024,
        }])

        df_cli_m_tot = pd.concat([df_cli_m, df_tot_cliente], ignore_index=True)

        def style_totale_cli(row):
            if row["Mese"] == "TOTALE":
                return [
                    "background-color: #dcfce7; font-weight: bold; color: #15803d"
                ] * len(row)
            return [""] * len(row)

        col_t1, col_t2 = st.columns([1, 1.2])

        with col_t1:
            st.markdown(f"#### 📄 Dettagli & Totale: **{cli_scelto}**")
            st.dataframe(
                df_cli_m_tot.style.apply(style_totale_cli, axis=1).format({
                    "2026 (€)": "€ {:,.2f}",
                    "2025 (€)": "€ {:,.2f}",
                    "2024 (€)": "€ {:,.2f}",
                }),
                use_container_width=True,
            )

        with col_t2:
            fig_cli_m = px.bar(
                df_cli_m,
                x="Mese",
                y=["2026 (€)", "2025 (€)", "2024 (€)"],
                barmode="group",
                title=f"Confronto Storico Mensile: {cli_scelto}",
                color_discrete_sequence=["#2563eb", "#60a5fa", "#93c5fd"],
                text_auto=",.0f",
            )
            # VALORI SCRITTI SEMPRE SOPRA LE COLONNE
            fig_cli_m.update_traces(textposition="outside")
            fig_cli_m.update_layout(
                legend_itemclick=False, legend_itemdoubleclick=False
            )
            st.plotly_chart(
                layout_grafico_chiaro(fig_cli_m), use_container_width=True
            )

    with t2:
        st.subheader("📊 Confronto Fatturato Mensile Generale")
        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=["Fatturato 2026", "Fatturato 2025", "Fatturato 2024"],
            barmode="group",
            title="Andamento Fatturato Mensile (€)",
            color_discrete_sequence=["#2563eb", "#60a5fa", "#93c5fd"],
            text_auto=",.0f",
        )
        # VALORI SCRITTI SEMPRE SOPRA LE COLONNE
        fig_f.update_traces(textposition="outside")
        fig_f.update_layout(
            legend_itemclick=False, legend_itemdoubleclick=False
        )
        st.plotly_chart(layout_grafico_chiaro(fig_f), use_container_width=True)

    with t3:
        st.subheader("👥 Costi Personale Mensili")
        fig_c = px.bar(
            df_costi,
            x="Mese",
            y=["Costi 2026", "Costi 2025", "Costi 2024"],
            barmode="group",
            title="Andamento Costi Personale (€)",
            color_discrete_sequence=["#e11d48", "#f43f5e", "#fda4af"],
            text_auto=",.0f",
        )
        # VALORI SCRITTI SEMPRE SOPRA LE COLONNE
        fig_c.update_traces(textposition="outside")
        fig_c.update_layout(
            legend_itemclick=False, legend_itemdoubleclick=False
        )
        st.plotly_chart(layout_grafico_chiaro(fig_c), use_container_width=True)

    with t4:
        st.subheader("⏱️ Ore Dirette e Indirette")
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            fig_dir = px.bar(
                df_ore_dirette,
                x="Mese",
                y=["Ore Dirette 2026", "Ore Dirette 2025"],
                barmode="group",
                title="Ore Dirette Lavorate (h)",
                color_discrete_sequence=["#16a34a", "#86efac"],
                text_auto=",.1f",
            )
            fig_dir.update_traces(textposition="outside")
            fig_dir.update_layout(
                legend_itemclick=False, legend_itemdoubleclick=False
            )
            st.plotly_chart(
                layout_grafico_chiaro(fig_dir), use_container_width=True
            )

        with col_o2:
            fig_ind = px.bar(
                df_ore_indirette,
                x="Mese",
                y=["Ore Indirette 2026", "Ore Indirette 2025"],
                barmode="group",
                title="Ore Indirette (h)",
                color_discrete_sequence=["#d97706", "#fde047"],
                text_auto=",.1f",
            )
            fig_ind.update_traces(textposition="outside")
            fig_ind.update_layout(
                legend_itemclick=False, legend_itemdoubleclick=False
            )
            st.plotly_chart(
                layout_grafico_chiaro(fig_ind), use_container_width=True
            )

    with t5:
        st.subheader("💶 Media Oraria (Fatturato / Ore Totali)")
        fig_media = px.bar(
            df_media_oraria,
            x="Mese",
            y=["Media Oraria 2026", "Media Oraria 2025", "Media Oraria 2024"],
            barmode="group",
            title="Media Oraria (€/h)",
            color_discrete_sequence=["#9333ea", "#c084fc", "#e9d5ff"],
            text_auto=",.2f",
        )
        # VALORI SCRITTI SEMPRE SOPRA LE COLONNE
        fig_media.update_traces(textposition="outside")
        fig_media.update_layout(
            legend_itemclick=False, legend_itemdoubleclick=False
        )
        st.plotly_chart(
            layout_grafico_chiaro(fig_media), use_container_width=True
        )

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    st.subheader("🤖 Assistente IA Gestionale")
    domanda = st.text_input(
        "Chiedi all'Assistente sui dati o sui clienti (es. Wittur, Sidel, etc.):"
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