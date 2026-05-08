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

# --- DATOS COMPLETOS (72 PARTIDOS) ---
fixture_datos = {
    "Grupo A": [{"id":"A1","L":"🇲🇽 México","V":"🇿🇦 Sudáfrica"},{"id":"A2","L":"🇰🇷 Corea Sur","V":"🇨🇿 Rep. Checa"},{"id":"A3","L":"🇲🇽 México","V":"🇰🇷 Corea Sur"},{"id":"A4","L":"🇨🇿 Rep. Checa","V":"🇿🇦 Sudáfrica"},{"id":"A5","L":"🇿🇦 Sudáfrica","V":"🇰🇷 Corea Sur"},{"id":"A6","L":"🇨🇿 Rep. Checa","V":"🇲🇽 México"}],
    "Grupo B": [{"id":"B1","L":"🇨🇦 Canadá","V":"🇧🇦 Bosnia"},{"id":"B2","L":"🇶🇦 Catar","V":"🇨🇭 Suiza"},{"id":"B3","L":"🇨🇦 Canadá","V":"🇶🇦 Catar"},{"id":"B4","L":"🇨🇭 Suiza","V":"🇧🇦 Bosnia"},{"id":"B5","L":"🇧🇦 Bosnia","V":"🇶🇦 Catar"},{"id":"B6","L":"🇨🇭 Suiza","V":"🇨🇦 Canadá"}],
    "Grupo C": [{"id":"C1","L":"🇧🇷 Brasil","V":"🇲🇦 Marruecos"},{"id":"C2","L":"🇭🇹 Haití","V":"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia"},{"id":"C3","L":"🇧🇷 Brasil","V":"🇭🇹 Haití"},{"id":"C4","L":"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia","V":"🇲🇦 Marruecos"},{"id":"C5","L":"🇲🇦 Marruecos","V":"🇭🇹 Haití"},{"id":"C6","L":"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia","V":"🇧🇷 Brasil"}],
    "Grupo D": [{"id":"D1","L":"🇺🇸 EE. UU.","V":"🇵🇾 Paraguay"},{"id":"D2","L":"🇦🇺 Australia","V":"🇹🇷 Turquía"},{"id":"D3","L":"🇺🇸 EE. UU.","V":"🇦🇺 Australia"},{"id":"D4","L":"🇹🇷 Turquía","V":"🇵🇾 Paraguay"},{"id":"D5","L":"🇵🇾 Paraguay","V":"🇦🇺 Australia"},{"id":"D6","L":"🇹🇷 Turquía","V":"🇺🇸 EE. UU."}],
    "Grupo E": [{"id":"E1","L":"🇩🇪 Alemania","V":"🇨🇼 Curazao"},{"id":"E2","L":"🇨🇮 C. Marfil","V":"🇪🇨 Ecuador"},{"id":"E3","L":"🇩🇪 Alemania","V":"🇨🇮 C. Marfil"},{"id":"E4","L":"🇪🇨 Ecuador","V":"🇨🇼 Curazao"},{"id":"E5","L":"🇨🇼 Curazao","V":"🇨🇮 C. Marfil"},{"id":"E6","L":"🇪🇨 Ecuador","V":"🇩🇪 Alemania"}],
    "Grupo F": [{"id":"F1","L":"🇳🇱 P. Bajos","V":"🇯🇵 Japón"},{"id":"F2","L":"🇸🇪 Suecia","V":"🇹🇳 Túnez"},{"id":"F3","L":"🇳🇱 P. Bajos","V":"🇸🇪 Suecia"},{"id":"F4","L":"🇹🇳 Túnez","V":"🇯🇵 Japón"},{"id":"F5","L":"🇯🇵 Japón","V":"🇸🇪 Suecia"},{"id":"F6","L":"🇹🇳 Túnez","V":"🇳🇱 P. Bajos"}],
    "Grupo G": [{"id":"G1","L":"🇧🇪 Bélgica","V":"🇪🇬 Egipto"},{"id":"G2","L":"🇮🇷 Irán","V":"🇳🇿 N. Zelanda"},{"id":"G3","L":"🇧🇪 Bélgica","V":"🇮🇷 Irán"},{"id":"G4","L":"🇳🇿 N. Zelanda","V":"🇪🇬 Egipto"},{"id":"G5","L":"🇪🇬 Egipto","V":"🇮🇷 Irán"},{"id":"G6","L":"🇳🇿 N. Zelanda","V":"🇧🇪 Bélgica"}],
    "Grupo H": [{"id":"H1","L":"🇪🇸 España","V":"🇨🇻 Cabo Verde"},{"id":"H2","L":"🇺🇾 Uruguay","V":"🇸🇦 A. Saudí"},{"id":"H3","L":"🇪🇸 España","V":"🇺🇾 Uruguay"},{"id":"H4","L":"🇸🇦 A. Saudí","V":"🇨🇻 Cabo Verde"},{"id":"H5","L":"🇨🇻 Cabo Verde","V":"🇺🇾 Uruguay"},{"id":"H6","L":"🇸🇦 A. Saudí","V":"🇪🇸 España"}],
    "Grupo I": [{"id":"I1","L":"🇫🇷 Francia","V":"🇸🇳 Senegal"},{"id":"I2","L":"🇮🇶 Irak","V":"🇳🇴 Noruega"},{"id":"I3","L":"🇫🇷 Francia","V":"🇮🇶 Irak"},{"id":"I4","L":"🇳🇴 Noruega","V":"🇸🇳 Senegal"},{"id":"I5","L":"🇸🇳 Senegal","V":"🇮🇶 Irak"},{"id":"I6","L":"🇳🇴 Noruega","V":"🇫🇷 Francia"}],
    "Grupo J": [{"id":"J1","L":"🇦🇷 Argentina","V":"🇩🇿 Argelia"},{"id":"J2","L":"🇦🇹 Austria","V":"🇯🇴 Jordania"},{"id":"J3","L":"🇦🇷 Argentina","V":"🇦🇹 Austria"},{"id":"J4","L":"🇯🇴 Jordania","V":"🇩🇿 Argelia"},{"id":"J5","L":"🇩🇿 Argelia","V":"🇦🇹 Austria"},{"id":"J6","L":"🇯🇴 Jordania","V":"🇦🇷 Argentina"}],
    "Grupo K": [{"id":"K1","L":"🇵🇹 Portugal","V":"🇨🇩 RD Congo"},{"id":"K2","L":"🇺🇿 Uzbekistán","V":"🇨🇴 Colombia"},{"id":"K3","L":"🇵🇹 Portugal","V":"🇺🇿 Uzbekistán"},{"id":"K4","L":"🇨🇴 Colombia","V":"🇨🇩 RD Congo"},{"id":"K5","L":"🇨🇩 RD Congo","V":"🇺🇿 Uzbekistán"},{"id":"K6","L":"🇨🇴 Colombia","V":"🇵🇹 Portugal"}],
    "Grupo L": [{"id":"L1","L":"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra","V":"🇭🇷 Croacia"},{"id":"L2","L":"🇬🇭 Ghana","V":"🇵🇦 Panamá"},{"id":"L3","L":"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra","V":"🇬🇭 Ghana"},{"id":"L4","L":"🇵🇦 Panamá","V":"🇭🇷 Croacia"},{"id":"L5","L":"🇭🇷 Croacia","V":"🇬🇭 Ghana"},{"id":"L6","L":"🇵🇦 Panamá","V":"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra"}]
}

equipos_podio = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "Países Bajos", "Bélgica", "Italia", "EE. UU.", "Canadá", "Marruecos", "Senegal", "Japón", "Ecuador", "Colombia", "Paraguay", "Croacia", "Suiza", "Corea del Sur", "Argelia"])

# --- ESTADO DE SESIÓN ---
if 'enviado' not in st.session_state:
    st.session_state.enviado = False

def reiniciar():
    st.session_state.enviado = False
    st.rerun()

# --- INTERFAZ ---
st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/Dunlop_Logo.svg", width=150)
st.title("🏆 PRODE DUNLOP 2026")

if st.session_state.enviado:
    st.success("✅ ¡Pronóstico guardado exitosamente!")
    if st.button("🔄 Cargar otro / Cerrar Sesión"):
        reiniciar()
    st.stop()

nombre = st.text_input("👤 TU NOMBRE COMPLETO:").strip().upper()

if nombre:
    tabs_main = st.tabs(["⚽ Grupos", "🏅 Podio Final", "💎 Bonus"])
    
    with st.form("prode_final_secure"):
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
            st.subheader("Seleccioná tu Podio")
            p1 = st.selectbox("🥇 1° CAMPEÓN", equipos_podio, index=0)
            p2 = st.selectbox("🥈 2° SUBCAMPEÓN", equipos_podio, index=1)
            p3 = st.selectbox("🥉 3° PUESTO", equipos_podio, index=2)
            p4 = st.selectbox("🏅 4° CUARTO", equipos_podio, index=3)

        with tabs_main[2]:
            st.subheader("Bonus Especiales")
            b1 = st.text_input("¿Último gol de Argentina en grupos?")
            b2 = st.text_input("¿Primer gol ganador Grupo J en Octavos?")

        st.divider()
        if st.form_submit_button("💾 GUARDAR PRONÓSTICO COMPLETO"):
            # --- VALIDACIÓN DE DUPLICADOS ---
            # Leemos la columna A del excel
            lista_nombres = ws_pronosticos.col_values(1)
            if nombre in lista_nombres:
                st.error(f"❌ ¡Error! El nombre '{nombre}' ya registró su Prode. No se permiten duplicados.")
            else:
                ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                datos_enviar.extend([
                    [nombre, "PODIO: 1° CAMPEÓN", p1, ""],
                    [nombre, "PODIO: 2° SUBCAMPEÓN", p2, ""],
                    [nombre, "PODIO: 3° TERCERO", p3, ""],
                    [nombre, "PODIO: 4° CUARTO", p4, ""],
                    [nombre, "BONUS: Último gol Arg", b1, ""],
                    [nombre, "BONUS: Primer gol Octavos", b2, ""]
                ])
                filas_finales = [f + [ahora] for f in datos_enviar]
                ws_pronosticos.append_rows(filas_finales)
                st.session_state.enviado = True
                st.rerun()
else:
    st.info("Escribí tu nombre para habilitar el fixture.")
