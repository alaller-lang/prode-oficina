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
        border-radius: 12px; font-weight: bold; width: 100%; height: 4em;
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

# --- EQUIPOS Y FIXTURE ---
equipos = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "Países Bajos", "Bélgica", "Italia", "EE. UU.", "Canadá", "Marruecos", "Senegal", "Japón", "Ecuador", "Colombia", "Chile", "Paraguay", "Suiza", "Croacia", "Nigeria"]) # Agregá más si querés

fixture_grupos = {
    "Grupo A": [{"id": "A1", "L": "🇲🇽 México", "V": "🇿🇦 Sudáfrica"}, {"id": "A2", "L": "🇰🇷 Corea Sur", "V": "🇨🇿 Rep. Checa"}],
    "Grupo J": [{"id": "J1", "L": "🇦🇷 Argentina", "V": "🇩🇿 Argelia"}, {"id": "J2", "L": "🇦🇹 Austria", "V": "🇯🇴 Jordania"}],
    # Podés completar el resto aquí...
}

# --- INTERFAZ ---
st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/Dunlop_Logo.svg", width=150)
st.title("🏆 PRODE DUNLOP 2026")
st.info("Puntos: Exacto (3), Ganador (1). Podio: 1° (10), 2° (7), 3° (5), 4° (3). Acierto semi sin orden (1).")

nombre = st.text_input("👤 TU NOMBRE COMPLETO:")

if nombre:
    tabs = st.tabs(["⚽ Fase de Grupos", "🏅 El Podio Final", "💎 Premios Bonus"])
    
    with st.form("prode_final"):
        final_data = []
        
        with tabs[0]:
            for grupo, partidos in fixture_grupos.items():
                st.subheader(grupo)
                for m in partidos:
                    c1, c2, c3, c4, c5 = st.columns([3, 1, 0.5, 1, 3])
                    with c1: st.write(f"**{m['L']}**")
                    with c2: gl = st.number_input("G", 0, 15, key=f"l_{m['id']}", label_visibility="collapsed")
                    with c3: st.write("v")
                    with c4: gv = st.number_input("G", 0, 15, key=f"v_{m['id']}", label_visibility="collapsed")
                    with c5: st.write(f"**{m['V']}**")
                    final_data.append([nombre, f"Partido: {m['L']} vs {m['V']}", gl, gv])

        with tabs[1]:
            st.subheader("Tu Pronóstico del Podio")
            st.write("Elegí el orden exacto para sumar hasta 10 puntos por acierto.")
            p1 = st.selectbox("🥇 CAMPEÓN (10 pts)", equipos, index=0)
            p2 = st.selectbox("🥈 SUBCAMPEÓN (7 pts)", equipos, index=1)
            p3 = st.selectbox("🥉 TERCER PUESTO (5 pts)", equipos, index=2)
            p4 = st.selectbox("🏅 CUARTO PUESTO (3 pts)", equipos, index=3)

        with tabs[2]:
            st.subheader("Retos Especiales (Premios aparte)")
            b1 = st.text_input("¿Quién hace el ÚLTIMO gol de ARG en grupos?")
            b2 = st.text_input("¿Quién hace el PRIMER gol del ganador del Grupo J en Octavos?")

        st.divider()
        if st.form_submit_button("💾 ENVIAR PRONÓSTICO COMPLETO"):
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
            # Agregar Semis y Bonus
            final_data.append([nombre, "POSICIÓN: 1° CAMPEÓN", p1, ""])
            final_data.append([nombre, "POSICIÓN: 2° SUBCAMPEÓN", p2, ""])
            final_data.append([nombre, "POSICIÓN: 3° TERCERO", p3, ""])
            final_data.append([nombre, "POSICIÓN: 4° CUARTO", p4, ""])
            final_data.append([nombre, "BONUS: Último gol Arg", b1, ""])
            final_data.append([nombre, "BONUS: Primer gol Octavos", b2, ""])
            
            ws_pronosticos.append_rows([f + [ahora] for f in final_data])
            st.success("¡Datos guardados! Buena suerte para el Mundial.")
            st.balloons()
