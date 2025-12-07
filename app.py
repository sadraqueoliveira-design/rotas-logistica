import streamlit as st
import pandas as pd

# Configuração da página para parecer um App
st.set_page_config(page_title="Folha de Serviço", page_icon="🚛", layout="centered")

# --- CSS PARA ESTILO (OPCIONAL) ---
# Isso deixa as tabelas mais bonitas e tira o padding excessivo
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 Folha de Serviço Digital")

# --- FUNÇÃO DE LEITURA (Blindada) ---
def carregar_dados(uploaded_file):
    try:
        nome_arquivo = uploaded_file.name.lower()
        df_raw = None
        
        # 1. Leitura
        if nome_arquivo.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')
        
        if df_raw is None:
            return None, "Erro na leitura."

        # 2. Busca Cabeçalho (Procurando Motorista e VPN)
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1:
            return None, "Não encontrei a linha de cabeçalho (Motorista/VPN)."

        # 3. Organiza
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()] # Remove colunas sem nome
        
        # 4. Limpeza VPN
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df, None
        else:
            return None, "Coluna VPN não encontrada."

    except Exception as e:
        return None, f"Erro: {str(e)}"

# --- BARRA LATERAL ---
st.sidebar.header("Gestão")
arquivo = st.sidebar.file_uploader("Carregar Escala Atualizada", type=['xlsx', 'xls', 'csv'])

df = None
if arquivo:
    df, erro = carregar_dados(arquivo)
    if erro:
        st.error(erro)

# Tenta ler local se não houver upload
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
    vpn_input = st.text_input("Insira o número da VPN:", max_chars=10, placeholder="Ex: 76628")
    
    if st.button("Consultar Escala Completa", type="primary"):
        vpn_input = vpn_input.strip()
        
        if vpn_input:
            # Busca
            res = df[df['VPN'] == vpn_input]
            
            if not res.empty:
                row = res.iloc[0] # Pega a primeira linha encontrada
                
                # --- CABEÇALHO DO MOTORISTA ---
                st.success(f"Motorista: **{row.get('Motorista', 'N/A')}**")
                
                # --- BLOCO 1: DADOS DA ROTA ---
                st.markdown("### 🚛 Dados da Viagem")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Rota", str(row.get('ROTA', '-')))
                c2.metric("Matrícula", str(row.get('Matrícula', '-')))
                c3.metric("Loja Nº", str(row.get('Nº LOJA', '-')))
                c4.metric("Tipo", str(row.get('TIPO', '-')))

                # --- BLOCO 2: HORÁRIOS ---
                st.markdown("### 🕒 Cronograma")
                col_h1, col_h2, col_h3 = st.columns(3)
                
                with col_h1:
                    st.info(f"**Chegada Azambuja**\n# {row.get('Hora chegada Azambuja', '--')}")
                with col_h2:
                    st.warning(f"**Descarga Loja**\n# {row.get('Hora descarga loja', '--')}")
                with col_h3:
                    st.error(f"**Retorno**\n# {row.get('Retorno', '--')}")

                st.write(f"📍 **Local de Descarga:** {row.get('Local descarga', 'Não especificado')}")

                # --- BLOCO 3: DETALHE DA CARGA (TABELA) ---
                st.markdown("---")
                st.markdown("### 📦 Manifesto de Carga")
                
                # Criar um dicionário apenas com os dados de carga para exibir limpo
                # Usamos .get() para garantir que não quebre se a coluna não existir
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
                # Exibe a tabela sem o índice (números 0,1,2 na esquerda)
                st.table(df_carga.set_index('Categoria'))

                # --- BLOCO 4: CONTACTOS ---
                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.markdown(f"📱 **Observação:** {row['WhatsApp']}")

            else:
                st.error("⛔ VPN não encontrada. Verifique se digitou corretamente.")
        else:
            st.warning("Por favor, digite a VPN.")
else:
    st.info("👈 O sistema aguarda o upload da escala do dia.")
