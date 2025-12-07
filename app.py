import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Folha de Serviço", page_icon="🚛", layout="centered")

# --- CSS PARA AJUSTES VISUAIS ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    /* Deixa as caixas de alerta (info/warning/error) com altura padrão */
    div[data-testid="stAlert"] {
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 Folha de Serviço Digital")

# --- FUNÇÃO DE LEITURA (MANTIDA) ---
def carregar_dados(uploaded_file):
    try:
        nome_arquivo = uploaded_file.name.lower()
        df_raw = None
        
        if nome_arquivo.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')
        
        if df_raw is None:
            return None, "Erro na leitura."

        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1:
            return None, "Não encontrei a linha de cabeçalho (Motorista/VPN)."

        df
