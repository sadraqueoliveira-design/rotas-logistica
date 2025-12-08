import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# =====================
# Logística App (Refactor)
# - leitura robusta de ficheiros Excel/CSV/XLSB
# - detecta coluna C como VPN quando necessário
# - interface Streamlit com Escala / Gestão
# =====================

# --- Configuração da página ---
st.set_page_config(page_title="Logística App", page_icon="🚛", layout="centered", initial_sidebar_state="collapsed")

# --- CSS básico ---
st.markdown("""
<style>
    .block-container{padding-top:1rem!important}
    .header-box{background:#004aad;padding:20px;border-radius:12px;text-align:center;color:white;margin-bottom:20px}
    .driver-card{background:#004aad;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;font-size:1.1rem;margin-bottom:10px}
    .vehicle-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px}
    .vehicle-item{background:#e3f2fd;padding:8px;border-radius:6px;text-align:center;border:1px solid #bbdefb}
    .vehicle-val{font-size:14px;font-weight:bold;color:#004aad}
    .time-block{background:#f8f9fa;padding:10px;border-radius:8px;border-left:6px solid #004aad;margin-bottom:5px}
    .carga-box{background:#fff;border:1px solid #eee;border-radius:8px;padding:10px;margin-top:10px}
    .info-row{display:flex;justify-content:space-between;gap:5px;margin:15px 0}
    .info-item{flex:1;text-align:center;padding:5px;border-radius:6px;color:white;font-size:0.9rem}
    thead tr th:first-child {display:none}
    tbody th {display:none}
</style>
""", unsafe_allow_html=True)


# ---------------------
# UTIL: detectar assinatura do ficheiro
# ---------------------
def detect_file_signature(file_like):
    """
    Lê os primeiros bytes para tentar identificar o formato.
    Retorna os primeiros 4 bytes (bytes object) ou b'' em erro.
    """
    try:
        file_like.seek(0)
        hdr = file_like.read(4)
        file_like.seek(0)
        return hdr
    except Exception:
        try:
            # tenta tratar file_like como bytes
            buf = BytesIO(file_like)
            hdr = buf.read(4)
            return hdr
        except Exception:
            return b''


# ---------------------
# Função robusta de leitura
# ---------------------
def ler_rotas(file_content):
    """
    file_content: file-like object (UploadedFile) ou buffer bytes.
    Tenta: openpyxl (.xlsx), xlrd (.xls), pyxlsb (.xlsb), e fallback CSV.
    Normaliza nomes de colunas e força coluna C como VPN se necessário.
    Retorna DataFrame ou None.
    """
    tried = []
    try:
        filename = getattr(file_content, "name", None)
        ext = None
        if filename and "." in filename:
            ext = filename.lower().split(".")[-1]

        hdr = detect_file_signature(file_content)
        is_zip = isinstance(hdr, (bytes, bytearray)) and hdr.startswith(b'PK')                 # xlsx/xlsm .zip-based
        is_ole = isinstance(hdr, (bytes, bytearray)) and hdr.startswith(b'\xD0\xCF\x11\xE0')    # old .xls OLE

        def normalize_df(df):
            # Normaliza nomes das colunas: converte para str, remove espaços duplicados e trim
            df = df.copy()
            new_cols = []
            for c in df.columns:
                s = str(c)
                s = re.sub(r'\s+', ' ', s).strip()
                new_cols.append(s)
            df.columns = new_cols

            # Se não existir 'VPN', forçar coluna 3 (índice 2) como 'VPN' quando houver >=3 colunas
            if 'VPN' not in df.columns and len(df.columns) >= 3:
                original = df.columns[2]
                df.rename(columns={original: 'VPN'}, inplace=True)

            # Limpa valores de VPN
            if 'VPN' in df.columns:
                df['VPN'] = df['VPN'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

            # Drop linhas totalmente vazias
            df = df.dropna(how='all').reset_index(drop=True)
            return df

        # 1) Try openpyxl (xlsx)
        if is_zip or ext in ("xlsx", "xlsm", "xltx", "xltm"):
            try:
                df = pd.read_excel(file_content, header=0, engine="openpyxl")
                return normalize_df(df)
            except Exception as e:
                tried.append(f"openpyxl:{e}")

        # 2) Try xlrd (xls)
        if is_ole or ext == "xls":
            try:
                df = pd.read_excel(file_content, header=0, engine="xlrd")
                return normalize_df(df)
            except Exception as e:
                tried.append(f"xlrd:{e}")

        # 3) Try pyxlsb (xlsb)
        if ext == "xlsb":
            try:
                df = pd.read_excel(file_content, header=0, engine="pyxlsb")
                return normalize_df(df)
            except Exception as e:
                tried.append(f"pyxlsb:{e}")

        # 4) Tentar engines gerais (openpyxl, pyxlsb, xlrd)
        for engine in ("openpyxl", "pyxlsb", "xlrd"):
            try:
                df = pd.read_excel(file_content, header=0, engine=engine)
                return normalize_df(df)
            except Exception as e:
                tried.append(f"{engine}:{e}")

        # 5) Fallback: CSV ; e ,
        try:
            file_content.seek(0)
            df = pd.read_csv(file_content, header=0, sep=';', encoding='latin1')
            return normalize_df(df)
        except Exception as e:
            tried.append(f"csv_semicolon:{e}")
            try:
                file_content.seek(0)
                df = pd.read_csv(file_content, header=0, sep=',', encoding='latin1')
                return normalize_df(df)
            except Exception as e2:
                tried.append(f"csv_comma:{e2}")

        st.error("Não foi possível ler o ficheiro. Tentativas: " + " | ".join(tried))
        return None

    except Exception as e:
        st.error(f"Erro inesperado na leitura do ficheiro: {e}")
        return None


# ---------------------
# Variáveis e ficheiros locais
# ---------------------
DB_FILE = "dados_rotas.source"
DATE_FILE = "data_manual.txt"
ADMINS = {"Admin": "123", "Gestor": "2025"}

# --- Data manual ---
if os.path.exists(DATE_FILE):
    try:
        with open(DATE_FILE, "r") as f:
            dt = datetime.strptime(f.read().strip(), "%Y-%m-%d")
    except Exception:
        dt = datetime.now()
else:
    dt = datetime.now()

# --- Carregar DB salvo ---
df_rotas = None
if os.path.exists(DB_FILE):
    try:
        with open(DB_FILE, "rb") as f:
            df_rotas = ler_rotas(BytesIO(f.read()))
    except Exception:
        df_rotas = None

# ---------------------
# Interface: Sidebar
# ---------------------
with st.sidebar:
    st.header("🚛 MENU")
    menu = st.radio("Ir para:", ["Escala", "Gestão"], label_visibility="collapsed")
    if df_rotas is not None:
        st.success(f"Rotas carregadas: {len(df_rotas)}")
        with st.expander("🛠️ Ver Colunas (Debug)"):
            st.write(list(df_rotas.columns))

# ---------------------
# Escala
# ---------------------
if menu == "Escala":
    st.markdown(f'<div class="header-box"><h3>ESCALA DIÁRIA</h3><p>{dt.strftime("%d/%m/%Y")}</p></div>', unsafe_allow_html=True)

    if df_rotas is None or df_rotas.empty:
        st.warning("Sem dados carregados. Vá a Gestão para carregar a planilha.")
    else:
        with st.form("busca"):
            c1, c2 = st.columns([2, 1])
            vpn_input = c1.text_input("VPN", placeholder="Ex: 76628", label_visibility="collapsed")
            btn = c2.form_submit_button("BUSCAR")

        if btn and vpn_input:
            vpn_search = vpn_input.strip()

            # detectar coluna VPN explicitamente ou por índice (coluna C)
            col_vpn = next((c for c in df_rotas.columns if c.strip().lower() == "vpn"), None)
            if col_vpn is None and len(df_rotas.columns) >= 3:
                col_vpn = df_rotas.columns[2]

            if col_vpn is None:
                st.error("A coluna VPN não foi encontrada na base. Verifique a planilha.")
            else:
                res = df_rotas[df_rotas[col_vpn].astype(str).str.strip() == vpn_search]

                if res.empty:
                    st.error("Nenhum registo encontrado para o VPN informado.")
                else:
                    for idx, row in res.iterrows():
                        st.markdown("---")
                        motorista = row.get("Motorista", row.get("Motorista ", "-"))
                        st.markdown(f'<div class="driver-card">👤 {motorista}</div>', unsafe_allow_html=True)

                        mat = row.get("Matrícula", row.get("Matricula", row.get("Matricula ", "-")))
                        mov = row.get("Móvel", row.get("Movél", "-"))
                        rota = row.get("ROTA", "-")
                        loja = row.get("Nº LOJA", row.get("NºLOJA", "-"))

                        st.markdown(f"""
                        <div class="vehicle-grid">
                            <div class="vehicle-item"><div>MATRÍCULA</div><div class="vehicle-val">{mat}</div></div>
                            <div class="vehicle-item"><div>MÓVEL</div><div class="vehicle-val">{mov}</div></div>
                            <div class="vehicle-item"><div>ROTA</div><div class="vehicle-val">{rota}</div></div>
                            <div class="vehicle-item"><div>LOJA</div><div class="vehicle-val">{loja}</div></div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Horários
                        col_cheg = next((c for c in df_rotas.columns if "chegada" in c.lower()), None)
                        col_desc = next((c for c in df_rotas.columns if "hora descarga" in c.lower() or "descarga loja" in c.lower()), None)
                        col_loc = next((c for c in df_rotas.columns if "local descarga" in c.lower() or "local" in c.lower()), None)

                        hora_cheg = row.get(col_cheg, "--") if col_cheg else "--"
                        hora_desc = row.get(col_desc, "--") if col_desc else "--"
                        local_desc = row.get(col_loc, "Loja") if col_loc else "Loja"

                        c1, c2 = st.columns(2)
                        c1.markdown(f'<div class="time-block"><div>CHEGADA</div><h3>{hora_cheg}</h3><b style="color:#004aad">AZAMBUJA</b></div>', unsafe_allow_html=True)
                        c2.markdown(f'<div class="time-block" style="border-left-color:#d32f2f"><div>DESCARGA</div><h3>{hora_desc}</h3><b style="color:#d32f2f">{str(local_desc).upper()}</b></div>', unsafe_allow_html=True)

                        # Cargas
                        ignorar = [
                            "motorista","vpn","matricula","matrícula","movel","móvel",
                            "rota","loja","hora","chegada","descarga","local",
                            "turno","filtro","retorno","tipo","total suportes","unnamed"
                        ]

                        cargas = {}
                        for col in df_rotas.columns:
                            col_lower = str(col).lower()
                            if any(x in col_lower for x in ignorar):
                                continue
                            val = str(row.get(col, '')).strip()
                            if val and val not in ['0', '0.0', '0,0', 'nan', 'None', '']:
                                nome_display = re.sub(r'\s+', ' ', str(col)).strip()
                                nome_display = nome_display.replace("Azambuja", "").replace("Salvesen", "").replace("Total", "").strip()
                                if "talho" in col_lower:
                                    nome_display = "🥩 Carne / Talho"
                                elif "peixe" in col_lower:
                                    nome_display = "🐟 Peixe"
                                elif "congelad" in col_lower:
                                    nome_display = "❄️ Congelados"
                                elif "ambiente" in col_lower:
                                    nome_display = "📦 Ambiente"
                                elif "fruta" in col_lower:
                                    nome_display = "🍎 Fruta"
                                elif "recolha" in col_lower:
                                    nome_display = "♻️ Recolha"

                                cargas[nome_display] = val

                        if cargas:
                            st.markdown('<div class="carga-box"><b>📦 CARGA / PALETES</b>', unsafe_allow_html=True)
                            df_c = pd.DataFrame(list(cargas.items()), columns=["Tipo", "Qtd"])
                            st.table(df_c.set_index("Tipo"))
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Rodapé
                        v_ret = str(row.get('Retorno', '-'))
                        cor_ret = "#008000" if v_ret not in ['0', '-', 'nan', 'Vazio', 'None', ''] else "#333"
                        v_sup = str(row.get('Total Suportes', row.get('Total Suportes ', '0')))

                        st.markdown(f'''
                        <div class="info-row">
                            <div class="info-item" style="background:#7b1fa2">SUPORTES<br><b>{v_sup}</b></div>
                            <div class="info-item" style="background:white;color:{cor_ret};border:1px solid #ccc">RETORNO<br><b>{v_ret}</b></div>
                            <div class="info-item" style="background:#388e3c">TIPO<br><b>{row.get("TIPO", "-")}</b></div>
                        </div>''', unsafe_allow_html=True)

# ---------------------
# Gestão
# ---------------------
elif menu == "Gestão":
    st.header("Gestão")
    p = st.text_input("Senha", type="password")
    if p in ADMINS.values():
        nd = st.date_input("Data:", value=dt)
        if st.button("Salvar Data"):
            try:
                with open(DATE_FILE, "w") as f:
                    f.write(str(nd))
                st.success("Data salva.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro ao salvar data: {e}")

        up = st.file_uploader("Arquivo", type=['csv', 'xlsx', 'xls', 'xlsb'])
        if up:
            df = ler_rotas(up)
            if df is not None:
                st.write(f"Lido: {len(df)} linhas")
                st.dataframe(df.head(50))
                if st.button("Gravar"):
                    try:
                        with open(DB_FILE, "wb") as f:
                            f.write(up.getbuffer())
                        st.success("OK! Dados gravados.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao gravar: {e}")
    else:
        if p:
            st.error("Senha incorreta.")
        else:
            st.info("Insira a senha de Gestor para aceder à gestão.")
