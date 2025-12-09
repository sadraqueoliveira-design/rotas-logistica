import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CSS ---
st.markdown("""
<style>
    .block-container{padding-top:1rem!important}
    .header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}
    .driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2rem;margin-bottom:10px}
    .vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
    .vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}
    .vehicle-val{font-size:14px;font-weight:bold;color:#004aad}
    .time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}
    .carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}
    .info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}
    .info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}
    button[kind="primary"]{width:100%;height:50px;font-size:18px!important}
    thead tr th:first-child {display:none}
    tbody th {display:none}
</style>
""", unsafe_allow_html=True)

# --- 3. LEITURA INTELIGENTE ---
def ler_rotas(file_content):
    try:
        # Tenta ler com diferentes configurações
        try: df = pd.read_csv(file_content, header=0, sep=',', encoding='utf-8')
        except:
            file_content.seek(0)
            try: df = pd.read_csv(file_content, header=0, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                try: df = pd.read_csv(file_content, header=0, sep=',', encoding='latin1')
                except: return None # Falha total

        # --- LIMPEZA DE NOMES DAS COLUNAS ---
        # 1. Remove espaços extras ("Matricula " -> "Matricula")
        df.columns = df.columns.astype(str).str.strip()
        
        # 2. Mapa de Correção (baseado no seu ficheiro)
        mapa_correcao = {
            'Matricula': 'Matrícula', 
            'Movél': 'Móvel', 
            'NºLOJA': 'Nº LOJA',
            'Motorista ': 'Motorista', # Espaço extra comum
            'VPN': 'VPN',
            'Talho': 'Carne' # Renomeia Talho para Carne se preferir
        }
        
        # Aplica correções
        for col_real in df.columns:
            for errado, certo in mapa_correcao.items():
                if errado.lower() in col_real.lower():
                    df.rename(columns={col_real: certo}, inplace=True)

        # --- FILTRAGEM DE DADOS ---
        if 'VPN' in df.columns:
            # Remove sufixo .0 (ex: 76628.0 -> 76628)
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            # Remove linhas inválidas
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            # Garante que tem motorista
            if 'Motorista' in df.columns:
                df = df[df['Motorista'].notna()]

        return df

    except Exception as e:
        st.error(f"Erro ao ler ficheiro: {e}")
        return None

# --- VARIÁVEIS ---
DB_FILE = "dados_rotas.source" 
DATE_FILE = "data_manual.txt"
ADMINS = {"Admin": "123", "Gestor": "2025"}

# --- LÓGICA DE DATA ---
if os.path.exists(DATE_FILE):
    with open(DATE_FILE, "r") as f: 
        dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
else: dt = datetime.now()

# --- CARREGAR DADOS ---
df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f: df_rotas = ler_rotas(BytesIO(f.read()))

# --- INTERFACE ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")
    if df_rotas is not None: 
        st.success(f"Rotas: {len(df_rotas)}")

if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)
    
    if df_rotas is not None:
        with st.form("busca"):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")
            
        if btn and vpn:
            # Filtra por VPN ou Nome (parcial)
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            # Se não achou por VPN exata, tenta pelo nome
            if res.empty and 'Motorista' in df_rotas.columns:
                 res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    # 1. MOTORISTA
                    st.markdown(f'<div class="driver-card">👤 {row.get("Motorista", "-")}</div>', unsafe_allow_html=True)
                    
                    # 2. VEÍCULO
                    mat = row.get("Matrícula", "-")
                    mov = row.get("Móvel", "-")
                    rota = row.get("ROTA", "-")
                    loja = row.get("Nº LOJA", "-")
                    
                    st.markdown(f'''
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{mat}</div></div>
                        <div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{mov}</div></div>
                        <div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{rota}</div></div>
                        <div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{loja}</div></div>
                    </div>''', unsafe_allow_html=True)
                    
                    # 3. HORÁRIOS
                    col_cheg = next((c for c in df_rotas.columns if "chegada" in c.lower()), 'Hora chegada Azambuja')
                    col_desc = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), 'Hora descarga loja')
                    col_loc = next((c for c in df_rotas.columns if "local descarga" in c.lower()), 'Local descarga')
                    
                    val_loc = str(row.get(col_loc,"Loja")).upper()
                    if val_loc == "NAN": val_loc = "LOJA"

                    c1, c2 = st.columns(2)
                    c1.markdown(f'<div class="time-block"><div>CHEGADA</div><h3>{row.get(col_cheg,"--")}</h3><b style="color:#004aad">AZAMBUJA</b></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="time-block" style="border-left-color:#d32f2f"><div>DESCARGA</div><h3>{row.get(col_desc,"--")}</h3><b style="color:#d32f2f">{val_loc}</b></div>', unsafe_allow_html=True)
                    
                    # 4. CARGAS (COM PEIXE E CARNE)
                    # Lista do que NÃO queremos mostrar aqui
                    ignorar = [
                        "motorista", "vpn", "matrícula", "matricula", "móvel", "movel", 
                        "rota", "loja", "hora", "chegada", "descarga", "local", 
                        "turno", "filtro", "retorno", "tipo", "total suportes", "unnamed", "recolha"
                    ]
                    
                    cargas = {}
                    for col in df_rotas.columns:
                        col_lower = str(col).lower()
                        # Se não for uma coluna proibida...
                        if not any(x in col_lower for x in ignorar):
                            val = str(row.get(col, '')).strip()
                            
                            # E se tiver valor válido (>0)
                            if val and val not in ['0', '0.0', '0,0', 'nan', 'None', '']:
                                
                                # Limpeza visual do nome
                                nome_show = col.replace("Azambuja", "").replace("Salvesen", "").replace("Total", "").strip()
                                
                                # Ícones e Nomes
                                if "talho" in col_lower or "carne" in col_lower: nome_show = "🥩 Carne"
                                elif "peixe" in col_lower: nome_show = "🐟 Peixe"
                                elif "congelados" in col_lower: nome_show = "❄️ Congelados"
                                elif "ambiente" in col_lower: nome_show = "📦 Ambiente"
                                elif "fruta" in col_lower: nome_show = "🍎 Fruta"
                                
                                cargas[nome_show] = val
                    
                    if cargas:
                        st.markdown('<div class="carga-box"><b>📦 CARGA / PALETES</b>', unsafe_allow_html=True)
                        df_c = pd.DataFrame(list(cargas.items()), columns=["Tipo", "Qtd"])
                        st.table(df_c.set_index("Tipo"))
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.info("Sem carga especificada.")
                    
                    # 5. RODAPÉ
                    v_ret = str(row.get('Retorno', '-'))
                    cor_ret = "#008000" if v_ret not in ['0','-','nan','Vazio','None'] else "#333"
                    v_sup = str(row.get('Total Suportes', row.get('Total Suportes ', '0')))
                    
                    st.markdown(f'''
                    <div class="info-row">
                        <div class="info-item" style="background:#7b1
