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

# --- DATOS (LISTA CORTA PARA EVITAR CORTES) ---
grupos = {
    "A": ["🇲🇽 México vs 🇿🇦 Sudáfrica", "🇰🇷 Corea Sur vs 🇨🇿 Rep. Checa"],
    "J": ["🇦🇷 Argentina vs 🇩🇿 Argelia", "🇦🇹 Austria vs 🇯🇴 Jordania"]
}
equipos = sorted(["Argentina", "Brasil", "México", "España", "Francia", "Uruguay", "Alemania"])

# --- RANKING ---
def get_ranking():
    try:
        p, r = ws_p.get_all_values(), ws_r.get_all_values()
        if len(p)<2 or len(r)<2: return None
        dfp = pd.DataFrame(p[1:], columns=['Nombre','Partido','GLu','GVu','Fecha'])
        dfr = pd.DataFrame(r[1:], columns=['Partido','GLr','GVr'])
        dfp = dfp[dfp['Partido'].str.contains("vs")].copy()
        for c in ['GLu','GVu','GLr','GVr']: 
            if c in dfp.columns: dfp[c] = pd.to_numeric(dfp[c], errors='coerce')
            if c in dfr.columns: dfr[c] = pd.to_numeric(dfr[c], errors='coerce')
        dfm = dfp.merge(dfr, on="Partido")
        def pts(x):
            if x['GLu']==x['GLr'] and x['GVu']==x['GVr']: return 3
            su, sr = (x['GLu']>x['GVu'])-(x['GLu']<x['GVu']), (x['GLr']>x['GVr'])-(x['GLr']<x['GVr'])
            return 1 if su==sr else 0
        dfm['Pts'] = dfm.apply(pts, axis=1)
        return dfm.groupby('Nombre')['Pts'].sum().reset_index().sort_values('Pts', ascending=False)
    except: return None

# --- NAVEGACIÓN ---
opc = st.sidebar.radio("MENÚ", ["📝 Cargar", "📊 Ranking", "⚙️ Admin"])

if opc == "📝 Cargar":
    if st.session_state.get('ok'):
        st.success("¡Guardado!"); st.button("Otro", on_click=lambda: st.session_state.update({'ok':False}))
        st.stop()
    nom = st.text_input("NOMBRE:").upper()
    if nom:
        with st.form("f"):
            res = []
            t1, t2 = st.tabs(["Partidos", "Finales"])
            with t1:
                for g, ps in grupos.items():
                    st.write(f"**Grupo {g}**")
                    for p in ps:
                        c1, c2, c3, c4, c5 = st.columns([3,1,0.5,1,3])
                        with c1: st.write(p.split(" vs ")[0])
                        with c2: gl = st.number_input("G",0,15,key=f"l_{p}")
                        with c3: st.write("v")
                        with c4: gv = st.number_input("G",0,15,key=f"v_{p}")
                        with c5: st.write(p.split(" vs ")[1])
                        res.append([nom, p, gl, gv])
            with t2:
                p1 = st.selectbox("Campeón", equipos)
                b1 = st.text_input("Último gol ARG:")
            if st.form_submit_button("GUARDAR"):
                h = datetime.now().strftime("%Y-%m-%d %H:%M")
                res.extend([[nom,"P1",p1,""],[nom,"B1",b1,""]])
                ws_p.append_rows([fila+[h] for fila in res])
                st.session_state.ok = True; st.rerun()

elif opc == "📊 Ranking":
    rk = get_ranking()
    if rk is not None: st.table(rk)
    else: st.info("Sin datos.")

elif opc == "⚙️ Admin":
    pw = st.text_input("Clave:", type="password")
    if pw == "DUNLOP2026":
        with st.form("ad"):
            p = st.selectbox("Partido:", [x for g in grupos.values() for x in g])
            l, v = st.number_input("L",0,15), st.number_input("V",0,15)
            if st.form_submit_button("OK"):
                ws_r.append_row([p, l, v]); st.success("Cargado")
