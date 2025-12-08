import streamlit as st
import pandas as pd
import csv
from io import StringIO

# --- 1. CONFIGURAÇÃO DA PÁGINA (OBRIGATÓRIO SER O PRIMEIRO COMANDO) ---
st.set_page_config(
    page_title="Pesquisa de Rotas",
    page_icon="🚚",
    layout="wide"
)

# --- 2. FUNÇÃO DE CARREGAMENTO DE DADOS ---
def load_data(uploaded_file):
    """
    Lê o CSV, tenta diferentes codificações e limpa os dados.
    """
    routes = []
    
    # Tenta ler o ficheiro lidando com acentos (UTF-8 ou Latin-1)
    bytes_data = uploaded_file.getvalue()
    try:
        string_data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        string_data = bytes_data.decode("latin-1")

    stringio = StringIO(string_data)
    reader = csv.reader(stringio, delimiter=',')
    
    for row in reader:
        # Pula linhas que não tenham colunas suficientes
        if len(row) < 10:
            continue
            
        # Mapeia colunas (Baseado no seu ficheiro teste.xlsx)
        # Col 1: Motorista, Col 2: VPN
        motorista = row[1].strip()
        vpn = row[2].strip()
        
        # Filtra cabeçalhos e linhas de rodapé com '0'
        if motorista == "Motorista" or not vpn or vpn == "0":
            continue
            
        if not vpn.isdigit():
            continue

        routes.append({
            "motorista": motorista,
            "vpn": vpn,
            "matricula": row[3].strip(),
            "rota": row[5].strip(),
            "nLoja": row[6].strip(),
            "horaChegada": row[7].strip(),
            "local": row[8].strip(),
            "horaDescarga": row[9].strip(),
            # Proteção caso a coluna 11 não exista em alguma linha
            "tipo": row[11].strip() if len(row) > 11 else ""
        })
            
    return routes

# --- 3. INTERFACE PRINCIPAL ---

# Título da Aplicação
st.title("🚚 Pesquisa de Rotas e Horários")
st.markdown("---")

# Barra Lateral (Sidebar)
with st.sidebar:
    st.header("📂 Carregar Dados")
    uploaded_file = st.file_uploader(
        "Arraste o ficheiro CSV aqui", 
        type=["csv"],
        help="O ficheiro deve ser o export do Excel em formato CSV."
    )
    st.info("Nota: Se o ficheiro vier do Excel, certifique-se que está gravado como CSV.")

# Lógica de Exibição
if uploaded_file is not None:
    # Se o ficheiro existe, processa
    try:
        data = load_data(uploaded_file)
        
        if len(data) == 0:
            st.warning("O ficheiro foi lido, mas não foram encontradas rotas válidas. Verifique o formato.")
        else:
            st.sidebar.success(f"✅ {len(data)} rotas carregadas com sucesso!")
            
            # --- ÁREA DE PESQUISA ---
            col1, col2 = st.columns([3, 1])
            with col1:
                search_query = st.text_input("🔍 Pesquisar por VPN ou Motorista:", placeholder="Ex: 76628 ou José")
            
            # Filtra os resultados
            if search_query:
                term = search_query.lower()
                results = [r for r in data if term in r['vpn'].lower() or term in r['motorista'].lower()]
                
                if len(results) > 0:
                    st.write(f"Encontrados **{len(results)}** resultados:")
                    
                    # Exibe os cartões
                    for item in results:
                        with st.container():
                            # CSS Injetado para estilizar o cartão
                            st.markdown(f"""
                            <div style="
                                border: 1px solid #444; 
                                padding: 20px; 
                                border-radius: 12px; 
                                margin-bottom: 15px; 
                                background-color: #1e1e1e; 
                                color: #e0e0e0;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 10px;">
                                    <div>
                                        <h3 style="margin: 0; color: #fff;">👤 {item['motorista']}</h3>
                                        <span style="color: #888; font-family: monospace;">VPN: {item['vpn']}</span>
                                    </div>
                                    <div style="text-align: right;">
                                        <span style="background-color: #d32f2f; color: white; padding: 5px 10px; border-radius: 6px; font-weight: bold;">
                                            🚛 {item['matricula']}
                                        </span>
                                    </div>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                    <div>
                                        <p style="margin: 5px 0;"><strong>📍 Destino:</strong> {item['local']}</p>
                                        <p style="margin: 5px 0; font-size: 0.9em; color: #aaa;">Rota: {item['rota']} | Loja: {item['nLoja']}</p>
                                    </div>
                                    <div style="background-color: #2d2d2d; padding: 10px; border-radius: 8px;">
                                        <p style="margin: 5px 0;">📥 Chegada Azambuja: <code style="color: #90caf9;">{item['horaChegada']}</code></p>
                                        <p style="margin: 5px 0;">📦 Descarga Loja: <code style="color: #a5d6a7;">{item['horaDescarga']}</code></p>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning(f"Nenhum resultado encontrado para '{search_query}'.")
            else:
                st.info("👆 Digite uma VPN ou nome acima para ver os detalhes.")
                
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro. Detalhes: {e}")

else:
    # --- TELA INICIAL (QUANDO NÃO HÁ ARQUIVO) ---
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h2>👋 Bem-vindo!</h2>
        <p>Para começar, carregue o ficheiro CSV na barra lateral à esquerda.</p>
        <p style="color: #666; font-size: 0.9em;">Aguardando ficheiro...</p>
    </div>
    """, unsafe_allow_html=True)
