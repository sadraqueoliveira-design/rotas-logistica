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
    
    /* Locais em Destaque (AZAMBUJA e LOJA) */
    .location-highlight { font-size: 0.8rem; font-weight: 900; text-transform: uppercase; margin: 0;}
    .text-blue { color: #0d47a1; } /* Cor para Azambuja */
    .text-red { color: #d32f2f; }  /* Cor para Loja */
    
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
    div[data-testid="stTextInput"] { margin-bottom: 0
