import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz 

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered")

# ==========================================
# 🔐 ADMINS
# ==========================================
ADMINS = {
    "Admin Principal": "admin123",
    "Gestor Tráfego": "trafego2025",
    "Escritório": "office99",
}

# --- 2. ESTILO CSS (VISUAL LIMPO E FUNCIONAL) ---
st.markdown("""
<style>
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;}
    footer {visibility: hidden;}
    
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    
    /* Menu Lateral */
    section[data-testid="stSidebar"] { background-color: #f0f2f6; }
    
    /* CABEÇALHO */
    .header-box {
        background: linear-gradient(135deg, #004aad 0%, #003380 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .header-title { 
        font-size: 26px; font-weight: 900; margin: 0; line-height: 1.1; 
        text-transform: uppercase; letter-spacing: 1px;
    }
    .header-date { 
        font-size: 20px; font-weight: bold; color: #FFD700; 
        margin-top: 5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Blocos de Horário */
    .time-block {
        background-color: #f8f9fa; padding: 8px; border-radius: 6px;
        border-left: 4px solid #004aad; margin-bottom: 5px;
    }
    .time-label { font-size: 0.7rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.3rem; font-weight: bold; color: #333; margin: 2px 0; line-height: 1.1; }
    .location-highlight { font-size: 0.9rem; font-weight: 900; text-transform: uppercase; margin: 0;}
    .text-blue { color: #0d47a1; } .text-red { color: #d32f2f; }
    
    /* Barra Fina */
    .info-row { display: flex; justify-content: space-between; gap: 4px; margin-top: 8px; margin-bottom: 8px; }
    .info-item { flex: 1; text-align: center; padding: 4px 2px; border-radius: 4px; color: white; }
    .info-item-retorno { flex: 1; text-align: center; padding: 3px 2px; border-radius: 4px; background-color: white; border: 1px solid #ddd; }
    .info-label { font-size: 0.6rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 0px; line-height: 1;}
    .info-label-dark { font-size: 0.6rem; text-transform: uppercase; color: #666; display: block; margin-bottom: 0px; line-height: 1; font-weight: bold;}
    .info-val { font-size: 1.0rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; } .bg-green { background-color: #388e3c; }
    .rota-separator { text-align: center; margin: 20px 0 10px 0; font-size: 0.9rem; font-weight: bold; color: #004aad; background-color: #e3f2fd; padding: 6px; border-radius: 4px; }

    /* Ajustes Gerais */
    div[data-testid="stTextInput"] { margin-bottom: 0px; }
    div[data-testid="metric-container"] { background-color: #fff; border: 1px solid #eee; padding: 5px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÃO LEITURA ---
def ler_rotas(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith('xlsx'): df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try: df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except: df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')
        header_idx = -1
        for index, row in df_raw.iterrows():
            txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in txt and "vpn" in txt:
                header_idx = index; break
        if header_idx == -1: return None
        df_raw.columns = df_raw.iloc[header_idx]; df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, df.columns.notna()]
        if 'VPN' in df.columns: df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return df
    except: return None

# --- 4. CARREGAMENTO ---
df_rotas = None
if os.path.exists("rotas.csv.xlsx"):
    with open("rotas.csv.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read()); mem.name = "rotas.csv.xlsx"
        df_rotas = ler_rotas(mem)

# --- LÓGICA DE DATA MANUAL (FIXA E SEGURA) ---
data_final = datetime.now()
try:
    if os.path.exists("data_manual.txt"):
        with open("data_manual.txt", "r") as f:
            data_str = f.read().strip()
            data_final = datetime.strptime(data_str, "%Y-%m-%d")
except: pass

data_hoje_str = data_final.strftime("%d/%m")
dias = {0:"Domingo", 1:"Segunda", 2:"Terça", 3:"Quarta", 4:"Quinta", 5:"Sexta", 6:"Sábado"}
dia_sem = dias[data_final.weekday()]

# --- 5. MENU LATERAL ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/004aad/truck.png", width=60)
    st.markdown("### Menu Principal")
    menu = st.radio("Navegação:", ["🚛 Minha Escala", "⚙️ Gestão"])

# ==================================================
# PÁGINA 1: MINHA ESCALA
# ==================================================
if menu == "🚛 Minha Escala":
    
    st.markdown(f"""
    <div class="header-box">
        <div class="header-title">Minha Escala</div>
        <div class="header-date">📅 {dia_sem}, {data_hoje_str}</div>
    </div>
    """, unsafe_allow_html=True)

    if df_rotas is not None:
        with st.form(key='busca_rotas'):
            vpn = st.text_input("vpn", label_visibility="collapsed", placeholder="Digite a VPN...")
            btn = st.form_submit_button("🔍 VER ROTAS", type="primary")

        if btn and vpn:
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            if not res.empty:
                total = len(res)
                for i, (idx, row) in enumerate(res.iterrows()):
                    if total > 1: st.markdown(f"<div class='rota-separator'>📍 VIAGEM {i+1} de {total}</div>", unsafe_allow_html=True)
                    
                    # Motorista
                    st.markdown(f"""<div style='background-color: #004aad; color: white; padding: 8px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);'>👤 {row.get('Motorista', '-')}</div>""", unsafe_allow_html=True)
                    
                    # Veículo
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("MATR", str(row.get('Matrícula', '-')))
                    c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                    c3.metric("ROTA", str(row.get('ROTA', '-')))
                    c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                    
                    # Horários
                    loc_desc = str(row.get('Local descarga', 'Loja')).upper()
                    cc, cd = st.columns(2)
                    with cc: st.markdown(f"""<div class="time-block" style="border-left-color: #0d47a1;"><div class="time-label">CHEGADA</div><div class="time-value">{row.get('Hora chegada Azambuja', '--')}</div><div class="location-highlight text-blue">AZAMBUJA</div></div>""", unsafe_allow_html=True)
                    with cd: st.markdown(f"""<div class="time-block" style="border-left-color: #d32f2f;"><div class="time-label">DESCARGA</div><div class="time-value">{row.get('Hora descarga loja', '--')}</div><div class="location-highlight text-red">{loc_desc}</div></div>""", unsafe_allow_html=True)
                    
                    # Barra Fina
                    v_sup = '0'
                    for c in df_rotas.columns: 
                        if "total suportes" in c.lower(): v_sup = str(row.get(c, '0')); break
                    
                    v_ret = str(row.get('Retorno', '-'))
                    cor_ret = "#008000" if v_ret not in ['0','-','nan','Vazio','None','○','o','O'] else "#333"
                    
                    st.markdown(f"""
                    <div class="info-row">
                        <div class="info-item bg-purple"><span class="info-label">SUPORTES</span><span class="info-val">📦 {v_sup}</span></div>
                        <div class="info-item-retorno"><span class="info-label-dark">RETORNO</span><span class="info-val" style="color:{cor_ret}">{v_ret}</span></div>
                        <div class="info-item bg-green"><span class="info-label">TIPO</span><span class="info-val">{row.get('TIPO', '-')}</span></div>
                    </div>""", unsafe_allow_html=True)
                    
                    # Carga
                    with st.expander(f"🔎 Carga Viagem {i+1}"):
                        cols = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", "Frota Refrigerado", "Peixe", "Talho"]
                        dd = {"Cat": [], "Qtd": []}
                        for cn in cols:
                            match = next((c for c in df_rotas.columns if cn.lower() in c.lower()), None)
                            if match:
                                v = str(row.get(match, '0'))
                                if v not in ['0', 'nan']: dd["Cat"].append(cn.replace("Azambuja ","").replace("Total ","")); dd["Qtd"].append(v)
                        if dd["Cat"]: st.table(pd.DataFrame(dd).set_index("Cat"))
                        else: st.caption("Sem carga especial.")
                        
                    if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                         st.info(f"📱 {row['WhatsApp']}")
            else: st.error("❌ VPN não encontrada.")
        else: st.warning("Digite a VPN.")
    else: st.warning("⚠️ Aguardando escala.")

# ==================================================
# PÁGINA 2: GESTÃO
# ==================================================
elif menu == "⚙️ Gestão":
    st.header("🔐 Acesso Restrito")
    usuario = st.selectbox("Usuário", ["Selecionar..."] + list(ADMINS.keys()))
    senha = st.text_input("Senha", type="password")
    
    if usuario != "Selecionar..." and senha == ADMINS.get(usuario):
        st.success(f"Bem-vindo, {usuario}!")
        st.markdown("---")
        
        # 1. DATA
        st.subheader("1. Configurar Data da Escala")
        nova_data = st.date_input("Escolha a data da escala:", value=data_final)
        if st.button("💾 Salvar Data"):
            with open("data_manual.txt", "w") as f: f.write(str(nova_data))
            st.success("Data Atualizada! Dê Refresh na página.")
            
        st.markdown("---")
        
        # 2. UPLOAD
        st.subheader("2. Carregar Arquivo de Rotas")
        up_rotas = st.file_uploader("Arquivo Rotas (Excel/CSV)", type=['xlsx','csv'])
        if up_rotas:
            df_novo = ler_rotas(up_rotas)
            if df_novo is not None: 
                df_rotas = df_novo
                st.success("✅ Arquivo carregado com sucesso!")
            else: st.error("Erro ao ler arquivo.")
    elif senha: st.error("Senha incorreta!")
