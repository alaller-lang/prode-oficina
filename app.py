import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN DE PÁGINA ---
# Esto ayuda a que se adapte mejor a cualquier pantalla
st.set_page_config(page_title="DUNLOP PRODE 2026", page_icon="🏆")

# --- ESTILO LIMPIO Y PROFESIONAL ---
st.markdown("""
    <style>
    /* Ocultar elementos innecesarios */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* Botón Principal Dunlop */
    div.stButton > button:first-child {
        background-color: #FFD200 !important;
        color: black !important;
        font-weight: bold !important;
        border: 1px solid black !important;
        height: 3em !important;
        width: 100% !important;
    }
    
    /* Pestañas más legibles */
    .stTabs [data-baseweb="tab"] {
        padding-left: 10px !important;
        padding-right: 10px !important;
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

# --- FIXTURE (Lista Compacta) ---
fixture = {
    "A": ["México vs Sudáfrica","Corea Sur vs Rep. Checa","México vs Corea Sur","Rep. Checa vs Sudáfrica","Sudáfrica vs Corea Sur","Rep. Checa vs México"],
    "B": ["Canadá vs Bosnia","Catar vs Suiza","Canadá vs Catar","Suiza vs Bosnia","Bosnia vs Catar","Suiza vs Canadá"],
    "C": ["Brasil vs Marruecos","Haití vs Escocia","Brasil vs Haití","Escocia vs Marruecos","Marruecos vs Haití","Escocia vs Brasil"],
    "D": ["EE. UU. vs Paraguay","Australia vs Turquía","EE. UU. vs Australia","Turquía vs Paraguay","Paraguay vs Australia","Turquía vs EE. UU."],
    "E": ["Alemania vs Curazao","C. Marfil vs Ecuador","Alemania vs C. Marfil","Ecuador vs Curazao","Curazao vs C. Marfil","Ecuador vs Alemania"],
    "F": ["P. Bajos vs Japón","Suecia vs Túnez","P. Bajos vs Suecia","Túnez vs Japón","Japón vs Suecia","Túnez vs P. Bajos"],
    "G": ["Bélgica vs Egipto","Irán vs N. Zelanda","Bélgica vs Irán","N. Zelanda vs Egipto","Egipto vs Irán","N. Zelanda vs Bélgica"],
    "H": ["España vs Cabo Verde","Uruguay vs A. Saudí","España vs Uruguay","A. Saudí vs Cabo Verde","Cabo Verde vs Uruguay","A. Saudí vs España"],
    "I": ["Francia vs Senegal","Irak vs Noruega","Francia vs Irak","Noruega vs Senegal","Senegal vs Irak","Noruega vs Francia"],
    "J": ["Argentina vs Argelia","Austria vs Jordania","Argentina vs Austria","Jordania vs Argelia","Argelia vs Austria","Jordania vs Argentina"],
    "K": ["Portugal vs RD Congo","Uzbekistán vs Colombia","Portugal vs Uzbekistán","Colombia vs RD Congo","RD Congo vs Uzbekistán","Colombia vs Portugal"],
    "L": ["Inglaterra vs Croacia","Ghana vs Panamá","Inglaterra vs Ghana","Panamá vs Croacia","Croacia vs Ghana","Panamá vs Inglaterra"]
}
equipos = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "P. Bajos", "Bélgica", "Italia", "EE. UU.", "Marruecos", "Colombia", "Ecuador"])

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

# --- MENÚ ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Dunlop_Logo.svg/500px-Dunlop_Logo.svg.png", width=150)
opc = st.sidebar.selectbox("MENÚ", ["📝 Cargar Prode", "📊 Ranking", "🔍 Ver Otros", "⚙️ Admin"])

# --- SECCIONES ---
if opc == "📝 Cargar Prode":
    st.header("🏆 Mi Pronóstico 2026")
    if st.session_state.get('ok'):
        st.success("✅ Guardado correctamente.")
        st.stop()
    
    nom = st.text_input("Tu Nombre Completo:").upper().strip()
    if nom:
        with st.form("f"):
            t_g, t_p, t_b = st.tabs(["⚽ GRUPOS", "🏅 PODIO", "💎 BONUS"])
            res = []
            with t_g:
                st_g = st.tabs(list(fixture.keys()))
                for i, l in enumerate(fixture.keys()):
                    with st_g[i]:
                        for p in fixture[l]:
                            c1, c2, c3 = st.columns([2, 1, 2])
                            eqs = p.split(" vs ")
                            with c1: st.write(f"**{eqs[0]}**")
                            with c2: 
                                sub_c1, sub_c2 = st.columns(2)
                                gl = sub_c1.number_input("L", 0, 15, key=f"l_{p}", label_visibility="collapsed")
                                gv = sub_c2.number_input("V", 0, 15, key=f"v_{p}", label_visibility="collapsed")
                            with c3: st.write(f"**{eqs[1]}**")
                            res.append([nom, p, gl, gv])
            with t_p:
                p1 = st.selectbox("1° - Campeón", equipos, index=0)
                p2 = st.selectbox("2° - Subcampeón", equipos, index=1)
                p3 = st.selectbox("3° - Tercero", equipos, index=2)
                p4 = st.selectbox("4° - Cuarto", equipos, index=3)
            with t_b:
                b1 = st.text_input("Último gol ARG grupos:")
                b2 = st.text_input("Primer gol Ganador J Octavos:")
            
            if st.form_submit_button("GUARDAR PRODE"):
                if nom in [n.upper() for n in ws_p.col_values(1)]: st.error("Ya participaste.")
                else:
                    h = datetime.now().strftime("%d/%m/%Y %H:%M")
                    res.extend([[nom,"P1",p1,""],[nom,"P2",p2,""],[nom,"P3",p3,""],[nom,"P4",p4,""],[nom,"B1",b1,""],[nom,"B2",b2,""]])
                    ws_p.append_rows([f+[h] for f in res])
                    st.session_state.ok = True; st.rerun()

elif opc == "📊 Ranking":
    st.header("📊 Posiciones")
    rk = get_ranking()
    if rk is not None: st.dataframe(rk, use_container_width=True, hide_index=True)
    else: st.info("Sin datos.")

elif opc == "🔍 Ver Otros":
    st.header("🔍 Ver Prode de...")
    p_raw = ws_p.get_all_values()
    if len(p_raw) > 1:
        df_v = pd.DataFrame(p_raw[1:], columns=['Nombre','Partido','GL','GV','F'])
        per = st.selectbox("Compañero:", sorted(df_v['Nombre'].unique()))
        if per:
            st.table(df_v[df_v['Nombre'] == per][['Partido','GL','GV']])
    else: st.info("Vacío.")

elif opc == "⚙️ Admin":
    st.header("⚙️ Admin")
    pw = st.text_input("Clave:", type="password")
    if pw == "DUNLOP2026":
        with st.form("a"):
            allm = [p for s in fixture.values() for p in s]
            ps = st.selectbox("Partido:", sorted(allm))
            c1, c2 = st.columns(2)
            rl, rv = c1.number_input("L",0,15), c2.number_input("V",0,15)
            if st.form_submit_button("GUARDAR"):
                filas = ws_r.get_all_values()
                enc = False
                for i, f in enumerate(filas):
                    if f[0] == ps: ws_r.update(f'A{i+1}:C{i+1}', [[ps, rl, rv]]); enc = True; break
                if not enc: ws_r.append_row([ps, rl, rv])
                st.success("OK")
