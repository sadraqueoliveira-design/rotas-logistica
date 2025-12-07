import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO (Fundamental para o menu aparecer) ---
st.set_page_config(
    page_title="Logística App", 
    page_icon="🚛", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# ==========================================
# 🔐 ADMINS
# ==========================================
ADMINS = {
    "Admin Principal": "admin123",
    "Gestor Tráfego": "trafego2025",
    "Escritório": "office99",
}

# --- 2. ESTILO CSS (Compacto e Correto) ---
st.markdown("""
<style>
    /* Oculta Rodapé mas MOSTRA O CABEÇALHO (Onde fica o botão do menu) */
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;} 
    footer {visibility: hidden;}
    
    /* Ajuste do topo para o botão do menu não ficar tapado */
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    
    /* CABEÇALHO DA PÁGINA (Azul com Data Amarela) */
    .header-box {
        background: linear-gradient(135deg, #004aad 0%, #003380 100%);
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }
    .header-title { 
        font-size: 24px; font-weight: 900; margin: 0; line-height: 1.1; 
        text-transform: uppercase; letter-spacing: 1px;
    }
    .header-date { 
        font-size: 20px; /* DATA GRANDE */
        font-weight: bold; color: #FFD700; /* AMARELO */
        margin-top: 5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* CARTÃO MOTORISTA */
    .driver-card {
        background-color: #004aad; color: white;
        padding: 8px; border-radius: 6px;
        text-align: center; font-weight: bold; font-size: 1.1rem;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* GRELHA VEÍCULO (2x2) */
    .vehicle-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 10px;
    }
    .vehicle-item {
        background-color: #e3f2fd; padding: 5px; border-radius: 5px; text-align: center;
    }
    .vehicle-label { font-size: 9px; color: #666; text-transform: uppercase; font-weight: bold; margin-bottom: 0;}
    .vehicle-val { font-size: 13px; font-weight: bold; color: #004aad; line-height: 1.1;}
    
    /* BLOCOS HORÁRIO */
    .time-block {
        background-color: #f8f9fa; padding: 6px; border-radius: 6px;
        border-left: 4px solid #004aad; margin-bottom: 5px;
    }
    .time-label { font-size: 0.7rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.4rem; font-weight: bold; color: #333; margin: 0; line-height: 1.1; }
    .location-highlight { font-size: 0.9rem; font-weight: 900; text-transform: uppercase; margin: 0;}
    .text-blue { color: #0d47a1; } .text-red { color: #d32f2f; }
    
    /* BARRA FINA (STATUS) */
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
    button[kind="primary"] { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÃO LEITURA SIMPLES ---
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

# --- 5. DATA MANUAL (CONTROLO TOTAL) ---
# Se existe arquivo de data, lê. Se não, usa hoje.
data_final = datetime.now()
if os.path.exists("data_manual.txt"):
    try:
        with open("data_manual.txt", "r") as f:
            data_str = f.read().strip()
            data_final = datetime.strptime(data_str, "%Y-%m-%d")
    except: pass

data_hoje_str = data_final.strftime("%d/%m")
dias = {0:"Domingo", 1:"Segunda", 2:"Terça", 3:"Quarta", 4:"Quinta", 5:"Sexta", 6:"Sábado"}
dia_sem = dias[data_final.weekday()]

# --- 6. MENU LATERAL ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/004aad/truck.png", width=60)
    st.markdown("### Menu")
    menu = st.radio("Ir para:", ["🚛 Minha Escala", "⚙️ Gestão"])

# ==================================================
# PÁGINA 1: MINHA ESCALA
# ==================================================
if menu == "🚛 Minha Escala":
    
    # CABEÇALHO COM DATA CERTA
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
                    
                    # 1. MOTORISTA
                    st.markdown(f"""<div class="driver-card">👤 {row.get('Motorista', '-')}</div>""", unsafe_allow_html=True)
                    
                    # 2. VEÍCULO (GRELHA 2x2)
                    st.markdown(f"""
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div class="vehicle-label">MATRÍCULA</div><div class="vehicle-val">{row.get('Matrícula', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">MÓVEL</div><div class="vehicle-val">{row.get('Móvel', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">ROTA</div><div class="vehicle-val">{row.get('ROTA', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">LOJA</div><div class="vehicle-val">{row.get('Nº LOJA', '-')}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 3. HORÁRIOS
                    loc_desc = str(row.get('Local descarga', 'Loja')).upper()
                    cc, cd = st.columns(2)
                    with cc: st.markdown(f"""<div class="time-block" style="border-left-color: #0d47a1;"><div class="time-label">CHEGADA</div><div class="time-value">{row.get('Hora chegada Azambuja', '--')}</div><div class="location-highlight text-blue">AZAMBUJA</div></div>""", unsafe_allow_html=True)
                    with cd: st.markdown(f"""<div class="time-block" style="border-left-color: #d32f2f;"><div class="time-label">DESCARGA</div><div class="time-value">{row.get('Hora descarga loja', '--')}</div><div class="location-highlight text-red">{loc_desc}</div></div>""", unsafe_allow_html=True)
                    
                    # 4. BARRA FINA
                    v_sup = '0'
                    for c in df_rotas.columns: 
                        if "total suportes" in c.lower(): v_sup = str(row.get(c, '0')); break
                    
                    v_ret = str(row.get('Retorno', '-'))
                    # Lógica Cor Verde (Ignora '0', '-', vazio, 'o')
                    cor_ret = "#008000" if v_ret not in ['0','-','nan','Vazio','None','○','o','O'] else "#333"
                    
                    st.markdown(f"""
                    <div class="info-row">
                        <div class="info-item bg-purple"><span class="info-label">SUPORTES</span><span class="info-val">📦 {v_sup}</span></div>
                        <div class="info-item-retorno"><span class="info-label-dark">RETORNO</span><span class="info-val" style="color:{cor_ret}">{v_ret}</span></div>
                        <div class="info-item bg-green"><span class="info-label">TIPO</span><span class="info-val">{row.get('TIPO', '-')}</span></div>
                    </div>""", unsafe_allow_html=True)
                    
                    # 5. CARGA
                    with st.expander(f"🔎 Ver Carga Viagem {i+1}"):
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
        st.success(f"Logado como {usuario}")
        st.markdown("---")
        
        # 1. SELETOR DE DATA MANUAL
        st.subheader("1. Configurar Data da Escala")
        nova_data = st.date_input("Selecione a data que vai aparecer no App:", value=data_final)
        
        if st.button("💾 Salvar Data"):
            with open("data_manual.txt", "w") as f: f.write(str(nova_data))
            st.success(f"Data mudada para {nova_data.strftime('%d/%m/%Y')}! Atualize a página.")
            
        st.markdown("---")
        
        # 2. UPLOAD ARQUIVO
        st.subheader("2. Carregar Arquivo de Rotas")
        up_rotas = st.file_uploader("Arquivo Rotas (Excel/CSV)", type=['xlsx','csv'])
        if up_rotas:
            df_novo = ler_rotas(up_rotas)
            if df_novo is not None: 
                df_rotas = df_novo
                st.success("✅ Arquivo atualizado!")
            else: st.error("Erro ao ler arquivo.")
            
    elif senha: st.error("Senha incorreta!")
