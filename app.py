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

# --- 3. ESTILO (CSS OTIMIZADO) ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 0.5rem; padding-bottom: 0rem;}
    
    /* Cabeçalho */
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
    
    /* Horários */
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
    
    /* BARRA HORIZONTAL COMPACTA */
    .info-row {
        display: flex;
        justify-content: space-between;
        gap: 5px;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    .info-item {
        flex: 1;
        text-align: center;
        padding: 5px;
        border-radius: 5px;
        color: white;
    }
    .info-label { font-size: 0.6rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 2px; }
    .info-val { font-size: 1.0rem; font-weight: bold; line-height: 1; }
    
    .bg-purple { background-color: #7b1fa2; }
    .bg-orange { background-color: #f57c00; }
    .bg-green { background-color: #388e3c; }

    /* Ajustes Gerais */
    div[data-testid="stTextInput"] input { padding: 8px; font-size: 16px; }
    div[data-testid="metric-container"] { padding: 5px; }
    div[data-testid="metric-container"] label { font-size: 0.7rem; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 1.0rem; }
</style>
""", unsafe_allow_html=True)

# --- 4. CABEÇALHO ---
st.markdown(f"""
<div class="header-box">
    <div style="font-size: 24px;">🚛</div>
    <div>
        <div class="header-title">Minha Escala</div>
        <div class="header-date">{dia_sem}, {data_hoje}</div>
    </div>
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
        df.columns = df.columns.astype(str).str.strip()
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
        vpn = st.text_input("vpn", label_visibility="collapsed", placeholder="Digite a VPN aqui...")
        btn = st.form_submit_button("🔍 VER ROTA", type="primary")

    if btn:
        vpn = vpn.strip()
        if vpn:
            res = df[df['VPN'] == vpn]
            if not res.empty:
                row = res.iloc[0]
                
                # Motorista
                st.markdown(f"<div style='background:#eee; padding:5px; border-radius:5px; text-align:center; font-weight:bold; margin-bottom:5px;'>👤 {row.get('Motorista', '-')}</div>", unsafe_allow_html=True)
                
                # Veículo
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MATRÍCULA", str(row.get('Matrícula', '-')))
                c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                c3.metric("ROTA", str(row.get('ROTA', '-')))
                c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                # Horários
                local_descarga = str(row.get('Local descarga', 'Loja')).upper()
                cc, cd = st.columns(2)
                with cc:
                    st.markdown(f"""
                    <div class="time-block" style="border-left-color: #0d47a1;">
                        <div class="time-label">CHEGADA AZB</div>
                        <div class="time-value">{row.get('Hora chegada Azambuja', '--')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cd:
                    st.markdown(f"""
                    <div class="time-block" style="border-left-color: #d32f2f;">
                        <div class="time-label">DESCARGA</div>
                        <div class="time-value">{row.get('Hora descarga loja', '--')}</div>
                        <div class="location-highlight">{local_descarga}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # BARRA COMPACTA
                val_suportes = '0'
                for col in df.columns:
                    if "total suportes" in col.lower():
                        val_suportes = str(row.get(col, '0'))
                        break
                
                st.markdown(f"""
                <div class="info-row">
                    <div class="info-item bg-purple">
                        <span class="info-label">SUPORTES</span>
                        <span class="info-val">📦 {val_suportes}</span>
                    </div>
                    <div class="info-item bg-orange">
                        <span class="info-label">RETORNO</span>
                        <span class="info-val">🔙 {row.get('Retorno', '-')}</span>
                    </div>
                    <div class="info-item bg-green">
                        <span class="info-label">TIPO</span>
                        <span class="info-val">📋 {row.get('TIPO', '-')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Carga
                with st.expander("🔎 Ver Carga", expanded=False):
                    cols = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", 
                            "Frota Refrigerado", "Peixe", "Talho"]
                    dd = {"Cat": [], "Qtd": []}
                    for i in cols:
                        col_match = next((c for c in df.columns if i.lower() in c.lower()), None)
                        if col_match:
                            v = str(row.get(col_match, '0'))
                            if v != '0' and v.lower() != 'nan':
                                dd["Cat"].append(i.replace("Azambuja ", "").replace("Total ", ""))
                                dd["Qtd"].append(v)
                                
                    if dd["Cat"]: st.table(pd.DataFrame(dd).set_index("Cat"))
                    else: st.caption("Sem carga especial.")
                
                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 {row['WhatsApp']}")
            else: st.error("❌ VPN não encontrada.")
        else: st.warning("Digite a VPN.")
else:
    st.warning("⚠️ Aguardando arquivo.")
