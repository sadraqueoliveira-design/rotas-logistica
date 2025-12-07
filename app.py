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

# --- 3. ESTILO (CSS) ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    .header-box {
        background-color: #004aad;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .header-title { font-size: 24px; font-weight: bold; margin: 0; }
    .header-date { font-size: 16px; opacity: 0.9; margin-top: 5px; }
    
    /* Estilo para os blocos de horário ficarem mais cheios */
    .time-block {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #004aad;
        margin-bottom: 10px;
    }
    .time-label { font-size: 0.9rem; color: #666; font-weight: bold; text-transform: uppercase; }
    .time-value { font-size: 1.8rem; font-weight: bold; color: #333; margin: 5px 0; }
    .time-location { font-size: 1.1rem; color: #004aad; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. CABEÇALHO ---
st.markdown(f"""
<div class="header-box">
    <div style="font-size: 40px;">🚛</div>
    <div class="header-title">Minha Escala</div>
    <div class="header-date">📅 {dia_sem}, {data_hoje}</div>
</div>
""", unsafe_allow_html=True)

# --- 5. FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith('xlsx'):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try: df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except: df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        header_idx = -1
        for index, row in df_raw.iterrows():
            txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in txt and "vpn" in txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()]
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        return None
    except: return None

# Carrega arquivo
df = None
nome = "rotas.csv.xlsx"
if os.path.exists(nome):
    try:
        with open(nome, "rb") as f:
            from io import BytesIO
            mem = BytesIO(f.read())
            mem.name = nome
            df = carregar_dados(mem)
    except: pass

# Admin
with st.sidebar:
    st.header("Gestão")
    if st.text_input("Senha", type="password") == "admin123":
        up = st.file_uploader("Upload", type=['xlsx', 'csv'])
        if up:
            novo = carregar_dados(up)
            if novo is not None:
                df = novo
                st.success("Atualizado!")

# --- 6. TELA MOTORISTA ---
if df is not None:
    with st.form(key='busca'):
        st.markdown("**Digite sua VPN:**")
        vpn = st.text_input("vpn", label_visibility="collapsed", placeholder="Ex: 76628")
        btn = st.form_submit_button("🔍 BUSCAR ROTA", type="primary")

    if btn:
        vpn = vpn.strip()
        if vpn:
            res = df[df['VPN'] == vpn]
            if not res.empty:
                row = res.iloc[0]
                
                st.info(f"👤 **{row.get('Motorista', '-') }**")
                
                # Info Geral
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MATRÍCULA", str(row.get('Matrícula', '-')))
                c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                c3.metric("ROTA", str(row.get('ROTA', '-')))
                c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                st.markdown("---")
                
                # --- HORÁRIOS COM LOCAIS (AQUI MUDOU) ---
                # Pegamos o local de descarga para exibir junto da hora
                local_descarga = row.get('Local descarga', 'Loja')
                
                cc, cd = st.columns(2)
                
                with cc:
                    # Bloco Chegada
                    st.markdown(f"""
                    <div class="time-block" style="border-left-color: #0d47a1;">
                        <div class="time-label">CHEGADA</div>
                        <div class="time-value">{row.get('Hora chegada Azambuja', '--')}</div>
                        <div class="time-location">📍 Azambuja</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cd:
                    # Bloco Descarga
                    st.markdown(f"""
                    <div class="time-block" style="border-left-color: #e65100;">
                        <div class="time-label">DESCARGA</div>
                        <div class="time-value">{row.get('Hora descarga loja', '--')}</div>
                        <div class="time-location">📍 {local_descarga}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Retorno e Tipo
                cr, ct = st.columns(2)
                cr.error(f"🔙 **Retorno:** {row.get('Retorno', '--')}")
                ct.success(f"📋 **Tipo:** {row.get('TIPO', '-')}")

                # Carga
                with st.expander("📦 Ver Carga", expanded=True):
                    cols = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", 
                            "Frota Refrigerado", "Peixe", "Talho", "Total Suportes"]
                    dd = {"Cat": [], "Qtd": []}
                    for i in cols:
                        v = str(row.get(i, '0'))
                        if v != '0' and v.lower() != 'nan':
                            dd["Cat"].append(i.replace("Azambuja ", "").replace("Total ", ""))
                            dd["Qtd"].append(v)
                    if dd["Cat"]: st.table(pd.DataFrame(dd).set_index("Cat"))
                    else: st.caption("Sem carga especial.")
                
                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 Obs: {row['WhatsApp']}")
            else: st.error("❌ VPN não encontrada.")
        else: st.warning("Digite a VPN.")
else:
    st.warning("⚠️ Aguardando arquivo.")
