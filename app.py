import streamlit as st
import pandas as pd

# Configuração básica
st.set_page_config(page_title="Minha Rota", page_icon="🚚", layout="centered")

# --- CSS LIMPO (Apenas para esconder o menu e aumentar o botão) ---
# Removi qualquer código que mexa na caixa de texto (Input) para evitar bloqueios
st.markdown("""
<style>
    /* Esconde menu e rodapé */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Aumenta apenas o Botão para ficar fácil de clicar */
    div.stButton > button {
        width: 100%;
        height: 3em;
        font-size: 18px;
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* Estilo dos Cartões de Informação */
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        border: 1px solid #ddd;
    }
    .big-text { font-size: 1.4rem; font-weight: bold; color: #333; }
    .small-text { font-size: 0.9rem; color: #666; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        # Tenta ler Excel ou CSV
        if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        # Busca cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()]
        
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        return None
    except:
        return None

# --- CARREGAR ARQUIVO (Memória ou Upload) ---
df = None
try:
    with open("teste tfs.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read())
        mem.name = "teste tfs.xlsx"
        df = carregar_dados(mem)
except:
    pass

# --- MENU ADMIN (LATERAL) ---
with st.sidebar:
    st.header("🔧 Admin")
    senha = st.text_input("Senha", type="password")
    if senha == "admin123":
        st.success("Logado")
        upload = st.file_uploader("Carregar Escala", type=['xlsx','csv'])
        if upload:
            df_up = carregar_dados(upload)
            if df_up is not None:
                df = df_up
                st.success("✅ Atualizado!")

# --- TELA PRINCIPAL ---
st.markdown("<h2 style='text-align: center;'>🚚 Minha Escala</h2>", unsafe_allow_html=True)

if df is not None:
    st.write("Digite sua VPN abaixo:")
    
    # Campo simples, sem estilo customizado, para garantir funcionamento
    vpn_input = st.text_input("VPN", label_visibility="collapsed", placeholder="Ex: 76628")
    
    # Botão de busca
    if st.button("🔍 BUSCAR ROTA"):
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            if not res.empty:
                row = res.iloc[0]
                
                # Exibição dos dados
                st.markdown(f"<div style='text-align:center; margin-bottom:10px; font-size:1.2rem;'>Olá, <b>{row.get('Motorista', 'Motorista')}</b></div>", unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""<div class="metric-card"><div class="small-text">ROTA</div><div class="big-text">{row.get('ROTA', '-')}</div></div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div class="metric-card"><div class="small-text">LOJA</div><div class="big-text">{row.get('Nº LOJA', '-')}</div></div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-card" style="background-color: #e3f2fd; border-color: #90caf9;">
                    <div class="small-text">CHEGADA AZAMBUJA</div>
                    <div class="big-text" style="color: #0d47a1;">{row.get('Hora chegada Azambuja', '--')}</div>
                </div>
                <div class="metric-card" style="background-color: #fff3e0; border-color: #ffcc80;">
                    <div class="small-text">DESCARGA LOJA</div>
                    <div class="big-text" style="color: #e65100;">{row.get('Hora descarga loja', '--')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if row.get('Retorno'):
                     st.error(f"⚠️ RETORNO: {row.get('Retorno')}")

                with st.expander("📦 VER CARGA"):
                    cols_check = ["Azambuja Ambiente", "Azambuja Congelados", "Peixe", "Talho", "Total Suportes"]
                    dados = {"Item": [], "Qtd": []}
                    
                    for col in cols_check:
                        val = str(row.get(col, '0'))
                        if val != '0' and val.lower() != 'nan':
                            # Limpa o nome da coluna para ficar bonito
                            nome_limpo = col.replace("Azambuja ", "").replace("Total ", "")
                            dados["Item"].append(nome_limpo)
                            dados["Qtd"].append(val)
                            
                    if dados["Item"]:
                        st.table(pd.DataFrame(dados).set_index("Item"))
                    else:
                        st.info("Sem carga registrada.")
                    
                    st.caption(f"Local: {row.get('Local descarga','-')}")

            else:
                st.error("❌ VPN não encontrada.")
        else:
            st.warning("Digite o número.")
else:
    st.info("⚠️ Aguardando carregamento da escala.")
