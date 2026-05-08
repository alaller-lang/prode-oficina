import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Prode Dunlop 2026", page_icon="🏆", layout="wide")

# --- CONEXIÓN ---
@st.cache_resource
def conectar_hojas():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info_claves = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info_claves, scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Prode_Mundial_2026")
    return spreadsheet.worksheet("pronosticos"), spreadsheet.worksheet("resultados_reales")

ws_pronos, ws_reales = conectar_hojas()

# --- LÓGICA DE PUNTOS ---
def calcular_ranking():
    # Traer datos de empleados y resultados reales
    df_pronos = pd.DataFrame(ws_pronos.get_all_records())
    df_reales = pd.DataFrame(ws_reales.get_all_records())
    
    if df_pronos.empty or df_reales.empty:
        return None

    # Unir tablas por partido
    df_master = df_pronos.merge(df_reales, on="Partido", suffixes=('_user', '_real'))
    
    def puntos_partido(row):
        # Acierto Exacto (3 pts)
        if row['Goles Local_user'] == row['Goles Local_real'] and row['Goles Visitante_user'] == row['Goles Visitante_real']:
            return 3
        # Acierto Ganador/Empate (1 pt)
        signo_user = (row['Goles Local_user'] > row['Goles Visitante_user']) - (row['Goles Local_user'] < row['Goles Visitante_user'])
        signo_real = (row['Goles Local_real'] > row['Goles Visitante_real']) - (row['Goles Local_real'] < row['Goles Visitante_real'])
        if signo_user == signo_real:
            return 1
        return 0

    df_master['Puntos'] = df_master.apply(puntos_partido, axis=1)
    ranking = df_master.groupby('Nombre')['Puntos'].sum().reset_index().sort_values(by='Puntos', ascending=False)
    return ranking

# --- INTERFAZ ---
st.title("🏆 SISTEMA PRODE DUNLOP 2026")

menu = st.sidebar.radio("Navegación", ["🏠 Inicio / Carga", "📊 Ranking en Vivo", "⚙️ Administrador"])

# --- SECCIÓN 1: CARGA DE PRONÓSTICOS (Lo que ya tenías) ---
if menu == "🏠 Inicio / Carga":
    st.subheader("Cargá tu Prode")
    # ... (Aquí va todo el código de carga que ya pegamos antes) ...
    # Nota: Por brevedad no repito los 72 partidos, mantené el bloque del formulario anterior aquí.
    st.info("Completá tus datos en las pestañas y dale a Guardar.")

# --- SECCIÓN 2: RANKING (Puntajes parciales) ---
elif menu == "📊 Ranking en Vivo":
    st.subheader("Tabla de Posiciones Oficial")
    with st.spinner("Calculando puntajes..."):
        ranking = calcular_ranking()
        if ranking is not None:
            st.table(ranking) # Muestra la tabla de puntos sin que puedan tocar nada
        else:
            st.warning("Todavía no hay resultados cargados por el administrador.")

# --- SECCIÓN 3: ADMINISTRADOR (Solo vos) ---
elif menu == "⚙️ Administrador":
    st.subheader("Panel de Control")
    clave = st.text_input("Clave de acceso:", type="password")
    
    if clave == "DUNLOP2026": # Clave de ejemplo
        st.write("Bienvenido Alberto. Cargá los resultados reales:")
        with st.form("admin_results"):
            partido_nombre = st.text_input("Nombre del Partido (exacto):", placeholder="Ej: Argentina vs Argelia")
            g_l = st.number_input("Goles Local Real", 0, 15)
            g_v = st.number_input("Goles Visitante Real", 0, 15)
            if st.form_submit_button("Actualizar Resultado"):
                ws_reales.append_row([partido_nombre, g_l, g_v])
                st.success("Resultado guardado y ranking actualizado.")
    elif clave != "":
        st.error("Clave incorrecta")
