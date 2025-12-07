import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Portal Logística - Rotas", page_icon="🚚", layout="centered")

st.title("🚚 Consulta de Rota Diária")

# Função para encontrar o cabeçalho correto
def carregar_dados(uploaded_file):
    try:
        # Tenta ler as primeiras linhas para achar onde está a coluna "Motorista"
        # Lê as primeiras 5 linhas
        preview = pd.read_csv(uploaded_file, header=None, nrows=5)
        
        # Procura em qual linha está a palavra "Motorista"
        header_row = -1
        for i, row in preview.iterrows():
            if row.astype(str).str.contains("Motorista").any():
                header_row = i
                break
        
        if header_row == -1:
            return None, "Coluna 'Motorista' não encontrada."

        # Lê o arquivo novamente usando a linha correta como cabeçalho
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, header=header_row)
        
        # Limpeza básica
        df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True)
        df['Telemóvel'] = df['Telemóvel'].astype(str).str.replace(r'\.0$', '', regex=True)
        return df, None
    except Exception as e:
        return None, str(e)

# Upload do Arquivo (Admin)
st.sidebar.header("Área do Gestor")
arquivo = st.sidebar.file_uploader("Atualizar Escala (CSV)", type=['csv'])

# Se não houver upload, tenta ler um arquivo padrão local (opcional)
df = pd.DataFrame()
if arquivo:
    df, erro = carregar_dados(arquivo)
    if erro:
        st.error(f"Erro ao ler arquivo: {erro}")
else:
    st.info("👈 Por favor, carregue o arquivo CSV na barra lateral.")

# Área de Login do Motorista
st.markdown("---")

if not df.empty:
    st.subheader("Acesso do Motorista")
    st.write("Digite seu **Telemóvel** ou **VPN** para visualizar sua rota.")
    
    login_id = st.text_input("Identificação:", max_chars=15)

    if st.button("Buscar Rota"):
        # Limpar espaços em branco que possam vir do Excel
        login_id = login_id.strip()
        
        # Filtrar o motorista (busca exata)
        motorista = df[(df['Telemóvel'] == login_id) | (df['VPN'] == login_id)]

        if not motorista.empty:
            row = motorista.iloc[0]
            
            st.success(f"Olá, **{row['Motorista']}**!")
            
            # Cartões de Informação
            c1, c2 = st.columns(2)
            c1.metric("🚛 Rota", str(row['ROTA']))
            c2.metric("📍 Loja Destino", str(row['Nº LOJA']))

            st.markdown("### 🕒 Detalhes da Viagem")
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"**Chegada Azambuja:**\n{row['Hora chegada Azambuja']}")
            with col_b:
                st.warning(f"**Hora Descarga:**\n{row['Hora descarga loja']}")

            with st.expander("📦 Ver Detalhes da Carga (Clique aqui)"):
                st.write(f"**Local Descarga:** {row['Local descarga']}")
                st.write(f"**Total Suportes:** {row['Total Suportes']}")
                st.write(f"**Ambiente:** {row['Azambuja Ambiente']}")
                st.write(f"**Congelados:** {row['Azambuja Congelados']}")
                
        else:
            st.error("❌ Número não encontrado. Verifique se digitou corretamente ou contacte o tráfego.")