import streamlit as st
import pandas as pd

# Configuração simples padrão
st.set_page_config(page_title="Rotas Logística", page_icon="🚚")

# --- SEM CÓDIGOS CSS / SEM ESTILOS VISUAIS ---
# Removemos qualquer tentativa de estilizar para garantir que o clique funcione.

# --- 1. FUNÇÃO DE LEITURA (A MAIS ROBUSTA) ---
def carregar_dados(uploaded_file):
    try:
        # Tenta ler como Excel
        if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            # Tenta ler como CSV
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        # Procura a linha de cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        # Define cabeçalho e limpa
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()]
        
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        return None
    except:
        return None

# --- 2. CARREGAR DADOS ---
df = None
# Tenta ler arquivo local 'teste tfs.xlsx' se existir
try:
    with open("teste tfs.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read())
        mem.name = "teste tfs.xlsx"
        df = carregar_dados(mem)
except:
    pass

# --- 3. MENU ADMIN (BARRA LATERAL) ---
# Usamos o menu padrão, sem esconder nada
with st.sidebar:
    st.header("Área do Gestor")
    senha = st.text_input("Senha Admin", type="password")
    
    if senha == "admin123":
        st.success("Acesso Permitido")
        upload = st.file_uploader("Carregar Nova Escala", type=['xlsx', 'csv'])
        if upload:
            novo_df = carregar_dados(upload)
            if novo_df is not None:
                df = novo_df
                st.success("Arquivo carregado com sucesso!")
            else:
                st.error("Erro ao ler o arquivo.")

# --- 4. TELA DO MOTORISTA ---
st.title("🚚 Consulta de Rotas")

if df is not None:
    st.write("Digite o número da sua VPN abaixo:")
    
    # --- CAMPO DE TEXTO PADRÃO ---
    # Sem truques, sem formatação especial. É o componente nativo.
    vpn_input = st.text_input("Número da VPN", placeholder="Ex: 76628")
    
    if st.button("Pesquisar Rota"):
        vpn_input = vpn_input.strip()
        
        if vpn_input:
            # Filtra os dados
            resultado = df[df['VPN'] == vpn_input]
            
            if not resultado.empty:
                row = resultado.iloc[0]
                
                st.success(f"Olá, {row.get('Motorista', 'Motorista')}")
                
                # Exibe dados principais
                col1, col2, col3 = st.columns(3)
                col1.metric("Rota", str(row.get('ROTA', '-')))
                col2.metric("Loja", str(row.get('Nº LOJA', '-')))
                col3.metric("Matrícula", str(row.get('Matrícula', '-')))
                
                st.markdown("---")
                
                # Horários
                c_chegada, c_descarga = st.columns(2)
                c_chegada.info(f"Chegada Azambuja:\n\n**{row.get('Hora chegada Azambuja', '--')}**")
                c_descarga.warning(f"Descarga Loja:\n\n**{row.get('Hora descarga loja', '--')}**")
                
                if row.get('Retorno'):
                    st.error(f"Retorno: {row.get('Retorno')}")

                # Tabela de Carga
                st.subheader("📦 Detalhes da Carga")
                
                # Filtra colunas de carga para mostrar
                cols_carga = ["Azambuja Ambiente", "Azambuja Congelados", "Peixe", "Talho", "Total Suportes"]
                lista_carga = {"Tipo": [], "Quantidade": []}
                
                for item in cols_carga:
                    valor = str(row.get(item, '0'))
                    # Só mostra se tiver valor diferente de 0
                    if valor != '0' and valor.lower() != 'nan':
                        nome_limpo = item.replace("Azambuja ", "").replace("Total ", "")
                        lista_carga["Tipo"].append(nome_limpo)
                        lista_carga["Quantidade"].append(valor)
                
                if lista_carga["Tipo"]:
                    st.table(pd.DataFrame(lista_carga))
                else:
                    st.write("Nenhuma carga específica registrada.")
                    
                st.caption(f"Local de Descarga: {row.get('Local descarga', '-')}")
                
            else:
                st.error("Número de VPN não encontrado.")
        else:
            st.warning("Por favor, digite um número.")
else:
    st.info("Aguardando carregamento da planilha de rotas.")
