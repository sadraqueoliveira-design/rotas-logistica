import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz 

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered")

# ==========================================
# 🔐 LISTA DE ADMINISTRADORES
# ==========================================
ADMINS = {
    "Admin Principal": "admin123",
    "Gestor Tráfego": "trafego2025",
    "Escritório": "office99",
    # Adicione mais aqui se precisar
}

# --- 2. ESTILO CSS (Compacto e Otimizado) ---
st.markdown("""
<style>
    /* Oculta rodapé e menu de 3 pontos, mas DEIXA o cabeçalho visível para o menu lateral */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    
    /* Menu Lateral */
    section[data-testid="stSidebar"] { background-color: #f0f2f6; }
    
    /* Cabeçalho */
    .header-box {
        background-color: #004aad;
        padding: 8px;
        border-radius: 6px;
        text-align: center;
        color: white;
        margin-bottom: 5px;
        display: flex; align-items: center; justify-content: center; gap: 8px;
    }
    .header-title { font-size: 16px; font-weight: bold; margin: 0; line-height: 1; }
    .header-date { font-size: 11px; opacity: 0.9; margin: 0; }
    
    /* Rotas: Blocos de Horário */
    .time-block {
        background-color: #f8f9fa; padding: 5px; border-radius: 5px;
        border-left: 3px solid #004aad; margin-bottom: 5px;
    }
    .time-label { font-size: 0.6rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.1rem; font-weight: bold; color: #333; margin: 0; line-height: 1.1; }
    
    /* Locais em Destaque */
    .location-highlight { font-size: 0.8rem; font-weight: 900; text-transform: uppercase; margin: 0;}
    .text-blue { color: #0d47a1; } .text-red { color: #d32f2f; }
    
    /* Barra Fina */
    .info-row { display: flex; justify-content: space-between; gap: 4px; margin-top: 5px; margin-bottom: 5px; }
    .info-item { flex: 1; text-align: center; padding: 3px 2px; border-radius: 4px; color: white; }
    .info-item-retorno { flex: 1; text-align: center; padding: 2px 2px; border-radius: 4px; background-color: white; border: 1px solid #ddd; }
    .info-label { font-size: 0.5rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 0px; line-height: 1;}
    .info-label-dark { font-size: 0.5rem; text-transform: uppercase; color: #666; display: block; margin-bottom: 0px; line-height: 1; font-weight: bold;}
    .info-val { font-size: 0.9rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; } .bg-green { background-color: #388e3c; }

    /* Separador Rotas */
    .rota-separator { text-align: center; margin: 15px 0 5px 0; font-size: 0.8rem; font-weight: bold; color: #004aad; background-color: #e3f2fd; padding: 4px; border-radius: 4px; }

    div[data-testid="metric-container"] { padding: 4px; margin: 0px; }
    div[data-testid="metric-container"] label { font-size: 0.6rem; margin-bottom: 0px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 0.9rem; }
    div[data-testid="stTextInput"] { margin-bottom: 0px; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÃO DE LEITURA ---
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
    # Data
    try: fuso = pytz.timezone('Europe/Lisbon'); agora = datetime.now(fuso)
    except: agora = datetime.now()
    data_hoje = agora.strftime("%d/%m"); dias = {0:"Seg", 1:"Ter", 2:"Qua", 3:"Qui", 4:"Sex", 5:"Sáb", 6:"Dom"}
    dia_sem = dias[agora.weekday()]

    st.markdown(f"""
    <div class="header-box">
        <div style="font-size: 20px;">🚛</div>
        <div><div class="header-title">Minha Escala</div><div class="header-date">{dia_sem}, {data_hoje}</div></div>
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
                    
                    # Motorista (Azul destaque)
                    st.markdown(f"""<div style='background-color: #004aad; color: white; padding: 6px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 1.0rem; margin-bottom: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);'>👤 {row.get('Motorista', '-')}</div>""", unsafe_allow_html=True)
                    
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
                    
                    # Barra Fina (Lógica de Cores)
                    v_sup = '0'
                    for c in df_rotas.columns: 
                        if "total suportes" in c.lower(): v_sup = str(row.get(c, '0')); break
                    
                    v_ret = str(row.get('Retorno', '-'))
                    # Ignora zeros e simbolos vazios para a cor verde
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
                        else: st.caption("Vazio")
                        
                    if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                         st.info(f"📱 {row['WhatsApp']}")
            else: st.error("❌ VPN não encontrada.")
    else: st.warning("⚠️ Aguardando escala.")

# ==================================================
# PÁGINA 2: GESTÃO (MULTI ADMIN)
# ==================================================
elif menu == "⚙️ Gestão":
    st.header("🔐 Acesso Restrito")
    
    # Login Multi-Usuário
    usuario = st.selectbox("Selecione seu Usuário", ["Selecionar..."] + list(ADMINS.keys()))
    senha = st.text_input("Digite sua Senha", type="password")
    
    if usuario != "Selecionar..." and senha == ADMINS.get(usuario):
        st.success(f"Bem-vindo, {usuario}!")
        st.markdown("---")
        
        st.subheader("Atualizar Arquivo de Rotas")
        up_rotas = st.file_uploader("Selecione o arquivo Excel ou CSV", type=['xlsx','csv'])
        
        if up_rotas:
            df_novo = ler_rotas(up_rotas)
            if df_novo is not None: 
                df_rotas = df_novo
                st.success("✅ Rotas atualizadas com sucesso!")
            else:
                st.error("Erro ao ler arquivo.")
                
    elif senha:
        st.error("Senha incorreta!")
