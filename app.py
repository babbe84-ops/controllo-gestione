import io
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

st.set_page_config(
    page_title="Sintec - Dashboard Controllo di Gestione", layout="wide"
)

# --- SCHERMATA DI LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Accesso Riservato - Sintec S.r.l.")
    with st.form("login_form"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        submit_button = st.form_submit_button("Accedi")

    if submit_button:
        if username == "sintec" and password == "Sintec2026!":
            st.session_state["authenticated"] = True
            st.success("Accesso effettuato con successo!")
            st.rerun()
        else:
            st.error("Credenziali non valide")
    st.stop()

# --- DATI FATTURATO E COSTI MESI ANNO ---
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

# --- DATI ORE DIRETTE E ORE INDIRETTE ---
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

# --- DATI MEDIA ORARIA (FATTURATO / ORE TOTALI) ---
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

# --- DATI CLIENTO / FATTURATO ---
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

# Dettagli mensili comparativi per cliente (Gen-Lug)
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

# --- DATI RIASSUNTIVI ANNO 2026 ---
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

# --- INTERFACCIA STREAMLIT ---
st.title("📊 Sintec S.r.l. - Controllo di Gestione")

st.sidebar.header("Navigazione")
sezione = st.sidebar.radio(
    "Menu Principale", ["📈 Dashboard Grafica", "🤖 Assistente IA (Testo e Voce)"]
)

st.sidebar.markdown("---")
st.sidebar.link_button(
    "📓 Apri Notebook Google",
    "https://notebook.google.com/notebook/e4078841-d0c1-4aed-8a70-1ee190c51016",
)

if sezione == "📈 Dashboard Grafica":
    st.sidebar.subheader("Filtri Visualizzazione")
    anno_selezionato = st.sidebar.selectbox(
        "Seleziona Anno da Analizzare", [2026, 2024]
    )

    file_upload = st.sidebar.file_uploader(
        "📁 Carica 'SCHEDA CONTROLLO ORE-FATTURATO' (.xlsx)", type=["xlsx"]
    )
    if file_upload:
        st.sidebar.success("File caricato! Aggiornamento dati in corso...")

    label_anno = (
        "2026 (Parziale Gen–Lug)"
        if anno_selezionato == 2026
        else str(anno_selezionato)
    )

    st.markdown(
        f"### 🎯 Risultati **{label_anno}** in Confronto al **2025** (Anno di Riferimento)"
    )

    # --- CALCOLI REALI E PREVISIONALI MATEMATICI ---
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

    diff_f = tot_f_sel - tot_f_2025_tot
    diff_c = tot_c_sel - tot_c_2025_tot
    diff_mol = mol_sel - mol_2025_tot

    col1, col2, col3 = st.columns(3)

    col1.metric(
        f"Fatturato Totale {label_anno}",
        f"€ {tot_f_sel:,.2f}",
        delta=f"€ {diff_f:,.2f} vs Tot 2025",
    )
    col1.caption(
        f"🔮 **Previsionale Fine Anno:** € {prev_f_sel:,.2f}  \n📌 **2025 Gen–Lug:** € {tot_f_2025_parz:,.2f} | **2025 Consuntivo:** € {tot_f_2025_tot:,.2f}"
    )

    col2.metric(
        f"Costi Personale {label_anno}",
        f"€ {tot_c_sel:,.2f}",
        delta=f"€ {diff_c:,.2f} vs Tot 2025",
        delta_color="inverse",
    )
    col2.caption(
        f"🔮 **Previsionale Fine Anno:** € {prev_c_sel:,.2f}  \n📌 **2025 Gen–Lug:** € {tot_c_2025_parz:,.2f} | **2025 Consuntivo:** € {tot_c_2025_tot:,.2f}"
    )

    col3.metric(
        f"Margine Operativo {label_anno}",
        f"€ {mol_sel:,.2f}",
        delta=f"€ {diff_mol:,.2f} vs Tot 2025",
    )
    col3.caption(
        f"🔮 **Previsionale Fine Anno:** € {prev_mol_sel:,.2f}  \n📌 **2025 Gen–Lug:** € {mol_2025_parz:,.2f} | **2025 Consuntivo:** € {mol_2025_tot:,.2f}"
    )

    st.markdown("---")
    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "📊 Confronto Fatturato",
        "👥 Costi Totali Personale",
        "⏱️ Ore Dirette",
        "⚙️ Ore Indirette",
        "💶 Media Oraria (Fatturato/Ore)",
        "📋 Dettaglio Dipendenti",
        "🍕 Analisi Fatturato per Cliente",
    ])

    with t1:
        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=[f"Fatturato {anno_selezionato}", "Fatturato 2025"],
            barmode="group",
            title=f"Confronto Fatturato Mensile: {label_anno} vs 2025",
            labels={"value": "Euro (€)", "variable": "Anno"},
            text_auto=",.0f",
        )
        fig_f.update_traces(textposition="outside")
        st.plotly_chart(fig_f, use_container_width=True)

    with t2:
        # GRAFICO A COLONNE / BARRE RAGGRUPPATE PER I COSTI DEL PERSONALE
        fig_c = px.bar(
            df_costi,
            x="Mese",
            y=[f"Costi {anno_selezionato}", "Costi 2025"],
            barmode="group",
            title=f"Confronto Costi Personale Mensili: {label_anno} vs 2025",
            labels={"value": "Euro (€)", "variable": "Anno"},
            text_auto=",.0f",
        )
        fig_c.update_traces(textposition="outside")
        st.plotly_chart(fig_c, use_container_width=True)

    with t3:
        tot_dir_26 = df_ore_dirette["Ore Dirette 2026"].sum()
        tot_dir_25_parz = df_ore_dirette["Ore Dirette 2025"].iloc[:7].sum()
        tot_dir_25_tot = df_ore_dirette["Ore Dirette 2025"].sum()
        diff_dir = tot_dir_26 - tot_dir_25_parz

        prev_dir_26 = (
            (tot_dir_26 / mesi_consolidati) * 12
            if anno_selezionato == 2026
            else tot_dir_26
        )

        st.subheader("⏱️ Andamento Ore Dirette (Lavoro Operativo)")
        c_dir1, c_dir2 = st.columns(2)
        c_dir1.metric(
            "Ore Dirette 2026 (Gen–Lug)",
            f"{tot_dir_26:,.1f} h",
            delta=f"{diff_dir:,.1f} h vs 2025 Gen-Lug",
        )
        c_dir2.caption(
            f"🔮 **Previsionale Fine Anno 2026:** {prev_dir_26:,.1f} h  \n📌 **Ore Dirette 2025 Parziale (Gen–Lug):** {tot_dir_25_parz:,.1f} h  \n📌 **Consuntivo 2025 Totale:** {tot_dir_25_tot:,.1f} h"
        )

        fig_dir = px.bar(
            df_ore_dirette,
            x="Mese",
            y=["Ore Dirette 2026", "Ore Dirette 2025"],
            barmode="group",
            title=f"Confronto Ore Dirette Mensili: {label_anno} vs 2025",
            labels={"value": "Ore (h)", "variable": "Anno"},
            text_auto=",.1f",
        )
        fig_dir.update_traces(textposition="outside")
        st.plotly_chart(fig_dir, use_container_width=True)

    with t4:
        tot_ind_26 = df_ore_indirette["Ore Indirette 2026"].sum()
        tot_ind_25_parz = df_ore_indirette["Ore Indirette 2025"].iloc[:7].sum()
        tot_ind_25_tot = df_ore_indirette["Ore Indirette 2025"].sum()
        diff_ind = tot_ind_26 - tot_ind_25_parz

        prev_ind_26 = (
            (tot_ind_26 / mesi_consolidati) * 12
            if anno_selezionato == 2026
            else tot_ind_26
        )

        st.subheader("⚙️ Andamento Ore Indirette (Gestione / Struttura)")
        c_ind1, c_ind2 = st.columns(2)
        c_ind1.metric(
            "Ore Indirette 2026 (Gen–Lug)",
            f"{tot_ind_26:,.1f} h",
            delta=f"{diff_ind:,.1f} h vs 2025 Gen-Lug",
            delta_color="inverse",
        )
        c_ind2.caption(
            f"🔮 **Previsionale Fine Anno 2026:** {prev_ind_26:,.1f} h  \n📌 **Ore Indirette 2025 Parziale (Gen–Lug):** {tot_ind_25_parz:,.1f} h  \n📌 **Consuntivo 2025 Totale:** {tot_ind_25_tot:,.1f} h"
        )

        fig_ind = px.bar(
            df_ore_indirette,
            x="Mese",
            y=["Ore Indirette 2026", "Ore Indirette 2025"],
            barmode="group",
            title=f"Confronto Ore Indirette Mensili: {label_anno} vs 2025",
            labels={"value": "Ore (h)", "variable": "Anno"},
            text_auto=",.1f",
        )
        fig_ind.update_traces(textposition="outside")
        st.plotly_chart(fig_ind, use_container_width=True)

    with t5:
        st.subheader("💶 Media Oraria (Fatturato / Ore Totali)")

        media_2026_gen_lug = 31.42
        media_2025_gen_lug = 29.23
        diff_media = media_2026_gen_lug - media_2025_gen_lug

        m1, m2 = st.columns(2)
        m1.metric(
            "Media Oraria 2026 (Gen–Lug)",
            f"€ {media_2026_gen_lug:,.2f} / h",
            delta=f"€ {diff_media:,.2f} / h vs 2025 Gen-Lug",
        )
        m2.caption(
            f"📌 **Media Oraria 2025 Parziale (Gen–Lug):** € {media_2025_gen_lug:,.2f} / h  \n📌 **Consuntivo 2025 Totale:** € 30.12 / h  \n📌 **Consuntivo 2024 Totale:** € 28.83 / h"
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
            title=f"Confronto Media Oraria (€/h): {label_anno} vs 2025 vs 2024",
            labels={"value": "Euro per Ora (€/h)", "variable": "Anno"},
            text_auto=",.2f",
        )
        fig_media.update_traces(textposition="outside")
        st.plotly_chart(fig_media, use_container_width=True)

    with t6:
        st.subheader(
            "📊 TOTALE ANNO 2026 (PARZIALE GEN–LUG) - COSTI DEL PERSONALE"
        )

        def evidenzia_totale(row):
            if "TOTALE SINTEC" in row["COGNOME"]:
                return [
                    "background-color: #fff3cd; font-weight: bold; color: #856404"
                ] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_riassunto_2026.style.apply(evidenzia_totale, axis=1).format({
                "COSTO TOT": "€ {:,.2f}",
                "ORE TOT": "{:,.1f}",
                "COSTO ORARIO": "€ {:,.2f}",
            }),
            use_container_width=True,
            height=530,
        )

        st.markdown("---")

        st.subheader("🔎 Analisi Mese per Mese per Dipendente (Gen–Lug 2026)")
        dipendente_scelto = st.selectbox(
            "Seleziona un Dipendente per il dettaglio mensile:",
            list(dati_dipendenti_mensili.keys()),
        )

        costi_dip = dati_dipendenti_mensili[dipendente_scelto]["Costo"]
        ore_dip = dati_dipendenti_mensili[dipendente_scelto]["Ore"]

        df_dip = pd.DataFrame({
            "Mese": mesi,
            "Costo Totale (€)": costi_dip,
            "Ore Totali": ore_dip,
        })
        df_dip["Costo Orario (€/h)"] = (
            df_dip["Costo Totale (€)"] / df_dip["Ore Totali"]
        ).fillna(0).round(2)

        st.write(
            f"**Prospetto Mensile 2026 (Parziale Gen-Lug) - {dipendente_scelto}**"
        )
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
            title=f"Andamento Mensile Costi - {dipendente_scelto} (Gen–Lug 2026)",
        )
        fig_dip.update_traces(textposition="outside")
        st.plotly_chart(fig_dip, use_container_width=True)

    with t7:
        st.subheader("🍕 Ripartizione Percentuale del Fatturato per Cliente")

        col_pie1, col_pie2 = st.columns([1.2, 1])

        with col_pie1:
            fig_pie = px.pie(
                df_clienti_2026,
                values="Fatturato 2026",
                names="Cliente",
                title="Quota Fatturato per Cliente (Anno 2026 Gen–Lug)",
                hole=0.3,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_pie2:
            st.markdown("#### 📋 Graduatoria Fatturato Clienti")
            df_cli_sorted = df_clienti_2026.sort_values(
                by="Fatturato 2026", ascending=False
            ).reset_index(drop=True)
            tot_cli = df_cli_sorted["Fatturato 2026"].sum()
            df_cli_sorted["% Sul Totale"] = (
                df_cli_sorted["Fatturato 2026"] / tot_cli * 100
            ).round(2)

            st.dataframe(
                df_cli_sorted.style.format({
                    "Fatturato 2026": "€ {:,.2f}",
                    "% Sul Totale": "{:.2f} %",
                }),
                use_container_width=True,
                height=420,
            )

        st.markdown("---")
        st.subheader(
            "🔎 Dettaglio Mensile per Cliente e Confronto Anni Precedenti"
        )

        cliente_scelto = st.selectbox(
            "Seleziona un Cliente per visualizzare lo storico mensile:",
            list(dati_clienti_mensili.keys()),
        )

        df_cli_m = pd.DataFrame({
            "Mese": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug"],
            "Fatturato 2026 (€)": dati_clienti_mensili[cliente_scelto]["2026"],
            "Fatturato 2025 (€)": dati_clienti_mensili[cliente_scelto]["2025"],
            "Fatturato 2024 (€)": dati_clienti_mensili[cliente_scelto]["2024"],
        })

        st.write(
            f"**Andamento Mensile Fatturato (Gen–Lug) - {cliente_scelto}**"
        )
        st.dataframe(
            df_cli_m.style.format({
                "Fatturato 2026 (€)": "€ {:,.2f}",
                "Fatturato 2025 (€)": "€ {:,.2f}",
                "Fatturato 2024 (€)": "€ {:,.2f}",
            }),
            use_container_width=True,
        )

        fig_cli_m = px.bar(
            df_cli_m,
            x="Mese",
            y=[
                "Fatturato 2026 (€)",
                "Fatturato 2025 (€)",
                "Fatturato 2024 (€)",
            ],
            barmode="group",
            title=f"Confronto Storico Mensile: {cliente_scelto} (2026 vs 2025 vs 2024)",
            text_auto=",.0f",
        )
        fig_cli_m.update_traces(textposition="outside")
        st.plotly_chart(fig_cli_m, use_container_width=True)

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    st.subheader("Assistente Virtuale Sintec")
    st.write(
        "Poni qualsiasi domanda relativa a Fatturato, Ore e Costi del Personale."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        domanda = st.text_input(
            "Scrivi una domanda:",
            placeholder="Es. Qual è la percentuale di fatturato del cliente CALF nel 2026?",
        )
    with col2:
        st.write("Oppure parla:")
        audio = mic_recorder(
            start_prompt="🎙️ Registra",
            stop_prompt="⏹️ Ferma",
            key="recorder",
            format="wav",
        )

    if domanda:
        st.markdown("---")
        st.markdown("### 💡 Risposta dell'Assistente:")

        if "OPENAI_API_KEY" in st.secrets:
            try:
                prompt_sistema = """
                Sei l'assistente virtuale di Controllo di Gestione di Sintec S.r.l.
                Rispondi in modo professionale, sintetico e preciso.
                Dati aziendali principali:
                - Fatturato 2026 Gen-Lug: € 490.149,83 | Previsionale 2026 (12 mesi): € 840.256,85 | Consuntivo 2025: € 801.134,71
                - Costi Personale 2026 Gen-Lug: € 268.016,84 | Previsionale 2026 (12 mesi): € 459.457,44 | Consuntivo 2025: € 453.488,81
                - Margine 2026 Gen-Lug: € 222.132,99 | Previsionale 2026 (12 mesi): € 380.799,41 | Consuntivo 2025: € 347.645,90
                - Media Oraria 2026 Gen-Lug: € 31,42/h | Consuntivo 2025: € 30,12/h
                - Ore Dirette 2026 Gen-Lug: 14.114,0 h | Previsionale 2026: 24.195,4 h | Consuntivo 2025: 25.026,0 h
                - Ore Indirette 2026 Gen-Lug: 1.488,5 h | Previsionale 2026: 2.551,7 h | Consuntivo 2025: 1.573,0 h
                """
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": domanda},
                    ],
                )
                risposta = response.choices[0].message.content
                st.success(risposta)
            except Exception as e:
                st.error(f"Errore nell'elaborazione dell'API OpenAI: {e}")

        domanda_lower = domanda.lower()

        if "media oraria" in domanda_lower:
            fig_m = px.bar(
                df_media_oraria.iloc[:7],
                x="Mese",
                y=["Media Oraria 2026", "Media Oraria 2025", "Media Oraria 2024"],
                barmode="group",
                title="💶 Media Oraria (€/h): 2026 vs 2025 vs 2024 (Gen-Lug)",
                text_auto=",.2f",
            )
            fig_m.update_traces(textposition="outside")
            st.plotly_chart(fig_m, use_container_width=True)

        elif "ore dirette" in domanda_lower:
            fig_a = px.bar(
                df_ore_dirette.iloc[:7],
                x="Mese",
                y=["Ore Dirette 2026", "Ore Dirette 2025"],
                barmode="group",
                title="⏱️ Andamento Ore Dirette: 2026 vs 2025 (Gen-Lug)",
                text_auto=",.1f",
            )
            fig_a.update_traces(textposition="outside")
            st.plotly_chart(fig_a, use_container_width=True)

        elif "ore indirette" in domanda_lower:
            fig_b = px.bar(
                df_ore_indirette.iloc[:7],
                x="Mese",
                y=["Ore Indirette 2026", "Ore Indirette 2025"],
                barmode="group",
                title="⚙️ Andamento Ore Indirette: 2026 vs 2025 (Gen-Lug)",
                text_auto=",.1f",
            )
            fig_b.update_traces(textposition="outside")
            st.plotly_chart(fig_b, use_container_width=True)

        elif "fatturato" in domanda_lower or "grafico" in domanda_lower:
            fig_c = px.bar(
                df_fat.iloc[:7],
                x="Mese",
                y=["Fatturato 2026", "Fatturato 2025"],
                barmode="group",
                title="📊 Andamento Fatturato: 2026 vs 2025 (Gen-Lug)",
                text_auto=",.0f",
            )
            fig_c.update_traces(textposition="outside")
            st.plotly_chart(fig_c, use_container_width=True)