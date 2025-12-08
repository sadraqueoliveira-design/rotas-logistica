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

# --- 2. ESTILO CSS ---
CSS_STYLE = """
<style>
    .block-container {padding-top: 1rem !important; padding-bottom: 5rem !important;}
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;} 
    footer {visibility: hidden;}
    
    .header-box {
        background-color: #004aad;
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        color: white;
        margin-bottom: 25px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border: 2px solid #003380;
    }
    .header-title { 
        font-size: 28px !important; font-weight: 900 !important; 
        margin: 0 !important; line-height: 1.2 !important; 
        text-transform: uppercase; letter-spacing: 1px;
    }
    .header-date { 
        font-size: 22px !important; font-weight: bold !important; 
        color: #FFD700 !important; margin-top
