import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# ARQUIVOS E SENHAS
ADMINS = {"Admin Principal": "admin123", "Gestor Tráfego": "trafego2025", "Escritório": "office99"}
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"

# --- 2. ESTILO CSS (Simplificado para evitar erros de sintaxe) ---
st.markdown('<style>.block-container{padding-top:1rem!important;padding-bottom:5rem!important}#MainMenu{visibility:visible!important}header{visibility:visible!important}footer{visibility:hidden}.header-box{background-color:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:25px;box-shadow:0 4px 8px rgba(0,0,0,.2);border:2px solid #003380}.header-title{font-size:26px!important;font-weight:900!important;margin:0!important;text-transform:uppercase}.header-date{font-size:20px!important;font-weight:bold!important;color:#FFD700!important;margin-top:5px!important}.driver-card{background-color:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}.vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}.vehicle-item{background-color:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}.vehicle-label{font-size:10px;color:#555;text-transform:uppercase;font-weight:bold;margin-bottom:0}.vehicle-val{font-size:14px;font-weight:bold;color:#004aad;line-height:1.1}.time-block{background-color:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}.time-label{font-size:.75rem;color:#666;font-weight:bold;text-transform:uppercase;margin:0}.time-value{font-size:1.6rem;font-weight:bold;color:#333;margin:0;line-height:1}.location-highlight{font-size:.85rem;font-weight:800;text-transform:uppercase;margin-top:2px}.text-blue{color:#0d47a1}.text-red{color:#d32f2f}.info-row{display:flex;justify-content:space-between;gap:6px;margin-top:15px;margin-bottom:15px}.info-item{flex:1;text-align:center;padding:6px 2px;border-radius:6px;color:white;font-size:.9rem}.info-item-retorno{flex:1;text-align:center;padding:5px 2px;border-radius:6px;background-color:white;border:1px solid #ddd}.info-label{font-size:.65rem;text-transform:uppercase;opacity:.9;display:block;margin-bottom:2px;line-height:1}.info-label-dark{font-size:.65rem;text-transform:uppercase;color:#666;display:block;margin-bottom:2px;line-height:1;font-weight:bold}.info-val{font-size:1.1rem;font-weight:bold;line-height:1.1}.bg-purple{background-color:#7b1fa2}.bg-green{background-color:#388e3c}.rota-separator{text-align:center;margin:30px 0 15px 0;font-size:1rem;font-weight:bold;color:#004aad;background-color:#e3f2fd;padding:8px;border-radius:6px;border:1px dashed #004aad}.carga-box{background-color:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}.carga-title{font-size:.8rem;font-weight:bold;color:#444;margin-bottom:5px;text-transform:uppercase;border-bottom:1px solid #eee;padding-bottom:5px}button[kind="primary"]{width:100%;border-radius:8px;height:50px;font-weight:bold;font-size:18px!important}</style>', unsafe_allow_html=True)

# --- 3. FUNÇÃO LEITURA ---
def ler_rotas(file_content):
    try:
        # Tenta ler com diferentes configurações
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

        # Renomeia colunas 1 e 2 para garantir que pegamos Motorista e VPN
        cols = list(df.columns)
        if len(cols) > 3:
            df.rename(columns={cols[1]: 'Motorista', cols[2]: 'VPN'}, inplace=True)
            
        df.columns = df.columns.astype(str).str.strip()
        
        # Correção de Nomes
        correcoes = {'Matricula': 'Matrícula', 'Movél': 'Móvel', 'NºLOJA': 'Nº LOJA'}
        for errado, certo in correcoes.items():
            for c_real in df.columns:
                if errado.lower() in c_real.lower():
                    df.rename(columns={c_real: certo}, inplace=True)

        # Filtra Lixo
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Remove linhas inválidas
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Remove linhas de cabeçalho repetido
            df = df[df['Motorista'] != 'Motorista']

        return df
    except Exception as e:
        st.error(f"Erro ao processar ficheiro: {e}")
        return None

# --- 4. CARREGAMENTO DADOS ---
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
dias_sem = {0:"Domingo", 1:"Segunda", 2:"Terça", 3:"Quarta", 4:"Quinta", 5:"Sexta", 6:"Sábado"}
dia_str = dias_sem[data_final.weekday()]

# --- 6. MENU ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center'>🚛 LOGÍSTICA</h2>", unsafe_allow_html=True)
    menu = st.radio("Menu", ["🏠 Escala", "⚙️ Gestão"], label_visibility="collapsed")
    if df_rotas is not None: 
        st.success(f"Carregado: {len(df_rotas)} rotas")
        # DEBUG: Mostra colunas se expandir (útil para verificar nomes das cargas)
        with st.expander("Ver Colunas (Debug)"):
            st.write(list(df_rotas.columns))

# ==================================================
# PÁGINA 1: ESCALA
# ==================================================
if menu == "🏠 Escala":
    st.markdown(f'<div class="header-box"><div class="header-title">ESCALA DIÁRIA</div><div class="header-date">📅 {dia_str}, {data_hoje_str}</div></div>', unsafe_allow_html=True)

    if df_rotas is not None:
        with st.form(key='busca'):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("vpn", placeholder="VPN ou Nome", label_visibility="collapsed")
            btn = c2.form_submit_button("🔍 BUSCAR", type="primary")

        if btn and vpn:
            # Filtro
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            if res.empty and len(vpn) > 3:
                res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                total = len(res)
                for i, (idx, row) in enumerate(res.iterrows()):
                    if total > 1: st.markdown(f"<div class='rota-separator'>📍 VIAGEM {i+1} de {total}</div>", unsafe_allow_html=True)
                    
                    # Motorista
                    st.markdown(f'<div class="driver-card">👤 {row.get("Motorista", "-")}</div>', unsafe_allow_html=True)
                    
                    # Veículo
                    st.markdown(f'''
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div class="vehicle-label">MATRÍCULA</div><div class="vehicle-val">{row.get("Matrícula", "-")}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">MÓVEL</div><div class="vehicle-val">{row.get("Móvel", "-")}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">ROTA</div><div class="vehicle-val">{row.get("ROTA", "-")}</div></div>
                        <div class="vehicle-item"><div class="vehicle-label">LOJA</div><div class="vehicle-val">{row.get("Nº LOJA", "-")}</div></div>
                    </div>''', unsafe_allow_html=True)
                    
                    # Horários
                    col_cheg = next((c for c in df_rotas.columns if "chegada" in c.lower()), 'Hora chegada Azambuja')
                    col_loc = next((c for c in df_rotas.columns if "local descarga" in c.lower()), 'Local descarga')
                    col_desc = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora descarga loja')
                    
                    tc1, tc2 = st.columns(2)
                    with tc1: st.markdown(f'<div class="time-block" style="border-left-color:#0d47a1"><div class="time-label">CHEGADA</div><div class="time-value">{row.get(col_cheg,"--")}</div><div class="location-highlight text-blue">AZAMBUJA</div></div>', unsafe_allow_html=True)
                    with tc2: st.markdown(f'<div class="time-block" style="border-left-color:#d32f2f"><div class="time-label">DESCARGA</div><div class="time-value">{row.get(col_desc,"--")}</div><div class="location-highlight text-red">{str(row.get(col_loc,"Loja")).upper()}</div></div>', unsafe_allow_html=True)
                    
                    # Rodapé
                    v_ret = str(row.get('Retorno', '-'))
                    cor_ret = "#008000" if v_ret not in ['0','-','nan','Vazio','None'] else "#333"
                    v_sup = str(row.get('Total Suportes', row.get('Total Suportes ', '0')))
                    
                    st.markdown(f'''
                    <div class="info-row">
                        <div class="info-item bg-purple"><span class="info-label">SUPORTES</span><span class="info-val">📦 {v_sup}</span></div>
                        <div class="info-item-retorno"><span class="info-label-dark">RETORNO</span><span class="info-val" style="color:{cor_ret}">{v_ret}</span></div>
                        <div class="info-item bg-green"><span class="info-label">TIPO</span><span class="info-val">{row.get("TIPO", "-")}</span></div>
                    </div>''', unsafe_allow_html=True)

                    # --- CARGAS (LÓGICA AUTOMÁTICA) ---
                    # Lista de colunas a ignorar (Metadados)
                    ignorar = ["motorista","vpn","matricula","matrícula","movel","móvel","rota","loja","hora","chegada","descarga","local","turno","filtro","retorno","tipo","total suportes"]
                    
                    dados_carga = {}
                    for col in df_rotas.columns:
                        c_low = str(col).lower()
                        # Se NÃO for metadado, assume que é carga
                        if not any(x in c_low for x in ignorar):
                            val = str(row.get(col, '')).strip()
                            # Se tiver valor válido (>0)
                            if val and val not in ['0', '0.0', '0,0', 'nan', 'None', '']:
                                # Limpa nome
                                nome_limpo = str(col).replace("Azambuja", "").replace("Total", "").strip()
                                if not nome_limpo: nome_limpo = col
                                dados_carga[nome_limpo] = val
                    
                    if dados_carga:
                        st.markdown('<div class="carga-box"><div class="carga-title">📦 DETALHES DA CARGA</div>', unsafe_allow_html=True)
                        df_c = pd.DataFrame(list(dados_carga.items()), columns=["Item", "Qtd"])
                        st.markdown("<style>thead{display:none}tbody th{display:none}td{padding:4px 8px!important;border-bottom:1px solid #f0f0f0}</style>", unsafe_allow_html=True)
                        st.table(df_c.set_index("Item"))
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.caption("Sem carga extra.")

            else: st.error("❌ Não encontrado.")
        else:
            if not btn: st.info("👆 Digite a VPN.")
    else: st.warning("⚠️ Nenhuma escala carregada. Vá a Gestão.")

# ==================================================
# PÁGINA 2: GESTÃO
# ==================================================
elif menu == "⚙️ Gestão":
    st.header("🔐 Gestão")
    u = st.selectbox("Usuário", ["..."] + list(ADMINS.keys()))
    p = st.text_input("Senha", type="password")
    
    if u != "..." and p == ADMINS.get(u):
        st.success(f"Olá {u}")
        nd = st.date_input("Data App:", value=data_final)
        if st.button("💾 Salvar Data"):
            with open(DATE_FILE, "w") as f: f.write(str(nd))
            st.success("Data salva!"); st.rerun()
            
        st.markdown("---")
        up = st.file_uploader("Arquivo Rotas", type=['xlsx','csv'])
        if up:
            dfp = ler_rotas(up)
            if dfp is not None:
                st.write(f"✅ {len(dfp)} linhas.")
                if st.button("🚀 UPLOAD"):
                    with open(DB_FILE, "wb") as f: f.write(up.getbuffer())
                    st.success("Guardado!"); st.balloons()
            else: st.error("Erro leitura.")
    elif p: st.error("Senha errada.")
