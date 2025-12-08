import streamlit as st
import pandas as pd
import csv
from io import StringIO

# Configuração da página
st.set_page_config(page_title="Pesquisa de Rotas", page_icon="🚚")

def load_data(uploaded_file):
    """
    Lê o ficheiro CSV, limpa as linhas 'sujas' (com 0) e organiza as colunas.
    """
    routes = []
    
    # Decodifica o arquivo carregado
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    
    # Lê linha a linha para ter controlo total (como fizemos no React)
    reader = csv.reader(stringio, delimiter=',')
    
    for row in reader:
        # Garante que a linha tem colunas suficientes
        if len(row) < 10:
            continue
            
        # Mapeamento das colunas baseado no seu ficheiro 'teste.xlsx - Folha1.csv'
        # Col 1: Motorista, Col 2: VPN, Col 3: Matricula, Col 5: Rota
        motorista = row[1].strip()
        vpn = row[2].strip()
        
        # Lógica de filtragem (igual ao React):
        # 1. Ignorar cabeçalhos ("Motorista")
        # 2. Ignorar linhas de rodapé com '0'
        if motorista == "Motorista" or not vpn or vpn == "0":
            continue
            
        # Verifica se VPN é numérico (para evitar lixo)
        if not vpn.isdigit():
            continue

        # Cria o objeto de dados
        routes.append({
            "motorista": motorista,
            "vpn": vpn,
            "matricula": row[3].strip(),
            "rota": row[5].strip(),
            "nLoja": row[6].strip(),
            "horaChegada": row[7].strip(),
            "local": row[8].strip(),
            "horaDescarga": row[9].strip(),
            "tipo": row[11].strip() if len(row) > 11 else ""
        })
            
    return routes

# --- Interface Gráfica (Streamlit) ---

st.title("🚚 Pesquisa de Rotas")

# Upload do Arquivo
uploaded_file = st.sidebar.file_uploader("Carregar Planilha (.csv)", type=["csv"])

if uploaded_file:
    # Carrega os dados
    try:
        data = load_data(uploaded_file)
        st.sidebar.success(f"{len(data)} rotas carregadas.")
        
        # Campo de Pesquisa
        vpn_search = st.text_input("Digite a VPN ou Nome do Motorista", placeholder="Ex: 76628")
        
        if vpn_search:
            # Filtra os dados
            search_term = vpn_search.lower()
            results = [
                r for r in data 
                if search_term in r['vpn'].lower() or search_term in r['motorista'].lower()
            ]
            
            if results:
                st.write(f"Encontradas **{len(results)}** rotas:")
                
                # Exibe cada resultado como um "Card"
                for item in results:
                    with st.container():
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #262730; color: white;">
                            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 8px;">
                                <div>
                                    <strong style="font-size: 1.1em;">👤 {item['motorista']}</strong><br>
                                    <span style="color: #aaa;">VPN: {item['vpn']}</span>
                                </div>
                                <div style="background-color: #ff4b4b; padding: 4px 8px; border-radius: 5px; font-weight: bold;">
                                    🚛 {item['matricula']}
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                <div>
                                    <p><strong>📍 {item['local']}</strong></p>
                                    <p style="font-size: 0.9em; color: #ccc;">Rota: {item['rota']} | Loja: {item['nLoja']}</p>
                                </div>
                                <div>
                                    <p>🕒 Chegada Azambuja: <code>{item['horaChegada']}</code></p>
                                    <p>📦 Descarga Loja: <code>{item['horaDescarga']}</code></p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Nenhuma rota encontrada para essa VPN.")
        else:
            st.info("Digite uma VPN acima para buscar.")
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, carregue o arquivo CSV na barra lateral para começar.")
