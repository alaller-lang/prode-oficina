import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Prode Dunlop 2026", page_icon="🏆", layout="wide")

# --- ESTILO ---
st.markdown("""<style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #FFD200 !important; color: black !important; border-radius: 12px; font-weight: bold; width: 100%; height: 3.5em; }
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; background-color: #1a1a1a; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white; }
    .stTabs [aria-selected="true"] { background-color: #FFD200 !important; color: black !important; }
</style>""", unsafe_allow_html=True)

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
    "G": ["Bélgica vs Egipto","Irán vs N. Zelanda","Bélgica vs Irán","N. Zelanda vs Egipto","Egipto vs Irán","N. Zelanda vs Bélgica"],
    "H": ["España vs Cabo Verde","Uruguay vs A. Saudí","España vs Uruguay","A. Saudí vs Cabo Verde","Cabo Verde vs Uruguay","A. Saudí vs España"],
    "I": ["Francia vs Senegal","Irak vs Noruega","Francia vs Irak","Noruega vs Senegal","Senegal vs Irak","Noruega vs Francia"],
    "J": ["Argentina vs Argelia","Austria vs Jordania","Argentina vs Austria","Jordania vs Argelia","Argelia vs Austria","Jordania vs Argentina"],
    "K": ["Portugal vs RD Congo","Uzbekistán vs Colombia","Portugal vs Uzbekistán","Colombia vs RD Congo","RD Congo vs Uzbekistán","Colombia vs Portugal"],
    "L": ["Inglaterra vs Croacia","Ghana vs Panamá","Inglaterra vs Ghana","Panamá vs Croacia","Croacia vs Ghana","Panamá vs Inglaterra"]
}
equipos = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "P. Bajos", "Bélgica", "Italia", "EE. UU.", "Marruecos", "Colombia", "Ecuador", "Croacia", "Japón", "Corea del Sur", "Senegal"])

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

# --- MENU ---
opc = st.sidebar.radio("MENÚ", ["📝 Cargar Prode", "📊 Ranking", "🔍 Ver Pronósticos", "⚙️ Admin"])

if opc == "📝 Cargar Prode":
    if 'bloqueo' not in st.session_state: st.session_state.bloqueo = False
    
    if st.session_state.bloqueo:
        st.success("🎉 ¡Tu pronóstico ha sido enviado con éxito! Ya estás participando.")
        st.info("No puedes cargar más de un prode desde el mismo navegador.")
        st.stop()
        
    nom = st.text_input("NOMBRE COMPLETO:").upper().strip()
    if nom:
        with st.form("f"):
            res = []
            t1, t2, t3 = st.tabs(["⚽ Grupos", "🏅 Podio Final", "💎 Bonus Especiales"])
            with t1:
                stbs = st.tabs([f"Grup {k}" for k in fixture.keys()])
                for i, (letra, lista_p) in enumerate(fixture.items()):
                    with stbs[i]:
                        for p in lista_p:
                            c1,c2,c3,c4,c5 = st.columns([3,1,0.5,1,3])
                            eqs = p.split(" vs ")
                            with c1: st.write(f"**{eqs[0]}**")
                            with c2: gl = st.number_input("G",0,15,key=f"l_{p}",label_visibility="collapsed")
                            with c3: st.write("v")
                            with c4: gv = st.number_input("G",0,15,key=f"v_{p}",label_visibility="collapsed")
                            with c5: st.write(f"**{eqs[1]}**")
                            res.append([nom, p, gl, gv])
            with t2:
                p1 = st.selectbox("🥇 CAMPEÓN", equipos, index=0)
                p2 = st.selectbox("🥈 SUBCAMPEÓN", equipos, index=1)
                p3 = st.selectbox("🥉 TERCER PUESTO", equipos, index=2)
                p4 = st.selectbox("🏅 CUARTO PUESTO", equipos, index=3)
            with t3:
                b1 = st.text_input("¿Quién hace el ÚLTIMO GOL de Argentina en grupos?")
                b2 = st.text_input("¿Quién hace el PRIMER GOL del ganador del Grupo J en Octavos?")
            if st.form_submit_button("💾 GUARDAR TODO"):
                registrados = ws_p.col_values(1)
                if nom in [n.upper() for n in registrados]: st.error("❌ Este nombre ya ha participado.")
                else:
                    h = datetime.now().strftime("%d/%m/%Y %H:%M")
                    res.extend([[nom,"P1",p1,""],[nom,"P2",p2,""],[nom,"P3",p3,""],[nom,"P4",p4,""],[nom,"B1",b1,""],[nom,"B2",b2,""]])
                    ws_p.append_rows([fila+[h] for fila in res])
                    st.session_state.bloqueo = True
                    st.rerun()

elif opc == "📊 Ranking":
    st.header("🏆 Tabla de Posiciones")
    rk = get_ranking()
    if rk is not None: st.dataframe(rk, use_container_width=True, hide_index=True)
    else: st.info("Sin resultados aún.")

elif opc == "🔍 Ver Pronósticos":
    st.header("🔍 Consultar Pronóstico de un Compañero")
    p_raw = ws_p.get_all_values()
    if len(p_raw) > 1:
        df_ver = pd.DataFrame(p_raw[1:], columns=['Nombre','Partido','G_L','G_V','Fecha'])
        lista_nombres = sorted(df_ver['Nombre'].unique())
        persona = st.selectbox("Selecciona a quién quieres ver:", lista_nombres)
        if persona:
            sub_df = df_ver[df_ver['Nombre'] == persona]
            # Separamos partidos de podios/bonus
            partidos_df = sub_df[sub_df['Partido'].str.contains(" vs ")]
            otros_df = sub_df[~sub_df['Partido'].str.contains(" vs ")]
            
            c_v1, c_v2 = st.columns([2, 1])
            with c_v1:
                st.write(f"### Partidos de {persona}")
                st.table(partidos_df[['Partido', 'G_L', 'G_V']])
            with c_v2:
                st.write("### Podio y Bonus")
                st.table(otros_df[['Partido', 'G_L']])
    else:
        st.info("Todavía nadie cargó su prode.")

elif opc == "⚙️ Admin":
    st.header("⚙️ Panel de Control")
    pw = st.text_input("Clave:", type="password")
    if pw == "DUNLOP2026":
        ta1, ta2, ta3 = st.tabs(["⚽ Partidos", "🏅 Podio Oficial", "💎 Bonus"])
        with ta1:
            with st.form("a1"):
                allm = [p for s in fixture.values() for p in s]
                ps = st.selectbox("Elegí el Partido:", sorted(allm))
                cl, cv = st.columns(2)
                rl, rv = cl.number_input("Local", 0, 15), c2.number_input("Visitante", 0, 15)
                if st.form_submit_button("ACTUALIZAR RESULTADO"):
                    filas = ws_r.get_all_values()
                    encontrado = False
                    for i, fila in enumerate(filas):
                        if fila[0] == ps:
                            ws_r.update(f'A{i+1}:C{i+1}', [[ps, rl, rv]])
                            encontrado = True
                            break
                    if not encontrado: ws_r.append_row([ps, rl, rv])
                    st.success(f"Resultado de {ps} guardado.")
        with ta2:
            with st.form("a2"):
                r1, r2, r3, r4 = st.selectbox("1°", equipos), st.selectbox("2°", equipos), st.selectbox("3°", equipos), st.selectbox("4°", equipos)
                if st.form_submit_button("GUARDAR PODIO"):
                    datos = ws_r.get_all_values()
                    finales = [f for f in datos if not f[0].startswith("PODIO")]
                    finales.extend([["PODIO 1", r1, ""], ["PODIO 2", r2, ""], ["PODIO 3", r3, ""], ["PODIO 4", r4, ""]])
                    ws_r.clear(); ws_r.append_rows(finales)
                    st.success("Podio actualizado.")
        with ta3:
            with st.form("a3"):
                rb1, rb2 = st.text_input("B1 (Último gol ARG):"), st.text_input("B2 (Primer gol Ganador J):")
                if st.form_submit_button("GUARDAR BONUS"):
                    datos = ws_r.get_all_values()
                    finales = [f for f in datos if not f[0].startswith("BONUS")]
                    finales.extend([["BONUS 1", rb1, ""], ["BONUS 2", rb2, ""]])
                    ws_r.clear(); ws_r.append_rows(finales)
                    st.success("Bonus actualizados.")
