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
def conectar_hojas():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    info_claves = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info_claves, scopes=scope)
    client = gspread.authorize(creds)
    ss = client.open("Prode_Mundial_2026")
    return ss.worksheet("pronosticos"), ss.worksheet("resultados_reales")

ws_pronos, ws_reales = conectar_hojas()

# --- DATOS FIXTURE ---
fixture_datos = {
    "Grupo A": [{"id":"A1","L":"🇲🇽 México","V":"🇿🇦 Sudáfrica"},{"id":"A2","L":"🇰🇷 Corea Sur","V":"🇨🇿 Rep. Checa"},{"id":"A3","L":"🇲🇽 México","V":"🇰🇷 Corea Sur"},{"id":"A4","L":"🇨🇿 Rep. Checa","V":"🇿🇦 Sudáfrica"},{"id":"A5","L":"🇿🇦 Sudáfrica","V":"🇰🇷 Corea Sur"},{"id":"A6","L":"🇨🇿 Rep. Checa","V":"🇲🇽 México"}],
    "Grupo B": [{"id":"B1","L":"🇨🇦 Canadá","V":"🇧🇦 Bosnia"},{"id":"B2","L":"🇶🇦 Catar","V":"🇨🇭 Suiza"},{"id":"B3","L":"🇨🇦 Canadá","V":"🇶🇦 Catar"},{"id":"B4","L":"🇨🇭 Suiza","V":"🇧🇦 Bosnia"},{"id":"B5","L":"🇧🇦 Bosnia","V":"🇶🇦 Catar"},{"id":"B6","L":"🇨🇭 Suiza","V":"🇨🇦 Canadá"}],
    "Grupo C": [{"id":"C1","L":"🇧🇷 Brasil","V":"🇲🇦 Marruecos"},{"id":"C2","L":"🇭🇹 Haití","V":"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia"},{"id":"C3","L":"🇧🇷 Brasil","V":"🇭🇹 Haití"},{"id":"C4","L":"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia","V":"🇲🇦 Marruecos"},{"id":"C5","L":"🇲🇦 Marruecos","V":"🇭🇹 Haití"},{"id":"C6","L":"🏴󠁧󠁢󠁳󠁣󠁴󠁿 Escocia","V":"🇧🇷 Brasil"}],
    "Grupo D": [{"id":"D1","L":"🇺🇸 EE. UU.","V":"🇵🇾 Paraguay"},{"id":"D2","L":"🇦🇺 Australia","V":"🇹🇷 Turquía"},{"id":"D3","L":"🇺🇸 EE. UU.","V":"🇦🇺 Australia"},{"id":"D4","L":"🇹🇷 Turquía","V":"🇵🇾 Paraguay"},{"id":"D5","L":"🇵🇾 Paraguay","V":"🇦🇺 Australia"},{"id":"D6","L":"🇹🇷 Turquía","V":"🇺🇸 EE. UU."}],
    "Grupo E": [{"id":"E1","L":"🇩🇪 Alemania","V":"🇨🇼 Curazao"},{"id":"E2","L":"🇨🇮 C. Marfil","V":"🇪🇨 Ecuador"},{"id":"E3","L":"🇩🇪 Alemania","V":"🇨🇮 C. Marfil"},{"id":"E4","L":"🇪🇨 Ecuador","V":"🇨🇼 Curazao"},{"id":"E5","L":"🇨🇼 Curazao","V":"🇨🇮 C. Marfil"},{"id":"E6","L":"🇪🇨 Ecuador","V":"🇩🇪 Alemania"}],
    "Grupo f": [{"id":"F1","L":"🇳🇱 P. Bajos","V":"🇯🇵 Japón"},{"id":"F2","L":"🇸🇪 Suecia","V":"🇹🇳 Túnez"},{"id":"F3","L":"🇳🇱 P. Bajos","V":"🇸🇪 Suecia"},{"id":"F4","L":"🇹🇳 Túnez","V":"🇯🇵 Japón"},{"id":"F5","L":"🇯🇵 Japón","V":"🇸🇪 Suecia"},{"id":"F6","L":"🇹🇳 Túnez","V":"🇳🇱 P. Bajos"}],
    "Grupo G": [{"id":"G1","L":"🇧🇪 Bélgica","V":"🇪🇬 Egipto"},{"id":"G2","L":"🇮🇷 Irán","V":"🇳🇿 N. Zelanda"},{"id":"G3","L":"🇧🇪 Bélgica","V":"🇮🇷 Irán"},{"id":"G4","L":"🇳🇿 N. Zelanda","V":"🇪🇬 Egipto"},{"id":"G5","L":"🇪🇬 Egipto","V":"🇮🇷 Irán"},{"id":"G6","L":"🇳🇿 N. Zelanda","V":"🇧🇪 Bélgica"}],
    "Grupo H": [{"id":"H1","L":"🇪🇸 España","V":"🇨🇻 Cabo Verde"},{"id":"H2","L":"🇺🇾 Uruguay","V":"🇸🇦 A. Saudí"},{"id":"H3","L":"🇪🇸 España","V":"🇺🇾 Uruguay"},{"id":"H4","L":"🇸🇦 A. Saudí","V":"🇨🇻 Cabo Verde"},{"id":"H5","L":"🇨🇻 Cabo Verde","V":"🇺🇾 Uruguay"},{"id":"H6","L":"🇸🇦 A. Saudí","V":"🇪🇸 España"}],
    "Grupo I": [{"id":"I1","L":"🇫🇷 Francia","V":"🇸🇳 Senegal"},{"id":"I2","L":"🇮🇶 Irak","V":"🇳🇴 Noruega"},{"id":"I3","L":"🇫🇷 Francia","V":"🇮🇶 Irak"},{"id":"I4","L":"🇳🇴 Noruega","V":"🇸🇳 Senegal"},{"id":"I5","L":"🇸🇳 Senegal","V":"🇮🇶 Irak"},{"id":"I6","L":"🇳🇴 Noruega","V":"🇫🇷 Francia"}],
    "Grupo J": [{"id":"J1","L":"🇦🇷 Argentina","V":"🇩🇿 Argelia"},{"id":"J2","L":"🇦🇹 Austria","V":"🇯🇴 Jordania"},{"id":"J3","L":"🇦🇷 Argentina","V":"🇦🇹 Austria"},{"id":"J4","L":"🇯🇴 Jordania","V":"🇩🇿 Argelia"},{"id":"J5","L":"🇩🇿 Argelia","V":"🇦🇹 Austria"},{"id":"J6","L":"🇯🇴 Jordania","V":"🇦🇷 Argentina"}],
    "Grupo K": [{"id":"K1","L":"🇵🇹 Portugal","V":"🇨🇩 RD Congo"},{"id":"K2","L":"🇺🇿 Uzbekistán","V":"🇨🇴 Colombia"},{"id":"K3","L":"🇵🇹 Portugal","V":"🇺🇿 Uzbekistán"},{"id":"K4","L":"🇨🇴 Colombia","V":"🇨🇩 RD Congo"},{"id":"K5","L":"🇨🇩 RD Congo","V":"🇺🇿 Uzbekistán"},{"id":"K6","L":"🇨🇴 Colombia","V":"🇵🇹 Portugal"}],
    "Grupo L": [{"id":"L1","L":"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra","V":"🇭🇷 Croacia"},{"id":"L2","L":"🇬🇭 Ghana","V":"🇵🇦 Panamá"},{"id":"L3","L":"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra","V":"🇬🇭 Ghana"},{"id":"L4","L":"🇵🇦 Panamá","V":"🇭🇷 Croacia"},{"id":"L5","L":"🇭🇷 Croacia","V":"🇬🇭 Ghana"},{"id":"L6","L":"🇵🇦 Panamá","V":"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra"}]
}
equipos_podio = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "Países Bajos", "Bélgica", "Italia", "EE. UU.", "Canadá", "Marruecos", "Senegal", "Japón", "Ecuador", "Colombia", "Paraguay", "Croacia", "Suiza", "Corea del Sur", "Argelia"])

# --- LÓGICA DE RANKING MEJORADA ---
def obtener_ranking():
    try:
        # Traemos todas las filas, sin depender de los nombres de los encabezados
        data_p = ws_pronos.get_all_values()
        data_r = ws_reales.get_all_values()
        
        if len(data_p) < 2 or len(data_r) < 2: return None
        
        # Convertimos a DataFrame usando la primera fila como nombres
        df_p = pd.DataFrame(data_p[1:], columns=data_p[0])
        df_r = pd.DataFrame(data_r[1:], columns=data_r[0])
        
        # Limpieza de nombres de columnas (quitar espacios locos)
        df_p.columns = df_p.columns.str.strip()
        df_r.columns = df_r.columns.str.strip()

        # Filtrar solo partidos
        df_p = df_p[df_p['Partido'].str.contains("vs", na=False)].copy()
        
        # Asegurar que los goles sean números
        df_p['Goles Local'] = pd.to_numeric(df_p['Goles Local'], errors='coerce').fillna(0)
        df_p['Goles Visitante'] = pd.to_numeric(df_p['Goles Visitante'], errors='coerce').fillna(0)
        df_r['Goles Local'] = pd.to_numeric(df_r['Goles Local'], errors='coerce').fillna(0)
        df_r['Goles Visitante'] = pd.to_numeric(df_r['Goles Visitante'], errors='coerce').fillna(0)

        df_m = df_p.merge(df_r, on="Partido", suffixes=('_u', '_r'))
        
        def calcular(row):
            if row['Goles Local_u'] == row['Goles Local_r'] and row['Goles Visitante_u'] == row['Goles Visitante_r']:
                return 3
            res_u = (row['Goles Local_u'] > row['Goles Visitante_u']) - (row['Goles Local_u'] < row['Goles Visitante_u'])
            res_r = (row['Goles Local_r'] > row['Goles Visitante_r']) - (row['Goles Local_r'] < row['Goles Visitante_r'])
            return 1 if res_u == res_r else 0

        df_m['Pts'] = df_m.apply(calcular, axis=1)
        res = df_m.groupby('Nombre')['Pts'].sum().reset_index().sort_values('Pts', ascending=False)
        return res
    except Exception as e:
        return f"Error en datos: {e}"

# --- MENU ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/3/3d/Dunlop_Logo.svg", width=120)
    opcion = st.radio("MENÚ", ["📝 Cargar mi Prode", "📊 Ranking en Vivo", "⚙️ Admin"])

if opcion == "📝 Cargar mi Prode":
    if 'enviado' not in st.session_state: st.session_state.enviado = False
    if st.session_state.enviado:
        st.success("✅ Guardado.")
        if st.button("Cargar otro"): 
            st.session_state.enviado = False
            st.rerun()
        st.stop()
    
    nombre = st.text_input("👤 TU NOMBRE COMPLETO:").strip().upper()
    if nombre:
        tabs = st.tabs(["⚽ Grupos", "🏅 Podio", "💎 Bonus"])
        with st.form("f_prode"):
            datos = []
            with tabs[0]:
                sub = st.tabs(list(fixture_datos.keys()))
                for i, (g, p_list) in enumerate(fixture_datos.items()):
                    with sub[i]:
                        for m in p_list:
                            c1, c2, c3, c4, c5 = st.columns([3, 1, 0.5, 1, 3])
                            with c1: st.write(f"**{m['L']}**")
                            with c2: gl = st.number_input("G", 0, 15, key=f"l_{m['id']}", label_visibility="collapsed")
                            with c3: st.write("v")
                            with c4: gv = st.number_input("G", 0, 15, key=f"v_{m['id']}", label_visibility="collapsed")
                            with c5: st.write(f"**{m['V']}**")
                            datos.append([nombre, f"{m['L']} vs {m['V']}", gl, gv])
            with tabs[1]:
                p1 = st.selectbox("🥇 Campeón", equipos_podio, index=0)
                p2 = st.selectbox("🥈 Subcampeón", equipos_podio, index=1)
                p3 = st.selectbox("🥉 Tercero", equipos_podio, index=2)
                p4 = st.selectbox("🏅 Cuarto", equipos_podio, index=3)
            with tabs[2]:
                b1 = st.text_input("Último gol ARG:")
                b2 = st.text_input("Primer gol Octavos:")

            if st.form_submit_button("💾 GUARDAR"):
                col1 = ws_pronos.col_values(1)
                if nombre in [n.upper() for n in col1]:
                    st.error("Ya participaste.")
                else:
                    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    datos.extend([[nombre,"P1",p1,""],[nombre,"P2",p2,""],[nombre,"P3",p3,""],[nombre,"P4",p4,""],[nombre,"B1",b1,""],[nombre,"B2",b2,""]])
                    ws_pronos.append_rows([f + [ahora] for f in datos])
                    st.session_state.enviado = True
                    st.rerun()

elif opcion == "📊 Ranking en Vivo":
    st.header("🏆 Posiciones")
    res = obtener_ranking()
    if isinstance(res, pd.DataFrame):
        st.dataframe(res, hide_index=True, use_container_width=True)
    elif res is None:
        st.info("Esperando resultados del admin.")
    else:
        st.error(res)

elif opcion == "⚙️ Admin":
    st.header("Admin")
    pw = st.text_input("Clave:", type="password")
    if pw == "DUNLOP2026":
        partidos = []
        for g in fixture_datos.values():
            for p in g: partidos.append(f"{p['L']} vs {p['V']}")
        sel = st.selectbox("Partido:", partidos)
        c1, c2 = st.columns(2)
        rl = c1.number_input("Local", 0, 15)
        rv = c2.number_input("Visitante", 0, 15)
        if st.button("Guardar"):
            ws_reales.append_row([sel, rl, rv])
            st.success("Ok.")
