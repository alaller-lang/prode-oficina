import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Prode Dunlop 2026", page_icon="🏆", layout="wide")

# --- CONEXIÓN ---
@st.cache_resource
def conectar():
    info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    ss = gspread.authorize(creds).open("Prode_Mundial_2026")
    return ss.worksheet("pronosticos"), ss.worksheet("resultados_reales")

ws_p, ws_r = conectar()

# --- EL FIXTURE COMPLETO (COMPACTO) ---
partidos = [
    "México vs Sudáfrica","Corea Sur vs Rep. Checa","México vs Corea Sur","Rep. Checa vs Sudáfrica","Sudáfrica vs Corea Sur","Rep. Checa vs México",
    "Canadá vs Bosnia","Catar vs Suiza","Canadá vs Catar","Suiza vs Bosnia","Bosnia vs Catar","Suiza vs Canadá",
    "Brasil vs Marruecos","Haití vs Escocia","Brasil vs Haití","Escocia vs Marruecos","Marruecos vs Haití","Escocia vs Brasil",
    "EE. UU. vs Paraguay","Australia vs Turquía","EE. UU. vs Australia","Turquía vs Paraguay","Paraguay vs Australia","Turquía vs EE. UU.",
    "Alemania vs Curazao","C. Marfil vs Ecuador","Alemania vs C. Marfil","Ecuador vs Curazao","Curazao vs C. Marfil","Ecuador vs Alemania",
    "P. Bajos vs Japón","Suecia vs Túnez","P. Bajos vs Suecia","Túnez vs Japón","Japón vs Suecia","Túnez vs P. Bajos",
    "Bélgica vs Egipto","Irán vs N. Zelanda","Bélgica vs Irán","N. Zelanda vs Egipto","Egipto vs Irán","N. Zelanda vs Bélgica",
    "España vs Cabo Verde","Uruguay vs A. Saudí","España vs Uruguay","A. Saudí vs Cabo Verde","Cabo Verde vs Uruguay","A. Saudí vs España",
    "Francia vs Senegal","Irak vs Noruega","Francia vs Irak","Noruega vs Senegal","Senegal vs Irak","Noruega vs Francia",
    "Argentina vs Argelia","Austria vs Jordania","Argentina vs Austria","Jordania vs Argelia","Argelia vs Austria","Jordania vs Argentina",
    "Portugal vs RD Congo","Uzbekistán vs Colombia","Portugal vs Uzbekistán","Colombia vs RD Congo","RD Congo vs Uzbekistán","Colombia vs Portugal",
    "Inglaterra vs Croacia","Ghana vs Panamá","Inglaterra vs Ghana","Panamá vs Croacia","Croacia vs Ghana","Panamá vs Inglaterra"
]
equipos_podio = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Alemania", "Inglaterra", "Uruguay", "Portugal", "P. Bajos", "Bélgica", "Italia", "EE. UU.", "Marruecos", "Colombia", "Ecuador"])

# --- LÓGICA RANKING ---
def get_ranking():
    try:
        p_raw, r_raw = ws_p.get_all_values(), ws_r.get_all_values()
        if len(p_raw)<2 or len(r_raw)<2: return None
        dfp = pd.DataFrame(p_raw[1:], columns=['Nombre','Partido','GLu','GVu','Fecha'])
        dfr = pd.DataFrame(r_raw[1:], columns=['Partido','GLr','GVr'])
        dfp = dfp[dfp['Partido'].str.contains("vs", na=False)].copy()
        for c in ['GLu','GVu']: dfp[c] = pd.to_numeric(dfp[c], errors='coerce').fillna(0)
        for c in ['GLr','GVr']: dfr[c] = pd.to_numeric(dfr[c], errors='coerce').fillna(0)
        dfm = dfp.merge(dfr, on="Partido")
        def pts(x):
            if x['GLu']==x['GLr'] and x['GVu']==x['GVr']: return 3
            su, sr = (x['GLu']>x['GVu'])-(x['GLu']<x['GVu']), (x['GLr']>x['GVr'])-(x['GLr']<x['GVr'])
            return 1 if su==sr else 0
        dfm['Pts'] = dfm.apply(pts, axis=1)
        return dfm.groupby('Nombre')['Pts'].sum().reset_index().sort_values('Pts', ascending=False)
    except: return None

# --- MENÚ ---
opc = st.sidebar.radio("MENÚ", ["📝 Cargar Prode", "📊 Ranking", "⚙️ Admin"])

if opc == "📝 Cargar Prode":
    if 'ok' not in st.session_state: st.session_state.ok = False
    if st.session_state.ok:
        st.success("✅ ¡Pronóstico guardado!"); st.button("Cargar otro", on_click=lambda: st.session_state.update({'ok':False}))
        st.stop()
    
    nom = st.text_input("NOMBRE COMPLETO:").upper().strip()
    if nom:
        with st.form("f"):
            res = []
            st.subheader("⚽ Fase de Grupos")
            for p in partidos:
                c1, c2, c3, c4, c5 = st.columns([3, 1, 0.5, 1, 3])
                eqs = p.split(" vs ")
                with c1: st.write(f"**{eqs[0]}**")
                with c2: gl = st.number_input("G", 0, 15, key=f"l_{p}", label_visibility="collapsed")
                with c3: st.write("v")
                with c4: gv = st.number_input("G", 0, 15, key=f"v_{p}", label_visibility="collapsed")
                with c5: st.write(f"**{eqs[1]}**")
                res.append([nom, p, gl, gv])
            
            st.divider()
            c_f1, c_f2 = st.columns(2)
            camp = c_f1.selectbox("Campeón:", equipos_podio)
            bon = c_f2.text_input("Goleador:")
            
            if st.form_submit_button("GUARDAR MI PRODE"):
                if nom in [n.upper() for n in ws_p.col_values(1)]: st.error("Ya registrado.")
                else:
                    h = datetime.now().strftime("%d/%m/%Y %H:%M")
                    res.extend([[nom, "CAMP", camp, ""], [nom, "B1", bon, ""]])
                    ws_p.append_rows([f + [h] for f in res])
                    st.session_state.ok = True; st.rerun()

elif opc == "📊 Ranking":
    rk = get_ranking()
    if rk is not None: st.dataframe(rk, use_container_width=True, hide_index=True)
    else: st.info("Sin resultados.")

elif opc == "⚙️ Admin":
    pw = st.text_input("Clave:", type="password")
    if pw == "DUNLOP2026":
        with st.form("ad"):
            psel = st.selectbox("Partido:", partidos)
            c1, c2 = st.columns(2)
            rl, rv = c1.number_input("L", 0, 15), c2.number_input("V", 0, 15)
            if st.form_submit_button("OK"):
                ws_r.append_row([psel, rl, rv]); st.success("Guardado")
