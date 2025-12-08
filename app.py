# Retry: write corrected code using triple-double quotes for the outer string to avoid conflict with inner triple-single quotes.
corrected_code = """import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from io import BytesIO

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title=\"Logística App\", page_icon=\"🚛\", layout=\"centered\", initial_sidebar_state=\"collapsed\")

# --- 2. CSS ---
st.markdown(\"\"\"
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
    button[kind=\"primary\"]{width:100%;height:50px;font-size:18px!important}
    /* Esconde indices das tabelas */
    thead tr th:first-child {display:none}
    tbody th {display:none}
</style>
\"\"\", unsafe_allow_html=True)

# --- 3. LEITURA ROBUSTA ---
def ler_rotas(file_content):
    \"\"\"
    Lê um Excel/CSV enviado e normaliza colunas, removendo espaços extras e mapeando nomes.
    Retorna um DataFrame limpo ou None em caso de erro.
    \"\"\"
    try:
        # Se recebemos um objeto tipo UploadedFile (Streamlit) ou BytesIO
        if hasattr(file_content, \"read\"):
            content = file_content.read()
            file_content.seek(0)
        else:
            # caminho para arquivo
            with open(file_content, \"rb\") as f:
                content = f.read()

        # Tenta ler como Excel primeiro
        df = None
        try:
            df = pd.read_excel(BytesIO(content), header=0)
        except Exception:
            # tenta csv com ; então com ,
            try:
                df = pd.read_csv(BytesIO(content), header=0, sep=';', encoding='latin1')
            except Exception:
                df = pd.read_csv(BytesIO(content), header=0, sep=',', encoding='latin1')

        # Se leitura falhou
        if df is None:
            raise ValueError(\"Não foi possível ler o arquivo como Excel ou CSV.\")

        # Normaliza os nomes das colunas: remove múltiplos espaços, tabs e trim
        new_cols = []
        for c in df.columns:
            s = str(c)
            s = re.sub(r'\\s+', ' ', s)  # substitui qualquer whitespace por um espaço simples
            s = s.strip()               # remove espaços no começo/fim
            new_cols.append(s)
        df.columns = new_cols

        # Mapeamento de nomes importantes (variações encontradas)
        mapa = {
            'Matricula': 'Matrícula',
            'Matricula ': 'Matrícula',
            'Matrícula ': 'Matrícula',
            'Movél': 'Móvel',
            'Movel': 'Móvel',
            'NºLOJA': 'Nº LOJA',
            'N LOJA': 'Nº LOJA',
            'Total Suportes ': 'Total Suportes',
            'Total Suportes': 'Total Suportes',
            'Hora descarga loja': 'Hora descarga loja',
            'Hora descarga loja ': 'Hora descarga loja',
            'Local descarga ': 'Local descarga',
            'Local descarga': 'Local descarga',
            'Local descarga ': 'Local descarga',
            'Hora chegada Azambuja': 'Hora chegada Azambuja'
        }

        for c_original in list(df.columns):
            for chave, valor in mapa.items():
                if chave.lower() == c_original.lower():
                    df.rename(columns={c_original: valor}, inplace=True)

        # FORÇA A CORREÇÃO DAS COLUNAS 1 e 2 (Motorista e VPN) se houver linhas de cabeçalho embaralhadas
        cols = list(df.columns)
        if len(cols) > 5:
            # Só renomeia pela posição se as colunas existentes não corresponderem ao esperado
            # Encontramos colunas que pareçam ser Motorista e VPN pelo conteúdo da terceira linha, se existir
            df_columns_lower = [c.lower() for c in df.columns]
            # Se não existir coluna 'motorista' mas existe na posição 1 algo que parece nome, forçamos
            if 'motorista' not in df_columns_lower and len(cols) > 2:
                try:
                    df.columns.values[1] = 'Motorista'
                    df.columns.values[2] = 'VPN'
                except Exception:
                    pass

        # LIMPEZA de valores de VPN e filtragem de linhas inválidas
        if 'VPN' in df.columns:
            df['VPN'] = df['VPN'].astype(str).str.replace(r'\\.0$', '', regex=True).str.strip()
            df = df[~df['VPN'].isin(['0', 'nan', '', 'None', 'VPN'])]

        # Remove linhas que são repetição do cabeçalho (ex: linha com \"Motorista\" em coluna Motorista)
        if 'Motorista' in df.columns:
            df = df[df['Motorista'].astype(str).str.lower() != 'motorista']

        # Reset index
        df = df.reset_index(drop=True)

        return df
    except Exception as e:
        st.error(f\"Erro leitura: {e}\")
        return None

# --- VARIÁVEIS ---
DB_FILE = \"dados_rotas.source\" 
DATE_FILE = \"data_manual.txt\"
ADMINS = {\"Admin\": \"123\", \"Gestor\": \"2025\"}

# --- LÓGICA DE DATA ---
if os.path.exists(DATE_FILE):
   
