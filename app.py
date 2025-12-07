import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Folha de Serviço", page_icon="🚛", layout="centered")

# --- CSS PARA AJUSTES VISUAIS ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    div[data-testid="stAlert"] {
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 Folha de Serviço Digital")

# --- FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    # O bloco try deve englobar toda a lógica de leitura
    try:
        nome_arquivo = uploaded_file.name.lower()
        df_raw = None
        
        # 1. Tenta ler o arquivo dependendo da extensão
        if nome_arquivo.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            # Tenta ler CSV com diferentes configurações
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')
        
        if df_raw is None:
            return None, "Erro na leitura do arquivo."

        # 2. Busca pela linha de cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            # Procura por "motorista" e "vpn" na mesma linha
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1:
            return None, "Não encontrei a linha de cabeçalho contendo 'Motorista' e 'VPN'."

        # 3. Aplica o cabeçalho e limpa os dados
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        
        # Remove colunas vazias
        df = df.loc[:, df.columns.notna()] 
        
        # Limpa a coluna VPN
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df, None
        else:
            return None, "Coluna VPN não encontrada após processamento."

    except Exception as e:
        # Se der qualquer erro acima, cai aqui
        return None, f"Erro técnico ao processar: {str(e)}"

# --- BARRA LATERAL ---
st.sidebar.header("Gestão")
arquivo = st.sidebar.file_uploader("Carregar Escala Atualizada", type=['xlsx', 'xls', 'csv'])

df = None

# Se o usuário fez upload
if arquivo:
    df, erro = carregar_dados(arquivo)
    if erro:
        st.error(erro)

# Se não fez upload, tenta ler arquivo local (backup)
if df is None:
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
    
    # Campo de busca
    vpn_input = st.text_input("Insira o número da VPN:", max_chars=10, placeholder="Ex: 76628")
    
    if st.button("Consultar Escala", type="primary"):
        vpn_input = vpn_input.strip()
        
        if vpn_input:
            # Filtra os dados
            res = df[df['VPN'] == vpn_input]
            
            if not res.empty:
                row = res.iloc[0]
                
                # --- EXIBIÇÃO DOS DADOS ---
                st.success(f"Motorista: **{row.get('Motorista', 'N/A')}**")
                
                # Bloco 1: Identificação
                st.markdown("### 🚛 Identificação")
                c1, c2, c3 = st.columns(3)
                c1.metric("Rota", str(row.get('ROTA', '-')))
                c2.metric("Matrícula", str(row.get('Matrícula', '-')))
                c3.metric("Loja Nº", str(row.get('Nº LOJA', '-')))

                # Bloco 2: Operação (Horários, Retorno, Tipo)
                st.markdown("### 🕒 Operação")
                k1, k2, k3, k4 = st.columns(4)
                
                with k1:
                    st.info(f"**Chegada Azb**\n\n{row.get('Hora chegada Azambuja', '--')}")
                with k2:
                    st.warning(f"**Descarga**\n\n{row.get('Hora descarga loja', '--')}")
                with k3:
                    st.error(f"**Retorno**\n\n{row.get('Retorno', '--')}")
                with k4:
                    st.metric("Tipo", str(row.get('TIPO', '-')))

                st.caption(f"📍 Local: {row.get('Local descarga', 'Não especificado')}")

                # Bloco 3: Tabela de Carga
                st.markdown("---")
                st.markdown("### 📦 Manifesto de Carga")
                
                dados_carga = {
                    "Categoria": [
                        "🌡️ Ambiente", 
                        "❄️ Congelados", 
                        "🍖 Salsesen", 
                        "🍦 Frota Refrigerado", 
                        "🐟 Peixe", 
                        "🥩 Talho",
                        "📦 Total Suportes"
                    ],
                    "Quantidade": [
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
                st.table(df_carga.set_index('Categoria'))

                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 **Obs:** {row['WhatsApp']}")

            else:
                st.error("⛔ VPN não encontrada.")
        else:
            st.warning("Por favor, digite a VPN.")
else:
    st.info("👈 Carregue a escala na barra lateral para começar.")
