import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Minha Rota", page_icon="🚚", layout="centered")

# --- CSS CORRIGIDO (PARA DESBLOQUEAR A DIGITAÇÃO) ---
st.markdown("""
<style>
    /* Remove o menu e rodapé completamente para não bloquear cliques */
    #MainMenu {display: none;}
    footer {display: none;}
    header {display: none;}
    
    /* Estilo do Botão */
    div.stButton > button {
        width: 100%;
        height: 3em;
        font-size: 20px;
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* CORREÇÃO DO CAMPO DE TEXTO */
    /* Garante que o campo esteja clicável e visível */
    div[data-testid="stTextInput"] {
        z-index: 1000; /* Traz para frente */
    }
    div[data-testid="stTextInput"] input {
        font-size: 20px;
        text-align: center;
        min-height: 50px;
    }
    
    /* Cartões */
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        border: 1px solid #e6e6e6;
    }
    .big-text { font-size: 1.5rem; font-weight: bold; color: #1f2937; }
    .small-text { font-size: 0.9rem; color: #6b7280; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

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

# --- LÓGICA DE DADOS ---
df = None
try:
    with open("teste tfs.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read())
        mem.name = "teste tfs.xlsx"
        df = carregar_dados(mem)
except:
    pass

# --- ÁREA DE ADMIN (MENU LATERAL) ---
with st.sidebar:
    st.header("🔧 Gestor")
    senha = st.text_input("Senha", type="password")
    if senha == "admin123":
        upload = st.file_uploader("Carregar Arquivo", type=['xlsx','csv'])
        if upload:
            df_up = carregar_dados(upload)
            if df_up is not None:
                df = df_up
                st.success("Atualizado!")

# --- TELA DO APP ---
st.markdown("<h2 style='text-align: center;'>🚚 Minha Escala</h2>", unsafe_allow_html=True)

if df is not None:
    # Campo de VPN
    st.write("") 
    vpn_input = st.text_input("Sua VPN:", placeholder="Digite aqui...", max_chars=10, label_visibility="collapsed")
    
    if st.button("🔍 VER MINHA ROTA"):
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            if not res.empty:
                row = res.iloc[0]
                
                # Exibição
                st.markdown(f"<div style='text-align:center; margin-bottom:15px; font-size:1.2rem;'>Olá, <b>{row.get('Motorista', 'Motorista')}</b></div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="small-text">ROTA</div>
                        <div class="big-text">{row.get('ROTA', '-')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="small-text">LOJA</div>
                        <div class="big-text">{row.get('Nº LOJA', '-')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-card" style="background-color: #e3f2fd; border: 1px solid #90caf9;">
                    <div class="small-text">CHEGADA AZAMBUJA</div>
                    <div class="big-text" style="color: #0d47a1;">{row.get('Hora chegada Azambuja', '--')}</div>
                </div>
                <div class="metric-card" style="background-color: #fff3e0; border: 1px solid #ffcc80;">
                    <div class="small-text">DESCARGA LOJA</div>
                    <div class="big-text" style="color: #e65100;">{row.get('Hora descarga loja', '--')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if row.get('Retorno'):
                     st.error(f"⚠️ **RETORNO:** {row.get('Retorno')}")

                with st.expander("📦 VER CARGA", expanded=False):
                    dados = {
                        "Item": ["Ambiente", "Congelados", "Peixe", "Talho", "Suportes"],
                        "Qtd": [
                            row.get('Azambuja Ambiente',0), 
                            row.get('Azambuja Congelados',0),
                            row.get('Peixe',0),
                            row.get('Talho',0),
                            row.get('Total Suportes',0)
                        ]
                    }
                    d_show = pd.DataFrame(dados)
                    d_show = d_show[d_show['Qtd'].astype(str) != '0'] 
                    if not d_show.empty:
                        st.table(d_show.set_index('Item'))
                    else:
                        st.info("Sem dados de carga.")
                    
                    st.caption(f"Local: {row.get('Local descarga','-')}")

            else:
                st.error("❌ VPN não encontrada.")
        else:
            st.warning("⚠️ Digite a VPN.")
else:
    st.info("Aguardando escala...")
