import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz 

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="App Rotas",
    page_icon="🚛",
    layout="centered"
)

# --- 2. DATA ---
try:
    fuso = pytz.timezone('Europe/Lisbon')
    agora = datetime.now(fuso)
except:
    agora = datetime.now()

data_hoje = agora.strftime("%d/%m")
dias = {0:"Seg", 1:"Ter", 2:"Qua", 3:"Qui", 4:"Sex", 5:"Sáb", 6:"Dom"}
dia_sem = dias[agora.weekday()]

# --- 3. ESTILO (CSS OTIMIZADO) ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem;}
    
    /* Cabeçalho */
    .header-box {
        background-color: #004aad;
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        color: white;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    .header-title { font-size: 16px; font-weight: bold; margin: 0; line-height: 1; }
    .header-date { font-size: 11px; opacity: 0.9; margin: 0; }
    
    /* Blocos de Horário */
    .time-block {
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 5px;
        border-left: 3px solid #004aad;
        margin-bottom: 5px;
    }
    .time-label { font-size: 0.6rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #333; margin: 0; line-height: 1.1; }
    
    /* Locais em Destaque */
    .location-highlight { font-size: 0.8rem; font-weight: 900; text-transform: uppercase; margin: 0;}
    .text-blue { color: #0d47a1; } 
    .text-red { color: #d32f2f; }
    
    /* BARRA HORIZONTAL ULTRA FINA */
    .info-row {
        display: flex;
        justify-content: space-between;
        gap: 4px;
        margin-top: 5px;
        margin-bottom: 5px;
    }
    .info-item {
        flex: 1;
        text-align: center;
        padding: 3px 2px;
        border-radius: 4px;
        color: white;
    }
    .info-label { font-size: 0.5rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 0px; line-height: 1;}
    .info-val { font-size: 0.9rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; }
    .bg-orange { background-color: #f57c00; }
    .bg-green { background-color: #388e3c; }

    div[data-testid="metric-container"] { padding: 4px; margin: 0px; }
    div[data-testid="metric-container"] label { font-size: 0.6rem; margin-bottom: 0px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 0.9rem; }
    div[data-testid="stTextInput"] { margin-bottom: 0px; }
</style>
""", unsafe_allow_html=True)

# --- 4. CABEÇALHO ---
st.markdown(f"""
<div class="header-box">
    <div style="font-size: 20px;">🚛</div>
    <div>
        <div class="header-title">Minha Escala</div>
        <div class="header-date">{dia_sem}, {data_hoje}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith('xlsx'):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try: df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except: df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        header_idx = -1
        for index, row in df_raw.iterrows():
            txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in txt and "vpn" in txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, df.columns.notna()]
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        return None
    except: return None

# Carrega arquivo
df = None
nome = "rotas.csv.xlsx"
if os.path.exists(nome):
    try:
        with open(nome, "rb") as f:
            from io import BytesIO
            mem = BytesIO(f.read())
            mem.name = nome
            df = carregar_dados(mem)
    except: pass

# Admin
with st.sidebar:
    st.header("Gestão")
    if st.text_input("Senha", type="password") == "admin123":
        up = st.file_uploader("Upload", type=['xlsx', 'csv'])
        if up:
            novo = carregar_dados(up)
            if novo is not None:
                df = novo
                st.success("Atualizado!")

# --- 6. TELA MOTORISTA ---
if df is not None:
    with st.form(key='busca'):
        vpn = st.text_input("vpn", label_visibility="collapsed", placeholder="Digite a VPN...")
        btn = st.form_submit_button("🔍 VER ROTA", type="primary")

    if btn:
        vpn = vpn.strip()
        if vpn:
            res = df[df['VPN'] == vpn]
            if not res.empty:
                row = res.iloc[0]
                
                # --- MUDANÇA AQUI: NOME DO MOTORISTA EM DESTAQUE ---
                # Fundo Azul Escuro, Texto Branco, Letra Maior (1.1rem)
                st.markdown(f"""
                <div style='background-color: #004aad; color: white; padding: 8px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                    👤 {row.get('Motorista', '-')}
                </div>
                """, unsafe_allow_html=True)
                
                # Veículo
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MATR", str(row.get('Matrícula', '-')))
                c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                c3.metric("ROTA", str(row.get('ROTA', '-')))
                c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                # Horários
                local_descarga = str(row.get('Local descarga', 'Loja')).upper()
                
                cc, cd = st.columns(2)
                
                # Bloco CHEGADA
                with cc:
                    st.markdown(f"""
                    <div class="time-block" style="border-left-color: #0d47a1;">
                        <div class="time-label">CHEGADA</div>
                        <div class="time-value">{row.get('Hora chegada Azambuja', '--')}</div>
                        <div class="location-highlight text-blue">AZAM
