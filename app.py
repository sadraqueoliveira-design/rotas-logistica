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

data_hoje = agora.strftime("%d/%m/%Y")
dias = {0:"Segunda", 1:"Terça", 2:"Quarta", 3:"Quinta", 4:"Sexta", 5:"Sábado", 6:"Domingo"}
dia_sem = dias[agora.weekday()]

# --- 3. ESTILO (CSS OTIMIZADO PARA CELULAR) ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem;}
    
    /* Cabeçalho Compacto */
    .header-box {
        background-color: #004aad;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    .header-title { font-size: 18px; font-weight: bold; margin: 0; }
    .header-date { font-size: 12px; opacity: 0.9; }
    
    /* Blocos de Horário */
    .time-block {
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 6px;
        border-left: 4px solid #004aad;
        margin-bottom: 5px;
    }
    .time-label { font-size: 0.65rem; color: #666; font-weight: bold; text-transform: uppercase; }
    .time-value { font-size: 1.2rem; font-weight: bold; color: #333; margin: 0px 0; }
    .location-highlight { font-size: 0.9rem; color: #d32f2f; font-weight: 900; text-transform: uppercase; }
    
    /*
