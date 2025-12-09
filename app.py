import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Logística App",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- ESTILO CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    .header-box { 
        background: #004aad; padding: 20px; border-radius: 12px; 
        text-align: center; color: white; margin-bottom: 20px; 
    }
    .driver-card {
        background: #004aad; color: white; padding: 10px; 
        border-radius: 8px; text-align: center; font-weight: bold; 
        font-size: 1.2rem; margin-bottom: 10px;
    }
    .vehicle-grid {
        display: grid; grid-template-columns: 1fr 1fr; 
        gap: 8px; margin-bottom: 12px;
    }
    .vehicle-item {
        background: #e3f2fd; padding: 8px; border-radius: 6px; 
        text-align: center; border: 1px solid #bbdefb;
    }
    .vehicle-val { font-size: 14px; font-weight: bold; color: #004aad; }
    .time-block {
        background: #f8f9fa; padding: 10px; border-radius: 8px; 
        border-left: 6px solid #004aad; margin-bottom: 5px;
    }
    .carga-box {
        background: #fff; border: 1px solid #eee; 
        border-radius: 8px; padding: 10px; margin-top: 10px;
    }
    .info-row {
        display: flex; justify-content: space-between; 
        gap: 5px; margin: 15px 0;
    }
    .info-item {
        flex: 1; text-align: center; padding: 5px; 
        border-radius: 6px; color: white; font-size: 0.9rem;
    }
    button[kind="primary"] { 
        width: 100%; height: 50px; font-size: 18px !important; 
    }
    thead tr th:first-child { display: none; }
    tbody th { display: none; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE LEITURA ---
def ler_rotas(file_content):
    try:
        # Tenta ler o CSV de várias formas
        try: 
            df = pd.read_csv(file_content, header=None, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            try: 
                df = pd.read_csv(file_content, header=None, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try: 
                    df = pd.read_csv(file_content, header=None, sep=',', encoding='latin1')
                except: 
                    return None

        # Procura onde começa o cabeçalho (Motorista / VPN)
        header_idx = -1
        for i, row in df.head(15).iterrows():
            linha = row.astype(str).str.lower().str.cat(sep=' ')
            if 'motorista' in linha and 'vpn' in linha:
                header_idx = i
                break
        
        if header_idx == -1: 
            header_idx = 0

        # Define as colunas corretas
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx+1:].reset_index(drop=True)

        # Limpa nomes das colunas
        df.columns = df.columns.astype(str).str.strip()
        
        # Corrige nomes comuns
        correcoes = {
            'Matricula': 'Matrícula', 'Movél': 'Móvel',
            'NºLOJA': 'Nº LOJA', 'Motorista ': 'Motorista',
            'Talho': 'Carne', 'N LOJA': 'Nº LOJA'
        }
        for real in df.columns:
            for errado, certo in correcoes.items():
                if errado.lower() in real.lower():
                    df.rename(columns={real: certo}, inplace=True)

        # Filtra dados vazios
        if 'VPN' in df.columns:
            # Limpa coluna VPN
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True)
            df['VPN'] = df['VPN'].str.strip()
            
            # Remove linhas inválidas
            filtro_lixo = ['0', 'nan', '', 'None', 'VPN']
            df = df[~df['VPN'].isin(filtro_lixo)]
            
            # Garante que Motorista existe
            col_mot = next((c for c in df.columns if 'motorista' in c.lower()), None)
            if col_mot:
                df = df[df[col_mot].notna()]

        return df
    except Exception as e:
        st.error(f"Erro na leitura: {e}")
        return None

# --- FICHEIROS ---
DB_FILE = "dados_rotas.source"
DATE_FILE = "data_manual.txt"

# --- DATA ---
if os.path.exists(DATE_FILE):
    try:
        with open(DATE_FILE, "r") as f:
            texto = f.read().strip()
            dt = datetime.strptime(texto, "%Y-%m-%d")
    except:
        dt = datetime.now()
else:
    dt = datetime.now()

# --- CARREGAR DADOS ---
df_rotas = None
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "rb") as f:
            df_rotas = ler_rotas(BytesIO(f.read()))
    except:
        pass

# --- MENU LATERAL ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Navegação", ["Escala Diária", "Gestão"])
    
    st.markdown("---")
    if df_rotas is not None:
        st.success(f"Carregado: {len(df_rotas)} rotas")
    else:
        st.warning("Sem dados.")

# ==========================================
# PÁGINA 1: ESCALA
# ==========================================
if menu == "Escala Diária":
    data_fmt = dt.strftime("%d/%m/%Y")
    st.markdown(f"""
    <div class="header-box">
        <h3>ESCALA DIÁRIA</h3>
        <p>{data_fmt}</p>
    </div>
    """, unsafe_allow_html=True)

    if df_rotas is not None:
        with st.form("busca"):
            c1, c2 = st.columns([2, 1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628")
            btn = c2.form_submit_button("BUSCAR")

        if btn and vpn:
            vpn_limpo = vpn.strip()
            # Filtra por VPN
            res = df_rotas[df_rotas['VPN'] == vpn_limpo]
            
            # Se não achar, tenta por nome
            if res.empty:
                col_mot = next((c for c in df_rotas.columns if 'motorista' in c.lower()), None)
                if col_mot:
                    filtro = df_rotas[col_mot].astype(str).str.lower()
                    res = df_rotas[filtro.str.contains(vpn_limpo.lower())]

            if not res.empty:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    
                    # 1. MOTORISTA
                    col_mot = next((c for c in df_rotas.columns if 'motorista' in c.lower()), 'Motorista')
                    nome = row.get(col_mot, "-")
                    st.markdown(f'<div class="driver-card">👤 {nome}</div>', unsafe_allow_html=True)

                    # 2. VEÍCULO
                    mat = row.get("Matrícula", "-")
                    mov = row.get("Móvel", "-")
                    rota = row.get("ROTA", "-")
                    lo
