import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS ---
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
    thead tr th:first-child {display:none}
    tbody th {display:none}
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÃO DE LEITURA ---
def ler_rotas(file_content):
    try:
        # Tenta ler CSV com diferentes configurações
        try: df = pd.read_csv(file_content, header=0, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            try: df = pd.read_csv(file_content, header=0, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try: df = pd.read_csv(file_content, header=0, sep=',', encoding='latin1')
                except: return None 

        # --- LIMPEZA DE NOMES DAS COLUNAS ---
        # 1. Remove espaços no início/fim ("Motorista " -> "Motorista")
        df.columns = df.columns.astype(str).str.strip()
        
        # 2. Mapa de Correção (baseado no seu ficheiro)
        mapa_correcao = {
            'Matricula': 'Matrícula', 
            'Movél': 'Móvel', 
            'NºLOJA': 'Nº LOJA',
            'Motorista': 'Motorista', 
            'VPN': 'VPN',
            'Talho': 'Carne' 
        }
        
        # Aplica correções de nomes
        for col_real in df.columns:
            for errado, certo in mapa_correcao.items():
                if errado.lower() in col_real.lower():
                    df.rename(columns={col_real: certo}, inplace=True)

        # --- FILTRAGEM DE DADOS ---
        if 'VPN' in df.columns:
            # Remove sufixo .0 e converte para texto
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Remove linhas vazias ou lixo
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Garante que tem motorista
            if 'Motorista' in df.columns:
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
# Verifica se existe ficheiro de data, senão usa hoje
if os.path.exists(DATE_FILE):
    try:
        with open(DATE_FILE, "r") as f: 
            dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
    except: dt = datetime.now()
else: 
    dt = datetime.now()

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

if menu == "Escala":
    st.markdown(f'<div class="header-box
