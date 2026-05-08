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
        width: 100%;
        height: 3.5em;
        font-size: 18px;
    }
    h1 { color: #1a1a1a; font-family: 'Arial Black'; text-align: center; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] {
        background-color: #e0e0e0;
        border-radius: 5px;
        padding: 8px 15px;
    }
    .stTabs [aria-selected="true"] { background-color: #FFD200; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_hoja():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info_claves = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info_claves, scopes=scope)
    client = gspread.authorize(creds)
    return client.open("Prode_Mundial_2026").worksheet("pronosticos")

ws_pronosticos = conectar_hoja()

# --- DATOS DEL FIXTURE COMPLETO ---
fixture_datos = {
    "Grupo A": [{"id": "A1", "L": "🇲🇽 México", "V": "🇿🇦 Sudáfrica"}, {"id": "A2", "L": "🇰🇷 Corea Sur", "V": "🇨🇿 Rep. Checa"}],
    "Grupo B": [{"id": "B1", "L": "🇨🇦 Canadá", "V": "🇧🇦 Bosnia"}, {"id": "B2", "L": "🇶🇦 Catar", "V": "🇨🇭 Suiza"}],
    "Grupo C": [{"id": "C1", "L": "🇧🇷 Brasil", "V": "🇲🇦 Marruecos"}, {"id": "C2", "L": "🇭🇹 Haití", "V": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia"}],
    "Grupo D": [{"id": "D1", "L": "🇺🇸 EE. UU.", "V": "🇵🇾 Paraguay"}, {"id": "D2", "L": "🇦🇺 Australia", "V": "🇹🇷 Turquía"}],
    "Grupo E": [{"id": "E1", "L": "🇩🇪 Alemania", "V": "🇨🇼 Curazao"}, {"id": "E2", "L": "🇨🇮 C. Marfil", "V": "🇪🇨 Ecuador"}],
    "Grupo F": [{"id": "F1", "L": "🇳🇱 P. Bajos", "V": "🇯🇵 Japón"}, {"id": "F2", "L": "🇸🇪 Suecia", "V": "🇹🇳 Túnez"}],
    "Grupo G": [{"id": "G1", "L": "🇧🇪 Bélgica", "V": "🇪🇬 Egipto"}, {"id": "G2", "L": "🇮🇷 Irán", "V": "🇳🇿 N. Zelanda"}],
    "Grupo H": [{"id": "H1", "L": "🇪🇸 España", "V": "🇨🇻 Cabo Verde"}, {"id": "H2", "L": "🇺🇾 Uruguay", "V": "🇸🇦 A. Saudí"}],
    "Grupo I": [{"id": "I1", "L": "🇫🇷 Francia", "V": "🇸🇳 Senegal"}, {"id": "I2", "L": "🇮🇶 Irak", "V": "🇳🇴 Noruega"}],
    "Grupo J": [{"id": "J1", "L": "🇦🇷 Argentina", "V": "🇩🇿 Argelia"}, {"id": "J2", "L": "🇦🇹 Austria", "V": "🇯🇴 Jordania"}],
    "Grupo K": [{"id": "K1", "L": "🇵🇹 Portugal", "V": "🇨🇩 RD Congo"}, {"id": "K2", "L": "🇺🇿 Uzbekistán", "V": "🇨🇴 Colombia"}],
    "Grupo L": [{"id": "L1", "L": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra", "V": "🇭🇷 Croacia"}, {"id": "L2", "L": "🇬🇭 Ghana", "V": "🇵🇦 Panamá"}]
}

# --- INTERFAZ ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/Dunlop_Logo.svg", width=120)
with col_title:
    st.title("PRODE OFICIAL DUNLOP 2026")

nombre = st.text_input("👤 TU NOMBRE Y APELLIDO:", placeholder="Ej: Juan Perez")

if nombre:
    st.markdown(f"### Hola **{nombre}**! Completá tus resultados por grupo:")
    
    tab_list = st.tabs(list(fixture_datos.keys()))
    
    with st.form("form_completo"):
        resultados_totales = []
        
        for i, (grupo, partidos) in enumerate(fixture_datos.items()):
            with tab_list[i]:
                st.subheader(f"Partidos del {grupo}")
                for m in partidos:
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])
                    with col1: st.write(f"**{m['L']}**")
                    with col2: r_l = st.number_input("G", min_value=0, max_value=15, step=1, key=f"l_{m['id']}", label_visibility="collapsed")
                    with col3: st.write("vs")
                    with col4: r_v = st.number_input("G", min_value=0, max_value=15, step=1, key=f"v_{m['id']}", label_visibility="collapsed")
                    with col5: st.write(f"**{m['V']}**")
                    resultados_totales.append([nombre, f"{m['L']} vs {m['V']}", r_l, r_v])

        st.divider()
        enviar = st.form_submit_button("💾 GUARDAR TODOS LOS GRUPOS")

        if enviar:
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
            filas_finales = [f + [ahora] for f in resultados_totales]
            try:
                ws_pronosticos.append_rows(filas_finales)
                st.success(f"¡Brillante {nombre}! Se guardaron {len(filas_finales)} partidos.")
                st.balloons()
            except:
                st.error("Error al guardar. Verificá tu conexión.")
else:
    st.warning("👈 Por favor, escribí tu nombre arriba para empezar.")
