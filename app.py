import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Minha Rota", page_icon="🚚")

# --- 1. FUNÇÃO DE LEITURA (Blindada para rotas.csv.xlsx) ---
def carregar_dados(uploaded_file):
    try:
        # Verifica se é Excel
        if uploaded_file.name.lower().endswith('xlsx'):
            df_raw = pd.read_excel(uploaded_file, header=None)
        else:
            # Verifica se é CSV
            try:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=';', encoding='latin1')
            except:
                df_raw = pd.read_csv(uploaded_file, header=None, sep=',', encoding='utf-8')

        # Procura cabeçalho
        header_idx = -1
        for index, row in df_raw.iterrows():
            linha_txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in linha_txt and "vpn" in linha_txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        # Ajusta dados
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

# --- 2. TENTA CARREGAR O ARQUIVO AUTOMATICAMENTE ---
df = None
nome_arquivo_oficial = "rotas.csv.xlsx" # Nome exato do arquivo

try:
    if os.path.exists(nome_arquivo_oficial):
        with open(nome_arquivo_oficial, "rb") as f:
            from io import BytesIO
            mem = BytesIO(f.read())
            mem.name = nome_arquivo_oficial
            df = carregar_dados(mem)
except:
    pass

# --- 3. BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.header("Gestão")
    if st.text_input("Senha Admin", type="password") == "admin123":
        st.success("Logado")
        upload = st.file_uploader("Carregar Arquivo", type=['xlsx', 'csv'])
        if upload:
            novo_df = carregar_dados(upload)
            if novo_df is not None:
                df = novo_df
                st.success("Atualizado com sucesso!")

# --- 4. TELA DO MOTORISTA ---
st.title("🚚 Minha Escala")

if df is not None:
    # Formulário para garantir que a digitação não trava
    with st.form(key='busca'):
        vpn_input = st.text_input("Digite o número da VPN:", placeholder="Ex: 76628")
        btn_buscar = st.form_submit_button("🔍 BUSCAR ROTA")

    if btn_buscar:
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            
            if not res.empty:
                row = res.iloc[0]
                
                # --- IDENTIFICAÇÃO ---
                st.success(f"Motorista: **{row.get('Motorista', '-') }**")
                
                # MUDANÇA AQUI: 4 Colunas, com Matrícula na esquerda e Móvel adicionado
                c1, c2, c3, c4 = st.columns(4)
                
                c1.metric("MATRÍCULA", str(row.get('Matrícula', '-'))) # <--- Lado Esquerdo
                c2.metric("ROTA", str(row.get('ROTA', '-')))
                c3.metric("LOJA", str(row.get('Nº LOJA', '-')))
                c4.metric("MÓVEL", str(row.get('Móvel', '-')))         # <--- Adicionado
                
                st.markdown("---")
                
                # --- HORÁRIOS ---
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.info(f"**Chegada Azambuja**\n\n### {row.get('Hora chegada Azambuja', '--')}")
                with col_h2:
                    st.warning(f"**Descarga Loja**\n\n### {row.get('Hora descarga loja', '--')}")

                # --- RETORNO E TIPO (PEQUENOS) ---
                st.markdown(f"""
                <div style="display: flex; gap: 20px; margin-top: 10px; padding: 10px; background-color: #f0f2f6; border-radius: 5px;">
                    <div>
                        <span style="font-size: 0.8em; color: gray;">RETORNO:</span><br>
                        <span style="font-weight: bold; color: #d32f2f;">{row.get('Retorno', '--')}</span>
                    </div>
                    <div style="border-left: 1px solid #ccc; padding-left: 20px;">
                        <span style="font-size: 0.8em; color: gray;">TIPO:</span><br>
                        <span style="font-weight: bold;">{row.get('TIPO', '-')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.caption(f"📍 Local Descarga: {row.get('Local descarga', '-')}")

                # --- TABELA DE CARGA ---
                st.subheader("📦 Manifesto de Carga")
                
                cols_carga = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", 
                              "Frota Refrigerado", "Peixe", "Talho", "Total Suportes"]
                
                dados_carga = {"Categoria": [], "Quantidade": []}
                
                for item in cols_carga:
                    qtd = str(row.get(item, '0'))
                    if qtd != '0' and qtd.lower() != 'nan':
                        nome_bonito = item.replace("Azambuja ", "").replace("Total ", "")
                        dados_carga["Categoria"].append(nome_bonito)
                        dados_carga["Quantidade"].append(qtd)
                
                if dados_carga["Categoria"]:
                    st.table(pd.DataFrame(dados_carga).set_index("Categoria"))
                else:
                    st.caption("Nenhuma carga específica registrada.")
                    
                # WhatsApp
                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 Obs: {row['WhatsApp']}")

            else:
                st.error("❌ VPN não encontrada.")
        else:
            st.warning("⚠️ Digite um número.")

else:
    st.warning("⚠️ Arquivo 'rotas.csv.xlsx' não encontrado.")
    st.info("O administrador precisa carregar a escala.")
