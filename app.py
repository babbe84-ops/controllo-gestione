# Esempio per la tabella dei dipendenti:
event_dip = st.dataframe(
    df_riassunto_2026,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row" # Abilita il click sulla riga
)

# Se l'utente clicca su una riga, mostriamo la tabella di dettaglio in basso
if event_dip and event_dip["selection"]["rows"]:
    row_idx = event_dip["selection"]["rows"][0]
    dip_selezionato = df_riassunto_2026.iloc[row_idx]["COGNOME"]
    
    st.markdown(f"### 🔍 Dettaglio Analitico: **{dip_selezionato}**")
    
    # Tabella dettagliata che appare solo al click
    df_dettaglio_singolo = pd.DataFrame({
        "Mese": mesi,
        "Costo Totale (€)": dati_dipendenti_mensili[dip_selezionato]["Costo"],
        "Ore Totali": dati_dipendenti_mensili[dip_selezionato]["Ore"]
    })
    st.dataframe(df_dettaglio_singolo, use_container_width=True)