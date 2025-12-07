import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz 

# --- 1. CONFIGURAÇÃO (Barra lateral expandida por padrão) ---
st.set_page_config(
    page_title="Logística App", 
    page_icon="🚛", 
    layout="centered", 
    initial_sidebar_state="collapsed" # Começa fechado para dar espaço, mas o botão estará lá
)

# ==========================================
# 🔐 ADMINS
# ==========================================
ADMINS = {
    "Admin Principal": "admin123",
    "Gestor Tráfego": "trafego2025",
    "Escritório": "office99",
}

# --- 2. ESTILO CSS (CORRIGIDO PARA O MENU) ---
st.markdown("""
<style>
    /* GARANTIR QUE O BOTÃO DO MENU E CABEÇALHO APARECEM */
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;}
    footer {visibility: hidden;}
    
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    
    /* Cabeçalho Azul */
    .header-box {
        background: linear-gradient(90deg, #004aad 0%, #0066cc 100%);
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        display: flex; align-items: center; justify-content: center; gap: 10px;
    }
    .header-title { font-size: 18px; font-weight: bold; margin: 0; line-height: 1; }
    .header-date { font-size: 12px; opacity: 0.9; margin: 0; font-weight: normal; }
    
    /* Cartão Motorista */
    .driver-card {
        background-color: white;
        border-left: 5px solid #004aad;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 8px;
        display: flex; align-items: center; gap: 10px;
    }
    .driver-icon { font-size: 20px; }
    .driver-name { font-size: 16px; font-weight: bold; color: #333; }
    
    /* Grelha Veículo */
    .vehicle-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 5px;
        margin-bottom: 10px;
    }
    .vehicle-item {
        background-color: #e3f2fd;
        padding: 5px;
        border-radius: 5px;
        text-align: center;
    }
    .vehicle-label { font-size: 10px; color: #666; text-transform: uppercase; font-weight: bold; }
    .vehicle-val { font-size: 14px; font-weight: bold; color: #004aad; }
    
    /* Horários */
    .time-container { display: flex; gap: 5px; margin-bottom: 8px; }
    .time-block {
        flex: 1;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 6px;
        border-left: 4px solid #333;
        text-align: left;
    }
    .time-label { font-size: 10px; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 20px; font-weight: bold; color: #333; margin: 2px 0; line-height: 1; }
    .location-text { font-size: 12px; font-weight: 900; text-transform: uppercase; margin: 0; }
    
    /* Barra Fina */
    .info-row { display: flex; justify-content: space-between; gap: 4px; margin-bottom: 8px; }
    .info-item { flex: 1; text-align: center; padding: 4px; border-radius: 4px; color: white; display: flex; flex-direction: column; justify-content: center; }
    .info-item-retorno { flex: 1; text-align: center; padding: 4px; border-radius: 4px; background-color: white; border: 1px solid #ddd; display: flex; flex-direction: column; justify-content: center; }
    
    .info-label { font-size: 9px; text-transform: uppercase; opacity: 0.9; line-height: 1; margin-bottom: 2px; }
    .info-label-dark { font-size: 9px; text-transform: uppercase; color: #666; line-height: 1; margin-bottom: 2px; font-weight: bold; }
    .info-val { font-size: 14px; font-weight: bold; line-height: 1; }
    
    .bg-purple { background-color: #7b1fa2; } 
    .bg-green { background-color: #2e7d32; }
    
    .rota-separator { text-align: center; margin: 15px 0 5px 0; font-size: 0.8rem; font-weight: bold; color: #004aad; background-color: #e3f2fd; padding: 4px; border-radius: 4px; }
    
    div[data-testid="stTextInput"] { margin-bottom: 0px; }
    button[kind="primary"] { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÕES ---
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

# --- 5. MENU LATERAL ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/004aad/truck.png", width=50)
    st.markdown("### Menu")
    menu = st.radio("Navegação:", ["🚛 Minha Escala", "⚙️ Gestão"])

# ==================================================
# PÁGINA 1: MINHA ESCALA
# ==================================================
if menu == "🚛 Minha Escala":
    try: fuso = pytz.timezone('Europe/Lisbon'); agora = datetime.now(fuso)
    except: agora = datetime.now()
    data_hoje = agora.strftime("%d/%m"); dias = {0:"Seg", 1:"Ter", 2:"Qua", 3:"Qui", 4:"Sex", 5:"Sáb", 6:"Dom"}
    dia_sem = dias[agora.weekday()]

    st.markdown(f"""
    <div class="header-box">
        <div style="font-size: 24px;">🚛</div>
        <div><div class="header-title">Minha Escala</div><div class="header-date">{dia_sem}, {data_hoje}</div></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Aviso se o menu estiver escondido (Ajuda visual)
    if 'menu_aviso' not in st.session_state:
        st.session_state['menu_aviso'] = True
    
    # Input de VPN
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
                    
                    # 1. MOTORISTA
                    st.markdown(f"""
                    <div class="driver-card">
                        <div class="driver-icon">👤</div>
                        <div class="driver-name">{row.get('Motorista', '-')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. GRELHA VEÍCULO
                    st.markdown(f"""
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div class="vehicle-label">MATRÍCULA</div><div class="vehicle-val">{row.get('Matrícula', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">TELEMÓVEL</div><div class="vehicle-val">{row.get('Móvel', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">ROTA</div><div class="vehicle-val">{row.get('ROTA', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">LOJA</div><div class="vehicle-val">{row.get('Nº LOJA', '-')}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 3. HORÁRIOS
                    loc_desc = str(row.get('Local descarga', 'Loja')).upper()
                    st.markdown(f"""
                    <div class="time-container">
                        <div class="time-block" style="border-left-color: #004aad;">
                            <div class="time-label">CHEGADA</div>
                            <div class="time-value">{row.get('Hora chegada Azambuja', '--')}</div>
                            <div class="location-text" style="color: #004aad;">AZAMBUJA</div>
                        </div>
                        <div class="time-block" style="border-left-color: #d32f2f;">
                            <div class="time-label">DESCARGA</div>
                            <div class="time-value">{row.get('Hora descarga loja', '--')}</div>
                            <div class="location-text" style="color: #d32f2f;">{loc_desc}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 4. BARRA FINA
                    v_sup = '0'
                    for c in df_rotas.columns: 
                        if "total suportes" in c.lower(): v_sup = str(row.get(c, '0')); break
                    
                    v_ret = str(row.get('Retorno', '-'))
                    cor_ret = "#2e7d32" if v_ret not in ['0','-','nan','Vazio','None','○','o','O'] else "#999"
                    weight_ret = "bold" if cor_ret == "#2e7d32" else "normal"
                    
                    st.markdown(f"""
                    <div class="info-row">
                        <div class="info-item bg-purple"><span class="info-label">SUPORTES</span><span class="info-val">📦 {v_sup}</span></div>
                        <div class="info-item-retorno"><span class="info-label-dark">RETORNO</span><span class="info-val" style="color:{cor_ret}; font-weight:{weight_ret}">{v_ret}</span></div>
                        <div class="info-item bg-green"><span class="info-label">TIPO</span><span class="info-val">{row.get('TIPO', '-')}</span></div>
                    </div>""", unsafe_allow_html=True)
                    
                    # 5. CARGA
                    with st.expander(f"🔎 Ver Carga Detalhada"):
                        cols = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", "Frota Refrigerado", "Peixe", "Talho"]
                        dd = {"Cat": [], "Qtd": []}
                        for cn in cols:
                            match = next((c for c in df_rotas.columns if cn.lower() in c.lower()), None)
                            if match:
                                v = str(row.get(match, '0'))
                                if v not in ['0', 'nan']: dd["Cat"].append(cn.replace("Azambuja ","").replace("Total ","")); dd["Qtd"].append(v)
                        if dd["Cat"]: st.table(pd.DataFrame(dd).set_index("Cat"))
                        else: st.caption("Nenhuma carga específica registada.")
                        
                    if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                         st.info(f"📱 {row['WhatsApp']}")
            else: st.error("❌ VPN não encontrada.")
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
        up_rotas = st.file_uploader("Arquivo Rotas (Excel/CSV)", type=['xlsx','csv'])
        if up_rotas:
            df_novo = ler_rotas(up_rotas)
            if df_novo is not None: df_rotas = df_novo; st.success("✅ Atualizado!")
            else: st.error("Erro no arquivo.")
    elif senha: st.error("Senha incorreta!")
