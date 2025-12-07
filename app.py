import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teste Sistema", page_icon="🔧")

st.title("🔧 TESTE DE DIGITAÇÃO")

st.write("Se você consegue ler isso, o site carregou.")

# --- DADOS FALSOS (SIMULANDO O EXCEL) ---
# Isso elimina o risco do arquivo não carregar
dados_exemplo = {
    'VPN': ['12345', '76628', '99999'],
    'Motorista': ['Teste João', 'José Manuel', 'Maria Teste'],
    'ROTA': ['100', '6429', '200'],
    'Nº LOJA': ['L1', 'B53', 'L2'],
    'Hora chegada Azambuja': ['10:00', '04:18', '12:00'],
    'Hora descarga loja': ['12:00', '06:30', '14:00']
}
df = pd.DataFrame(dados_exemplo)

st.markdown("---")
st.subheader("1. Tente digitar abaixo:")
st.write("(Use o número **76628** ou **12345** para testar)")

# Campo de texto simples
vpn_input = st.text_input("Digite a VPN aqui:")

if st.button("Buscar"):
    st.write(f"Você digitou: {vpn_input}")
    
    # Filtra nos dados falsos
    res = df[df['VPN'] == vpn_input]
    
    if not res.empty:
        st.success("✅ FUNCIONOU! O sistema achou o motorista.")
        st.write(res)
    else:
        st.error("❌ VPN não encontrada nos dados de teste.")

st.markdown("---")
st.info("Se você conseguiu digitar e clicar no botão 'Buscar', o problema NÃO é o código, é o seu arquivo Excel que não está carregando.")
