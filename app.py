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
    
    /* Locais em Destaque */
    .location-highlight { font-size: 0.8rem; font-weight: 900; text-transform: uppercase; margin: 0;}
    .text-blue { color: #0d47a1; } 
    .text-red { color: #d32f2f; }
    
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
    
    /* Estilo Especial para o Retorno (Fundo Branco + Borda) */
    .info-item-retorno {
        flex: 1;
        text-align: center;
        padding: 2px 2px;
        border-radius: 4px;
        background-color: white;
        border: 1px solid #ddd;
    }
    
    .info-label { font-size: 0.5rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 0px; line-height: 1;}
    .info-label-dark { font-size: 0.5rem; text-transform: uppercase; color: #666; display: block; margin-bottom: 0px; line-height: 1; font-weight: bold;}
    
    .info-val { font-size: 0.9rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; }
    .bg-green { background-color: #388e3c; }

    /* Separador */
    .rota-separator {
        text-align: center;
        margin: 15px 0 5px 0;
        font-size: 0.8rem;
        font-weight: bold;
        color: #004aad;
        background-color: #e3f2fd;
        padding: 4px;
        border-radius: 4px;
    }

    div[data-testid="metric-container"] { padding: 4px; margin: 0px; }
    div[data-testid="metric-container"] label { font-size: 0.6rem; margin-bottom: 0px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 0.9rem; }
    div[data-testid="stTextInput"] { margin-bottom: 0px; }
</style>
""", unsafe_allow_html=True)

# --- 4. CABEÇALHO ---
st.markdown(f"""
<div class="header-box">
    <div style="font-size: 20px;">🚛</div>
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
        vpn = st.text_input("vpn", label_visibility="collapsed", placeholder="Digite a VPN...")
        btn = st.form_submit_button("🔍 VER ROTAS", type="primary")

    if btn:
        vpn = vpn.strip()
        if vpn:
            res = df[df['VPN'] == vpn]
            
            if not res.empty:
                total_rotas = len(res)
                
                for i, (index, row) in enumerate(res.iterrows()):
                    numero_rota = i + 1
                    
                    if total_rotas > 1:
                         st.markdown(f"<div class='rota-separator'>📍 VIAGEM {numero_rota}</div>", unsafe_allow_html=True)
                    
                    # MOTORISTA
                    st.markdown(f"""
                    <div style='background-color: #004aad; color: white; padding: 6px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 1.0rem; margin-bottom: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);'>
                        👤 {row.get('Motorista', '-')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Veículo
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("MATR", str(row.get('Matrícula', '-')))
                    c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                    c3.metric("ROTA", str(row.get('ROTA', '-')))
                    c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                    
                    # Horários
                    local_descarga = str(row.get('Local descarga', 'Loja')).upper()
                    
                    cc, cd = st.columns(2)
                    
                    with cc:
                        st.markdown(f"""
                        <div class="time-block" style="border-left-color: #0d47a1;">
                            <div class="time-label">CHEGADA</div>
                            <div class="time-value">{row.get('Hora chegada Azambuja', '--')}</div>
                            <div class="location-highlight text-blue">AZAMBUJA</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with cd:
                        st.markdown(f"""
                        <div class="time-block" style="border-left-color: #d32f2f;">
                            <div class="time-label">DESCARGA</div>
                            <div class="time-value">{row.get('Hora descarga loja', '--')}</div>
                            <div class="location-highlight text-red">{local_descarga}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # --- BARRA FINA (RETORNO VERDE) ---
                    val_suportes = '0'
                    for col in df.columns:
                        if "total suportes" in col.lower():
                            val_suportes = str(row.get(col, '0'))
                            break
                    
                    val_retorno = str(row.get('Retorno', '-'))
                    
                    # LÓGICA DE COR AJUSTADA:
                    # Adicionei '○', 'o', 'O' à lista de ignorados para ficarem PRETO/CINZA.
                    cor_texto_retorno = "#333333" 
                    if val_retorno not in ['0', '-', 'nan', 'Vazio', 'None', '○', 'o', 'O']:
                        cor_texto_retorno = "#008000" # VERDE
                    
                    st.markdown(f"""
                    <div class="info-row">
                        <div class="info-item bg-purple">
                            <span class="info-label">SUPORTES</span>
                            <span class="info-val">📦 {val_suportes}</span>
                        </div>
                        
                        <div class="info-item-retorno">
                            <span class="info-label-dark">RETORNO</span>
                            <span class="info-val" style="color: {cor_texto_retorno}; font-size: 1.0rem;">
                                {val_retorno}
                            </span>
                        </div>
                        
                        <div class="info-item bg-green">
                            <span class="info-label">TIPO</span>
                            <span class="info-val">{row.get('TIPO', '-')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Carga
                    with st.expander(f"🔎 Carga Viagem {numero_rota}", expanded=False):
                        cols = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", 
                                "Frota Refrigerado", "Peixe", "Talho"]
                        dd = {"Cat": [], "Qtd": []}
                        for col_name in cols:
                            col_match = next((c for c in df.columns if col_name.lower() in c.lower()), None)
                            if col_match:
                                v = str(row.get(col_match, '0'))
                                if v != '0' and v.lower() != 'nan':
                                    dd["Cat"].append(col_name.replace("Azambuja ", "").replace("Total ", ""))
                                    dd["Qtd"].append(v)
                                    
                        if dd["Cat"]: st.table(pd.DataFrame(dd).set_index("Cat"))
                        else: st.caption("Sem carga especial.")
                    
                    if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                         st.info(f"📱 {row['WhatsApp']}")
                         
            else: st.error("❌ VPN não encontrada.")
        else: st.warning("Digite a VPN.")
else:
    st.warning("⚠️ Aguardando arquivo.")
