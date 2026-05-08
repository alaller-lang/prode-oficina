import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Prode Dunlop 2026", page_icon="🏆", layout="wide")

# --- ESTILO INSTITUCIONAL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { 
        background-color: #FFD200 !important; 
        color: black !important; 
        border-radius: 10px;
        font-weight: bold;
    }
    h1 { color: #1a1a1a; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_hoja():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        info_claves = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info_claves, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Prode_Mundial_2026")
    except Exception as e:
        st.error("Error de conexión con las llaves.")
        st.stop()

sheet = conectar_hoja()
ws_pronosticos = sheet.worksheet("pronosticos")

# --- FIXTURE REAL COMPLETO (Simplificado para el ejemplo) ---
# Aquí podés agregar todos los grupos siguiendo esta estructura:
fixture_datos = {
    "Grupo A": [
        {"id": "A1", "L": "🇲🇽 México", "V": "🇿🇦 Sudáfrica"},
        {"id": "A2", "L": "🇰🇷 Corea Sur", "V": "🇨🇿 Rep. Checa"},
        {"id": "A3", "L": "🇲🇽 México", "V": "🇰🇷 Corea Sur"},
        {"id": "A4", "L": "🇨🇿 Rep. Checa", "V": "🇿🇦 Sudáfrica"}
    ],
    "Grupo J (Arg)": [
        {"id": "J1", "L": "🇦🇷 Argentina", "V": "🇩🇿 Argelia"},
        {"id": "J2", "L": "🇦🇹 Austria", "V": "🇯🇴 Jordania"},
        {"id": "J3", "L": "🇦🇷 Argentina", "V": "🇦🇹 Austria"},
        {"id": "J4", "L": "🇯🇴 Jordania", "V": "🇩🇿 Argelia"}
    ]
}

# --- INTERFAZ ---
# Logo de Dunlop (URL oficial)
st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/Dunlop_Logo.svg", width=150)
st.title("🏆 PRODE MUNDIAL 2026")

nombre = st.text_input("👤 TU NOMBRE Y APELLIDO:")

if nombre:
    tab_list = st.tabs(list(fixture_datos.keys()))
    
    with st.form("form_prode"):
        todos_los_resultados = []
        
        for i, grupo in enumerate(fixture_datos.keys()):
            with tab_list[i]:
                st.subheader(f"Partidos del {grupo}")
                for m in fixture_datos[grupo]:
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])
                    with col1: st.write(f"**{m['L']}**")
                    with col2: res_l = st.number_input("Goles", min_value=0, step=1, key=f"l_{m['id']}", label_visibility="collapsed")
                    with col3: st.write("vs")
                    with col4: res_v = st.number_input("Goles", min_value=0, step=1, key=f"v_{m['id']}", label_visibility="collapsed")
                    with col5: st.write(f"**{m['V']}**")
                    todos_los_resultados.append([nombre, f"{m['L']} vs {m['V']}", res_l, res_v])

        st.divider()
        enviar = st.form_submit_button("💾 GUARDAR TODOS MIS PRONÓSTICOS")

        if enviar:
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
            filas_a_guardar = [fila + [ahora] for fila in todos_los_resultados]
            try:
                ws_pronosticos.append_rows(filas_a_guardar)
                st.success(f"¡Hecho {nombre}! Tus pronósticos se guardaron en el Excel.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
else:
    st.info("👈 Por favor, escribí tu nombre arriba para empezar a cargar.")

st.sidebar.write("---")
st.sidebar.image("https://www.dunlop.com/wp-content/themes/dunlop/img/dunlop-logo.png", width=100)
st.sidebar.write("Prode Dunlop v1.0")
