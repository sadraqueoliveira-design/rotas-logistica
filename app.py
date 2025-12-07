import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz # Para o fuso horário

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="App Rotas",
    page_icon="🚛",
    layout="centered"
)

# --- 2. DATA (Configurada para Portugal) ---
try:
    fuso = pytz.timezone('Europe/Lisbon')
    agora = datetime.now(fuso)
except:
    agora = datetime.now() # Se der erro, usa hora do servidor

data_hoje = agora.strftime("%d/%m/%Y")
dias = {0:"Segunda", 1:"Terça", 2:"Quarta", 3:"Quinta", 4:"Sexta", 5:"Sábado", 6:"Domingo"}
dia_sem = dias[agora.weekday()]

# --- 3. ESTILO (CSS SIMPLIFICADO) ---
# Aqui estava o problema. Removi as margens negativas exageradas.
st.markdown("""
<style>
    /* Esconde menu padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove espaço extra do topo do Streamlit */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* BARRA AZUL (SIMPLES E SEGURA) */
    .header-box {
        background-color: #004aad;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Estilo do Texto */
    .header-title {
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }
    .header-date {
        font-size: 16px;
        opacity: 0.9;
        margin-top: 5px;
    }
    
    /* Inputs e Cartões */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 4. EXIBIR CABEÇALHO ---
st.markdown(f"""
<div class="header-box">
    <div style="font-size: 40px;">🚛</div>
    <div class="header-title">Minha Escala</div>
    <div class="header-date">📅 {dia_sem}, {data_hoje}</div>
</div>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE DADOS ---
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
    # FORMULÁRIO DE BUSCA
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
                
                # Nome
                st.info(f"👤 **{row.get('Motorista', '-') }**")
                
                # Info Principal
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MATRÍCULA", str(row.get('Matrícula', '-')))
                c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                c3.metric("ROTA", str(row.get('ROTA', '-')))
                c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                st.markdown("---")
                
                # Horários
                cc, cd = st.columns(2)
                cc.markdown(f"**🕒 Chegada**\n## {row.get('Hora chegada Azambuja', '--')}")
                cd.markdown(f"**📦 Descarga**\n## {row.get('Hora descarga loja', '--')}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Etiquetas
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
                    st.caption(f"📍 Local: {row.get('Local descarga', '-')}")
                
                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 Obs: {row['WhatsApp']}")
            else: st.error("❌ VPN não encontrada.")
        else: st.warning("Digite a VPN.")
else:
    st.warning("⚠️ Aguardando arquivo.")
