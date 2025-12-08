import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
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

# --- 2. ESTILO CSS (Separado para evitar erros) ---
CSS_STYLE = """
<style>
    /* Ajuste de Espaçamento e Menu */
    .block-container {padding-top: 1rem !important; padding-bottom: 5rem !important;}
    #MainMenu {visibility: visible !important;}
    header {visibility: visible !important;} 
    footer {visibility: hidden;}
    
    /* Cabeçalho */
    .header-box {
        background-color: #004aad;
        padding: 20px; 
        border-radius: 12px; 
        text-align: center; 
        color: white;
        margin-bottom: 25px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        border: 2px solid #003380;
    }
    .header-title { 
        font-size: 28px !important; font-weight: 900 !important; 
        margin: 0 !important; line-height: 1.2 !important; 
        text-transform: uppercase; letter-spacing: 1px;
    }
    .header-date { 
        font-size: 22px !important; font-weight: bold !important; 
        color: #FFD700 !important; margin-top: 8px !important; 
    }
    
    /* Cartões */
    .driver-card {
        background-color: #004aad; color: white; padding: 10px; border-radius: 8px;
        text-align: center; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px;
    }
    .vehicle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
    .vehicle-item { background-color: #e3f2fd; padding: 8px; border-radius: 6px; text-align: center; border: 1px solid #bbdefb; }
    .vehicle-label { font-size: 10px; color: #555; text-transform: uppercase; font-weight: bold; margin-bottom: 0;}
    .vehicle-val { font-size: 14px; font-weight: bold; color: #004aad; line-height: 1.1;}
    
    /* Blocos de Tempo */
    .time-block {
        background-color: #f8f9fa; padding: 10px; border-radius: 8px;
        border-left: 6px solid #004aad; margin-bottom: 5px;
    }
    .time-label { font-size: 0.75rem; color: #666; font-weight: bold; text-transform: uppercase; margin: 0; }
    .time-value { font-size: 1.6rem; font-weight: bold; color: #333; margin: 0; line-height: 1; }
    .location-highlight { font-size: 0.85rem; font-weight: 800; text-transform: uppercase; margin-top: 2px;}
    .text-blue { color: #0d47a1; } .text-red { color: #d32f2f; }
    
    /* Rodapé do Cartão */
    .info-row { display: flex; justify-content: space-between; gap: 6px; margin-top: 15px; margin-bottom: 15px; }
    .info-item { flex: 1; text-align: center; padding: 6px 2px; border-radius: 6px; color: white; font-size: 0.9rem;}
    .info-item-retorno { flex: 1; text-align: center; padding: 5px 2px; border-radius: 6px; background-color: white; border: 1px solid #ddd; }
    .info-label { font-size: 0.65rem; text-transform: uppercase; opacity: 0.9; display: block; margin-bottom: 2px; line-height: 1;}
    .info-label-dark { font-size: 0.65rem; text-transform: uppercase; color: #666; display: block; margin-bottom: 2px; line-height: 1; font-weight: bold;}
    .info-val { font-size: 1.1rem; font-weight: bold; line-height: 1.1; }
    
    .bg-purple { background-color: #7b1fa2; } .bg-green { background-color: #388e3c; }
    .rota-separator { text-align: center; margin: 30px 0 15px 0; font-size: 1rem; font-weight: bold; color: #004aad; background-color: #e3f2fd; padding: 8px; border-radius: 6px; border: 1px dashed #004aad;}
    
    /* Tabela de Carga */
    .carga-box { background-color: #fff; border: 1px solid #eee; border-radius: 8px; padding: 10px; margin-top: 10px; }
    .carga-title { font-size: 0.8rem; font-weight: bold; color: #444; margin-bottom: 5px; text-transform: uppercase; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    
    button[kind="primary"] { width: 100%; border-radius: 8px; height: 50px; font-weight: bold; font-size: 18px !important;}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# --- 3. FUNÇÃO LEITURA ---
def ler_rotas(file_content):
    try:
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

        cols = list(df.columns)
        # Se houver colunas suficientes, renomeia as chaves principais
        if len(cols) > 3:
            # Assume que a col 1 é Motorista e 2 é VPN
            df.rename(columns={cols[1]: 'Motorista', cols[2]: 'VPN'}, inplace=True)
            
        df.columns = df.columns.astype(str).str.strip()
        
        correcoes = {'Matricula': 'Matrícula', 'Movél': 'Móvel', 'NºLOJA': 'Nº LOJA'}
        for errado, certo in correcoes.items():
            for c_real in df.columns:
                if errado.lower() in c_real.lower():
                    df.rename(columns={c_real: certo}, inplace=True)

        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
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
    if df_rotas is not None: st.success(f"Dados: {len(df_rotas)} rotas")

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
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            if res.empty and len(vpn) > 3:
                 res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                total = len(res)
                for i, (idx, row) in enumerate(res.iterrows()):
                    if total > 1: st.markdown(f"<div class='rota-separator'>📍 VIAGEM {i+1} de {total}</div>", unsafe_allow_html=True)
                    
                    # Motorista
                    st.markdown(f"""<div class="driver-card">👤 {row.get('Motorista', '-')}</div>""", unsafe_allow_html=True)
                    
                    # Veículo
                    st.markdown(f"""
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div class="vehicle-label">MATRÍCULA</div><div class="vehicle-val">{row.get('Matrícula', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">MÓVEL</div><div class="vehicle-val">{row.get('Móvel', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">ROTA</div><div class="vehicle-val">{row.get('ROTA', '-')}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">LOJA</div><div class="vehicle-val">{row.get('Nº LOJA', '-')}</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Horários
                    h_cheg_col = next((c for c in df_rotas.columns if "chegada" in c.lower()), 'Hora chegada Azambuja')
                    loc_col = next((c for c in df_rotas.columns if "local descarga" in c.lower()), 'Local descarga')
                    h_desc_col = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora descarga loja')
                    
                    loc_desc = str(row.get(loc_col, 'Loja')).upper()
                    
                    cc, cd = st.columns(2)
                    with cc: st.markdown(f"""<div class="time-block" style="border-left-color: #0d47a1;"><div class="time-label">CHEGADA</div><div class="time-value">{row.get(h_cheg_col, '--')}</div><div class="location-highlight text-blue">AZAMBUJA</div></div>""", unsafe_allow_html=True)
                    with cd: st.markdown(f"""<div class="time-block" style="border-left-color: #d32f2f;"><div class="time-label">DESCARGA</div><div class="time-value">{row.get(h_desc_col, '--')}</div><div class="location-highlight text-red">{loc_desc}</div></div>""", unsafe_allow_html=True)
                    
                    # Info Extra
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

                    # Cargas
                    keywords_carga = ["ambiente", "congelados", "salvesen", "fruta", "refrigerado", "peixe", "talho", "recolha"]
                    
                    carga_dict = {}
                    for col in df_rotas.columns:
                        if any(x in col.lower() for x in ["hora", "chegada", "descarga", "motorista", "vpn", "matricula", "rota", "loja", "tipo", "retorno", "total suportes"]): continue
                        if any(k in col.lower() for k in keywords_carga):
                            val = str(row.get(col, '0')).strip()
                            if val not in ['0', 'nan', '', '0.0', 'None']:
                                clean_name = col.replace("Azambuja", "").replace("Total", "").strip()
                                if clean_name == "": clean_name = col
                                carga_dict[clean_name] = val
                    
                    if carga_dict:
                        st.markdown('<div class="carga-box"><div class="carga-title">📦 DETALHES DA CARGA</div>', unsafe_allow_html=True)
                        df_carga = pd.DataFrame(list(carga_dict.items()), columns=["Categoria", "Qtd"])
                        st.markdown("""<style>thead tr th:first-child {display:none} tbody th {display:none}</style>""", unsafe_allow_html=True)
                        st.table(df_carga.set_index("Categoria"))
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.caption("ℹ️ Sem carga.")

            else: st.error(f"❌ Não encontrado: {vpn}")
        else:
            if not btn: st.info("👆 Digite a VPN acima.")
    else: st.warning("⚠️ Nenhuma escala carregada.")

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
        nova_data = st.date_input("Data da Escala:", value=data_final)
        if st.button("💾 Atualizar Data"):
            with open(DATE_FILE, "w") as f: f.write(str(nova_data))
            st.success("Data salva!"); st.rerun()

        st.markdown("---")
        up_rotas = st.file_uploader("Carregar Planilha (Excel/CSV)", type=['xlsx','csv'])
        if up_rotas:
            df_preview = ler_rotas(up_rotas)
            if df_preview is not None:
                st.write(f"✅ {len(df_preview)} linhas identificadas.")
                st.dataframe(df_preview.head(3))
                if st.button("🚀 CONFIRMAR UPLOAD"):
                    with open(DB_FILE, "wb") as f: f.write(up_rotas.getbuffer())
                    st.success("Arquivo gravado!"); st.balloons()
            else: st.error("Erro na leitura.")
    elif senha: st.error("⛔ Senha incorreta!")
