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
    "Fatturato_2024": [
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
    "Fatturato_2025": [
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
    "Fatturato_2026": [
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
    "Costi_2024": [
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
    "Costi_2025": [
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
    "Costi_2026": [
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

# --- DATI RIASSUNTIVI ANNO 2026 (PARZIALE GEN-LUG 2026) ---
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

# --- DATI DETTAGLIO MENSILE PER SINGOLO DIPENDENTE ---
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

    # Etichetta dinamica per evidenziare il parziale 2026
    label_anno = (
        "2026 (Parziale Gen–Lug)"
        if anno_selezionato == 2026
        else str(anno_selezionato)
    )

    st.markdown(
        f"### 🎯 Risultati **{label_anno}** in Confronto al **2025** (Anno Completo di Riferimento)"
    )

    tot_f_sel = df_fat[f"Fatturato_{anno_selezionato}"].sum()
    tot_f_2025 = df_fat["Fatturato_2025"].sum()
    diff_f = tot_f_sel - tot_f_2025

    tot_c_sel = df_costi[f"Costi_{anno_selezionato}"].sum()
    tot_c_2025 = df_costi["Costi_2025"].sum()
    diff_c = tot_c_sel - tot_c_2025

    mol_sel = tot_f_sel - tot_c_sel
    mol_2025 = tot_f_2025 - tot_c_2025
    diff_mol = mol_sel - mol_2025

    col1, col2, col3 = st.columns(3)
    col1.metric(
        f"Fatturato Totale {label_anno}",
        f"€ {tot_f_sel:,.2f}",
        delta=f"€ {diff_f:,.2f} vs 2025",
    )
    col2.metric(
        f"Costi Personale {label_anno}",
        f"€ {tot_c_sel:,.2f}",
        delta=f"€ {diff_c:,.2f} vs 2025",
        delta_color="inverse",
    )
    col3.metric(
        f"Margine Operativo {label_anno}",
        f"€ {mol_sel:,.2f}",
        delta=f"€ {diff_mol:,.2f} vs 2025",
    )

    st.markdown("---")
    t1, t2, t3 = st.tabs([
        "📊 Confronto Fatturato",
        "👥 Costi Totali Personale",
        "📋 Dettaglio Dipendenti",
    ])

    with t1:
        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=[f"Fatturato_{anno_selezionato}", "Fatturato_2025"],
            barmode="group",
            title=f"Confronto Fatturato Mensile: {label_anno} vs 2025",
            labels={"value": "Euro (€)", "variable": "Anno"},
            text_auto=",.0f",
        )
        fig_f.update_traces(textposition="outside")
        st.plotly_chart(fig_f, use_container_width=True)

    with t2:
        fig_c = px.line(
            df_costi,
            x="Mese",
            y=[f"Costi_{anno_selezionato}", "Costi_2025"],
            markers=True,
            title=f"Confronto Costi Personale Mensili: {label_anno} vs 2025",
            labels={"value": "Euro (€)", "variable": "Anno"},
            text=[
                f"€{val:,.0f}" if val > 0 else ""
                for val in df_costi[f"Costi_{anno_selezionato}"]
            ],
        )
        fig_c.update_traces(textposition="top center")
        st.plotly_chart(fig_c, use_container_width=True)

    with t3:
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

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    st.subheader("Assistente Virtuale Sintec")
    st.write(
        "Poni qualsiasi domanda relativa a Fatturato, Ore e Costi del Personale."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        domanda = st.text_input(
            "Scrivi una domanda:",
            placeholder="Es. Quanto abbiamo fatturato a Wittur nei primi mesi del 2026?",
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
        st.info(f"Elaborazione richiesta per: **{domanda}**")