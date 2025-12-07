import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="App Rotas", page_icon="🚛", layout="centered")

# --- ESTILO VISUAL (CSS SEGURO) ---
st.markdown("""
<style>
    /* 1. Esconde o menu do Streamlit e o rodapé "Made with Streamlit" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 2. Remove o espaço branco vazio do topo para o App subir */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    
    /* 3. Estilo da Barra Azul no Topo */
    .app-header {
        background-color: #004aad; /* Azul Logística */
        padding: 20px;
        text-align: center;
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-top: -6rem; /* Puxa para cima para cobrir tudo */
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 4. Estilo dos Cartões de Informação */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA DE TÍTULO (Fake App Bar) ---
st.markdown('<div class="app-header">🚛 Minha Escala</div>', unsafe_allow_html=True)

# --- 1. FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith('xlsx'):
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

# --- 2. CARREGAR ARQUIVO AUTOMÁTICO ---
df = None
nome_arquivo_oficial = "rotas.csv.xlsx"

try:
    if os.path.exists(nome_arquivo_oficial):
        with open(nome_arquivo_oficial, "rb") as f:
            from io import BytesIO
            mem = BytesIO(f.read())
            mem.name = nome_arquivo_oficial
            df = carregar_dados(mem)
except:
    pass

# --- 3. BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.header("⚙️ Gestão")
    if st.text_input("Senha Admin", type="password") == "admin123":
        st.success("Acesso Liberado")
        upload = st.file_uploader("Carregar Escala", type=['xlsx', 'csv'])
        if upload:
            novo_df = carregar_dados(upload)
            if novo_df is not None:
                df = novo_df
                st.success("Atualizado!")

# --- 4. TELA PRINCIPAL ---

if df is not None:
    # Espaço para não colar no topo
    st.write("") 
    
    # Formulário de Busca
    with st.form(key='busca_app'):
        # Texto explicativo simples
        st.markdown("**Digite sua VPN:**")
        vpn_input = st.text_input("vpn", label_visibility="collapsed", placeholder="Ex: 76628")
        
        # Botão largo (style via Streamlit padrão para não quebrar)
        btn_buscar = st.form_submit_button("🔍 BUSCAR MINHA ROTA", type="primary")

    if btn_buscar:
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            
            if not res.empty:
                row = res.iloc[0]
                
                # Nome do Motorista em destaque
                st.info(f"👤 **{row.get('Motorista', '-') }**")
                
                # Linha 1: Dados do Veículo/Rota
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MATRÍCULA", str(row.get('Matrícula', '-')))
                c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                c3.metric("ROTA", str(row.get('ROTA', '-')))
                c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                st.markdown("---")
                
                # Linha 2: Horários
                c_cheg, c_desc = st.columns(2)
                with c_cheg:
                    st.markdown(f"**🕒 Chegada Azambuja**")
                    st.markdown(f"## {row.get('Hora chegada Azambuja', '--')}")
                with c_desc:
                    st.markdown(f"**📦 Descarga Loja**")
                    st.markdown(f"## {row.get('Hora descarga loja', '--')}")

                # Linha 3: Retorno e Tipo (Estilo Etiqueta)
                st.markdown("<br>", unsafe_allow_html=True)
                col_ret, col_tipo = st.columns(2)
                col_ret.error(f"🔙 **Retorno:** {row.get('Retorno', '--')}")
                col_tipo.success(f"📋 **Tipo:** {row.get('TIPO', '-')}")

                # Linha 4: Carga
                with st.expander("📦 Ver Carga Detalhada", expanded=True):
                    cols_carga = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", 
                                  "Frota Refrigerado", "Peixe", "Talho", "Total Suportes"]
                    dados_carga = {"Categoria": [], "Qtd": []}
                    
                    for item in cols_carga:
                        qtd = str(row.get(item, '0'))
                        if qtd != '0' and qtd.lower() != 'nan':
                            nome_bonito = item.replace("Azambuja ", "").replace("Total ", "")
                            dados_carga["Categoria"].append(nome_bonito)
                            dados_carga["Qtd"].append(qtd)
                    
                    if dados_carga["Categoria"]:
                        st.table(pd.DataFrame(dados_carga).set_index("Categoria"))
                    else:
                        st.caption("Sem carga especial.")
                    
                    st.caption(f"📍 Local: {row.get('Local descarga', '-')}")
                
                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 Obs: {row['WhatsApp']}")

            else:
                st.error(f"❌ VPN {vpn_input} não encontrada.")
        else:
            st.warning("⚠️ Digite um número.")
else:
    st.warning("⚠️ Aguardando arquivo.")
