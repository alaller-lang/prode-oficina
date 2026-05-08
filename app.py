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
        background-color: #FFD200; /* Amarillo Dunlop */
        color: black; 
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    .stTextInput>div>div>input { background-color: #ffffff; }
    h1 { color: #1a1a1a; font-family: 'Arial Black'; }
    .match-row {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #FFD200;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_path=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_hoja():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        info_claves = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(info_claves, scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Prode_Mundial_2026")
    except Exception as e:
        st.error("Error de conexión. Avisale al administrador.")
        st.stop()

sheet = conectar_hoja()
ws_pronosticos = sheet.worksheet("pronosticos")

# --- DATOS DEL FIXTURE ---
fixture_datos = {
    "Grupo A": [
        {"id": "A1", "fecha": "11/06", "L": "🇲🇽 México", "V": "🇿🇦 Sudáfrica"},
        {"id": "A2", "fecha": "11/06", "L": "🇰🇷 Corea Sur", "V": "🇨🇿 Rep. Checa"}
    ],
    "Grupo B": [
        {"id": "B1", "fecha": "12/06", "L": "🇨🇦 Canadá", "V": "🇧🇦 Bosnia"},
        {"id": "B2", "fecha": "13/06", "L": "🇶🇦 Catar", "V": "🇨🇭 Suiza"}
    ],
    "Grupo J (Argentina)": [
        {"id": "J1", "fecha": "16/06", "L": "🇦🇷 Argentina", "V": "🇩🇿 Argelia"},
        {"id": "J2", "fecha": "17/06", "L": "🇦🇹 Austria", "V": "🇯🇴 Jordania"}
    ]
    # Se pueden agregar todos los grupos siguiendo este formato
}

# --- INTERFAZ ---
# Logo (podés cambiar esta URL por la del logo de Dunlop)
st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/Dunlop_Logo.svg", width=200)
st.title("🏆 PRODE MUNDIAL 2026")
st.write("Cargá tus pronósticos por grupo. ¡No olvides darle al botón de guardar al final!")

nombre = st.text_input("👤 TU NOMBRE Y APELLIDO:", placeholder="Ej: Alberto Laller")

if nombre:
    # Creamos pestañas para los grupos
    tab1, tab2, tab3 = st.tabs(["Grupo A", "Grupo B", "Grupo J (Arg)"])
    
    with st.form("form_prode"):
        todos_los_resultados = []

        with tab1:
            for m in fixture_datos["Grupo A"]:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])
                with col1: st.write(f"**{m['L']}**")
                with col2: res_l = st.number_input("Goles", min_value=0, step=1, key=f"l_{m['id']}", label_visibility="collapsed")
                with col3: st.write("vs")
                with col4: res_v = st.number_input("Goles", min_value=0, step=1, key=f"v_{m['id']}", label_visibility="collapsed")
                with col5: st.write(f"**{m['V']}**")
                todos_los_resultados.append([nombre, f"{m['L']} vs {m['V']}", res_l, res_v])

        with tab2:
            for m in fixture_datos["Grupo B"]:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])
                with col1: st.write(f"**{m['L']}**")
                with col2: res_l = st.number_input("Goles", min_value=0, step=1, key=f"l_{m['id']}", label_visibility="collapsed")
                with col3: st.write("vs")
                with col4: res_v = st.number_input("Goles", min_value=0, step=1, key=f"v_{m['id']}", label_visibility="collapsed")
                with col5: st.write(f"**{m['V']}**")
                todos_los_resultados.append([nombre, f"{m['L']} vs {m['V']}", res_l, res_v])

        with tab3:
            for m in fixture_datos["Grupo J (Arg)"]:
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
            # Agregamos la fecha a cada fila
            filas_a_guardar = [fila + [ahora] for fila in todos_los_resultados]
            try:
                ws_pronosticos.append_rows(filas_a_guardar)
                st.success(f"¡Excelente {nombre}! Se guardaron todos tus resultados en el sistema.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
else:
    st.warning("👈 Por favor, ingresá tu nombre arriba para habilitar la carga de partidos.")

st.sidebar.image("https://www.dunlop.com/wp-content/themes/dunlop/img/dunlop-logo.png", width=150)
st.sidebar.write("---")
st.sidebar.info("Este es el Prode Oficial Dunlop 2026. Los datos se guardan directamente en el servidor central.")
