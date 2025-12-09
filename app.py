import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS (ESTILO) ---
st.markdown("""
<style>
    .block-container{padding-top:1rem!important}
    .header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}
    .driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}
    .vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
    .vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}
    .vehicle-val{font-size:14px;font-weight:bold;color:#004aad}
    .time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}
    .carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}
    .info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}
    .info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}
    button[kind="primary"]{width:100%;height:50px;font-size:18px!important}
    /* Esconde indices das tabelas */
    thead tr th:first-child {display:none}
    tbody th {display:none}
</style>
""", unsafe_allow_html=True)

# --- 3. LEITURA INTELIGENTE ---
def ler_rotas(file_content):
    try:
        # Tenta ler CSV com diferentes configurações
        try: df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            try: df_raw = pd.read_csv(file_content, header=None, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='latin1')

        # --- DETETAR ONDE ESTÁ O CABEÇALHO ---
        # Procura em qual linha aparecem as palavras chave "Motorista" e "VPN"
        header_idx = -1
        for i, row in df_raw.head(10).iterrows():
            row_txt = row.astype(str).str.lower().str.cat(sep=' ')
            if 'motorista' in row_txt and 'vpn' in row_txt:
                header_idx = i
                break
        
        if header_idx == -1:
            st.error("Não encontrei as colunas 'Motorista' e 'VPN'. Verifique o ficheiro.")
            return None

        # Redefine o DataFrame usando a linha correta como cabeçalho
        df_raw.columns = df_raw.iloc[header_idx]
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)

        # LIMPEZA DOS NOMES DAS COLUNAS
        # 1. Remove espaços extras (ex: "Matricula " vira "Matricula")
        # 2. Corrige nomes (ex: "Movél" vira "Móvel")
        df.columns = df.columns.astype(str).str.strip()
        
        mapa_correcao = {
            'Matricula': 'Matrícula', 
            'Movél': 'Móvel', 
            'NºLOJA': 'Nº LOJA',
            'Talho': 'Carne'  # <--- IMPORTANTE: Renomeia Talho para Carne internamente se quiser, ou trata na visualização
        }
        
        for col_real in df.columns:
            for errado, certo in mapa_correcao.items():
                if errado.lower() == col_real.lower(): # Comparação exata ignorando maiúsculas
                    df.rename(columns={col_real: certo}, inplace=True)

        # FILTRAGEM DE DADOS
        if 'VPN' in df.columns:
            # Remove .0 e espaços
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Remove linhas vazias ou lixo
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Remove linhas onde o Motorista está vazio ou é cabeçalho repetido
            df = df[df['Motorista'].astype(str).str.lower() != 'motorista']
            df = df[df['Motorista'].notna()]

        return df

    except Exception as e:
        st.error(f"Erro ao ler ficheiro: {e}")
        return None

# --- VARIÁVEIS ---
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"
ADMINS = {"Admin": "123", "Gestor": "2025"}

# --- LÓGICA DE DATA ---
if os.path.exists(DATE_FILE):
    with open(DATE_FILE, "r") as f: 
        dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
else: dt = datetime.now()

# --- CARREGAR DADOS ---
df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f: df_rotas = ler_rotas(BytesIO(f.read()))

# --- INTERFACE ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")
    if df_rotas is not None: 
        st.success(f"Rotas: {len(df_rotas)}")
        # Debug opcional
        # with st.expander("Colunas"): st.write(list(df_rotas.columns))

if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
    
    if df_rotas is not None:
        with st.form("busca"):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")
            
        if btn and vpn:
            # Filtra por VPN ou Nome (parcial)
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            if res.empty: res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    # 1. MOTORISTA
                    st.markdown(f'<div class="driver-card">👤 {row.get("Motorista", "-")}</div>', unsafe_allow_html=True)
                    
                    # 2. VEÍCULO
                    mat = row.get("Matrícula", "-")
                    mov = row.get("Móvel", "-")
                    rota = row.get("ROTA", "-")
                    loja = row.get("Nº LOJA", "-")
                    
                    st.markdown(f'''
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{mat}</div></div>
                        <div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{mov}</div></div>
                        <div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{rota}</div></div>
                        <div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{loja}</div></div>
                    </div>''', unsafe_allow_html=True)
                    
                    # 3. HORÁRIOS
                    # Procura colunas de forma flexível (contendo 'chegada', etc.)
                    col_cheg = next((c for c in df_rotas.columns if "chegada" in c.lower()), 'Hora chegada Azambuja')
                    col_desc = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora
                    
