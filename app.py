import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Rotas Logística", page_icon="🚚")

# --- 1. FUNÇÃO DE LEITURA (PREPARADA PARA O SEU ARQUIVO) ---
def carregar_dados(uploaded_file):
    try:
        # Tenta ler como Excel (Pois seu arquivo termina em .xlsx)
        if uploaded_file.name.lower().endswith('xlsx'):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            # Fallback para CSV
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        # Procura o cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        # Ajusta colunas
        df_raw.columns = df_raw.iloc[header_idx] 
        df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()]
        
        # Limpa VPN
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        return None
    except:
        return None

# --- 2. CARREGAMENTO AUTOMÁTICO DO ARQUIVO 'rotas.csv.xlsx' ---
df = None
nome_arquivo_oficial = "rotas.csv.xlsx"  # <--- AQUI ESTAVA O ERRO ANTES

try:
    if os.path.exists(nome_arquivo_oficial):
        with open(nome_arquivo_oficial, "rb") as f:
            from io import BytesIO
            mem = BytesIO(f.read())
            mem.name = nome_arquivo_oficial
            df = carregar_dados(mem)
except Exception as e:
    st.error(f"Erro ao tentar abrir o arquivo local: {e}")

# --- 3. BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.header("Área do Gestor")
    if st.text_input("Senha Admin", type="password") == "admin123":
        st.success("Logado")
        upload = st.file_uploader("Carregar Arquivo", type=['xlsx', 'csv'])
        if upload:
            novo_df = carregar_dados(upload)
            if novo_df is not None:
                df = novo_df
                st.success("Atualizado!")
            else:
                st.error("Formato inválido.")

# --- 4. TELA MOTORISTA ---
st.title("🚚 Consulta de Rotas")

if df is not None:
    st.write("Digite sua VPN:")
    
    # Campo de texto que funcionou no teste
    vpn_input = st.text_input("Número da VPN:", placeholder="Ex: 76628")
    
    if st.button("BUSCAR AGORA"):
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            if not res.empty:
                row = res.iloc[0]
                
                st.success(f"Motorista: {row.get('Motorista', '-')}")
                
                c1, c2 = st.columns(2)
                c1.metric("ROTA", str(row.get('ROTA', '-')))
                c2.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                st.info(f"Chegada: {row.get('Hora chegada Azambuja', '--')}")
                st.warning(f"Descarga: {row.get('Hora descarga loja', '--')}")
                
                if row.get('Retorno'):
                     st.error(f"RETORNO: {row.get('Retorno')}")

                st.markdown("### 📦 Carga")
                cols = ["Azambuja Ambiente", "Azambuja Congelados", "Peixe", "Talho", "Total Suportes"]
                dados = {"Tipo": [], "Qtd": []}
                for c in cols:
                    val = str(row.get(c, '0'))
                    if val != '0' and val.lower() != 'nan':
                         dados["Tipo"].append(c.replace("Azambuja ","").replace("Total ",""))
                         dados["Qtd"].append(val)
                
                if dados["Tipo"]:
                    st.table(pd.DataFrame(dados).set_index("Tipo"))
                else:
                    st.caption("Sem carga especial.")
            else:
                st.error("VPN não encontrada.")
        else:
            st.warning("Digite o número.")
else:
    st.warning(f"⚠️ O arquivo '{nome_arquivo_oficial}' não foi encontrado no GitHub.")
    st.info("Dica: Verifique se o nome do arquivo no GitHub é EXATAMENTE 'rotas.csv.xlsx'")
