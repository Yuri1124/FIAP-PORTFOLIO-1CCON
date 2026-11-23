def inicializar_colonia():
    """
    Retorna um dicionário com todos os dados da colônia.
    Usamos estrutura chave-valor (dicionário) para organizar
    as informações de forma eficiente.
    """

    # Estrutura hierárquica dos sistemas da colônia
    sistemas = {
        "energetico": {
            "solar": {"ativo": True, "capacidade_max": 60},
            "eolico": {"ativo": True, "capacidade_max": 40},
        },
        "suporte_vida": {
            "oxigenio": {"ativo": True, "prioridade": "CRITICA"},
            "temperatura": {"ativo": True, "prioridade": "CRITICA"},
            "agua": {"ativo": True, "prioridade": "ALTA"},
        },
        "nao_essenciais": {
            "laboratorio": {"ativo": True, "prioridade": "MEDIA"},
            "entretenimento": {"ativo": True, "prioridade": "BAIXA"},
            "iluminacao_extra": {"ativo": True, "prioridade": "BAIXA"},
        },
    }

    # Dados de monitoramento atuais (listas e chave-valor)
    monitoramento = {
        "energia_atual": 0,        # % de carga nas baterias
        "consumo_atual": 0,        # unidades de consumo
        "geracao_atual": 0,        # unidades geradas agora
        "velocidade_vento": 0,     # km/h
        "clima": "ensolarado",     # estado do clima
    }

    # Histórico para regressão (listas paralelas)
    historico = {
        "vento":  [5,  8,  10, 12, 15, 18, 20],   # velocidade do vento (km/h)
        "energia_eolica": [12, 20, 25, 30, 37, 45, 50],  # energia gerada (unidades)
    }

    return {"sistemas": sistemas, "monitoramento": monitoramento, "historico": historico}


def tomar_decisao(energia, consumo):
    """
    Recebe energia (% bateria) e consumo (unidades),
    aplica regras de decisão e retorna uma ação clara.

    Parâmetros:
        energia  (int/float): nível da bateria em %
        consumo  (int/float): consumo atual em unidades

    Retorna:
        str: mensagem de ação/alerta
    """

    # Classificar nível de consumo
    if consumo >= 70:
        nivel_consumo = "ALTO"
    elif consumo >= 40:
        nivel_consumo = "MEDIO"
    else:
        nivel_consumo = "BAIXO"

    # --- Regras de decisão (combinando condições) ---

    # Regra 1: Situação crítica - energia baixa E consumo alto
    if energia < 20 and nivel_consumo == "ALTO":
        return "CRÍTICO: Energia crítica + consumo alto → Desligar sistemas não essenciais IMEDIATAMENTE"

    # Regra 2: Alerta - energia baixa
    elif energia < 50 and nivel_consumo == "ALTO":
        return "ALERTA: Energia < 50% e consumo alto → Ativar MODO ECONOMIA"

    # Regra 3: Aviso - energia baixa mas consumo moderado
    elif energia < 50 and nivel_consumo == "MEDIO":
        return "AVISO: Energia abaixo de 50% → Reduzir consumo não essencial"

    # Regra 4: Atenção - energia baixa mas consumo baixo
    elif energia < 50:
        return "ATENÇÃO: Energia abaixo de 50% → Monitorar de perto"

    # Regra 5: Normal - energia boa
    elif energia >= 80 and nivel_consumo == "BAIXO":
        return "NORMAL: Sistema estável → Operação padrão"

    # Regra 6: Tudo bem
    else:
        return "OK: Energia suficiente → Continuar operação normal"


def verificar_suporte_vida(energia):
    """
    Garante que sistemas críticos permaneçam ligados.
    Prioridade máxima: suporte à vida sempre ativo.

    Parâmetros:
        energia (int/float): nível da bateria em %

    Retorna:
        dict: status de cada sistema
    """
    status = {}

    # Sistemas críticos: SEMPRE ligados (prioridade máxima)
    status["oxigenio"]    = "LIGADO (prioridade CRÍTICA)"
    status["temperatura"] = "LIGADO (prioridade CRÍTICA)"

    # Sistemas de alta prioridade: desligar só em emergência
    if energia < 15:
        status["agua"] = "REDUZIDO (emergência)"
    else:
        status["agua"] = "LIGADO (prioridade ALTA)"

    # Sistemas não essenciais: desligar quando energia < 50%
    if energia < 50:
        status["laboratorio"]     = "DESLIGADO (economia)"
        status["entretenimento"]  = "DESLIGADO (economia)"
        status["iluminacao_extra"] = "DESLIGADO (economia)"
    else:
        status["laboratorio"]     = "LIGADO"
        status["entretenimento"]  = "LIGADO"
        status["iluminacao_extra"] = "LIGADO"

    return status


def calcular_regressao(lista_x, lista_y):
    """
    Calcula os coeficientes a (inclinação) e b (intercepto)
    da reta que melhor se ajusta aos dados.

    Fórmula (mínimos quadrados):
        a = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
        b = (Σy - a*Σx) / n

    Parâmetros:
        lista_x (list): valores da variável independente (ex: vento)
        lista_y (list): valores da variável dependente   (ex: energia)

    Retorna:
        tuple: (a, b) coeficientes da reta
    """
    n = len(lista_x)

    soma_x  = sum(lista_x)
    soma_y  = sum(lista_y)
    soma_xy = sum(lista_x[i] * lista_y[i] for i in range(n))
    soma_x2 = sum(x ** 2 for x in lista_x)

    # Calcular inclinação (a) e intercepto (b)
    a = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x ** 2)
    b = (soma_y - a * soma_x) / n

    return a, b


def prever_energia_eolica(velocidade_vento, historico):
    """
    Usa regressão linear para estimar a energia eólica gerada
    com base na velocidade do vento.

    Parâmetros:
        velocidade_vento (float): velocidade atual do vento (km/h)
        historico        (dict) : dicionário com listas 'vento' e 'energia_eolica'

    Retorna:
        float: previsão de energia gerada
    """
    lista_vento  = historico["vento"]
    lista_energia = historico["energia_eolica"]

    a, b = calcular_regressao(lista_vento, lista_energia)

    previsao = a * velocidade_vento + b

    # Garantir que a previsão não seja negativa
    return max(0, round(previsao, 1))


def analisar_energia(geracao, consumo):
    """
    Compara a energia gerada com o consumo atual e
    retorna uma análise com recomendação.

    Parâmetros:
        geracao (float): energia sendo gerada agora
        consumo (float): energia sendo consumida agora

    Retorna:
        str: análise e recomendação
    """
    diferenca = geracao - consumo

    if consumo > geracao:
        deficit = consumo - geracao
        return (
            f"ALERTA: Consumo maior que geração!\n"
            f"Déficit de {deficit} unidades → Reduzir consumo ou aumentar geração"
        )

    elif geracao > consumo * 1.5:
        excedente = geracao - consumo
        return (
            f"SUGESTÃO: Geração muito acima do consumo!\n"
            f"Excedente de {excedente} unidades → Armazenar energia nas baterias"
        )

    elif geracao > consumo:
        excedente = geracao - consumo
        return (
            f"OK: Geração equilibrada.\n"
            f"Excedente de {excedente} unidades → Sistema estável"
        )

    else:
        return "PERFEITO: Geração igual ao consumo → Equilíbrio energético"


def gerar_relatorio(energia, consumo, geracao, velocidade_vento, historico):
    """
    Gera um relatório completo do estado da colônia,
    integrando decisões, análise de energia e previsão.

    Parâmetros:
        energia          (float): % bateria
        consumo          (float): consumo atual
        geracao          (float): geração atual
        velocidade_vento (float): vento em km/h
        historico        (dict) : dados históricos para regressão
    """
    separador = "=" * 55

    print(separador)
    print("COLÔNIA MARTE BASE ALPHA - RELATÓRIO DO SISTEMA")
    print(separador)

    # --- Dados de entrada ---
    print("\nDADOS DE ENTRADA:")
    print(f"   Bateria       : {energia}%")
    print(f"   Consumo atual : {consumo} unidades")
    print(f"   Geração atual : {geracao} unidades")
    print(f"   Velocidade vento: {velocidade_vento} km/h")

    # --- Decisão automática ---
    print("\nDECISÃO AUTOMÁTICA:")
    decisao = tomar_decisao(energia, consumo)
    print(f"   {decisao}")

    # --- Status dos sistemas ---
    print("\nSTATUS DOS SISTEMAS:")
    status = verificar_suporte_vida(energia)
    for sistema, estado in status.items():
        print(f"   {sistema:<20}: {estado}")

    # --- Análise de energia ---
    print("\nANÁLISE ENERGÉTICA:")
    analise = analisar_energia(geracao, consumo)
    for linha in analise.split("\n"):
        print(f"   {linha}")

    # --- Previsão eólica ---
    print("\nPREVISÃO EÓLICA (Regressão Linear):")
    previsao = prever_energia_eolica(velocidade_vento, historico)
    print(f"   Vento = {velocidade_vento} km/h → Energia prevista ≈ {previsao} unidades")

    print("\n" + separador)
    print("   FIM DO RELATÓRIO")
    print(separador + "\n")


if __name__ == "__main__":

    # Inicializar dados da colônia
    colonia = inicializar_colonia()
    historico = colonia["historico"]

    print("\n" + "=" * 55)
    print("  BEM-VINDO AO SISTEMA DA COLÔNIA MARTE BASE ALPHA")
    print("=" * 55)


    # EXEMPLO 1: Situação de alerta (energia baixa, consumo alto)

    print("\n>>> CENÁRIO 1: Energia baixa e consumo alto")
    gerar_relatorio(
        energia=40,
        consumo=70,
        geracao=40,
        velocidade_vento=11,
        historico=historico
    )


    # EXEMPLO 2: Situação positiva (geração alta, consumo baixo)

    print(">>> CENÁRIO 2: Geração alta, consumo baixo")
    gerar_relatorio(
        energia=85,
        consumo=30,
        geracao=80,
        velocidade_vento=18,
        historico=historico
    )


    # EXEMPLO 3: Situação crítica

    print(">>> CENÁRIO 3: Situação crítica")
    gerar_relatorio(
        energia=15,
        consumo=75,
        geracao=20,
        velocidade_vento=5,
        historico=historico
    )