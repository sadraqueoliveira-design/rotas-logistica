import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz 
import re 

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered")

# ==========================================
# 🔐 LISTA DE ADMINISTRADORES
# ==========================================
ADMINS = {
    "Admin Principal": "admin123",
    "Gestor Tráfego": "trafego2025",
    "Escritório": "office99",
}

# --- 2. ESTILO CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    
    /* Menu Lateral */
    .css-1d391kg, [data-testid="stSidebar"] { font-size: 16px !important; background-color: #f0f2f6; }
    
    /* CABEÇALHO (VISUAL LIMPO E DATA GRANDE) */
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
        font-size: 24px; font-weight: 900; margin: 0; line-height: 1.1; 
        text-transform: uppercase; letter-spacing: 1px;
    }
    .header-date { 
        font-size: 22px; /* DATA BEM VISÍVEL */
        font-weight: bold; color: #FFD700; /* AMARELO */
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

# --- 3. FUNÇÕES INTELIGENTES (CORRIGIDAS) ---

def extrair_data_do_arquivo(df_raw):
    # Procura data nas primeiras 20 linhas
    linhas_para_verificar = 20
    
    # PALAVRAS-CHAVE PARA DAR PRIORIDADE (Evita pegar datas aleatórias)
    keywords_prioridade = ["dia", "data", "escala", "serviço"]
    
    # 1. TENTA ACHAR DATA QUE TENHA "DIA" OU "DATA" NA MESMA LINHA (Prioridade Alta)
    for i in range(min(len(df_raw), linhas_para_verificar)):
        linha = df_raw.iloc[i].astype(str).values
        texto_linha = " ".join(linha).lower()
        
        # Só aceita se tiver uma palavra chave
        if any(k in texto_linha for k in keywords_prioridade):
            # Procura dd/mm/aaaa ou dd-mm-aaaa
            match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', texto_linha)
            if match:
                dia, mes, ano = match.groups()
                if len(ano) == 2: ano = "20" + ano
                try: return datetime(int(ano), int(mes), int(dia))
                except: continue
                
            # Procura formato yyyy-mm-dd (caso o Excel tenha convertido)
            match_iso = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', texto_linha)
            if match_iso:
                ano, mes, dia = match_iso.groups()
                try: return datetime(int(ano), int(mes), int(dia))
                except: continue

    # 2. SE NÃO ACHOU COM PALAVRA CHAVE, TENTA QUALQUER DATA (Fallback)
    for i in range(min(len(df_raw), linhas_para_verificar)):
        linha = df_raw.iloc[i].astype(str).values
        texto_linha = " ".join(linha).lower()
        
        match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', texto_linha)
        if match:
            dia, mes, ano = match.groups()
            if len(ano) == 2: ano = "20" + ano
            try: return datetime(int(ano), int(mes), int(dia))
            except: continue
            
    return None

def ler_rotas(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith('xlsx'): 
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try: df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except: df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')
            
        data_encontrada = extrair_data_do_arquivo(df_raw)
        
        header_idx = -1
        for index, row in df_raw.iterrows():
            txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in txt and "vpn" in txt:
                header_idx = index; break
        
        if header_idx == -1: return None, None
        
        df_raw.columns = df_raw.iloc[header_idx]
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df.columns = df.columns.astype(str).str.strip()
        df = df.loc[:, df.columns.notna()]
        if 'VPN' in df.columns: df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        return df, data_encontrada
    except: return None, None

# --- 4. CARREGAMENTO E DATA ---
df_rotas = None
data_final = None

# Tenta carregar arquivo
if os.path.exists("rotas.csv.xlsx"):
    with open("rotas.csv.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read()); mem.name = "rotas.csv.xlsx"
        df_rotas, data_detectada = ler_rotas(mem)

# Lógica de Data:
# 1. Verifica se existe arquivo de configuração manual (criado pelo Admin)
if os.path.exists("data_manual.txt"):
    try:
        with open("data_manual.txt", "r") as f:
            data_str = f.read().strip()
            data_final = datetime.strptime(data_str, "%Y-%m-%d")
    except: pass

# 2. Se não houver manual, usa a detectada no Excel
if data_final is None and 'data_detectada' in locals() and data_detectada:
    data_final = data_detectada

# 3. Se tudo falhar, usa hoje
if data_final is None:
    try: fuso = pytz.timezone('Europe/Lisbon'); data_final = datetime.now(fuso)
    except: data_final = datetime.now()

# Formata para exibir
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
    
    # CABEÇALHO (AGORA COM A DATA CERTA)
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
        
        # 1. UPLOAD
        st.subheader("1. Atualizar Arquivo")
        up_rotas = st.file_uploader("Arquivo Rotas (Excel/CSV)", type=['xlsx','csv'])
        if up_rotas:
            df_novo, data_det = ler_rotas(up_rotas)
            if df_novo is not None: 
                df_rotas = df_novo
                # Se carregou arquivo novo, apaga a data manual antiga para tentar detectar a nova
                if os.path.exists("data_manual.txt"): os.remove("data_manual.txt")
                
                msg = "✅ Rotas atualizadas!"
                if data_det: msg += f" Data detetada: {data_det.strftime('%d/%m')}"
                st.success(msg)
            else: st.error("Erro no arquivo.")
            
        st.markdown("---")
        
        # 2. CONTROLO MANUAL DE DATA
        st.subheader("2. Corrigir Data da Escala")
        st.info("Use isto se a data automática estiver errada.")
        
        # Define valor padrão do seletor
        padrao = data_final.date() if data_final else datetime.now().date()
        nova_data = st.date_input("Selecionar Data Correta:", value=padrao)
        
        if st.button("Salvar Data Manual"):
            with open("data_manual.txt", "w") as f:
                f.write(str(nova_data))
            st.success(f"Data fixada em {nova_data.strftime('%d/%m')}! (Dê Reboot App para aplicar)")
            
        if st.button("Voltar ao Automático"):
            if os.path.exists("data_manual.txt"): os.remove("data_manual.txt")
            st.success("Modo Automático restaurado.")

    elif senha: st.error("Senha incorreta!")
