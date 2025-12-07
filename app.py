import streamlit as st
import pandas as pd

# Configuração da página para parecer App Nativo
st.set_page_config(page_title="Minha Rota", page_icon="🚚", layout="centered")

# --- CSS: ESTILO DE APLICATIVO ---
# Isso remove margens extras, esconde menus e deixa botões grandes
st.markdown("""
<style>
    /* Esconde o menu hamburger e rodapé do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Botão Grande e Verde */
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
    
    /* Input de Texto Grande */
    div[data-testid="stTextInput"] input {
        font-size: 20px;
        text-align: center;
        height: 50px;
    }
    
    /* Cartões de Info */
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
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

# --- LÓGICA DE DADOS ---
# Tenta ler arquivo local (padrão)
df = None
try:
    with open("teste tfs.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read())
        mem.name = "teste tfs.xlsx"
        df = carregar_dados(mem)
except:
    pass

# --- ÁREA DE ADMIN (ESCONDIDA) ---
# Só aparece se clicar na sidebar, útil para você atualizar o arquivo pelo celular
with st.sidebar:
    st.header("🔧 Área do Gestor")
    senha = st.text_input("Senha Admin", type="password")
    if senha == "admin123": # <--- Mude sua senha aqui se quiser
        upload = st.file_uploader("Atualizar Escala Hoje", type=['xlsx','csv'])
        if upload:
            df_up = carregar_dados(upload)
            if df_up is not None:
                df = df_up
                st.success("Escala Atualizada!")

# --- TELA DO APP (MOTORISTA) ---
st.markdown("<h2 style='text-align: center;'>🚚 Minha Escala</h2>", unsafe_allow_html=True)

if df is not None:
    st.write("") # Espaço
    vpn_input = st.text_input("", placeholder="Digite sua VPN aqui", max_chars=10)
    
    if st.button("🔍 VER MINHA ROTA"):
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            if not res.empty:
                row = res.iloc[0]
                
                # NOME
                st.markdown(f"<div style='text-align:center; margin-bottom:15px; font-size:1.2rem;'>Olá, <b>{row.get('Motorista', 'Motorista')}</b></div>", unsafe_allow_html=True)
                
                # CARTÕES GRANDES (Mobile Friendly)
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

                # HORÁRIOS EM DESTAQUE
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
                
                # INFORMAÇÃO RETORNO
                if row.get('Retorno'):
                     st.error(f"⚠️ **RETORNO:** {row.get('Retorno')}")

                # TABELA DE CARGA SIMPLIFICADA
                with st.expander("📦 VER CARGA (Clique Aqui)", expanded=False):
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
                    # Só mostra o que tem quantidade > 0
                    d_show = d_show[d_show['Qtd'].astype(str) != '0'] 
                    st.table(d_show.set_index('Item'))
                    
                    st.caption(f"Local: {row.get('Local descarga','-')}")

            else:
                st.error("❌ VPN não encontrada.")
        else:
            st.warning("⚠️ Digite a VPN.")
else:
    st.info("Aguardando escala...")
