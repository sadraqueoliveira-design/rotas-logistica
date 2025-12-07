import streamlit as st
import pandas as pd

st.set_page_config(page_title="Portal Logística", page_icon="🚚", layout="centered")
st.title("🚚 Consulta de Rota (Via VPN)")

# --- FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        nome_arquivo = uploaded_file.name.lower()
        df_raw = None
        
        # 1. Leitura do arquivo (Excel ou CSV)
        if nome_arquivo.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            # Tenta CSV com separadores comuns
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')
        
        if df_raw is None:
            return None, "Erro na leitura bruta do arquivo."

        # 2. Busca INTELIGENTE pelo Cabeçalho (Agora procurando VPN)
        header_idx = -1
        for index, row in df_raw.iterrows():
            # Converte a linha para texto minúsculo para facilitar a busca
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            
            # AQUI ESTÁ A MUDANÇA: Procura "Motorista" e "VPN" apenas
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1:
            return None, "Não encontrei a linha de cabeçalho contendo 'Motorista' e 'VPN'."

        # 3. Define o cabeçalho correto
        df_raw.columns = df_raw.iloc[header_idx] # Define a linha achada como titulo
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True) # Pega os dados dali pra baixo
        
        # 4. Limpeza da Coluna VPN (Essencial)
        # Remove colunas vazias
        df = df.loc[:, df.columns.notna()]
        
        if 'VPN' in df.columns:
            # Transforma em texto, tira o ".0" do Excel e tira espaços em branco
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df, None
        else:
            return None, "Cabeçalho encontrado, mas a coluna 'VPN' não foi identificada corretamente."

    except Exception as e:
        return None, f"Erro técnico: {str(e)}"

# --- INTERFACE ---

st.sidebar.header("Gestão")
arquivo = st.sidebar.file_uploader("Carregar Escala", type=['xlsx', 'xls', 'csv'])

df = None

# Lógica de Carregamento
if arquivo:
    df, erro = carregar_dados(arquivo)
    if erro:
        st.error(erro)

# Se não tiver arquivo carregado na hora, tenta ler um local (opcional)
if df is None:
    try:
        # Tenta ler um arquivo local caso você tenha feito upload no GitHub com esse nome
        with open("teste tfs.xlsx", "rb") as f:
             # Pequeno hack para reusar a função de leitura
            from io import BytesIO
            arquivo_memoria = BytesIO(f.read())
            arquivo_memoria.name = "teste tfs.xlsx" # Simula nome
            df, erro = carregar_dados(arquivo_memoria)
    except:
        pass

# --- TELA DE LOGIN ---
st.markdown("---")

if df is not None:
    st.subheader("Login do Motorista")
    
    # MUDANÇA: Campo pede apenas VPN
    vpn_input = st.text_input("Digite o número da sua VPN:", max_chars=10)
    
    if st.button("Ver Rota"):
        vpn_input = vpn_input.strip()
        
        if not vpn_input:
            st.warning("Por favor, digite a VPN.")
        else:
            # Filtra apenas pela coluna VPN
            try:
                # Garante que estamos comparando texto com texto
                resultado = df[df['VPN'] == vpn_input]
                
                if not resultado.empty:
                    linha = resultado.iloc[0]
                    st.success(f"Bem-vindo(a), **{linha.get('Motorista', 'Motorista')}**!")
                    
                    # Exibição dos Dados
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Rota", str(linha.get('ROTA', '-')))
                    c2.metric("Matrícula", str(linha.get('Matrícula', '-')))
                    c3.metric("Loja", str(linha.get('Nº LOJA', '-')))
                    
                    st.info(f"📅 **Chegada Azambuja:** {linha.get('Hora chegada Azambuja', '--')} | **Descarga:** {linha.get('Hora descarga loja', '--')}")
                    
                    # Detalhes técnicos
                    with st.expander("📦 Ver Detalhes de Carga"):
                        cols_carga = ['Total Suportes', 'Azambuja Ambiente', 'Azambuja Congelados', 'Local descarga']
                        # Filtra apenas as colunas que realmente existem no arquivo
                        cols_existentes = [c for c in cols_carga if c in linha]
                        if cols_existentes:
                            st.table(linha[cols_existentes].astype(str))
                        else:
                            st.write("Detalhes de carga não disponíveis nas colunas lidas.")
                else:
                    st.error(f"VPN '{vpn_input}' não encontrada na escala de hoje.")
            except Exception as e:
                st.error(f"Erro ao buscar: {e}")

else:
    st.info("👈 Aguardando carregamento do arquivo de escala.")
