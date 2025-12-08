import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS (simples) ---
st.markdown("""
<style>
    .block-container{padding-top:1rem!important}
    .header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}
    .driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.1rem;margin-bottom:10px}
    .vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
    .vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}
    .vehicle-val{font-size:14px;font-weight:bold;color:#004aad}
    .time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}
    .carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}
    .info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}
    .info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}
</style>
""", unsafe_allow_html=True)


# --- UTIL: detectar assinatura do ficheiro ---
def detect_file_signature(file_like):
    """
    Lê os primeiros bytes para ajudar a detectar o tipo real do ficheiro.
    Retorna os primeiros 4 bytes (bytes object) ou b'' em erro.
    """
    try:
        # file_like pode ser UploadedFile (tem .seek/.read) ou bytes
        file_like.seek(0)
        hdr = file_like.read(4)
        file_like.seek(0)
        return hdr
    except Exception:
        try:
            # talvez seja bytes
            buf = BytesIO(file_like)
            hdr = buf.read(4)
            return hdr
        except Exception:
            return b''


# --- FUNÇÃO ROBUSTA DE LEITURA ---
def ler_rotas(file_content):
    """
    file_content: file-like object (UploadedFile) or bytes buffer.
    Tenta vários motores para Excel e CSV.
    Retorna DataFrame ou None e mostra mensagens via st.error.
    """
    tried = []
    try:
        # Se for UploadedFile (do Streamlit) ele é file-like com .name
