import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Prode Mundial 2026", page_icon="🏆")

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_hoja():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Leemos el secreto como un texto plano y lo convertimos a JSON
    info_claves = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info_claves, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Prode_Mundial_2026")

try:
    sheet = conectar_hoja()
    ws_pronosticos = sheet.worksheet("pronosticos")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- LÓGICA ---
st.title("🏆 Prode Oficina 2026")
hoy = datetime.now()

nombre = st.text_input("Tu Nombre:")
partido = st.selectbox("Partido:", ["Argentina vs España", "Brasil vs Francia", "México vs USA"])

c1, c2 = st.columns(2)
g_l = c1.number_input("Goles Local", min_value=0, step=1)
g_v = c2.number_input("Goles Visitante", min_value=0, step=1)

if st.button("Guardar Pronóstico"):
    if nombre:
        ws_pronosticos.append_row([nombre, partido, g_l, g_v, str(hoy)])
        st.success("¡Pronóstico guardado en el Excel!")
    else:
        st.warning("Por favor, poné tu nombre.")
