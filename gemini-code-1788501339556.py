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

# --- SCHERMATA DI LOGIN (Salvabile su iPhone / Chrome) ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔒 Accesso Riservato - Sintec S.r.l.")
    with st.form("login_form"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        submit_button = st.form_submit_button("Accedi")

    if submit_button:
        # Personalizza qui le tue credenziali
        if username == "sintec" and password == "Sintec2026!":
            st.session_state["authenticated"] = True
            st.success("Accesso effettuato con successo!")
            st.rerun()
        else:
            st.error("Credenziali non valide")
    st.stop()

# --- CARICAMENTO DATI ---
# Dati dal progetto Sintec
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

# --- INTERFACCIA WEB ---
st.title("📊 Sintec S.r.l. - Controllo di Gestione")

st.sidebar.header("Navigazione")
sezione = st.sidebar.radio(
    "Menu Principale", ["📈 Dashboard Grafica", "🤖 Assistente IA (Testo e Voce)"]
)

if sezione == "📈 Dashboard Grafica":
    anno = st.sidebar.selectbox("Anno di Riferimento KPI", [2026, 2025, 2024])

    c1, c2, c3 = st.columns(3)
    tot_f = df_fat[f"Fatturato_{anno}"].sum()
    tot_c = df_costi[f"Costi_{anno}"].sum()
    c1.metric("Totale Fatturato", f"€ {tot_f:,.2f}")
    c2.metric("Totale Costi Personale", f"€ {tot_c:,.2f}")
    c3.metric(
        "Margine Operativo",
        f"€ {(tot_f - tot_c):,.2f}",
        delta=f"{(((tot_f - tot_c) / tot_f) * 100 if tot_f > 0 else 0):.1f}% MOL",
    )

    st.markdown("---")
    t1, t2 = st.tabs(["📊 Fatturato Mensile", "👥 Costi del Personale"])

    with t1:
        fig_f = px.bar(
            df_fat,
            x="Mese",
            y=[f"Fatturato_{anno}"],
            title=f"Andamento Fatturato {anno}",
        )
        st.plotly_chart(fig_f, use_container_width=True)

    with t2:
        fig_c = px.line(
            df_costi,
            x="Mese",
            y=[f"Costi_{anno}"],
            markers=True,
            title=f"Andamento Costi Personale {anno}",
        )
        st.plotly_chart(fig_c, use_container_width=True)

elif sezione == "🤖 Assistente IA (Testo e Voce)":
    st.subheader("Assistente Virtuale Sintec")
    st.write(
        "Poni qualsiasi domanda relativa a Fatturato, Ore e Costi del Personale."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        domanda = st.text_input(
            "Scrivi una domanda:",
            placeholder="Es. Quanto abbiamo fatturato a Wittur nel 2026?",
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
        # Qui l'assistente consulta i dati del Notebook