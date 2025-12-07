import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz # Biblioteca de fuso horário (se disponível no streamlit cloud)

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="App Rotas",
    page_icon="https://img.icons8.com/ios-filled/50/4a90e2/truck.png",
    layout="centered"
)

# --- 2. DATA EM PORTUGUÊS (Blindada) ---
try:
    # Tenta pegar fuso horário de Portugal/Lisboa
    fuso = pytz.timezone('Europe/Lisbon')
    agora = datetime.now(fuso)
except:
    # Se der erro, usa horário padrão
    agora = datetime.now()

data_hoje = agora.strftime("%d/%m/%Y")
dias = {0:"Segunda", 1:"Terça", 2:"Quarta", 3:"Quinta", 4:"Sexta", 5:"Sábado", 6:"Domingo"}
dia_sem = dias[agora.weekday()]
texto_data = f"{dia_sem}, {data_hoje}"

# --- 3. ESTILO (CSS) ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding-top: 0rem; padding-bottom: 0rem;}
    
    /* Configuração da Barra Azul Fixa */
    .app-header {
        background-color: #004aad;
        padding: 15px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-left: -5rem; margin-right: -5rem; margin-top: -6rem; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Input e Botões */
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        padding: 10px; border-radius: 8px; box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 4. CABEÇALHO (HTML DIRETO - O SEGREDO ESTÁ AQUI) ---
# Usamos style="" direto na div para garantir que apareça
st.markdown(f"""
<div class="app-header">
    <img src="https://img.icons8.com/ios-filled/100/ffffff/truck.png" style="width: 50px; height: auto;">
    <div style="display: flex; flex-direction: column; align-items: flex-start;">
        <span style="font-size: 22px; font-weight: bold; line-height: 1.2;">Minha Escala</span>
        <span style="font-size: 14px; opacity: 0.9; font-weight: normal;">📅 {texto_data}</span>
    </div>
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

# Carregamento
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

# --- 6. TELA DO MOTORISTA ---
if df is not None:
    st.write("") 
    with st.form(key='busca'):
        st.markdown("**Digite sua VPN:**")
        vpn = st.text_input("vpn", label_visibility="collapsed", placeholder="Ex: 76628")
        btn = st.form_submit_button("🔍 BUSCAR MINHA ROTA", type="primary")

    if btn:
        vpn = vpn.strip()
        if vpn:
            res = df[df['VPN'] == vpn]
            if not res.empty:
                row = res.iloc[0]
                
                st.info(f"👤 **{row.get('Motorista', '-') }**")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MATRÍCULA", str(row.get('Matrícula', '-')))
                c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                c3.metric("ROTA", str(row.get('ROTA', '-')))
                c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                st.markdown("---")
                
                cc, cd = st.columns(2)
                cc.markdown(f"**🕒 Chegada**\n## {row.get('Hora chegada Azambuja', '--')}")
                cd.markdown(f"**📦 Descarga**\n## {row.get('Hora descarga loja', '--')}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                cr, ct = st.columns(2)
                cr.error(f"🔙 **Retorno:** {row.get('Retorno', '--')}")
                ct.success(f"📋 **Tipo:** {row.get('TIPO', '-')}")

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
