import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="expanded")

# 2. CSS
st.markdown('<style>.block-container{padding-top:1rem!important}.header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}.driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}.vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}.vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}.vehicle-val{font-size:14px;font-weight:bold;color:#004aad}.time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}.carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}.info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}.info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}button[kind="primary"]{width:100%;height:50px;font-size:18px!important}thead tr th:first-child{display:none}tbody th{display:none}</style>', unsafe_allow_html=True)

# 3. LEITURA INTELIGENTE
def ler_rotas(file_content):
    try:
        # Lê o ficheiro sem cabeçalho para analisar
        try: df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            try: df_raw = pd.read_csv(file_content, header=None, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try: df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='latin1')
                except: return None 

        # Procura a linha que contem "VPN" e "Motorista"
        header_idx = -1
        for i, row in df_raw.head(10).iterrows():
            txt = row.astype(str).str.lower().str.cat(sep=' ')
            if 'vpn' in txt and 'motorista' in txt:
                header_idx = i
                break
        
        # Se não achou, tenta achar só "Matricula" (caso falhe o resto)
        if header_idx == -1:
            for i, row in df_raw.head(10).iterrows():
                if 'matricula' in row.astype(str).str.lower().str.cat(sep=' '):
                    header_idx = i
                    break
        
        if header_idx == -1: header_idx = 0 # Fallback

        # Define Cabeçalho
        df_raw.columns = df_raw.iloc[header_idx]
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)

        # Limpa nomes das colunas
        df.columns = df.columns.astype(str).str.strip()

        # Renomeia colunas essenciais
        mapa = {
            'Matricula': 'Matrícula', 'Movél': 'Móvel', 
            'NºLOJA': 'Nº LOJA', 'Motorista ': 'Motorista', 'VPN ': 'VPN',
            'Talho': 'Carne', 'N LOJA': 'Nº LOJA'
        }
        for real in df.columns:
            for k, v in mapa.items():
                if k.lower() in real.lower():
                    df.rename(columns={real: v}, inplace=True)

        # --- CORREÇÃO DE SEGURANÇA ---
        # Se a coluna VPN ainda não existir, tenta pegar pela posição (Coluna 3)
        if 'VPN' not in df.columns and len(df.columns) > 3:
            # Assume estrutura padrão se os nomes falharem
            col_list = list(df.columns)
            df.rename(columns={col_list[1]: 'Motorista', col_list[2]: 'VPN'}, inplace=True)

        # Filtros Finais
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Filtra linhas vazias de motorista
            if 'Motorista' in df.columns:
                df = df[df['Motorista'].notna()]
        
        return df
    except Exception as e:
        st.error(f"Erro ao ler: {e}")
        return None

# --- DADOS ---
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"

if os.path.exists(DATE_FILE):
    try:
        with open(DATE_FILE, "r") as f: dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
    except: dt = datetime.now()
else: dt = datetime.now()

# Carregar Dados e VALIDAR SE ESTÃO BONS
df_rotas = None
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "rb") as f: df_rotas = ler_rotas(BytesIO(f.read()))
        # Se o ficheiro lido não tiver VPN, descarta-o para não dar erro
        if df_rotas is not None and 'VPN' not in df_rotas.columns:
            df_rotas = None
    except:
        df_rotas = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")
    st.markdown("---")
    if df_rotas is not None: 
        st.success(f"Rotas: {len(df_rotas)}")
    else:
        st.warning("⚠️ Dados inválidos ou vazios")

# --- PÁGINAS ---
if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
    
    if df_rotas is not None:
        with st.form("busca"):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")
            
        if btn and vpn:
            # Filtro seguro
            if 'VPN' in df_rotas.columns:
                res = df_rotas[df_rotas['VPN'] == vpn.strip()]
                
                # Fallback para nome
                if res.empty and 'Motorista' in df_rotas.columns:
                    res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

                if not res.empty:
                    for idx, row in res.iterrows():
                        st.markdown("---")
                        # 1. MOTORISTA
                        nom = row.get("Motorista", "-")
                        st.markdown(f'<div class="driver-card">👤 {nom}</div>', unsafe_allow_html=True)
                        
                        # 2. VEÍCULO
                        mat = row.get("Matrícula", "-")
                        mov = row.get("Móvel", "-")
                        rota = row.get("ROTA", "-")
                        loja = row.get("Nº LOJA", "-")
                        st.markdown(f'<div class="vehicle-grid"><div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{mat}</div></div><div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{mov}</div></div><div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{rota}</div></div><div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{loja}</div></div></div>', unsafe_allow_html=True)
                        
                        # 3. HORÁRIOS
                        c_cheg = next((c for c in df_rotas.columns if "chegada" in c.lower()), 'Hora chegada')
                        c_desc = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora descarga')
                        c_loc = next((c for c in df_rotas.columns if "local descarga" in c.lower()), 'Local')
                        
                        v_loc = str(row.get(c_loc,"Loja")).upper()
                        if "NAN" in v_loc: v_loc = "LOJA"

                        c1, c2 = st.columns(2)
                        c1.markdown(f'<div class="time-block"><div>CHEGADA</div><h3>{row.get(c_cheg,"--")}</h3><b style="color:#004aad">AZAMBUJA</b></div>', unsafe_allow_html=True)
                        c2.markdown(f'<div class="time-block" style="border-left-
