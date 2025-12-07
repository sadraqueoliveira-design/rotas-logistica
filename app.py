import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Folha de Serviço", page_icon="🚛", layout="centered")

# --- CSS PARA ESTILO ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 5px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    /* Estilo para as etiquetas menores */
    .small-label {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 0px;
    }
    .small-value {
        font-size: 1.1rem;
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 Folha de Serviço Digital")

# --- FUNÇÃO DE LEITURA (MANTIDA) ---
def carregar_dados(uploaded_file):
    try:
        nome_arquivo = uploaded_file.name.lower()
        df_raw = None
        
        if nome_arquivo.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')
        
        if df_raw is None:
            return None, "Erro na leitura."

        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1:
            return None, "Não encontrei a linha de cabeçalho."

        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()] 
        
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df, None
        else:
            return None, "Coluna VPN não encontrada."

    except Exception as e:
        return None, f"Erro: {str(e)}"

# --- BARRA LATERAL ---
st.sidebar.header("Gestão")
arquivo = st.sidebar.file_uploader("Carregar Escala", type=['xlsx', 'xls', 'csv'])

df = None
if arquivo:
    df, erro = carregar_dados(arquivo)
    if erro:
        st.error(erro)
else:
    try:
        with open("teste tfs.xlsx", "rb") as f:
            from io import BytesIO
            arquivo_memoria = BytesIO(f.read())
            arquivo_memoria.name = "teste tfs.xlsx"
            df, erro = carregar_dados(arquivo_memoria)
    except:
        pass

# --- TELA PRINCIPAL ---

if df is not None:
    st.markdown("---")
    st.subheader("🔒 Acesso do Motorista")
    vpn_input = st.text_input("Insira o número da VPN:", max_chars=10, placeholder="Ex: 76628")
    
    if st.button("Consultar Escala", type="primary"):
        vpn_input = vpn_input.strip()
        
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            
            if not res.empty:
                row = res.iloc[0]
                
                # --- CABEÇALHO ---
                st.success(f"Motorista: **{row.get('Motorista', 'N/A')}**")
                
                # --- ID ---
                c1, c2, c3 = st.columns(3)
                c1.metric("Rota", str(row.get('ROTA', '-')))
                c2.metric("Matrícula", str(row.get('Matrícula', '-')))
                c3.metric("Loja Nº", str(row.get('Nº LOJA', '-')))

                # --- OPERAÇÃO (AJUSTADO) ---
                st.markdown("### 🕒 Operação")
                
                # Colunas: 30% | 30% | 15% | 15%
                k1, k2, k3, k4 = st.columns([3, 3, 1.5, 1.5])
                
                with k1:
                    st.info(f"**Chegada Azambuja**\n\n### {row.get('Hora chegada Azambuja', '--')}")
                with k2:
                    st.warning(f"**Descarga Loja**\n\n### {row.get('Hora descarga loja', '--')}")
                
                # Retorno e Tipo menores e sem caixa colorida
                with k3:
                    st.markdown('<p class="small-label">Retorno</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="small-value">{row.get("Retorno", "--")}</p>', unsafe_allow_html=True)
                with k4:
                    st.markdown('<p class="small-label">Tipo</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="small-value">{row.get("TIPO", "-")}</p>', unsafe_allow_html=True)

                st.caption(f"📍 Local Descarga: {row.get('Local descarga', 'Não especificado')}")

                # --- CARGA ---
                st.markdown("---")
                st.markdown("### 📦 Manifesto")
                
                dados_carga = {
                    "Categoria": ["🌡️ Ambiente", "❄️ Congelados", "🍖 Salsesen", "🍦 Frota Refrig.", "🐟 Peixe", "🥩 Talho", "📦 Suportes"],
                    "Qtd": [
                        row.get('Azambuja Ambiente', '0'),
                        row.get('Azambuja Congelados', '0'),
                        row.get('Salsesen Azambuja', '0'),
                        row.get('Frota Refrigerado', '0'),
                        row.get('Peixe', '0'),
                        row.get('Talho', '0'),
                        row.get('Total Suportes', '0')
                    ]
                }
                
                df_carga = pd.DataFrame(dados_carga)
                # Filtra linhas onde a quantidade é 0 ou vazia para limpar a tela
                df_carga = df_carga[ (df_carga['Qtd'].astype(str) != '0') & (df_carga['Qtd'].astype(str) != 'nan') ]
                
                if not df_carga.empty:
                    st.table(df_carga.set_index('Categoria'))
                else:
                    st.info("Sem cargas registradas para esta rota.")

                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 **Obs:** {row['WhatsApp']}")

            else:
                st.error("⛔ VPN não encontrada.")
        else:
            st.warning("Por favor, digite a VPN.")
else:
    st.info("👈 Carregue a escala na barra lateral.")
