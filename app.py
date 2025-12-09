import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Logística App",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="expanded" # Menu sempre aberto
)

# 2. CSS (ESTILO) - Numa linha única para evitar erros de cópia
st.markdown('<style>.block-container{padding-top:1rem!important}.header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}.driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}.vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}.vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}.vehicle-val{font-size:14px;font-weight:bold;color:#004aad}.time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}.carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}.info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}.info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}button[kind="primary"]{width:100%;height:50px;font-size:18px!important}thead tr th:first-child{display:none}tbody th{display:none}</style>', unsafe_allow_html=True)

# 3. FUNÇÃO DE LEITURA INTELIGENTE
def ler_rotas(file_content):
    try:
        # A. Tenta ler o arquivo bruto (sem cabeçalho definido)
        try: df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            try: df_raw = pd.read_csv(file_content, header=None, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try: df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='latin1')
                except: return None

        # B. Procura onde está o cabeçalho real (Motorista e VPN)
        header_idx = -1
        # Analisa as primeiras 10 linhas
        for i, row in df_raw.head(10).iterrows():
            # Converte a linha toda para texto minúsculo
            linha_txt = row.astype(str).str.lower().str.cat(sep=' ')
            if 'motorista' in linha_txt and 'vpn' in linha_txt:
                header_idx = i
                break
        
        if header_idx == -1:
            st.error("Não encontrei as colunas 'Motorista' e 'VPN'.")
            return None

        # C. Define o cabeçalho correto
        df_raw.columns = df_raw.iloc[header_idx]
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)

        # D. Limpeza e Correção de Nomes
        df.columns = df.columns.astype(str).str.strip() # Remove espaços extras
        
        mapa = {
            'Matricula': 'Matrícula', 'Movél': 'Móvel', 
            'NºLOJA': 'Nº LOJA', 'Motorista ': 'Motorista',
            'Talho': 'Carne'
        }
        for real in df.columns:
            for k, v in mapa.items():
                if k.lower() in real.lower():
                    df.rename(columns={real: v}, inplace=True)

        # E. Filtra linhas vazias
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Garante que Motorista existe
            col_mot = next((c for c in df.columns if 'motorista' in c.lower()), None)
            if col_mot:
                df = df[df[col_mot].notna()]

        return df
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return None

# --- VARIÁVEIS ---
DB_FILE = "dados_rotas.source" 
DATE_FILE = "
