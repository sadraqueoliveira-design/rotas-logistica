import streamlit as st
import pandas as pd

st.set_page_config(page_title="Portal Logística", page_icon="🚚", layout="centered")
st.title("🚚 Consulta de Rota")

# --- FUNÇÃO DE LEITURA INTELIGENTE ---
def carregar_dados(uploaded_file):
    try:
        # Verifica a extensão do arquivo
        nome_arquivo = uploaded_file.name.lower()
        
        df_raw = None
        
        # 1. Se for Excel (.xlsx ou .xls)
        if nome_arquivo.endswith(('.xlsx', '.xls')):
            # Lê o Excel inteiro sem cabeçalho primeiro
            df_raw = pd.read_excel(uploaded_file, header=None)
            
        # 2. Se for CSV
        else:
            # Tenta ler com diferentes configurações
            encodings = ['utf-8', 'latin1', 'cp1252']
            separadores = [';', ',', '\t']
            
            for enc in encodings:
                for sep in separadores:
                    try:
                        uploaded_file.seek(0)
                        df_raw = pd.read_csv(uploaded_file, header=None, encoding=enc, sep=sep)
                        # Se leu mais de uma coluna, provavel que acertou o separador
                        if df_raw.shape[1] > 1:
                            break 
                    except:
                        continue
                if df_raw is not None and df_raw.shape[1] > 1:
                    break
        
        if df_raw is None:
            return None, "Formato de arquivo não reconhecido."

        # --- BUSCA PELO CABEÇALHO ---
        # Agora procuramos em qual linha está a palavra "Motorista"
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "telemóvel" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1:
            return None, "Não encontrei a linha de cabeçalho com 'Motorista' e 'Telemóvel'."

        # Recria o DataFrame usando a linha correta como cabeçalho
        df_raw.columns = df_raw.iloc[header_idx] # Define a linha achada como titulo
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True) # Pega os dados dali pra baixo
        
        # Limpeza de colunas essenciais
        cols_existentes = [c for c in df.columns if isinstance(c, str)] # Garante que colunas são strings
        df = df[cols_existentes] # Remove colunas NaN
        
        # Limpa VPN e Telemovel (tira .0 e espaços)
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        if 'Telemóvel' in df.columns:
            df['Telemóvel'] = df['Telemóvel'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
        return df, None

    except Exception as e:
        return None, f"Erro técnico: {str(e)}"

# --- INTERFACE ---

st.sidebar.header("Gestão")
arquivo = st.sidebar.file_uploader("Carregar Escala (Excel ou CSV)", type=['xlsx', 'xls', 'csv'])

df = None

# Tenta carregar o arquivo (Upload ou Local)
if arquivo:
    df, erro = carregar_dados(arquivo)
    if erro:
        st.error(erro)
else:
    # Tenta ler localmente (para quando você subir o arquivo no GitHub)
    try:
        # Tenta achar o Excel primeiro
        with open("teste tfs.xlsx", "rb") as f: # Se você subiu o xlsx
             pass # Só check
        # Se chegou aqui, tenta ler
        # (Logica simplificada para web: use o uploader lateral para testar primeiro)
        st.info("👈 Por favor, carregue o arquivo Excel na barra lateral.")
    except:
        st.info("👈 Carregue o arquivo na barra lateral.")

if df is not None:
    st.success("Arquivo carregado com sucesso!")
    st.markdown("---")
    
    st.subheader("Login do Motorista")
    login = st.text_input("Digite o Nº de Telemóvel ou VPN:")
    
    if st.button("Ver Rota"):
        login = login.strip()
        if not login:
            st.warning("Digite um número.")
        else:
            # Filtro
            try:
                res = df[ (df['Telemóvel'] == login) | (df['VPN'] == login) ]
                
                if not res.empty:
                    linha = res.iloc[0]
                    st.balloons()
                    st.header(f"Olá, {linha['Motorista']}")
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Rota", linha['ROTA'])
                    c2.metric("Matrícula", linha['Matrícula'])
                    c3.metric("Loja", linha['Nº LOJA'])
                    
                    st.info(f"**Horário:** Chegada {linha.get('Hora chegada Azambuja','?')} ➝ Descarga {linha.get('Hora descarga loja','?')}")
                    
                    with st.expander("Ver Detalhes da Carga"):
                        st.table(linha[['Total Suportes', 'Azambuja Ambiente', 'Azambuja Congelados']].astype(str))
                else:
                    st.error("Motorista não encontrado nesta escala.")
            except Exception as e:
                st.error(f"Erro ao filtrar: {e}")
