import streamlit as st
import pandas as pd

# Configuração simples (sem layouts complexos)
st.set_page_config(page_title="Rotas Logística", page_icon="🚚")

# --- 1. FUNÇÃO DE CARREGAMENTO (MANTIDA IGUAL) ---
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
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

# --- 2. CARREGAR ARQUIVO ---
df = None
try:
    with open("teste tfs.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read())
        mem.name = "teste tfs.xlsx"
        df = carregar_dados(mem)
except:
    pass

# --- 3. BARRA LATERAL (ADMIN) ---
# Usamos a sidebar padrão do Streamlit. Funciona sempre.
with st.sidebar:
    st.header("Área do Gestor")
    senha = st.text_input("Senha Admin", type="password")
    if senha == "admin123":
        st.success("Acesso Liberado")
        upload = st.file_uploader("Atualizar Escala", type=['xlsx','csv'])
        if upload:
            df_up = carregar_dados(upload)
            if df_up is not None:
                df = df_up
                st.success("Escala Atualizada!")

# --- 4. TELA PRINCIPAL (MOTORISTA) ---
st.title("🚚 Consulta de Rotas")

if df is not None:
    st.info("Digite sua VPN abaixo para ver a escala.")
    
    # --- MUDANÇA IMPORTANTE: FORMULÁRIO ---
    # Usar st.form ajuda muito no celular, pois evita recarregar a página enquanto digita
    with st.form(key='busca_rota'):
        # Input padrão, sem truques de esconder label
        vpn_input = st.text_input("Número da VPN:")
        submit_button = st.form_submit_button(label='🔍 BUSCAR AGORA')

    if submit_button:
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            if not res.empty:
                row = res.iloc[0]
                
                st.success(f"Motorista: {row.get('Motorista', 'Motorista')}")
                
                # Usando métricas nativas do Streamlit (são grandes e bonitas por padrão)
                c1, c2 = st.columns(2)
                c1.metric("ROTA", str(row.get('ROTA', '-')))
                c2.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                st.markdown("---")
                k1, k2 = st.columns(2)
                k1.metric("CHEGADA AZB", str(row.get('Hora chegada Azambuja', '--')))
                k2.metric("DESCARGA", str(row.get('Hora descarga loja', '--')))
                
                if row.get('Retorno'):
                     st.error(f"⚠️ RETORNO: {row.get('Retorno')}")

                st.markdown("### 📦 Carga")
                cols_check = ["Azambuja Ambiente", "Azambuja Congelados", "Peixe", "Talho", "Total Suportes"]
                dados = {"Item": [], "Qtd": []}
                for col in cols_check:
                    val = str(row.get(col, '0'))
                    if val != '0' and val.lower() != 'nan':
                        nome_limpo = col.replace("Azambuja ", "").replace("Total ", "")
                        dados["Item"].append(nome_limpo)
                        dados["Qtd"].append(val)
                
                if dados["Item"]:
                    st.table(pd.DataFrame(dados).set_index("Item"))
                else:
                    st.caption("Sem carga registrada.")
                    
                st.write(f"**Local:** {row.get('Local descarga','-')}")

            else:
                st.error(f"❌ VPN '{vpn_input}' não encontrada.")
        else:
            st.warning("Por favor, digite o número.")

else:
    st.warning("⚠️ O sistema está aguardando o arquivo de rotas.")
