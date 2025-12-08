def load_data(uploaded_file):
    """
    Lê o ficheiro CSV, lida com codificações diferentes (UTF-8 vs Latin-1),
    limpa as linhas 'sujas' e organiza as colunas.
    """
    routes = []
    
    # 1. TENTATIVA DE DECODIFICAÇÃO
    # Obtém os bytes brutos do arquivo
    bytes_data = uploaded_file.getvalue()
    
    try:
        # Tenta decodificar como UTF-8 (Padrão da Web)
        string_data = bytes_data.decode("utf-8")
    except UnicodeDecodeError:
        # Se falhar (erro 0xe9), tenta decodificar como Latin-1 (Padrão do Excel/Windows em Portugal)
        string_data = bytes_data.decode("latin-1")

    # Transforma a string em um objeto de arquivo para leitura
    stringio = StringIO(string_data)
    
    # Lê linha a linha
    reader = csv.reader(stringio, delimiter=',')
    
    for row in reader:
        # Garante que a linha tem colunas suficientes
        if len(row) < 10:
            continue
            
        # Mapeamento das colunas
        motorista = row[1].strip()
        vpn = row[2].strip()
        
        # Lógica de filtragem:
        # Ignora cabeçalho "Motorista", VPN vazia ou VPN "0"
        if motorista == "Motorista" or not vpn or vpn == "0":
            continue
            
        # Verifica se VPN é numérico
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
