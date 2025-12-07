import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rotas", page_icon="🚚", layout="centered")

# --- LEITURA DE DADOS ---
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, header=None)
        else:
            df = pd.read_csv(uploaded_file, header=None, sep=None, engine='python')

        # Procura cabeçalho
        header_idx = -1
        for index, row in df.iterrows():
            txt = row.astype(str).str.cat(sep=' ').lower()
            if "motorista" in txt and "vpn" in txt:
                header_idx = index
                break
        
        if header_idx == -1: return None
        
        df.columns = df.iloc[header_idx] 
        df = df.iloc[header_idx+1:].reset_index(drop=True)
        df = df.loc[:, df.columns.notna()]
        
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            return df
        return None
    except:
        return None

# Carrega arquivo local
df = None
try:
    with open("teste tfs.xlsx", "rb") as f:
        from io import BytesIO
        mem = BytesIO(f.read())
        mem.name = "teste tfs.xlsx"
        df = carregar_dados(mem)
except:
    pass

# Admin Sidebar
with st.sidebar:
    st.header("Admin")
    if st.text_input("Senha", type="password") == "admin123":
        up = st.file_uploader("Upload", type=['xlsx','csv'])
        if up:
            new_df = carregar_dados(up)
            if new_df is not None:
                df = new_df
                st.success("Ok")

# --- TELA MOTORISTA (MODO LISTA) ---
st.title("🚚 Minha Rota")

if df is not None:
    # 1. Cria lista de VPNs disponíveis
    # Adiciona uma opção vazia no início
    lista_vpns = ["Selecione..."] + sorted(df['VPN'].unique().tolist())
    
    st.info("Toque abaixo e selecione seu número:")
    
    # MUDANÇA: Selectbox em vez de Text Input
    # Isso usa o sistema nativo do celular, não tem como bloquear o teclado
    vpn_escolhida = st.selectbox("Sua VPN:", lista_vpns)
    
    if vpn_escolhida != "Selecione...":
        res = df[df['VPN'] == vpn_escolhida]
        if not res.empty:
            row = res.iloc[0]
            
            st.success(f"Motorista: {row.get('Motorista', '-')}")
            
            c1, c2 = st.columns(2)
            c1.metric("ROTA", str(row.get('ROTA', '-')))
            c2.metric("LOJA", str(row.get('Nº LOJA', '-')))
            
            st.warning(f"Chegada: {row.get('Hora chegada Azambuja', '--')}")
            st.error(f"Descarga: {row.get('Hora descarga loja', '--')}")
            
            with st.expander("📦 VER CARGA", expanded=True):
                 cols = ["Azambuja Ambiente", "Azambuja Congelados", "Peixe", "Talho", "Total Suportes"]
                 for c in cols:
                     val = str(row.get(c, '0'))
                     if val != '0' and val != 'nan':
                         st.write(f"**{c.replace('Azambuja ','')}:** {val}")

else:
    st.write("Aguardando dados...")
