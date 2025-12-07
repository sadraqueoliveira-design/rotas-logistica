import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="App Rotas",
    page_icon="https://img.icons8.com/ios-filled/50/4a90e2/truck.png",
    layout="centered"
)

# --- 2. ESTILO VISUAL (CSS) ---
st.markdown("""
<style>
    /* Esconde menus do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove espaço extra do topo */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    
    /* ESTILO DA BARRA AZUL */
    .app-header {
        background-color: #004aad;
        padding: 15px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-top: -6rem; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .app-header img {
        width: 45px;
        height: auto;
    }
    
    .app-header-text {
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Cartões */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BARRA DE TÍTULO ---
st.markdown("""
<div class="app-header">
    <img src="https://img.icons8.com/ios-filled/100/ffffff/truck.png">
    <div class="app-header-text">Minha Escala</div>
</div>
""", unsafe_allow_html=True)

# --- 4. FUNÇÃO DE LEITURA (SIMPLIFICADA) ---
def carregar_dados(uploaded_file):
    try:
        # Verifica extensão e lê o arquivo
        if uploaded_file.name.lower().endswith('xlsx'):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            # Tenta CSV de várias formas
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        # Busca cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        # Ajusta colunas
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df =
