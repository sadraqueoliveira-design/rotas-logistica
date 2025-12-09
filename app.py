import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="expanded")

# --- 2. CSS ---
st.markdown('<style>.block-container{padding-top:1rem!important}.header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}.driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}.vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}.vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}.vehicle-val{font-size:14px;font-weight:bold;color:#004aad}.time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}.carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}.info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}.info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}button[kind="primary"]{width:100%;height:50px;font-size:18px!important}thead tr th:first-child{display:none}tbody th{display:none}</style>', unsafe_allow_html=True)

# --- 3. LEITURA INTELIGENTE ---
def ler_rotas(file_content):
    try:
        # Lê bruto
        try: df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            try: df_raw = pd.read_csv(file_content, header=None, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try: df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='latin1')
                except: return None 

        # Procura cabeçalho
        header_idx = -1
        for i, row in df_raw.head(10).iterrows():
            t = row.astype(str).str.lower().str.cat(sep=' ')
            if 'motorista' in t and 'vpn' in t:
                header_idx = i
                break
        if header_idx == -1: header_idx = 0

        # Define colunas
        df_raw.columns = df_raw.iloc[header_idx]
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)

        # Limpa nomes
        df.columns = df.columns.astype(str).str.strip()
        mapa = {'Matricula':'Matrícula','Movél':'Móvel','NºLOJA':'Nº LOJA','Motorista ':'Motorista','Talho':'Carne'}
        for c in df.columns:
            for k,v in mapa.items():
                if k.lower() in c.lower(): df.rename(columns={c:v}, inplace=True)

        # Filtra
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$','',regex=True).str.strip()
            df = df[~df['VPN'].isin(['0','nan','','None','VPN'])]
            if 'Motorista' in df.columns: df = df[df['Motorista'].notna()]
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

# --- DADOS ---
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"

if os.path.exists(DATE_FILE):
    try:
        with open(DATE_FILE,"r") as f: dt = datetime.strptime(f.read().strip(),"%Y-%m-%d")
    except: dt = datetime.now()
else: dt = datetime.now()

df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE,"rb") as f: df_rotas = ler_rotas(BytesIO(f.read()))

# --- UI ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")
    if df_rotas is not None: st.success(f"Carregado: {len(df_rotas)}")

# --- PÁGINA ESCALA ---
if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
    
    if df_rotas is not None:
        with st.form("busca"):
            c1,c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")
            
        if btn and vpn:
            res = df_rotas[df_rotas['VPN']==vpn.strip()]
            if res.empty and 'Motorista' in df_rotas.columns:
                 res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    # MOTORISTA
                    n = row.get("Motorista","-")
                    st.markdown(f'<div class="driver-card">👤 {n}</div>', unsafe_allow_html=True)
                    
                    # VEICULO
                    ma = row.get("Matrícula","-")
                    mo = row.get("Móvel","-")
                    ro = row.get("ROTA","-")
                    lo = row.get("Nº LOJA","-")
                    st.markdown(f'<div class="vehicle-grid"><div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{ma}</div></div><div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{mo}</div></div><div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{ro}</div></div><div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{lo}</div></div></div>', unsafe_allow_html=True)
                    
                    # HORARIO
                    cc = next((c for c in df_rotas.columns if "chegada" in c.lower()), 'Hora chegada')
                    cd = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora descarga')
                    cl = next((c for c in df_rotas.columns if "local descarga" in c.lower()), 'Local')
                    vl = str(row.get(cl,"Loja")).upper()
                    if "NAN" in vl: vl="LOJA"

                    c1,c2=st.columns(2)
                    c1.markdown(f'<div class="time-block"><div>CHEGADA</div><h3>{row.get(cc,"--")}</h3><b style="color:#004aad">AZAMBUJA</b></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="time-block" style="border-left-color:#d32f2f"><div>DESCARGA</div><h3>{row.get(cd,"--")}</h3><b style="color:#d32f2f">{vl}</b></div>', unsafe_allow_html=True)
                    
                    # CARGA
                    ign=["motorista","vpn","matrícula","matricula","móvel","movel","rota","loja","hora","chegada","descarga","local","turno","filtro","retorno","tipo","total suportes","unnamed","recolha"]
                    cargas={}
                    for c in df_rotas.columns:
                        cl=str(c).lower()
                        if not any(x in cl for x in ign):
                            v=str(row.get(c,'')).strip()
                            if v and v not in ['0','0.0','nan','None','']:
                                nm=c.replace("Azambuja","").replace("Salvesen","").replace("Total","").strip()
                                if "carne" in cl: nm="🥩 Carne"
                                elif "peixe" in cl: nm="🐟 Peixe"
                                elif "congelados" in cl: nm="❄️ Congelados"
                                elif "ambiente" in cl: nm="📦 Ambiente"
                                elif "fruta" in cl: nm="🍎 Fruta"
                                cargas[nm]=v
                    
                    if cargas:
                        st.markdown('<div class="carga-box"><b>📦 CARGA</b>', unsafe_allow_html=True)
                        df_c=pd.DataFrame(list(cargas.items()),columns=["Tipo","Qtd"])
                        st.table(df_c.set_index("Tipo"))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # RODAPÉ
                    vr = str(row.get('Retorno','-'))
                    vs = str(row.get('Total Suportes','0'))
                    vt = row.get("TIPO","-")
                    cor = "#008000" if vr not in ['0','-','nan','Vazio'] else "#333"
                    
                    st.markdown(f'<div class="info-row"><div class="info-item" style="background:#7b1fa2">SUPORTES<br><b>{vs}</b></div><div class="info-item" style="background:white;color:{cor};border:1px solid #ccc">RETORNO<br><b>{vr}</b></div><div class="info
