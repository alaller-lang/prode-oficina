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
    try:
        info_claves = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info_claves, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Prode_Mundial_2026")
    except Exception as e:
        st.error(f"Error de configuración de llaves: {e}")
        st.stop()

try:
    sheet = conectar_hoja()
    ws_pronosticos = sheet.worksheet("pronosticos")
except Exception as e:
    st.error(f"Error de conexión con la planilla: {e}")
    st.stop()

# --- FIXTURE COMPLETO (FASE DE GRUPOS) ---
fixture = [
    "11/06: México vs Sudáfrica (Grupo A)",
    "11/06: Corea del Sur vs Rep. Checa (Grupo A)",
    "12/06: Canadá vs Bosnia (Grupo B)",
    "12/06: EE. UU. vs Paraguay (Grupo D)",
    "13/06: Catar vs Suiza (Grupo B)",
    "13/06: Brasil vs Marruecos (Grupo C)",
    "13/06: Haití vs Escocia (Grupo C)",
    "14/06: Australia vs Turquía (Grupo D)",
    "14/06: Alemania vs Curazao (Grupo E)",
    "14/06: Países Bajos vs Japón (Grupo F)",
    "14/06: Costa de Marfil vs Ecuador (Grupo E)",
    "15/06: Suecia vs Túnez (Grupo F)",
    "15/06: España vs Cabo Verde (Grupo H)",
    "15/06: Bélgica vs Egipto (Grupo G)",
    "15/06: Arabia Saudita vs Uruguay (Grupo H)",
    "16/06: Irán vs Nueva Zelanda (Grupo G)",
    "16/06: Francia vs Senegal (Grupo I)",
    "16/06: Irak vs Noruega (Grupo I)",
    "16/06: Argentina vs Argelia (Grupo J)",
    "17/06: Austria vs Jordania (Grupo J)",
    "17/06: Portugal vs RD Congo (Grupo K)",
    "17/06: Inglaterra vs Croacia (Grupo L)",
    "17/06: Ghana vs Panamá (Grupo L)",
    "17/06: Uzbekistán vs Colombia (Grupo K)",
    "18/06: Rep. Checa vs Sudáfrica (Grupo A)",
    "18/06: Suiza vs Bosnia (Grupo B)",
    "18/06: Canadá vs Catar (Grupo B)",
    "18/06: México vs Corea del Sur (Grupo A)",
    "19/06: EE. UU. vs Australia (Grupo D)",
    "19/06: Escocia vs Marruecos (Grupo C)",
    "19/06: Brasil vs Haití (Grupo C)",
    "20/06: Turquía vs Paraguay (Grupo D)",
    "20/06: Países Bajos vs Suecia (Grupo F)",
    "20/06: Alemania vs Costa de Marfil (Grupo E)",
    "20/06: Ecuador vs Curazao (Grupo E)",
    "21/06: Túnez vs Japón (Grupo F)",
    "21/06: España vs Arabia Saudí (Grupo H)",
    "21/06: Bélgica vs Irán (Grupo G)",
    "21/06: Uruguay vs Cabo Verde (Grupo H)",
    "21/06: Nueva Zelanda vs Egipto (Grupo G)",
    "22/06: Argentina vs Austria (Grupo J)",
    "22/06: Francia vs Irak (Grupo I)",
    "22/06: Noruega vs Senegal (Grupo I)",
    "22/06: Jordania vs Argelia (Grupo J)",
    "23/06: Portugal vs Uzbekistán (Grupo K)",
    "23/06: Inglaterra vs Ghana (Grupo L)",
    "23/06: Panamá vs Croacia (Grupo L)",
    "23/06: Colombia vs RD Congo (Grupo K)",
    "24/06: Rep. Checa vs México (Grupo A)",
    "24/06: Sudáfrica vs Corea del Sur (Grupo A)",
    "24/06: Suiza vs Canadá (Grupo B)",
    "24/06: Bosnia vs Catar (Grupo B)",
    "24/06: Marruecos vs Haití (Grupo C)",
    "24/06: Brasil vs Escocia (Grupo C)",
    "27/06: Jordania vs Argentina (Grupo J)",
    "27/06: Panamá vs Inglaterra (Grupo L)",
    "27/06: Croacia vs Ghana (Grupo L)",
    "27/06: Colombia vs Portugal (Grupo K)"
]

# --- INTERFAZ ---
st.title("🏆 Prode Oficina 2026")
st.write("Registrá tus pronósticos para la fase de grupos.")

nombre = st.text_input("Tu Nombre:")
partido_elegido = st.selectbox("Seleccioná el Partido:", fixture)

c1, c2 = st.columns(2)
g_l = c1.number_input("Goles Local", min_value=0, step=1, value=0)
g_v = c2.number_input("Goles Visitante", min_value=0, step=1, value=0)

if st.button("Guardar Pronóstico"):
    if nombre:
        try:
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ws_pronosticos.append_row([nombre, partido_elegido, g_l, g_v, ahora])
            st.success(f"¡Hecho! Pronóstico guardado para {partido_elegido}")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.warning("Por favor, escribí tu nombre antes de guardar.")

st.divider()
st.info("Recordá: Los puntos se calcularán automáticamente al finalizar cada partido.")
