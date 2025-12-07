import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="App Rotas", page_icon="https://img.icons8.com/ios-filled/50/4a90e2/truck.png", layout="centered")

# --- ESTILO VISUAL (CSS) ---
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
    
    /* ESTILO DA BARRA AZUL COM IMAGEM */
    .app-header {
        background-color: #004aad; /* Azul Logística */
        padding: 15px;
        color: white;
        /* Configuração Flex para alinhar imagem e texto */
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px; /* Espaço entre a imagem e o texto */
        
        /* Ajustes de margem para cobrir o topo */
        margin-left: -5rem;
        margin-right: -5rem;
        margin-top: -6rem; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Estilo da Imagem do Camião */
    .app-header img {
        width: 45px; /* Tamanho da imagem */
        height: auto;
    }
    
    /* Estilo do Texto do Título */
    .app-header-text {
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Estilo dos Cartões de Informação (Fundo branco) */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA DE TÍTULO COM IMAGEM ---
st.markdown("""
<div class="app-header">
    <img src="https://img.icons8.com/ios-filled/100/ffffff/truck.png" alt="Camião">
    <div class="app-header-text">Minha Escala</div>
</div>
""", unsafe_allow_html=True)


# --- 1. FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        # Verifica extensão
        if uploaded_file.name.lower().endswith('xlsx'):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            # Tenta CSV com ponto e vírgula
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                # Tenta CSV com vírgula (fallback)
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        # Procura a linha de cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        # Ajusta o DataFrame
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()]
        
        # Limpeza da VPN
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        return None
    except:
        return None

# --- 2. CARREGAR ARQUIVO AUTOMÁTICO ---
df = None
nome_arquivo_oficial = "rotas.csv.xlsx"

try:
    if os.path.exists(nome_arquivo_oficial):
        with open(nome_arquivo_oficial,
