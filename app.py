import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Logística App",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (ESTILO) ---
# Definido numa linha única para evitar erros de aspas
st.markdown('<style>.block-container{padding-top:1rem!important}.header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}.driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}.vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}.vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}.vehicle-val{font-size:14px;font-weight:bold;color:#004aad}.time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}.carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}.info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}.info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}button[kind="primary"]{width:100%;height:50px;font-size:18px!important}thead tr th:first-child{display:none}tbody th{display:none}</style>', unsafe_allow_html=True)

# --- 3. FUNÇÃO DE LEITURA ---
def ler_rotas(file_content):
    try:
        # Tenta ler CSV com UTF-8
        try:
            df = pd.read_csv(file_content, header=0, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            # Tenta ler CSV com Latin1 e ponto e vírgula
            try:
                df = pd.read_csv(file_content, header=0, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                # Tenta ler CSV com Latin1 e vírgula
                try:
                    df = pd.read_csv(file_content, header=0, sep=',', encoding='latin1')
                except:
                    return None

        # CORREÇÃO DE COLUNAS FORÇADA
        # Se houver mais de 5 colunas, assume que a 1 é Motorista e 2 é VPN
        cols = list(df.columns)
        if len(cols) > 5:
            df.columns.values[1] = 'Motorista'
            df.columns.values[2] = 'VPN'

        # Limpeza dos nomes das colunas (remove espaços)
        df.columns = df.columns.astype(str).str.strip()
        
        # Mapa de Correção de Nomes
        mapa = {
            'Matricula': 'Matrícula',
            'Movél': 'Móvel',
            'NºLOJA': 'Nº LOJA',
            'Talho': 'Carne'
        }
        
        for real in df.columns:
            for k, v in mapa.items():
                if k.lower() in real.lower():
                    df.rename(columns={real: v}, inplace=True)

        # Filtros de Dados
        if 'VPN' in df.columns:
            # Limpa VPN
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            # Remove linhas inválidas
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            
            # Remove linhas de cabeçalho repetido
            if 'Motorista' in df.columns:
                df = df[df['Motorista'].astype(str).str.lower() != 'motorista']
                df = df[df['Motorista'].notna()]

        return df
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
        return None

# --- DADOS E VARIÁVEIS ---
DB_FILE = "dados_rotas.source"
DATE_FILE = "data_manual.txt"

# Lógica de Data Expandida (para evitar erros)
if os.path.exists(DATE_FILE):
    try:
        with open(DATE_FILE, "r") as f:
            conteudo = f.read().strip()
            dt = datetime.strptime(conteudo, "%Y-%m-%d")
    except:
        dt = datetime.now()
else:
    dt = datetime.now()

# Carregar DataFrame
df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        df_rotas = ler_rotas(BytesIO(f.read()))

# --- MENU LATERAL ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Navegação:", ["Escala Diária", "Área de Gestão"])
    
    st.markdown("---")
    if df_rotas is not None:
        st.success(f"Carregado: {len(df_rotas)} rotas")
    else:
        st.warning("Sem dados carregados")

# ==================================================
# PÁGINA 1: ESCALA DIÁRIA
# ==================================================
if menu == "Escala Diária":
    # Cabeçalho
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    if df_rotas is not None:
        with st.form("busca"):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")
            
        if btn and vpn:
            # Filtra por VPN exata
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            
            # Se falhar, tenta nome parcial
            if res.empty and 'Motorista' in df_rotas.columns:
                 res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    
                    # 1. MOTORISTA
                    nom = row.get("Motorista", "-")
                    st
