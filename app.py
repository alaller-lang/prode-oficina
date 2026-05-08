elif opc == "⚙️ Admin":
    st.header("⚙️ Panel de Control")
    pw = st.text_input("Clave:", type="password")
    if pw == "DUNLOP2026":
        ta1, ta2, ta3 = st.tabs(["⚽ Partidos", "🏅 Podio Oficial", "💎 Bonus"])
        
        with ta1:
            with st.form("a1"):
                allm = [p for s in fixture.values() for p in s]
                ps = st.selectbox("Elegí el Partido:", sorted(allm))
                cl, cv = st.columns(2)
                rl = cl.number_input("Goles Local", 0, 15)
                rv = cv.number_input("Goles Visitante", 0, 15)
                
                if st.form_submit_button("ACTUALIZAR RESULTADO"):
                    # LÓGICA PARA NO DUPLICAR:
                    filas_actuales = ws_r.get_all_values()
                    encontrado = False
                    
                    # Buscamos si el partido ya está en el Sheet para actualizarlo
                    for i, fila in enumerate(filas_actuales):
                        if fila[0] == ps:
                            ws_r.update(f'A{i+1}:C{i+1}', [[ps, rl, rv]])
                            encontrado = True
                            break
                    
                    if not encontrado:
                        ws_r.append_row([ps, rl, rv])
                    
                    st.success(f"Resultado de {ps} guardado correctamente.")

        with ta2:
            with st.form("a2"):
                st.write("Elegí los puestos reales una vez que se definan:")
                r1 = st.selectbox("1° - Campeón", equipos)
                r2 = st.selectbox("2° - Subcampeón", equipos)
                r3 = st.selectbox("3° - Tercero", equipos)
                r4 = st.selectbox("4° - Cuarto", equipos)
                
                if st.form_submit_button("GUARDAR PODIO OFICIAL"):
                    # Borramos podios viejos si existen y ponemos los nuevos
                    datos_r = ws_r.get_all_values()
                    nuevas_filas = [f for f in datos_r if not f[0].startswith("PODIO")]
                    nuevas_filas.extend([["PODIO 1", r1, ""], ["PODIO 2", r2, ""], ["PODIO 3", r3, ""], ["PODIO 4", r4, ""]])
                    ws_r.clear()
                    ws_r.append_rows(nuevas_filas)
                    st.success("Podio oficial actualizado.")

        with ta3:
            with st.form("a3"):
                rb1 = st.text_input("Nombre del autor del ÚLTIMO GOL de ARG en grupos:")
                rb2 = st.text_input("Nombre del autor del PRIMER GOL del ganador J en octavos:")
                if st.form_submit_button("GUARDAR GANADORES BONUS"):
                    datos_r = ws_r.get_all_values()
                    nuevas_filas = [f for f in datos_r if not f[0].startswith("BONUS")]
                    nuevas_filas.extend([["BONUS 1", rb1, ""], ["BONUS 2", rb2, ""]])
                    ws_r.clear()
                    ws_r.append_rows(nuevas_filas)
                    st.success("Ganadores de bonus actualizados.")
