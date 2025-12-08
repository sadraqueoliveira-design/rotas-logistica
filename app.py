import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS ---
st.markdown("""
<style>
    .block-container{padding-top:1rem!important}
    .header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}
    .driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}
    .vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
    .vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}
    .vehicle-val{font-size:14px;font-weight:bold;color:#004aad}
    .time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}
    .carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}
    .info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}
    .info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}
    button[kind="primary"]{width:100%;height:50px;font-size:18px!important}
</style>
""", unsafe_allow_html=True)

# --- 3. LEITURA "CIRÚRGICA" DO SEU FICHEIRO ---
def ler_rotas(file_content):
    try:
        # 1. Lê a PRIMEIRA LINHA (Header=0) para pegar "Azambuja Ambiente", "Matricula", etc.
        try: df = pd.read_excel(file_content, header=0)
        except:
            file_content.seek(0)
            try: df = pd.read_csv(file_content, header=0, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                df = pd.read_csv(file_content, header=0, sep=',', encoding='latin1')

        # 2. CORREÇÃO FORÇADA DE COLUNAS (O SEGREDO)
        # No seu arquivo, a Coluna 1 é SEMPRE o Motorista e a Coluna 2 é SEMPRE a VPN.
        # Não importa o que diz o cabeçalho nessas posições.
        cols = list(df.columns)
        if len(cols) > 5:
            # Renomeia pelo Índice
            df.columns.values[1] = 'Motorista'
            df.columns.values[2] = 'VPN'
            
        # 3. Limpeza de Nomes das Colunas (Remove espaços duplos e extra espaços)
        df.columns = df.columns.astype(str).str.strip().str.replace('  ', ' ')
        
        # 4. Correção de Nomes Específicos
        mapa = {'Matricula': 'Matrícula', 'Movél': 'Móvel', 'NºLOJA': 'Nº LOJA'}
        for c_original in df.columns:
            for chave, valor in mapa.items():
                if chave.lower() in c_original.lower():
                    df.rename(columns={c_original: valor}, inplace=True)

        # 5. Filtragem de Linhas "Sujas" (Cabeçalhos repetidos e rodapés)
        if 'VPN' in df.columns:
            # Converte para texto e remove .0
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Remove linhas onde VPN é inválida ou é o próprio cabeçalho "VPN" repetido
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Garante que não é a linha de cabeçalho secundária
            df = df[df['Motorista'] != 'Motorista']

        return df
    except Exception as e:
        st.error(f"Erro leitura: {e}")
        return None

# --- VARIÁVEIS ---
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"
ADMINS = {"Admin": "123", "Gestor": "2025"}

# --- LÓGICA ---
if os.path.exists(DATE_FILE):
    with open(DATE_FILE, "r") as f: 
        dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
else: dt = datetime.now()

df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f: df_rotas = ler_rotas(BytesIO(f.read()))

# --- INTERFACE ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")
    if df_rotas is not None: 
        st.success(f"Carregado: {len(df_rotas)} rotas")
        # DEBUG: Mostra as colunas lidas para confirmar nomes
        with st.expander("Ver Colunas"): st.write(list(df_rotas.columns))

if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
    
    if df_rotas is not None:
        with st.form("busca"):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")
            
        if btn and vpn:
            # Filtro inteligente
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            if res.empty: res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    # CARTÃO MOTORISTA
                    st.markdown(f'<div class="driver-card">👤 {row.get("Motorista", "-")}</div>', unsafe_allow_html=True)
                    
                    # VEÍCULO
                    mat = row.get("Matrícula", row.get("Matricula", "-"))
                    mov = row.get("Móvel", row.get("Movél", "-"))
                    rota = row.get("ROTA", "-")
                    loja = row.get("Nº LOJA", "-")
                    st.markdown(f'''
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{mat}</div></div>
                        <div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{mov}</div></div>
                        <div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{rota}</div></div>
                        <div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{loja}</div></div>
                    </div>''', unsafe_allow_html=True)
                    
                    # HORÁRIOS
                    col_cheg = next((c for c in df_rotas.columns if "chegada" in c.lower()), 'Hora chegada Azambuja')
                    col_desc = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora descarga loja')
                    col_loc = next((c for c in df_rotas.columns if "local descarga" in c.lower()), 'Local descarga')
                    
                    c1, c2 = st.columns(2)
                    c1.markdown(f'<div class="time-block"><div>CHEGADA</div><h3>{row.get(col_cheg,"--")}</h3><b style="color:#004aad">AZAMBUJA</b></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="time-block" style="border-left-color:#d32f2f"><div>DESCARGA</div><h3>{row.get(col_desc,"--")}</h3><b style="color:#d32f2f">{str(row.get(col_loc,"Loja")).upper()}</b></div>', unsafe_allow_html=True)
                    
                    # CARGAS (IMPORTANTE: Lógica 'Pega Tudo')
                    # Ignoramos as colunas que já mostrámos acima
                    ignorar = ["motorista", "vpn", "matricula", "matrícula", "movel", "móvel", "rota", "loja", "hora", "chegada", "descarga", "local", "turno", "filtro", "retorno", "tipo", "total suportes"]
                    
                    cargas = {}
                    for col in df_rotas.columns:
                        # Se o nome da coluna não for um metadado (ignorar)
                        if not any(x in str(col).lower() for x in ignorar):
                            val = str(row.get(col, '')).strip()
                            # Se tiver valor (>0)
                            if val and val not in ['0', '0.0', 'nan', 'None', '']:
                                # Limpa o nome (Tira 'Azambuja', 'Salvesen', etc para ficar limpo)
                                nome_limpo = str(col).replace("Azambuja", "").replace("Salvesen", "").strip()
                                if not nome_limpo: nome_limpo = col
                                cargas[nome_limpo] = val
                    
                    if cargas:
                        st.markdown('<div class="carga-box"><b>📦 CARGA / PALETES</b>', unsafe_allow_html=True)
                        df_c = pd.DataFrame(list(cargas.items()), columns=["Tipo", "Qtd"])
                        st.table(df_c.set_index("Tipo"))
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.caption("Sem carga registada nesta linha.")

            else: st.error("Não encontrado.")
    else: st.warning("Sem dados. Vá a Gestão.")

elif menu == "Gestão":
    st.header("Gestão")
    p = st.text_input("Senha", type="password")
    if p == "123": # Senha Simples
        nd = st.date_input("Data:", value=dt)
        if st.button("Salvar Data"):
            with open(DATE_FILE, "w") as f: f.write(str(nd))
            st.rerun()
        
        up = st.file_uploader("Arquivo", type=['csv','xlsx'])
        if up:
            df = ler_rotas(up)
            if df is not None:
                st.write(f"Lido: {len(df)} linhas")
                st.dataframe(df.head())
                if st.button("Gravar"):
                    with open(DB_FILE, "wb") as f: f.write(up.getbuffer())
                    st.success("OK!"); st.rerun()
