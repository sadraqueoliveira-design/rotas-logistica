import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Logística App", 
    page_icon="🚛", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# ADMINS
ADMINS = {
    "Admin Principal": "admin123",
    "Gestor Tráfego": "trafego2025",
    "Escritório": "office99",
}

# ARQUIVOS
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"

# --- 2. ESTILO CSS (CORRIGIDO PARA O CABEÇALHO) ---
st.markdown("""
<style>
    /* 1. Remove espaços em branco do topo da página do Streamlit */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* 2. Esconde menu padrão e rodapé */
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;} 
    footer {visibility: hidden;}
    
    /* 3. Estilo do Cabeçalho (Header Box) */
    .header-box {
        background-color: #004aad; /* Azul Sólido */
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        color: white;
        margin-bottom: 25px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border: 2px solid #003380;
    }
    .header-title { 
        font-size: 28px !important; 
        font-weight: 900 !important; 
        margin: 0 !important; 
        line-height: 1.2 !important; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }
    .header-date { 
        font-size: 22px !important; 
        font-weight: bold !important; 
        color: #FFD700 !important; /* Amarelo */
        margin-top: 8px !important; 
    }
    
    /* 4. Estilo dos Cartões */
    .driver-card {
        background-color: #004aad; color: white; padding: 10px; border-radius: 8px;
        text-align: center; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px;
    }
    .vehicle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
    .vehicle-item { background-color: #e3f2fd; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #bbdefb; }
    .vehicle-label { font-size: 10px; color: #555; text-transform: uppercase; font-weight: bold; margin-bottom: 0;}
    .vehicle-val { font-size: 14px; font-weight: bold; color: #004aad; line-height: 1.1;}
    
    .time-block {
        background-color: #f8f9fa; padding: 10px; border-radius: 8px;
        border-left: 6px solid #004aad; margin-bottom: 5px;
    }
    .time-label { font-size: 0.75rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.6rem; font-weight: bold; color: #333; margin: 0; line-height: 1; }
    .location-highlight { font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-top: 2px;}
    .text-blue { color: #0d47a1; } .text-red { color: #d32f2f; }
    
    .info-row { display: flex; justify-content: space-between; gap: 6px; margin-top: 15px; margin-bottom: 15px; }
    .info-item { flex: 1; text-align: center; padding: 6px 2px; border-radius: 6px; color: white; font-size: 0.9rem;}
    .info-item-retorno { flex: 1; text-align: center; padding: 5px 2px; border-radius: 6px; background-color: white; border: 1px solid #ddd; }
    
    .info-label { font-size: 0.65rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 2px; line-height: 1;}
    .info-label-dark { font-size: 0.65rem; text-transform: uppercase; color: #666; display: block; margin-bottom: 2px; line-height: 1; font-weight: bold;}
    .info-val { font-size: 1.1rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; } .bg-green { background-color: #388e3c; }
    .rota-separator { text-align: center; margin: 30px 0 15px 0; font-size: 1rem; font-weight: bold; color: #004aad; background-color: #e3f2fd; padding: 8px; border-radius: 6px; border: 1px dashed #004aad;}
    
    /* Tabela de Carga */
    .carga-box { background-color: #fff; border: 1px solid #eee; border-radius: 8px; padding: 10px; margin-top: 10px; }
    .carga-title { font-size: 0.8rem; font-weight: bold; color: #444; margin-bottom: 5px; text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    
    button[kind="primary"] { width: 100%; border-radius: 8px; height: 50px; font-weight: bold; font-size: 18px !important;}
</style>
""", unsafe_allow_html=True
