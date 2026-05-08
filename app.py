import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="PRODE DUNLOP 2026", page_icon="🏆", layout="wide")

# --- DISEÑO A MEDIDA (CSS) ---
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Fondo de la App */
    .stApp {
        background-color: #ffffff;
    }

    /* Títulos en Negro Dunlop */
    h1, h2, h3 {
        color: #000000 !important;
        font-family: 'Arial Black', gadget, sans-serif;
    }

    /* BOTÓN AMARILLO DUNLOP - GRANDE PARA CELULAR */
    div.stButton > button:first-child {
        background-color: #FFD200 !important;
        color: #000000 !important;
        border: 2px solid #000000;
        border-radius: 15px;
        padding: 20px;
        font-size: 22px !important;
        font-weight: bold;
        width: 100%;
        margin-top: 20px;
        text-transform: uppercase;
    }

    /* Estilo de las pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #000000;
        border-radius: 10px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #ffffff;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFD200 !important;
        color: #000000 !important;
    }

    /* Inputs de goles más grandes */
    input {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
@st.cache_resource
def conectar():
    info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    ss = gspread.authorize(creds).open("Prode_Mundial_2026")
    return ss.worksheet("pronosticos"), ss.worksheet("resultados_reales")

ws_p, ws_r = conectar()

# --- FIXTURE ---
fixture = {
    "A": ["México vs Sudáfrica","Corea Sur vs Rep. Checa","México vs Corea Sur","Rep. Checa vs Sudáfrica","Sudáfrica vs Corea Sur","Rep. Checa vs México"],
    "B": ["Canadá vs Bosnia","Catar vs Suiza","Canadá vs Catar","Suiza vs Bosnia","Bosnia vs Catar","Suiza vs Canadá"],
    "C": ["Brasil vs Marruecos","Haití vs Escocia","Brasil vs Haití","Escocia vs Marruecos","Marruecos vs Haití","Escocia vs Brasil"],
    "D": ["EE. UU. vs Paraguay","Australia vs Turquía","EE. UU. vs Australia","Turquía vs Paraguay","Paraguay vs Australia","Turquía vs EE. UU."],
    "E": ["Alemania vs Curazao","C. Marfil vs Ecuador","Alemania vs C. Marfil","Ecuador vs Curazao","Curazao vs C. Marfil","Ecuador vs Alemania"],
    "F": ["P. Bajos vs Japón","Suecia vs Túnez","P. Bajos vs Suecia","Túnez vs Japón","Japón vs Suecia","Túnez vs P. Bajos"],
    "G": ["Bélgica vs Egipto","Irán vs N. Zelanda","Bélgica vs Irán","Nueva Zelanda vs Egipto","Egipto vs Irán","Nueva Zelanda vs Bélgica"],
    "H": ["España vs Cabo Verde","Uruguay vs A. Saudí","España vs Uruguay","A. Saudí vs Cabo Verde","Cabo Verde vs Uruguay","A. Saudí vs España"],
    "I": ["Francia vs Senegal","Irak vs Noruega","Francia vs Irak","Noruega vs Senegal","Senegal vs Irak","Noruega vs Francia"],
    "J": ["Argentina vs Argelia","Austria vs Jordania","Argentina vs Austria","Jordania vs Argelia","Argelia vs Austria","Jordania vs Argentina"],
    "K": ["Portugal vs RD Congo","Uzbekistán vs Colombia","Portugal vs Uzbekistán","Colombia vs RD Congo","RD Congo vs Uzbekistán","Colombia vs Portugal"],
    "L": ["Inglaterra vs Croacia","Ghana vs Panamá","Inglaterra vs Ghana","Panamá vs Croacia","Croacia vs Ghana","Panamá vs Inglaterra"]
}
equipos = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "P. Bajos", "Bélgica", "Italia", "EE. UU.", "Marruecos", "Colombia", "Ecuador"])

# --- MENU LATERAL CON LOGO ---
with st.sidebar:
    # Logo de Dunlop (URL directa de alta disponibilidad)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Dunlop_Logo.svg/1200px-Dunlop_Logo.svg.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center;'>PRODE 2026</h2>", unsafe_allow_html=True)
    opc = st.radio("IR A:", ["📝 CARGAR MI PRODE", "📊 RANKING", "🔍 VER OTROS", "⚙️ ADMIN"])

# --- LÓGICA RANKING ---
def get_ranking():
    try:
        p_raw, r_raw = ws_p.get_all_values(), ws_r.get_all_values()
        if len(p_raw)<2 or len(r_raw)<2: return None
        dfp = pd.DataFrame(p_raw[1:], columns=['Nombre','Partido','GLu','GVu','Fecha'])
        dfr = pd.DataFrame(r_raw[1:], columns=['Partido','GLr','GVr'])
        dfp = dfp[dfp['Partido'].str.contains("vs", na=False)].copy()
        for c in ['GLu','GVu','GLr','GVr']:
            if c in dfp.columns: dfp[c] = pd.to_numeric(dfp[c], errors='coerce').fillna(0)
            if c in dfr.columns: dfr[c] = pd.to_numeric(dfr[c], errors='coerce').fillna(0)
        dfm = dfp.merge(dfr, on="Partido")
        def pts(x):
            if x['GLu']==x['GLr'] and x['GVu']==x['GVr']: return 3
            su, sr = (x['GLu']>x['GVu'])-(x['GLu']<x['GVu']), (x['GLr']>x['GVr'])-(x['GLr']<x['GVr'])
            return 1 if su==sr else 0
        dfm['Pts'] = dfm.apply(pts, axis=1)
        return dfm.groupby('Nombre')['Pts'].sum().reset_index().sort_values('Pts', ascending=False)
    except: return None

# --- SECCIONES ---
if opc == "📝 CARGAR MI PRODE":
    st.write("### 👤 REGISTRO DE PRONÓSTICO")
    
    if st.session_state.get('bloqueo'):
        st.success("🏆 ¡LISTO! TU PRODE FUE ENVIADO.")
        st.stop()
        
    nom = st.text_input("ESCRIBÍ TU NOMBRE Y APELLIDO:").upper().strip()
    
    if nom:
        with st.form("prode_form"):
            t1, t2, t3 = st.tabs(["⚽ GRUPOS", "🏅 MI PODIO", "💎 BONUS"])
            
            with t1:
                st.info("Completá los goles de cada partido:")
                stbs = st.tabs(list(fixture.keys()))
                res = []
                for i, letra in enumerate(fixture.keys()):
                    with stbs[i]:
                        for p in fixture[letra]:
                            c1, c2, c3, c4, c5 = st.columns([3, 1, 0.5, 1, 3])
                            eqs = p.split(" vs ")
                            with c1: st.write(f"**{eqs[0]}**")
                            with c2: gl = st.number_input("G", 0, 15, key=f"l_{p}", label_visibility="collapsed")
                            with c3: st.write("-")
                            with c4: gv = st.number_input("G", 0, 15, key=f"v_{p}", label_visibility="collapsed")
                            with c5: st.write(f"**{eqs[1]}**")
                            res.append([nom, p, gl, gv])
            
            with t2:
                st.write("### ¿Quiénes llegan a la final?")
                p1 = st.selectbox("🥇 CAMPEÓN", equipos, index=0)
                p2 = st.selectbox("🥈 SUBCAMPEÓN", equipos, index=1)
                p3 = st.selectbox("🥉 3° PUESTO", equipos, index=2)
                p4 = st.selectbox("🏅 4° PUESTO", equipos, index=3)
            
            with t3:
                st.write("### Preguntas Bonus")
                b1 = st.text_input("¿Quién hace el último gol de ARG en grupos?")
                b2 = st.text_input("¿Quién hace el primer gol del ganador J en octavos?")
                
            if st.form_submit_button("💾 ENVIAR MI PRODE"):
                if nom in [n.upper() for n in ws_p.col_values(1)]:
                    st.error("❌ Ya participaste con este nombre.")
                else:
                    h = datetime.now().strftime("%d/%m/%Y %H:%M")
                    res.extend([[nom,"P1",p1,""],[nom,"P2",p2,""],[nom,"P3",p3,""],[nom,"P4",p4,""],[nom,"B1",b1,""],[nom,"B2",b2,""]])
                    ws_p.append_rows([fila+[h] for fila in res])
                    st.session_state.bloqueo = True
                    st.rerun()

elif opc == "📊 RANKING":
    st.write("## 🏆 Posiciones en Vivo")
    rk = get_ranking()
    if rk is not None:
        st.dataframe(rk, use_container_width=True, hide_index=True)
    else:
        st.info("Esperando resultados...")

elif opc == "🔍 VER OTROS":
    st.write("## 🔍 Consultar Prode")
    p_raw = ws_p.get_all_values()
    if len(p_raw) > 1:
        df_ver = pd.DataFrame(p_raw[1:], columns=['Nombre','Partido','G_L','G_V','Fecha'])
        per = st.selectbox("Elegí un compañero:", sorted(df_ver['Nombre'].unique()))
        if per:
            sub = df_ver[df_ver['Nombre'] == per]
            st.table(sub[sub['Partido'].str.contains(" vs ")][['Partido','G_L','G_V']])
            st.table(sub[~sub['Partido'].str.contains(" vs ")][['Partido','G_L']])

elif opc == "⚙️ ADMIN":
    pw = st.text_input("Clave:", type="password")
    if pw == "DUNLOP2026":
        st.write("### Cargar Resultado Real")
        allm = [p for s in fixture.values() for p in s]
        ps = st.selectbox("Partido:", sorted(allm))
        cl, cv = st.columns(2)
        rl, rv = cl.number_input("L",0,15), cv.number_input("V",0,15)
        if st.button("GUARDAR RESULTADO"):
            filas = ws_r.get_all_values()
            enc = False
            for i, fila in enumerate(filas):
                if fila[0] == ps:
                    ws_r.update(f'A{i+1}:C{i+1}', [[ps, rl, rv]])
                    enc = True
                    break
            if not enc: ws_r.append_row([ps, rl, rv])
            st.success("¡Resultado oficial cargado!")
