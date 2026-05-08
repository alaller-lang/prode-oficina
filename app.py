import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Prode Dunlop 2026", page_icon="🏆", layout="wide")

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { 
        background-color: #FFD200 !important; color: black !important; 
        border-radius: 12px; font-weight: bold; width: 100%; height: 3.5em;
    }
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; background-color: #1a1a1a; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white; }
    .stTabs [aria-selected="true"] { background-color: #FFD200 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
@st.cache_resource
def conectar_hoja():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info_claves = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info_claves, scopes=scope)
    return gspread.authorize(creds).open("Prode_Mundial_2026").worksheet("pronosticos")

ws_pronosticos = conectar_hoja()

# --- DATOS ---
equipos_podio = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "Países Bajos", "Bélgica", "Italia", "EE. UU.", "Canadá", "Marruecos", "Senegal", "Japón", "Ecuador", "Colombia", "Paraguay", "Suiza", "Croacia", "Corea del Sur", "Argelia", "Sudáfrica", "Rep. Checa"])

fixture_datos = {
    "Grupo A": [{"id":"A1","L":"🇲🇽 México","V":"🇿🇦 Sudáfrica"},{"id":"A2","L":"🇰🇷 Corea Sur","V":"🇨🇿 Rep. Checa"},{"id":"A3","L":"🇲🇽 México","V":"🇰🇷 Corea Sur"},{"id":"A4","L":"🇨🇿 Rep. Checa","V":"🇿🇦 Sudáfrica"},{"id":"A5","L":"🇿🇦 Sudáfrica","V":"🇰🇷 Corea Sur"},{"id":"A6","L":"🇨🇿 Rep. Checa","V":"🇲🇽 México"}],
    "Grupo J": [{"id":"J1","L":"🇦🇷 Argentina","V":"🇩🇿 Argelia"},{"id":"J2","L":"🇦🇹 Austria","V":"🇯🇴 Jordania"},{"id":"J3","L":"🇦🇷 Argentina","V":"🇦🇹 Austria"},{"id":"J4","L":"🇯🇴 Jordania","V":"🇩🇿 Argelia"},{"id":"J5","L":"🇩🇿 Argelia","V":"🇦🇹 Austria"},{"id":"J6","L":"🇯🇴 Jordania","V":"🇦🇷 Argentina"}]
    # (Podés reincorporar los otros grupos aquí siguiendo el mismo formato)
}

# --- CONTROL DE ESTADO (SESIÓN) ---
if 'enviado' not in st.session_state:
    st.session_state.enviado = False

def reiniciar_sesion():
    st.session_state.enviado = False
    st.rerun()

# --- INTERFAZ ---
st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/Dunlop_Logo.svg", width=150)
st.title("🏆 PRODE DUNLOP 2026")

# Si ya envió, mostramos mensaje de éxito y opción de salir
if st.session_state.enviado:
    st.success("✅ ¡Tus pronósticos han sido recibidos con éxito!")
    st.balloons()
    st.info("Ya podés cerrar esta pestaña. Si querés cargar los datos de otra persona, hacé clic abajo.")
    if st.button("🔄 Cargar otro usuario / Cerrar"):
        reiniciar_sesion()
    st.stop() # Detiene el resto del código para que no vea el formulario

# --- FORMULARIO DE CARGA ---
nombre = st.text_input("👤 TU NOMBRE COMPLETO:")

if nombre:
    tabs_main = st.tabs(["⚽ Fase de Grupos", "🏅 Podio Final", "💎 Bonus"])
    
    with st.form("prode_bloqueado"):
        datos_enviar = []
        
        with tabs_main[0]:
            sub_tabs = st.tabs(list(fixture_datos.keys()))
            for i, (grupo, partidos) in enumerate(fixture_datos.items()):
                with sub_tabs[i]:
                    for m in partidos:
                        c1, c2, c3, c4, c5 = st.columns([3, 1, 0.5, 1, 3])
                        with c1: st.write(f"**{m['L']}**")
                        with c2: gl = st.number_input("G", 0, 15, key=f"l_{m['id']}", label_visibility="collapsed")
                        with c3: st.write("v")
                        with c4: gv = st.number_input("G", 0, 15, key=f"v_{m['id']}", label_visibility="collapsed")
                        with c5: st.write(f"**{m['V']}**")
                        datos_enviar.append([nombre, f"Partido: {m['L']} vs {m['V']}", gl, gv])

        with tabs_main[1]:
            st.subheader("Podio Final")
            p1 = st.selectbox("🥇 1° CAMPEÓN", equipos_podio, index=0)
            p2 = st.selectbox("🥈 2° SUBCAMPEÓN", equipos_podio, index=1)
            p3 = st.selectbox("🥉 3° TERCERO", equipos_podio, index=2)
            p4 = st.selectbox("🏅 4° CUARTO", equipos_podio, index=3)

        with tabs_main[2]:
            st.subheader("Retos Especiales")
            b1 = st.text_input("Último gol ARG en grupos:")
            b2 = st.text_input("Primer gol Octavos (Ganador J):")

        st.divider()
        if st.form_submit_button("💾 ENVIAR PRONÓSTICO FINAL"):
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Preparar todas las filas
            datos_enviar.extend([
                [nombre, "PODIO: 1° CAMPEÓN", p1, "", ahora],
                [nombre, "PODIO: 2° SUBCAMPEÓN", p2, "", ahora],
                [nombre, "PODIO: 3° TERCERO", p3, "", ahora],
                [nombre, "PODIO: 4° CUARTO", p4, "", ahora],
                [nombre, "BONUS: Último gol Arg", b1, "", ahora],
                [nombre, "BONUS: Primer gol Octavos", b2, "", ahora]
            ])
            # Ajustar filas de partidos
            filas_finales = [f + [ahora] if len(f)==4 else f for f in datos_enviar]
            
            try:
                ws_pronosticos.append_rows(filas_finales)
                st.session_state.enviado = True # ACTIVAMOS EL BLOQUEO
                st.rerun() # RECARGAMOS PARA MOSTRAR EL MENSAJE DE ÉXITO
            except:
                st.error("Hubo un problema. Intentá de nuevo.")
else:
    st.info("Escribí tu nombre para habilitar la carga.")
