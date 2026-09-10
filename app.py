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
                layout_grafico_sintec(fig_pie),
                use_container_width=True,
                on_select="rerun",
                selection_mode="points",
                key="chart_clienti_pie"
            )

            # Cliccando sul grafico a torta si aggiorna il cliente
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

            # Tabella interattiva con gestione diretta dello stato
            event_cli = st.dataframe(
                df_cli_completo.style.apply(evidenzia_totale, col_chiave="Cliente", axis=1).format({
                    "Fatturato 2026 (Gen-Lug) (€)": "€ {:,.2f}",
                    "% Quota": "{:.2f} %"
                }),
                use_container_width=True,
                height=350,
                on_select="rerun",
                selection_mode="single-row"
            )

            # Aggiornamento automatico dello stato al click sulla riga
            if event_cli and "selection" in event_cli and event_cli["selection"]["rows"]:
                row_idx = event_cli["selection"]["rows"][0]
                cli_selezionato_riga = df_cli_completo.iloc[row_idx]["Cliente"]
                if cli_selezionato_riga in dati_clienti_mensili and st.session_state["cliente_selezionato"] != cli_selezionato_riga:
                    st.session_state["cliente_selezionato"] = cli_selezionato_riga
                    st.rerun()

        st.markdown("---")
        st.subheader("🔎 Dettaglio Mensile e Storico per Singolo Cliente")

        # Selezione sincronizzata con la tabella sopra
        idx_default = list(dati_clienti_mensili.keys()).index(st.session_state["cliente_selezionato"]) if st.session_state["cliente_selezionato"] in dati_clienti_mensili else 0

        cli_scelto = st.selectbox(
            "Seleziona Cliente da Verificare:",
            list(dati_clienti_mensili.keys()),
            index=idx_default,
            key="select_cli_box"
        )

        st.session_state["cliente_selezionato"] = cli_scelto