import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Prode Dunlop 2026", page_icon="🏆", layout="wide")

# --- ESTILO INSTITUCIONAL ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { 
        background-color: #FFD200 !important; color: black !important; 
        border-radius: 12px; font-weight: bold; width: 100%; height: 4em; font-size: 18px;
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

# --- EQUIPOS PARA EL PODIO ---
equipos_podio = sorted([
    "Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", 
    "Portugal", "Países Bajos", "Bélgica", "Italia", "EE. UU.", "Canadá", "Marruecos", "Senegal", 
    "Japón", "Ecuador", "Colombia", "Paraguay", "Suiza", "Croacia", "Corea del Sur", "Argelia"
])

# --- FIXTURE COMPLETO (72 PARTIDOS) ---
fixture_datos = {
    "Grupo A": [
        {"id": "A1", "L": "🇲🇽 México", "V": "🇿🇦 Sudáfrica"}, {"id": "A2", "L": "🇰🇷 Corea Sur", "V": "🇨🇿 Rep. Checa"},
        {"id": "A3", "L": "🇲🇽 México", "V": "🇰🇷 Corea Sur"}, {"id": "A4", "L": "🇨🇿 Rep. Checa", "V": "🇿🇦 Sudáfrica"},
        {"id": "A5", "L": "🇿🇦 Sudáfrica", "V": "🇰🇷 Corea Sur"}, {"id": "A6", "L": "🇨🇿 Rep. Checa", "V": "🇲🇽 México"}
    ],
    "Grupo B": [
        {"id": "B1", "L": "🇨🇦 Canadá", "V": "🇧🇦 Bosnia"}, {"id": "B2", "L": "🇶🇦 Catar", "V": "🇨🇭 Suiza"},
        {"id": "B3", "L": "🇨🇦 Canadá", "V": "🇶🇦 Catar"}, {"id": "B4", "L": "🇨🇭 Suiza", "V": "🇧🇦 Bosnia"},
        {"id": "B5", "L": "🇧🇦 Bosnia", "V": "🇶🇦 Catar"}, {"id": "B6", "L": "🇨🇭 Suiza", "V": "🇨🇦 Canadá"}
    ],
    "Grupo C": [
        {"id": "C1", "L": "🇧🇷 Brasil", "V": "🇲🇦 Marruecos"}, {"id": "C2", "L": "🇭🇹 Haití", "V": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia"},
        {"id": "C3", "L": "🇧🇷 Brasil", "V": "🇭🇹 Haití"}, {"id": "C4", "L": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "V": "🇲🇦 Marruecos"},
        {"id": "C5", "L": "🇲🇦 Marruecos", "V": "🇭🇹 Haití"}, {"id": "C6", "L": "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia", "V": "🇧🇷 Brasil"}
    ],
    "Grupo D": [
        {"id": "D1", "L": "🇺🇸 EE. UU.", "V": "🇵🇾 Paraguay"}, {"id": "D2", "L": "🇦🇺 Australia", "V": "🇹🇷 Turquía"},
        {"id": "D3", "L": "🇺🇸 EE. UU.", "V": "🇦🇺 Australia"}, {"id": "D4", "L": "🇹🇷 Turquía", "V": "🇵🇾 Paraguay"},
        {"id": "D5", "L": "🇵🇾 Paraguay", "V": "🇦🇺 Australia"}, {"id": "D6", "L": "🇹🇷 Turquía", "V": "🇺🇸 EE. UU."}
    ],
    "Grupo E": [
        {"id": "E1", "L": "🇩🇪 Alemania", "V": "🇨🇼 Curazao"}, {"id": "E2", "L": "🇨🇮 C. Marfil", "V": "🇪🇨 Ecuador"},
        {"id": "E3", "L": "🇩🇪 Alemania", "V": "🇨🇮 C. Marfil"}, {"id": "E4", "L": "🇪🇨 Ecuador", "V": "🇨🇼 Curazao"},
        {"id": "E5", "L": "🇨🇼 Curazao", "V": "🇨🇮 C. Marfil"}, {"id": "E6", "L": "🇪🇨 Ecuador", "V": "🇩🇪 Alemania"}
    ],
    "Grupo F": [
        {"id": "F1", "L": "🇳🇱 P. Bajos", "V": "🇯🇵 Japón"}, {"id": "F2", "L": "🇸🇪 Suecia", "V": "🇹🇳 Túnez"},
        {"id": "F3", "L": "🇳🇱 P. Bajos", "V": "🇸🇪 Suecia"}, {"id": "F4", "L": "🇹🇳 Túnez", "V": "🇯🇵 Japón"},
        {"id": "F5", "L": "🇯🇵 Japón", "V": "🇸🇪 Suecia"}, {"id": "F6", "L": "🇹🇳 Túnez", "V": "🇳🇱 P. Bajos"}
    ],
    "Grupo G": [
        {"id": "G1", "L": "🇧🇪 Bélgica", "V": "🇪🇬 Egipto"}, {"id": "G2", "L": "🇮🇷 Irán", "V": "🇳🇿 N. Zelanda"},
        {"id": "G3", "L": "🇧🇪 Bélgica", "V": "🇮🇷 Irán"}, {"id": "G4", "L": "🇳🇿 N. Zelanda", "V": "🇪🇬 Egipto"},
        {"id": "G5", "L": "🇪🇬 Egipto", "V": "🇮🇷 Irán"}, {"id": "G6", "L": "🇳🇿 N. Zelanda", "V": "🇧🇪 Bélgica"}
    ],
    "Grupo H": [
        {"id": "H1", "L": "🇪🇸 España", "V": "🇨🇻 Cabo Verde"}, {"id": "H2", "L": "🇺🇾 Uruguay", "V": "🇸🇦 A. Saudí"},
        {"id": "H3", "L": "🇪🇸 España", "V": "🇺🇾 Uruguay"}, {"id": "H4", "L": "🇸🇦 A. Saudí", "V": "🇨🇻 Cabo Verde"},
        {"id": "H5", "L": "🇨🇻 Cabo Verde", "V": "🇺🇾 Uruguay"}, {"id": "H6", "L": "🇸🇦 A. Saudí", "V": "🇪🇸 España"}
    ],
    "Grupo I": [
        {"id": "I1", "L": "🇫🇷 Francia", "V": "🇸🇳 Senegal"}, {"id": "I2", "L": "🇮🇶 Irak", "V": "🇳🇴 Noruega"},
        {"id": "I3", "L": "🇫🇷 Francia", "V": "🇮🇶 Irak"}, {"id": "I4", "L": "🇳🇴 Noruega", "V": "🇸🇳 Senegal"},
        {"id": "I5", "L": "🇸🇳 Senegal", "V": "🇮🇶 Irak"}, {"id": "I6",
