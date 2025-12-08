import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS ---
st.markdown("""
<style>
    .block-container{padding-top:1rem!important}
    .header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}
    .driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}
    .vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
    .vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}
    .vehicle-val{font-size:14px;font-weight:bold;color:#004aad}
    .time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}
    .carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}
    .info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}
    .info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE LEITURA ---
def ler_rotas(file_content):
    try:
        df = pd.read_excel(file_content, header=0)

        # Força coluna C como VPN
        col_vpn = df.columns[2]
        df.rename(columns={col_vpn: "VPN"}, inplace=True)

        # Normaliza VPN
        df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).strip()

        return df
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return None

# --- VARIÁVEIS ---
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"

# --- DATA ---
if os.path.exists(DATE_FILE):
    with open(DATE_FILE, "r") as f: 
        dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
else:
    dt = datetime.now()

# --- CARREGAR BASE ---
df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        df_rotas = ler_rotas(BytesIO(f.read()))

# --- MENU ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")

# --- ESCALA ---
if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    if df_rotas is None:
        st.warning("Nenhum arquivo carregado. Vá em Gestão.")
    else:
        with st.form("busca"):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 12345", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")

        if btn and vpn:
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]

            if res.empty:
                st.error("VPN não encontrado.")
            else:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    st.markdown(f'<div class="driver-card">👤 {row["Motorista"]}</div>', unsafe_allow_html=True)

                    # Veículos
                    st.markdown(f'''
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{row.get('Matrícula', '-')}</div></div>
                        <div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{row.get('Móvel', '-')}</div></div>
                        <div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{row.get('ROTA', '-')}</div></div>
                        <div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{row.get('Nº LOJA', '-')}</div></div>
                    </div>
                    ''', unsafe_allow_html=True)

# --- GESTÃO ---
elif menu == "Gestão":
    st.header("Gestão")

    senha = st.text_input("Senha", type="password")
    if senha == "123":
        data_nova = st.date_input("Data", value=dt)

        if st.button("Salvar Data"):
            with open(DATE_FILE, "w") as f:
                f.write(str(data_nova))
            st.success("Data salva!")

        up = st.file_uploader("Enviar arquivo de rotas", type=["xlsx", "csv"])
        if up:
            df = ler_rotas(up)
            if df is not None:
                st.write(df.head())
                if st.button("Gravar Base"):
                    with open(DB_FILE, "wb") as f:
                        f.write(up.getbuffer())
                    st.success("Base atualizada!")

    elif senha:
        st.error("Senha incorreta.")
