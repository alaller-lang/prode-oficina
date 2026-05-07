import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Prode Mundial 2026", page_icon="🏆")

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_hoja():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Nota: Aquí usaremos st.secrets para que sea seguro en la nube
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Prode_Mundial_2026")

sheet = conectar_hoja()
ws_pronosticos = sheet.worksheet("pronosticos")

# --- LÓGICA DE BLOQUEO (FASE 4 ANTECIPADA) ---
FECHA_INICIO = datetime(2026, 6, 11) # Ejemplo: Inicio del Mundial
hoy = datetime.now()

# --- INTERFAZ ---
st.title("🏆 Prode Oficina 2026")

menu = ["🏠 Inicio", "📝 Cargar Pronóstico", "🌟 Bonus Semifinalistas", "📊 Posiciones"]
choice = st.sidebar.selectbox("Menú", menu)

if choice == "🏠 Inicio":
    st.write("### ¡Bienvenido al Prode de la Oficina!")
    st.info("Cargá tus resultados antes de que empiecen los partidos.")

elif choice == "📝 Cargar Pronóstico":
    if hoy > FECHA_INICIO:
        st.error("🚫 El tiempo de carga ha finalizado. ¡Suerte a todos!")
    else:
        st.subheader("Registrá tu predicción")
        nombre = st.text_input("Tu Nombre:")
        partido = st.selectbox("Partido:", ["Argentina vs España", "Brasil vs Francia", "México vs USA"])
        
        c1, c2 = st.columns(2)
        g_l = c1.number_input("Goles Local", min_value=0, step=1)
        g_v = c2.number_input("Goles Visitante", min_value=0, step=1)
        
        if st.button("Guardar"):
            if nombre:
                ws_pronosticos.append_row([nombre, partido, g_l, g_v, str(hoy)])
                st.success("¡Pronóstico guardado!")
            else:
                st.warning("Poné tu nombre.")

elif choice == "🌟 Bonus Semifinalistas":
    st.subheader("¿Quiénes llegarán a Semis?")
    st.write("Elegí tus 4 candidatos antes del inicio.")
    # Aquí Gemini nos ayudará después a crear la pestaña 'especiales' en el Excel
    st.warning("Esta sección se habilitará cuando definamos los grupos.")

elif choice == "📊 Posiciones":
    st.subheader("Ranking General")
    st.write("Aquí se verán los puntos calculados en el Excel.")