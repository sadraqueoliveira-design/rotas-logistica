import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="Logística App", 
    page_icon="🚛", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# ADMINS
ADMINS = {
    "Admin Principal": "admin123",
    "Gestor Tráfego": "trafego2025",
    "Escritório": "office99",
}

# ARQUIVOS
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"

# --- 2. ESTILO CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;} 
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    
    .header-box {
        background: linear-gradient(135deg, #004aad 0%, #003380 100%);
        padding: 15px; border-radius: 12px; text-align: center; color: white;
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .header-title { font-size: 22px; font-weight: 900; margin: 0; line-height: 1.1; text-transform: uppercase; }
    .header-date { font-size: 24px; font-weight: bold; color: #FFD700; margin-top: 5px; }
    
    .driver-card {
        background-color: #004aad; color: white; padding: 10px; border-radius: 8px;
        text-align: center; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px;
    }
    .vehicle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
    .vehicle-item { background-color: #e3f2fd; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #bbdefb; }
    .vehicle-label { font-size: 10px; color: #555; text-transform: uppercase; font-weight: bold; margin-bottom: 0;}
    .vehicle-val { font-size: 14px; font-weight: bold; color: #004aad; line-height: 1.1;}
    
    .time-block {
        background-color: #f8f9fa; padding: 10px; border-radius: 8px;
        border-left: 5px solid #004aad; margin-bottom: 5px;
    }
    .time-label { font-size: 0.75rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.6rem; font-weight: bold; color: #333; margin: 0; line-height: 1; }
    .location-highlight { font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-top: 2px;}
    .text-blue { color: #0d47a1; } .text-red { color: #d32f2f; }
    
    .info-row { display: flex; justify-content: space-between; gap: 6px; margin-top: 15px; margin-bottom: 15px; }
    .info-item { flex: 1; text-align: center; padding: 6px 2px; border-radius: 6px; color: white; font-size: 0.9rem;}
    .info-item-retorno { flex: 1; text-align: center; padding: 5px 2px; border-radius: 6px; background-color: white; border: 1px solid #ddd; }
    .info-label { font-size: 0.65rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 2px; line-height: 1;}
    .info-label-dark { font-size: 0.65rem; text-transform: uppercase; color: #666; display: block; margin-bottom: 2px; line-height: 1; font-weight: bold;}
    .info-val { font-size: 1.1rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; } .bg-green { background-color: #388e3c; }
    .rota-separator { text-align: center; margin: 30px 0 15px 0; font-size: 1rem; font-weight: bold; color: #004aad; background-color: #e3f2fd; padding: 8px; border-radius: 6px; border: 1px dashed #004aad;}
    
    button[kind="primary"] { width: 100%; border-radius: 8px; height: 50px; font-weight: bold; font-size: 18px !important;}
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÃO LEITURA ESPECÍFICA PARA O SEU ARQUIVO ---
def ler_rotas(file_content):
    try:
        # Tenta ler como Excel ou CSV (vários encodings)
        # IMPORTANTE: header=0 lê a primeira linha (onde diz "Matricula", "Rota", etc.)
        try: df = pd.read_excel(file_content, header=0)
        except:
            file_content.seek(0)
            try: df = pd.read_csv(file_content, header=0, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try: df = pd.read_csv(file_content, header=0, sep=',', encoding='utf-8')
                except: 
                    file_content.seek(0)
                    df = pd.read_csv(file_content, header=0, sep=',', encoding='latin1')

        # --- CORREÇÃO DE COLUNAS ---
        # No seu arquivo:
        # Coluna indice 1 é o Motorista (mesmo que o cabeçalho diga 'Filtro' ou esteja vazio)
        # Coluna indice 2 é a VPN
        
        cols = list(df.columns)
        
        # Renomeia forçadamente as colunas vitais pelos indices
        if len(cols) > 3:
            df.rename(columns={
                cols[1]: 'Motorista',
                cols[2]: 'VPN'
            }, inplace=True)
            
        # Limpa os nomes das outras colunas (remove espaços extras)
        df.columns = df.columns.astype(str).str.strip()
        
        # Corrige erros de ortografia comuns no ficheiro
        correcoes = {
            'Matricula': 'Matrícula',    
            'Movél': 'Móvel',            
            'NºLOJA': 'Nº LOJA'
        }
        for errado, certo in correcoes.items():
            for c_real in df.columns:
                if errado.lower() in c_real.lower():
                    df.rename(columns={c_real: certo}, inplace=True)

        # --- FILTRAGEM DE LIXO ---
        # Remove linhas onde a VPN não é válida
        if 'VPN' in df.columns:
            # Converte para string
            df['VPN'] = df['VPN'].astype(str)
            # Remove sufixo .0
            df['VPN'] = df['VPN'].str.replace(r'\.0$', '', regex=True).str.strip()
            # Remove linhas vazias, 'nan', '0' ou cabeçalhos repetidos
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Remove linhas onde o Motorista é "Motorista" (cabeçalho secundário)
            df = df[df['Motorista'] != 'Motorista']

        return df
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
        return None

# --- 4. CARREGAMENTO ---
df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        mem = BytesIO(f.read())
        df_rotas = ler_rotas(mem)

# --- 5. DATA ---
data_final = datetime.now()
if os.path.exists(DATE_FILE):
    try:
        with open(DATE_FILE, "r") as f:
            data_str = f.read().strip()
            data_final = datetime.strptime(data_str, "%Y-%m-%d")
    except: pass

data_hoje_str = data_final.strftime("%d/%m")
dias = {0:"Domingo", 1:"Segunda", 2:"Terça", 3:"Quarta", 4:"Quinta", 5:"Sexta", 6:"Sábado"}
dia_sem = dias[data_final.weekday()]

# --- 6. MENU LATERAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🚛 LOGÍSTICA</h1>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navegação:", ["🏠 Minha Escala", "⚙️ Gestão / Upload"], label_visibility="collapsed")
    
    if df_rotas is not None:
        st.success(f"Dados carregados: {len(df_rotas)} rotas")
        # DEBUG: Ative se precisar ver se as colunas 'Motorista' e 'VPN' existem
        # st.write(df_rotas.columns)

# ==================================================
# PÁGINA 1: MINHA ESCALA
# ==================================================
if menu == "🏠 Minha Escala":
    
    st.markdown(f"""
    <div class="header-box">
        <div class="header-title">ESCALA DIÁRIA</div>
        <div class="header-date">📅 {dia_sem}, {data_hoje_str}</div>
    </div>
    """, unsafe_allow_html=True)

    if df_rotas is not None:
        with st.form(key='busca_rotas'):
            col_in, col_btn = st.columns([2, 1])
            vpn = st.text_input("vpn", label_visibility="collapsed", placeholder="Digite a VPN (Ex: 76628)")
            btn = st.form_submit_button("🔍 BUSCAR", type="primary")

        if btn and vpn:
            # Filtro exato
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            
            # Filtro parcial por nome
            if res.empty and len(vpn) > 3:
                 res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                total = len(res)
                for i, (idx, row) in enumerate(res.iterrows()):
                    if total > 1: 
                        st.markdown(f"<div class='rota-separator'>📍 VIAGEM {i+1} de {total}</div>", unsafe_allow_html=True)
                    
                    # 1. MOTORISTA
                    st.markdown(f"""<div class="driver-card">👤 {row.get('Motorista', '-')}</div>""", unsafe_allow_html=True)
                    
                    # 2. VEÍCULO 
                    # Usa get com valor default '-' para não dar erro se coluna faltar
                    matricula = row.get('Matrícula', '-')
                    movel = row.get('Móvel', '-')
                    rota = row.get('ROTA', '-')
                    nloja = row.get('Nº LOJA', '-')
                    
                    st.markdown(f"""
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div class="vehicle-label">MATRÍCULA</div><div class="vehicle-val">{matricula}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">MÓVEL</div><div class="vehicle-val">{movel}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">ROTA</div><div class="vehicle-val">{rota}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">LOJA</div><div class="vehicle-val">{nloja}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 3. HORÁRIOS - Busca flexível
                    # Procura coluna que contenha "chegada" e "azambuja"
                    h_cheg_col = next((c for c in df_rotas.columns if "chegada" in c.lower() and "azambuja" in c.lower()), 'Hora chegada Azambuja')
                    h_cheg = row.get(h_cheg_col, '--')

                    # Procura coluna local descarga
                    loc_col = next((c for c in df_rotas.columns if "local descarga" in c.lower()), 'Local descarga')
                    loc_desc = str(row.get(loc_col, 'Loja')).upper()
                    
                    # Procura hora descarga
                    h_desc_col = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora descarga loja')
                    h_desc = row.get(h_desc_col, '--')
                    
                    cc, cd = st.columns(2)
                    with cc: 
                        st.markdown(f"""<div class="time-block" style="border-left-color: #0d47a1;"><div class="time-label">CHEGADA</div><div class="time-value">{h_cheg}</div><div class="location-highlight text-blue">AZAMBUJA</div></div>""", unsafe_allow_html=True)
                    with cd: 
                        st.markdown(f"""<div class="time-block" style="border-left-color: #d32f2f;"><div class="time-label">DESCARGA</div><div class="time-value">{h_desc}</div><div class="location-highlight text-red">{loc_desc}</div></div>""", unsafe_allow_html=True)
                    
                    # 4. INFO EXTRA
                    v_sup = '0'
                    for c in df_rotas.columns: 
                        if "total suportes" in c.lower(): v_sup = str(row.get(c, '0')); break
                    
                    v_ret = str(row.get('Retorno', '-'))
                    cor_ret = "#008000" if v_ret not in ['0','-','nan','Vazio','None'] else "#333"
                    
                    st.markdown(f"""
                    <div class="info-row">
                        <div class="info-item bg-purple"><span class="info-label">SUPORTES</span><span class="info-val">📦 {v_sup}</span></div>
                        <div class="info-item-retorno"><span class="info-label-dark">RETORNO</span><span class="info-val" style="color:{cor_ret}">{v_ret}</span></div>
                        <div class="info-item bg-green"><span class="info-label">TIPO</span><span class="info-val">{row.get('TIPO', '-')}</span></div>
                    </div>""", unsafe_allow_html=True)

            else: 
                st.error(f"❌ Nenhuma rota encontrada para: {vpn}")
        else:
            if not btn: st.info("👆 Digite a VPN acima e clique em VER ROTAS.")
    else:
        st.warning("⚠️ Nenhuma escala carregada.")

# ==================================================
# PÁGINA 2: GESTÃO
# ==================================================
elif menu == "⚙️ Gestão / Upload":
    st.header("🔐 Área de Gestão")
    col1, col2 = st.columns(2)
    with col1: usuario = st.selectbox("Usuário", ["Selecionar..."] + list(ADMINS.keys()))
    with col2: senha = st.text_input("Senha", type="password")
    
    if usuario != "Selecionar..." and senha == ADMINS.get(usuario):
        st.success(f"🔓 {usuario}")
        
        # DATA
        st.subheader("1. Data da Escala")
        nova_data = st.date_input("Data:", value=data_final)
        if st.button("💾 Atualizar Data"):
            with open(DATE_FILE, "w") as f: f.write(str(nova_data))
            st.success("Data salva! Atualize a página.")

        # UPLOAD
        st.subheader("2. Upload Arquivo")
        up_rotas = st.file_uploader("Excel ou CSV", type=['xlsx','csv'])
        if up_rotas:
            df_preview = ler_rotas(up_rotas)
            if df_preview is not None:
                st.write(f"✅ {len(df_preview)} linhas válidas identificadas.")
                st.dataframe(df_preview.head(3))
                if st.button("🚀 CONFIRMAR UPLOAD"):
                    with open(DB_FILE, "wb") as f: f.write(up_rotas.getbuffer())
                    st.success("Arquivo gravado!")
                    st.balloons()
            else:
                st.error("Erro na leitura. Verifique o formato.")
    elif senha: 
        st.error("⛔ Senha incorreta!")
