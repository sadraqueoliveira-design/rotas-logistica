import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="App Rotas",
    page_icon="https://img.icons8.com/ios-filled/50/4a90e2/truck.png",
    layout="centered"
)

# --- 2. CÁLCULO DA DATA E DIA DA SEMANA ---
# Pega a data de hoje
agora = datetime.now()
data_formatada = agora.strftime("%d/%m/%Y") # Ex: 07/12/2025

# Traduz o dia da semana (Python devolve 0 para Segunda, 6 para Domingo)
dias_pt = {
    0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 
    3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"
}
dia_semana = dias_pt[agora.weekday()]

# --- 3. ESTILO VISUAL (CSS) ---
st.markdown("""
<style>
    /* Esconde menus do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    
    /* ESTILO DA BARRA AZUL */
    .app-header {
        background-color: #004aad;
        padding: 15px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-top: -6rem; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .app-header img {
        width: 50px;
        height: auto;
    }
    
    /* Texto do Título */
    .header-text-group {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    
    .app-title {
        font-size: 22px;
        font-weight: bold;
        line-height: 1.2;
    }
    
    .app-date {
        font-size: 14px;
        opacity: 0.9;
        font-weight: normal;
    }
    
    /* Cartões */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 4. BARRA DE TÍTULO (Com Data Dinâmica) ---
# Usamos f-string para inserir as variáveis Python no HTML
st.markdown(f"""
<div class="app-header">
    <img src="https://img.icons8.com/ios-filled/100/ffffff/truck.png">
    <div class="header-text-group">
        <div class="app-title">Minha Escala</div>
        <div class="app-date">{dia_semana}, {data_formatada}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. FUNÇÃO DE LEITURA ---
def carregar_dados(uploaded_file):
    try:
        if uploaded_file.name.lower().endswith('xlsx'):
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

# --- 6. CARREGAR ARQUIVO AUTOMÁTICO ---
df = None
nome_arquivo = "rotas.csv.xlsx"

try:
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "rb") as f:
            from io import BytesIO
            mem = BytesIO(f.read())
            mem.name = nome_arquivo
            df = carregar_dados(mem)
except:
    pass

# --- 7. MENU ADMIN ---
with st.sidebar:
    st.header("⚙️ Gestão")
    if st.text_input("Senha Admin", type="password") == "admin123":
        up = st.file_uploader("Carregar Escala", type=['xlsx', 'csv'])
        if up:
            novo = carregar_dados(up)
            if novo is not None:
                df = novo
                st.success("Atualizado!")

# --- 8. TELA PRINCIPAL ---
if df is not None:
    st.write("") 
    
    with st.form(key='busca_app'):
        st.markdown("**Digite sua VPN:**")
        vpn_input = st.text_input("vpn", label_visibility="collapsed", placeholder="Ex: 76628")
        btn_buscar = st.form_submit_button("🔍 BUSCAR MINHA ROTA", type="primary")

    if btn_buscar:
        vpn_input = vpn_input.strip()
        if vpn_input:
            res = df[df['VPN'] == vpn_input]
            
            if not res.empty:
                row = res.iloc[0]
                
                # Exibição
                st.info(f"👤 **{row.get('Motorista', '-') }**")
                
                # ORDEM: Matrícula | Móvel | Rota | Loja
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("MATRÍCULA", str(row.get('Matrícula', '-')))
                c2.metric("MÓVEL", str(row.get('Móvel', '-')))
                c3.metric("ROTA", str(row.get('ROTA', '-')))
                c4.metric("LOJA", str(row.get('Nº LOJA', '-')))
                
                st.markdown("---")
                
                cc, cd = st.columns(2)
                with cc:
                    st.markdown("**🕒 Chegada**")
                    st.markdown(f"## {row.get('Hora chegada Azambuja', '--')}")
                with cd:
                    st.markdown("**📦 Descarga**")
                    st.markdown(f"## {row.get('Hora descarga loja', '--')}")

                st.markdown("<br>", unsafe_allow_html=True)
                
                cr, ct = st.columns(2)
                cr.error(f"🔙 **Retorno:** {row.get('Retorno', '--')}")
                ct.success(f"📋 **Tipo:** {row.get('TIPO', '-')}")

                with st.expander("📦 Ver Carga Detalhada", expanded=True):
                    cols = ["Azambuja Ambiente", "Azambuja Congelados", "Salsesen Azambuja", 
                            "Frota Refrigerado", "Peixe", "Talho", "Total Suportes"]
                    dd = {"Categoria": [], "Qtd": []}
                    
                    for item in cols:
                        qtd = str(row.get(item, '0'))
                        if qtd != '0' and qtd.lower() != 'nan':
                            dd["Categoria"].append(item.replace("Azambuja ", "").replace("Total ", ""))
                            dd["Qtd"].append(qtd)
                    
                    if dd["Categoria"]:
                        st.table(pd.DataFrame(dd).set_index("Categoria"))
                    else:
                        st.caption("Sem carga especial.")
                    
                    st.caption(f"📍 Local: {row.get('Local descarga', '-')}")
                
                if 'WhatsApp' in row and str(row['WhatsApp']).lower() != 'nan':
                     st.info(f"📱 Obs: {row['WhatsApp']}")

            else:
                st.error(f"❌ VPN {vpn_input} não encontrada.")
        else:
            st.warning("⚠️ Digite um número.")
else:
    st.warning("⚠️ Aguardando arquivo de escala.")
