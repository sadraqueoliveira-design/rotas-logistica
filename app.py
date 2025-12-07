import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Portal Logística - Rotas", page_icon="🚚", layout="centered")

st.title("🚚 Consulta de Rota Diária")

# Função robusta para carregar dados
def carregar_dados(uploaded_file):
    # Lista de tentativas de codificação (para lidar com acentos do Excel)
    encodings = ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
    # Lista de separadores (vírgula ou ponto e vírgula)
    separadores = [',', ';']
    
    df = None
    erro_msg = ""

    # Loop para tentar todas as combinações de codificação e separador
    for encoding in encodings:
        for sep in separadores:
            try:
                uploaded_file.seek(0) # Volta ao inicio do arquivo
                # Lê apenas as primeiras linhas para testar
                preview = pd.read_csv(uploaded_file, header=None, nrows=10, encoding=encoding, sep=sep)
                
                # Procura onde está o cabeçalho "Motorista"
                header_row = -1
                for i, row in preview.iterrows():
                    # Converte a linha toda para string para procurar a palavra chave
                    linha_texto = row.astype(str).str.cat(sep=' ')
                    if "Motorista" in linha_texto and "Telemóvel" in linha_texto:
                        header_row = i
                        break
                
                if header_row != -1:
                    # Se achou, lê o arquivo completo com essa configuração
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, header=header_row, encoding=encoding, sep=sep)
                    
                    # Limpeza das colunas chave
                    if 'VPN' in df.columns:
                        df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True)
                    if 'Telemóvel' in df.columns:
                        df['Telemóvel'] = df['Telemóvel'].astype(str).str.replace(r'\.0$', '', regex=True)
                    
                    return df, None # Sucesso!
            except Exception as e:
                erro_msg = str(e)
                continue # Tenta a próxima combinação

    return None, "Não foi possível ler o arquivo. Verifique se é um CSV válido."

# --- INTERFACE ---

# Upload do Arquivo (Admin)
st.sidebar.header("Área do Gestor")
arquivo = st.sidebar.file_uploader("Atualizar Escala (CSV)", type=['csv'])

df = pd.DataFrame() # Inicializa vazio para evitar erro

# Se não houver upload, tenta ler um arquivo padrão local (opcional)
if arquivo:
    df_carregado, erro = carregar_dados(arquivo)
    if df_carregado is not None:
        df = df_carregado
    else:
        st.error(f"Erro ao ler arquivo: {erro}")
else:
    # Tenta ler arquivo local se existir no GitHub
    try:
        # Truque para abrir arquivo local como se fosse upload
        with open("rotas.csv", "rb") as f:
            # Precisamos transformar num objeto compatível com a função
            from io import BytesIO
            f_bytes = BytesIO(f.read())
            df_local, erro = carregar_dados(f_bytes)
            if df_local is not None:
                df = df_local
    except:
        st.info("👈 Por favor, carregue o arquivo CSV na barra lateral.")

# Área de Login do Motorista
st.markdown("---")

if df is not None and not df.empty:
    st.subheader("Acesso do Motorista")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        login_id = st.text_input("Digite seu Telemóvel ou VPN:", max_chars=15)
    
    if st.button("Buscar Rota"):
        login_id = login_id.strip()
        
        # Verifica se as colunas existem antes de filtrar
        if 'Telemóvel' in df.columns and 'VPN' in df.columns:
            motorista = df[(df['Telemóvel'] == login_id) | (df['VPN'] == login_id)]

            if not motorista.empty:
                row = motorista.iloc[0]
                st.success(f"Olá, **{row['Motorista']}**!")
                
                # Layout dos dados
                c1, c2 = st.columns(2)
                c1.metric("🚛 Rota", str(row['ROTA']))
                c2.metric("📍 Loja Destino", str(row['Nº LOJA']))

                st.markdown("### 🕒 Detalhes da Viagem")
                st.info(f"**Chegada Azambuja:** {row.get('Hora chegada Azambuja', '--')} \n\n **Descarga:** {row.get('Hora descarga loja', '--')}")

                with st.expander("📦 Ver Carga (Clique para abrir)"):
                    st.write(f"**Local:** {row.get('Local descarga', '-')}")
                    st.write(f"**Suportes:** {row.get('Total Suportes', '-')}")
                    st.write(f"**Ambiente:** {row.get('Azambuja Ambiente', '-')}")
                    st.write(f"**Congelados:** {row.get('Azambuja Congelados', '-')}")
            else:
                st.warning("⚠️ Número não encontrado na escala de hoje.")
        else:
            st.error("Erro no arquivo: Colunas 'Telemóvel' ou 'VPN' não encontradas.")
else:
    if arquivo: # Só mostra erro se tentou carregar arquivo
        st.warning("O arquivo foi carregado mas parece estar vazio ou num formato irreconhecível.")
