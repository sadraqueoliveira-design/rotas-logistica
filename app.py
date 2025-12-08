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

# --- 3. LEITURA ROBUSTA ---
def ler_rotas(file_content):
    try:
        try:
            df = pd.read_excel(file_content, header=0)
        except:
            file_content.seek(0)
            try:
                df = pd.read_csv(file_content, header=0, sep=';', encoding='latin1')
            except:
                file_content.seek(0)
                df = pd.read_csv(file_content, header=0, sep=',', encoding='latin1')

        # LIMPEZA PROFUNDA DOS NOMES DAS COLUNAS
        new_cols = []
        for c in df.columns:
            s = str(c)
            s = re.sub(r'\s+', ' ', s)  # remove múltiplos espaços
            s = s.strip()               # remove espaço final
            new_cols.append(s)
        df.columns = new_cols

        # RENOMEAÇÃO AUTOMÁTICA
        mapa = {
            'Matricula': 'Matrícula',
            'Matricula ': 'Matrícula',
            'Movél': 'Móvel',
            'N LOJA': 'Nº LOJA',
            'NºLOJA': 'Nº LOJA',
            'Hora descarga loja ': 'Hora descarga loja',
            'Local descarga ': 'Local descarga',
            'Total Suportes ': 'Total Suportes',
        }

        for col in list(df.columns):
            for chave, novo in mapa.items():
                if col.lower().strip() == chave.lower().strip():
                    df.rename(columns={col: novo}, inplace=True)

        # LIMPEZA VPN / Motoristas
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]
            df = df[df['Motorista'] != 'Motorista']

        return df

    except Exception as e:
        st.error(f"Erro leitura: {e}")
        return None

# --- DEFINIÇÕES ---
DB_FILE = "dados_rotas.source"
DATE_FILE = "data_manual.txt"

# --- DATA SALVA ---
if os.path.exists(DATE_FILE):
    with open(DATE_FILE, "r") as f:
        dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
else:
    dt = datetime.now()

# --- CARREGA DADOS ---
df_rotas = None
if os.path.exists(DB_FILE):
    with open(DB_FILE, "rb") as f:
        df_rotas = ler_rotas(BytesIO(f.read()))

# --- SIDEBAR ---
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")
    if df_rotas is not None:
        st.success(f"Rotas carregadas: {len(df_rotas)}")
        with st.expander("🛠️ Ver colunas (debug)"):
            st.write(list(df_rotas.columns))

# --- ESCALA ---
if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    if df_rotas is not None:
        with st.form("busca"):
            c1, c2 = st.columns([2,1])
            vpn = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")

        if btn and vpn:
            res = df_rotas[df_rotas['VPN'] == vpn.strip()]
            if res.empty:
                res = df_rotas[df_rotas['Motorista'].astype(str).str.lower().str.contains(vpn.lower())]

            if not res.empty:
                for idx, row in res.iterrows():
                    st.markdown("---")
                    st.markdown(f'<div class="driver-card">👤 {row.get("Motorista","-")}</div>', unsafe_allow_html=True)

                    # VEÍCULO
                    mat = row.get("Matrícula", "-")
                    mov = row.get("Móvel", "-")
                    rota = row.get("ROTA", "-")
                    loja = row.get("Nº LOJA", "-")

                    st.markdown(f"""
                    <div class="vehicle-grid">
                        <div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{mat}</div></div>
                        <div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{mov}</div></div>
                        <div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{rota}</div></div>
                        <div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{loja}</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # HORÁRIOS
                    col_cheg = next((c for c in df_rotas.columns if "chegada" in c.lower()), None)
                    col_desc = next((c for c in df_rotas.columns if "hora descarga" in c.lower()), None)
                    col_loc = next((c for c in df_rotas.columns if "local descarga" in c.lower()), None)

                    c1, c2 = st.columns(2)
                    c1.markdown(f'<div class="time-block"><div>CHEGADA</div><h3>{row.get(col_cheg,"--")}</h3><b>AZAMBUJA</b></div>', unsafe_allow_html=True)
                    c2.markdown(f'<div class="time-block" style="border-left-color:#d32f2f"><div>DESCARGA</div><h3>{row.get(col_desc,"--")}</h3><b>{str(row.get(col_loc,"Loja")).upper()}</b></div>', unsafe_allow_html=True)

                    # CARGAS
                    ignorar = [
                        "motorista","vpn","matricula","matrícula","movel","móvel","rota","loja",
                        "hora","chegada","descarga","local","turno","filtro","retorno","tipo",
                        "total suportes","unnamed"
                    ]

                    cargas = {}

                    for col in df_rotas.columns:
                        col_lower = col.lower()

                        if not any(x in col_lower for x in ignorar):
                            val = str(row.get(col, '')).strip()
                            if val and val not in ['0','0.0','0,0','nan','None','']:
                                nome_display = col

                                if "talho" in col_lower: nome_display = "🥩 Carne / Talho"
                                elif "peixe" in col_lower: nome_display = "🐟 Peixe"
                                elif "congelados" in col_lower: nome_display = "❄️ Congelados"
                                elif "ambiente" in col_lower: nome_display = "📦 Ambiente"
                                elif "fruta" in col_lower: nome_display = "🍎 Fruta"
                                elif "recolha" in col_lower: nome_display = "♻️ Recolha"

                                cargas[nome_display] = val

                    if cargas:
                        st.markdown('<div class="carga-box"><b>📦 CARGA / PALETES</b>', unsafe_allow_html=True)
                        df_c = pd.DataFrame(list(cargas.items()), columns=["Tipo","Qtd"])
                        st.table(df_c.set_index("Tipo"))
                        st.markdown('</div>', unsafe_allow_html=True)

                    # RODAPÉ
                    v_ret = str(row.get('Retorno','-'))
                    cor_ret = "#008000" if v_ret not in ['0','nan','-','None'] else "#333"

                    v_sup = str(row.get('Total Suportes', '0'))

                    st.markdown(f"""
                    <div class="info-row">
                        <div class="info-item" style="background:#7b1fa2">SUPORTES<br><b>{v_sup}</b></div>
                        <div class="info-item" style="background:white;color:{cor_ret};border:1px solid #ccc">RETORNO<br><b>{v_ret}</b></div>
                        <div class="info-item" style="background:#388e3c">TIPO<br><b>{row.get("TIPO","-")}</b></div>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.error("❌ Nenhum motorista encontrado.")
    else:
        st.warning("Sem dados carregados. Vá em Gestão.")

# --- GESTÃO ---
elif menu == "Gestão":
    st.header("Gestão")
    senha = st.text_input("Senha:", type="password")

    if senha == "123":
        nd = st.date_input("Data:", value=dt)
        if st.button("Salvar Data"):
            with open(DATE_FILE, "w") as f:
                f.write(str(nd))
            st.success("Data atualizada!")
            st.rerun()

        up = st.file_uploader("Enviar planilha", type=['csv','xlsx'])
        if up:
            df = ler_rotas(up)
            if df is not None:
                st.write(f"Lido: {len(df)} linhas")
                st.dataframe(df.head())

                if st.button("Gravar arquivo"):
                    with open(DB_FILE, "wb") as f:
                        f.write(up.getbuffer())
                    st.success("Arquivo gravado com sucesso!")
                    st.rerun()
    else:
        if senha:
            st.error("Senha incorreta.")
