import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

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

# NOME DOS ARQUIVOS DE DADOS
DB_FILE = "dados_rotas.source" # Onde guardamos a planilha
DATE_FILE = "data_manual.txt"  # Onde guardamos a data

# --- 2. ESTILO CSS (Compacto e Correto) ---
st.markdown("""
<style>
    /* Oculta Rodapé mas MOSTRA O CABEÇALHO */
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;} 
    footer {visibility: hidden;}
    
    /* Ajuste do topo */
    .block-container {padding-top: 1rem; padding-bottom: 3rem;}
    
    /* CABEÇALHO DA PÁGINA (Azul com Data Amarela) */
    .header-box {
        background: linear-gradient(135deg, #004aad 0%, #003380 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .header-title { 
        font-size: 22px; font-weight: 900; margin: 0; line-height: 1.1; 
        text-transform: uppercase; letter-spacing: 1px;
    }
    .header-date { 
        font-size: 24px; /* DATA GRANDE */
        font-weight: bold; color: #FFD700; /* AMARELO */
        margin-top: 5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* CARTÃO MOTORISTA */
    .driver-card {
        background-color: #004aad; color: white;
        padding: 10px; border-radius: 8px;
        text-align: center; font-weight: bold; font-size: 1.2rem;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* GRELHA VEÍCULO (2x2) */
    .vehicle-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;
    }
    .vehicle-item {
        background-color: #e3f2fd; padding: 8px; border-radius: 6px; text-align: center;
        border: 1px solid #bbdefb;
    }
    .vehicle-label { font-size: 10px; color: #555; text-transform: uppercase; font-weight: bold; margin-bottom: 0;}
    .vehicle-val { font-size: 14px; font-weight: bold; color: #004aad; line-height: 1.1;}
    
    /* BLOCOS HORÁRIO */
    .time-block {
        background-color: #f8f9fa; padding: 10px; border-radius: 8px;
        border-left: 5px solid #004aad; margin-bottom: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .time-label { font-size: 0.75rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.6rem; font-weight: bold; color: #333; margin: 0; line-height: 1; }
    .location-highlight { font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-top: 2px;}
    .text-blue { color: #0d47a1; } .text-red { color: #d32f2f; }
    
    /* BARRA FINA (STATUS) */
    .info-row { display: flex; justify-content: space-between; gap: 6px; margin-top: 15px; margin-bottom: 15px; }
    .info-item { flex: 1; text-align: center; padding: 6px 2px; border-radius: 6px; color: white; font-size: 0.9rem;}
    .info-item-retorno { flex: 1; text-align: center; padding: 5px 2px; border-radius: 6px; background-color: white; border: 1px solid #ddd; }
    
    .info-label { font-size: 0.65rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 2px; line-height: 1;}
    .info-label-dark { font-size: 0.65rem; text-transform: uppercase; color: #666; display: block; margin-bottom: 2px; line-height: 1; font-weight: bold;}
    .info-val { font-size: 1.1rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; } .bg-green { background-color: #388e3c; }
    .rota-separator { text-align: center; margin: 30px 0 15px 0; font-size: 1rem; font-weight: bold; color: #004aad; background-color: #e3f2fd; padding: 8px; border-radius: 6px; border: 1px dashed #004aad;}

    /* Ajustes Gerais */
    div[data-testid="stTextInput"] { margin-bottom: 0px; }
    button[kind="primary"] { width: 100%; border-radius: 8px; height: 50px; font-weight: bold; font-size: 18px !important;}
</style>
""", unsafe_allow_html=True)

# --- 3. FUNÇÃO LEITURA ROBUSTA ---
def ler_rotas(file_content):
    """
    Lê o ficheiro (bytes) tentando descobrir onde começa o cabeçalho.
    Suporta CSV sujo (com 0s no inicio) e problemas de encoding.
    """
    try:
        # Tenta ler como Excel primeiro
        try:
            df_raw = pd.read_excel(file_content, header=None)
        except:
            # Se falhar, tenta CSV com diferentes encodings
            file_content.seek(0)
            try:
                df_raw = pd.read_csv(file_content, header=None, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try:
                    df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='utf-8')
                except:
                    file_content.seek(0)
                    df_raw = pd.read_csv(file_content, header=None, sep=',', encoding='latin1')

        # Procura a linha de cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            # Converte a linha toda para texto minúsculo para procurar palavras chave
            txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in txt and "vpn" in txt:
                header_idx = index
                break
        
        if header_idx == -1:
            return None

        # Define a linha de cabeçalho correta
        df_raw.columns = df_raw.iloc[header_idx]
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        
        # Limpa nomes das colunas (remove espaços extras)
        df.columns = df.columns.astype(str).str.strip()
        
        # Remove colunas vazias
        df = df.loc[:, df.columns.notna()]
        df = df.loc[:, df.columns != 'nan']

        # Limpeza da coluna VPN (remove .0 e espaços)
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Remove linhas onde VPN é '0', 'nan' ou vazio
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None'])]
            
        return df
    except Exception as e:
        st.error(f"Erro técnico na leitura: {e}")
        return None

# --- 4. CARREGAMENTO INICIAL ---
df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        mem = BytesIO(f.read())
        df_rotas = ler_rotas(mem)

# --- 5. DATA MANUAL (CONTROLO TOTAL) ---
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
    st.markdown("---")
    st.caption("Sistema de Rotas v2.1")

# ==================================================
# PÁGINA 1: MINHA ESCALA
# ==================================================
if menu == "🏠 Minha Escala":
    
    # CABEÇALHO COM DATA CERTA
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
            # Filtra ignorando maiúsculas/minúsculas
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            
            # Se não encontrou por VPN, tenta por nome motorista (busca parcial)
            if res.empty and len(vpn) > 3:
                 res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                total = len(res)
                for i, (idx, row) in enumerate(res.iterrows()):
                    # Separador se houver mais de uma viagem
                    if total > 1: 
                        st.markdown(f"<div class='rota-separator'>📍 VIAGEM {i+1} de {total}</div>", unsafe_allow_html=True)
                    
                    # 1. MOTORISTA
                    mot = row.get('Motorista', '-')
                    st.markdown(f"""<div class="driver-card">👤 {mot}</div>""", unsafe_allow_html=True)
                    
                    # 2. VEÍCULO (GRELHA 2x2)
                    st.markdown(f"""
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div class="vehicle-label">MATRÍCULA</div><div class="vehicle-val">{row.get('Matricula', row.get('Matrícula', '-'))}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">MÓVEL</div><div class="vehicle-val">{row.get('Movél', row.get('Móvel', '-'))}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">ROTA</div><div class="vehicle-val">{row.get('ROTA', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">LOJA</div><div class="vehicle-val">{row.get('NºLOJA', row.get('Nº LOJA', '-'))}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 3. HORÁRIOS
                    # Tenta pegar coluna 'Local descarga ' (com espaço) ou sem espaço
                    loc_desc = str(row.get('Local descarga ', row.get('Local descarga', 'Loja'))).upper()
                    
                    cc, cd = st.columns(2)
                    with cc: 
                        h_cheg = row.get('Hora chegada Azambuja', '--')
                        st.markdown(f"""<div class="time-block" style="border-left-color: #0d47a1;"><div class="time-label">CHEGADA</div><div class="time-value">{h_cheg}</div><div class="location-highlight text-blue">AZAMBUJA</div></div>""", unsafe_allow_html=True)
                    with cd: 
                        h_desc = row.get('Hora descarga loja ', row.get('Hora descarga loja', '--'))
                        st.markdown(f"""<div class="time-block" style="border-left-color: #d32f2f;"><div class="time-label">DESCARGA</div><div class="time-value">{h_desc}</div><div class="location-highlight text-red">{loc_desc}</div></div>""", unsafe_allow_html=True)
                    
                    # 4. BARRA FINA
                    v_sup = '0'
                    # Procura coluna de suportes flexivelmente
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
                    
                    # 5. CARGA
                    with st.expander(f"🔎 Ver Carga Viagem {i+1}"):
                        cols = ["Azambuja   Ambiente", "Azambuja Congelados", "Salvesen  Azambuja", "Fruta Refrigerado", "Peixe", "Talho"]
                        dd = {"Categoria": [], "Paletes": []}
                        
                        # Itera sobre todas colunas do excel para achar match parcial
                        for c_excel in df_rotas.columns:
                            for c_ref in cols:
                                # Se o nome da coluna do excel contiver a palavra chave
                                if c_ref.split()[0].lower() in c_excel.lower():
                                    val = str(row.get(c_excel, '0'))
                                    # Se tiver valor real
                                    if val not in ['0', 'nan', '', '0.0']:
                                        clean_name = c_excel.replace("Azambuja", "").strip()
                                        dd["Categoria"].append(clean_name if clean_name else c_excel)
                                        dd["Paletes"].append(val)
                        
                        # Remove duplicados se houver e exibe
                        if dd["Categoria"]:
                            df_carga = pd.DataFrame(dd).drop_duplicates()
                            st.table(df_carga.set_index("Categoria"))
                        else:
                            st.caption("Nenhuma carga registada nesta linha.")
                        
            else: 
                st.error(f"❌ Nenhuma rota encontrada para: {vpn}")
                st.caption("Verifique se digitou a VPN correta ou o nome do motorista.")
        else:
            if not btn: st.info("👆 Digite a VPN acima e clique em VER ROTAS.")
    else:
        st.warning("⚠️ Nenhuma escala carregada no sistema.")
        st.markdown("**Peça ao gestor para carregar o ficheiro no menu Gestão.**")

# ==================================================
# PÁGINA 2: GESTÃO
# ==================================================
elif menu == "⚙️ Gestão / Upload":
    st.header("🔐 Área de Gestão")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.selectbox("Usuário", ["Selecionar..."] + list(ADMINS.keys()))
    with col2:
        senha = st.text_input("Senha", type="password")
    
    if usuario != "Selecionar..." and senha == ADMINS.get(usuario):
        st.success(f"🔓 Acesso permitido: {usuario}")
        
        # 1. SELETOR DE DATA MANUAL
        st.subheader("1. Configurar Data da Escala")
        nova_data = st.date_input("Data que aparece no App:", value=data_final)
        
        if st.button("💾 Atualizar Data"):
            with open(DATE_FILE, "w") as f: f.write(str(nova_data))
            st.success(f"Data mudada para {nova_data.strftime('%d/%m/%Y')}!")
            st.rerun() # Atualiza a página imediatamente
            
        st.markdown("---")
        
        # 2. UPLOAD ARQUIVO
        st.subheader("2. Carregar Planilha de Rotas")
        st.info("O sistema aceita Excel (.xlsx) ou CSV (.csv).")
        up_rotas = st.file_uploader("Arraste o ficheiro aqui", type=['xlsx','csv'])
        
        if up_rotas:
            # Mostra preview
            df_preview = ler_rotas(up_rotas)
            
            if df_preview is not None:
                st.write(f"✅ Pré-visualização: {len(df_preview)} linhas encontradas.")
                st.dataframe(df_preview.head(3))
                
                if st.button("🚀 CONFIRMAR E CARREGAR FICHEIRO"):
                    # GRAVA O ARQUIVO NO DISCO PARA PERSISTIR
                    with open(DB_FILE, "wb") as f:
                        f.write(up_rotas.getbuffer())
                    
                    st.success("✅ Arquivo gravado com sucesso! A escala foi atualizada.")
                    st.balloons()
            else:
                st.error("Erro ao ler o ficheiro. Verifique se tem as colunas 'Motorista' e 'VPN'.")
            
    elif senha: 
        st.error("⛔ Senha incorreta!")
