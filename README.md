import io

# ... dentro do if menu == "Gestão": ...

# Botão para baixar o modelo
if st.button("📥 Baixar Modelo de Exemplo"):
    # (Copie aqui a parte da criação do dicionário 'data' e do DataFrame 'df' do script ao lado)
    # ...
    
    # Gerar o Excel em memória
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        
    st.download_button(
        label="Confirmar Download",
        data=buffer,
        file_name="modelo_rotas.xlsx",
        mime="application/vnd.ms-excel"
    )
