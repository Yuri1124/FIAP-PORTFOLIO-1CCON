
# MISSÃO LEVIATHAN-7 — Sistema Inteligente de Monitoramento Operacional

from collections import deque  # Para implementar a fila de alertas

# 1 - DADOS SIMULADOS DA TELEMETRIA

# Dicionário de módulos (1 = operacional, 0 = falha)

modulos = {
    "suporte_vida":  1,
    "energia":       1,
    "comunicacao":   0,
    "habitat":       1,
    "laboratorio":   0,
    "armazenamento": 1
}

# Hierarquia da missão (Representa a estrutura em árvore dos sistemas dependentes)
hierarquia = {
    "energia": {
        "fusao_nuclear": 1,
        "baterias_reserva": 1,
        "distribuicao": 1
    },
    "habitat": {
        "oxigenio": 1,
        "temperatura_interna": 1,
        "pressao_interna": 1
    },
    "comunicacao": {
        "antena_principal": 0,
        "retransmissor_gelo": 1,
        "comunicacao_emergencia": 1
    }
}

# Leituras energéticas por ciclo (ciclo, geracao_kWh, consumo_kWh, reserva_%)

leituras_energia = [
    [1, 120,  95, 98],
    [2, 115, 102, 91],
    [3, 110, 108, 83],
    [4,  98, 115, 72],
    [5,  85, 118, 60],
    [6,  70, 122, 47],
]

# Variáveis ambientais
ambiente = {
    "temperatura_interna":  18.4,    # Celsius
    "temperatura_externa": -160.2,   # Celsius
    "pressao_casco":       -9999,    # VALOR INVÁLIDO (sensor danificado)
    "nivel_radiacao":        7.8,    # mSv/h — radiação de Júpiter
    "qualidade_sinal":       23,     # % — sinal via retransmissor no gelo
    "velocidade_corrente":    2.1,   # m/s — corrente submarina
}

# Log de eventos (Usamos uma lista e adicionamos com append() / consultamos com [-1])
log_eventos = []
log_eventos.append({"tempo": "T+00:00", "tipo": "BOOT",    "desc": "Sistema LEVIATHAN-7 reinicializado após impacto"})
log_eventos.append({"tempo": "T+00:12", "tipo": "FALHA",   "desc": "Comunicação principal perdida — antena danificada"})
log_eventos.append({"tempo": "T+00:15", "tipo": "ALERTA",  "desc": "Laboratório desligado automaticamente para economizar energia"})
log_eventos.append({"tempo": "T+00:31", "tipo": "ERRO",    "desc": "Sensor de pressão do casco retornando valor inválido (-9999 kPa)"})
log_eventos.append({"tempo": "T+01:04", "tipo": "ALERTA",  "desc": "Reserva de energia caindo abaixo de 80%"})
log_eventos.append({"tempo": "T+01:45", "tipo": "INFO",    "desc": "Modo de economia de energia ativado — nível 2"})
log_eventos.append({"tempo": "T+02:10", "tipo": "CRÍTICO", "desc": "Nível de radiação de Júpiter acima do limiar seguro (7.8 mSv/h)"})
log_eventos.append({"tempo": "T+03:00", "tipo": "INFO",    "desc": "Janela de comunicação de emergência em 3 horas via retransmissor"})

# Fila de alertas pendentes
fila_alertas = deque()

# 2 - FUNÇÕES AUXILIARES

def separador(titulo=""):
    """Imprime uma linha separadora com título opcional."""
    if titulo:
        print(f"\n{'='*60}")
        print(f"  {titulo}")
        print(f"{'='*60}")
    else:
        print("-" * 60)

def classificar_severidade(nivel):
    """Retorna o emoji de severidade para exibição visual."""
    if nivel == "CRÍTICO":
        return "🔴"
    elif nivel == "ALERTA":
        return "🟡"
    else:
        return "🟢"

# 3 - LEITURA E INTERPRETAÇÃO DE DADOS

def interpretar_dados():
    """
    Analisa os dados brutos e identifica anomalias e inconsistências.
    Retorna um dicionário com o resumo do estado atual da missão.
    """
    separador("LEITURA E INTERPRETAÇÃO DE DADOS")

    # Extraindo dados das listas para variáveis
    ciclo_atual      = leituras_energia[-1][0]   # Último ciclo registrado
    geracao_atual    = leituras_energia[-1][1]    # kWh gerados no ciclo atual
    consumo_atual    = leituras_energia[-1][2]    # kWh consumidos no ciclo atual
    reserva_atual    = leituras_energia[-1][3]    # % de reserva atual

    # Extraindo variáveis ambientais
    temp_interna  = ambiente["temperatura_interna"]
    pressao_casco = ambiente["pressao_casco"]
    radiacao      = ambiente["nivel_radiacao"]
    sinal         = ambiente["qualidade_sinal"]

    print(f"\n  Ciclo atual         : {ciclo_atual}")
    print(f"  Geração (kWh)       : {geracao_atual}")
    print(f"  Consumo (kWh)       : {consumo_atual}")
    print(f"  Reserva energética  : {reserva_atual}%")
    print(f"  Temperatura interna : {temp_interna}°C")
    print(f"  Radiação            : {radiacao} mSv/h")
    print(f"  Qualidade do sinal  : {sinal}%")

    # Detecção de inconsistência: pressão inválida
    # Regra: pressão fisicamente impossível (negativa ou acima de 200.000 kPa)
    # Expressão booleana: pressao_invalida
    pressao_invalida = (pressao_casco < 0) or (pressao_casco > 200000)

    if pressao_invalida:
        print(f"\n  ⚠️  INCONSISTÊNCIA DETECTADA: Sensor de pressão do casco")
        print(f"      Valor lido: {pressao_casco} kPa — fisicamente impossível")
        print(f"      Diagnóstico: sensor danificado pelo impacto")
        print(f"      Ação: dado IGNORADO — não acionar alarme de ruptura de casco")
        fila_alertas.append({
            "nivel": "ALERTA",
            "msg": "Sensor de pressão com falha — dado descartado",
            "acao": "Monitorar integridade do casco por sensores secundários"
        })

    return {
        "ciclo": ciclo_atual,
        "geracao": geracao_atual,
        "consumo": consumo_atual,
        "reserva": reserva_atual,
        "radiacao": radiacao,
        "sinal": sinal,
        "temp_interna": temp_interna,
        "pressao_invalida": pressao_invalida
    }

# 4 - TABELA DE STATUS DOS MÓDULOS

def exibir_status_modulos():
    """
    Exibe a tabela de status de todos os módulos críticos.
    Usa o dicionário 'modulos' para busca O(1) por nome.
    """
    separador("STATUS DOS MÓDULOS CRÍTICOS")
    print(f"\n  {'Módulo':<20} {'Status':<12} {'Indicador'}")
    print(f"  {'-'*20} {'-'*12} {'-'*10}")

    for nome, status in modulos.items():
        # Lógica booleana: status == 1 → operacional, status == 0 → falha
        if status == 1:
            estado    = "OPERACIONAL"
            indicador = "🟢"
        else:
            estado    = "FALHA"
            indicador = "🔴"
        print(f"  {nome:<20} {estado:<12} {indicador}")

# 5 - REGRAS LÓGICAS E DIAGNÓSTICO DA MISSÃO

def diagnosticar_missao(dados):
    """
    Aplica regras lógicas para classificar o estado operacional da missão.

    Expressão booleana principal do diagnóstico:
    STATUS_CRITICO = (reserva < 50) OR (suporte_vida == 0) OR
                     (radiacao > 10) OR (sinal < 10 AND comunicacao == 0)

    STATUS_ALERTA  = (reserva < 70 AND reserva >= 50) OR
                     (comunicacao == 0) OR (sinal < 30) OR
                     (laboratorio == 0)

    STATUS_NORMAL  = NOT STATUS_CRITICO AND NOT STATUS_ALERTA
    """
    separador("DIAGNÓSTICO OPERACIONAL")

    reserva      = dados["reserva"]
    radiacao     = dados["radiacao"]
    sinal        = dados["sinal"]
    suporte_vida = modulos["suporte_vida"]
    comunicacao  = modulos["comunicacao"]
    laboratorio  = modulos["laboratorio"]

    # Regra 1: Condição crítica de energia
    # AND: reserva baixa E consumo maior que geração
    energia_critica = (reserva < 50) and (dados["consumo"] > dados["geracao"])

    # Regra 2: Condição crítica de segurança
    # OR: falha de suporte à vida OU radiação letal
    seguranca_critica = (suporte_vida == 0) or (radiacao > 10.0)

    # Regra 3: Comunicação comprometida
    # AND + NOT: comunicação falhou E sinal fraco E NÃO há redundância
    comunicacao_comprometida = (comunicacao == 0) and (sinal < 30) and not (sinal > 50)

    # Regra 4: Alerta energético (não crítico ainda)
    # AND com faixa: reserva entre 50% e 70%
    alerta_energia = (reserva >= 50) and (reserva < 70)

    # Classificação final
    # Expressão booleana principal
    status_critico = energia_critica or seguranca_critica
    status_alerta  = (not status_critico) and (comunicacao_comprometida or alerta_energia or laboratorio == 0)
    status_normal  = not status_critico and not status_alerta

    # Exibição do diagnóstico
    print(f"\n  Reserva energética  : {reserva}%")
    print(f"  Geração vs Consumo  : {dados['geracao']} kWh vs {dados['consumo']} kWh")
    print(f"  Radiação            : {radiacao} mSv/h (limite: 10.0)")
    print(f"  Qualidade do sinal  : {sinal}%")
    print(f"  Suporte à vida      : {'OK' if suporte_vida else 'FALHA'}")

    print(f"\n  Regra 1 (energia crítica)       : {'ATIVADA' if energia_critica else 'Normal'}")
    print(f"  Regra 2 (segurança crítica)     : {'ATIVADA' if seguranca_critica else 'Normal'}")
    print(f"  Regra 3 (comunicação comprometida): {'ATIVADA' if comunicacao_comprometida else 'Normal'}")
    print(f"  Regra 4 (alerta de energia)     : {'ATIVADA' if alerta_energia else 'Normal'}")

    if status_critico:
        print(f"\n  🔴 STATUS FINAL: CRÍTICO")
        print(f"     Motivo: energia deficitária e/ou ameaça à segurança detectada")
    elif status_alerta:
        print(f"\n  🟡 STATUS FINAL: ALERTA")
        print(f"     Motivo: comunicação comprometida e/ou energia em declínio")
    else:
        print(f"\n  🟢 STATUS FINAL: NORMAL")

    return {
        "critico": status_critico,
        "alerta":  status_alerta,
        "normal":  status_normal,
        "energia_critica": energia_critica,
        "comunicacao_comprometida": comunicacao_comprometida
    }

# 6 - GERAÇÃO DE ALERTAS AUTOMÁTICOS

def gerar_alertas(dados, diagnostico):
    """
    Gera alertas automáticos com base no diagnóstico.
    Os alertas são enfileirados por prioridade (CRÍTICO > ALERTA > INFO).
    """
    separador("ALERTAS AUTOMÁTICOS")

    # Gerando alertas com base nas regras

    if modulos["comunicacao"] == 0:
        fila_alertas.append({
            "nivel": "CRÍTICO",
            "msg": "Comunicação principal OFFLINE — antena danificada",
            "acao": "Ativar protocolo de comunicação de emergência via retransmissor"
        })

    if diagnostico["energia_critica"]:
        fila_alertas.append({
            "nivel": "CRÍTICO",
            "msg": f"Energia em colapso — reserva: {dados['reserva']}%, consumo supera geração",
            "acao": "Desligar todos os sistemas não essenciais imediatamente"
        })

    if dados["radiacao"] > 5.0:
        fila_alertas.append({
            "nivel": "ALERTA",
            "msg": f"Radiação elevada de Júpiter: {dados['radiacao']} mSv/h",
            "acao": "Reforçar blindagem eletrônica — monitorar sistemas sensíveis"
        })

    if modulos["laboratorio"] == 0:
        fila_alertas.append({
            "nivel": "ALERTA",
            "msg": "Laboratório científico OFFLINE",
            "acao": "Preservar amostras coletadas — aguardar restabelecimento de energia"
        })

    if dados["sinal"] < 30:
        fila_alertas.append({
            "nivel": "ALERTA",
            "msg": f"Qualidade de sinal crítica: {dados['sinal']}%",
            "acao": "Aguardar próxima janela de comunicação (T+03:00)"
        })

    # Exibindo fila de alertas por ordem de chegada
    # Alertas CRÍTICOS são exibidos primeiro, depois ALERTA, depois INFO
    criticos = [a for a in fila_alertas if a["nivel"] == "CRÍTICO"]
    alertas  = [a for a in fila_alertas if a["nivel"] == "ALERTA"]
    infos    = [a for a in fila_alertas if a["nivel"] == "INFO"]

    todos_ordenados = criticos + alertas + infos

    print(f"\n  Total de alertas na fila: {len(todos_ordenados)}\n")

    for i, alerta in enumerate(todos_ordenados, 1):
        icone = classificar_severidade(alerta["nivel"])
        print(f"  [{i}] {icone} [{alerta['nivel']}] {alerta['msg']}")
        print(f"       → Ação: {alerta['acao']}\n")

# 7 - ANÁLISE E PREVISÃO DE DADOS (Regressão Linear Simples)

def prever_energia():
    """
    Aplica regressão linear simples para prever quando a reserva de energia
    chegará ao ponto crítico de não-retorno (20%).

    Metodologia:
    - Dados: reserva energética ao longo dos 6 ciclos registrados
    - Técnica: regressão linear y = a*x + b (implementada manualmente)
    - Resultado: estimativa do ciclo em que a reserva atingirá 20%
    - Sem bibliotecas externas — apenas Python puro
    """
    separador("ANÁLISE E PREVISÃO ENERGÉTICA")

    # Extraindo as séries de ciclos e reservas das leituras
    ciclos   = [linha[0] for linha in leituras_energia]   # [1, 2, 3, 4, 5, 6]
    reservas = [linha[3] for linha in leituras_energia]   # [98, 91, 83, 72, 60, 47]

    n = len(ciclos)

    # Cálculo da regressão linear: y = a*x + b
    # Fórmula do coeficiente angular (a):
    # a = (n * Σ(x*y) - Σx * Σy) / (n * Σ(x²) - (Σx)²)
    soma_x   = sum(ciclos)
    soma_y   = sum(reservas)
    soma_xy  = sum(ciclos[i] * reservas[i] for i in range(n))
    soma_x2  = sum(ciclos[i] ** 2 for i in range(n))

    a = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x ** 2)
    b = (soma_y - a * soma_x) / n

    print(f"\n  Dados utilizados (ciclo → reserva %):")
    for i in range(n):
        print(f"    Ciclo {ciclos[i]}: {reservas[i]}%")

    print(f"\n  Equação da regressão linear: reserva = {a:.2f} × ciclo + {b:.2f}")
    print(f"  Coeficiente angular (a = {a:.2f}): queda de ~{abs(a):.1f}% por ciclo")

    # Previsão: em qual ciclo a reserva chegará a 20%?
    # Resolvendo: 20 = a*x + b → x = (20 - b) / a
    LIMITE_CRITICO = 20  # % — abaixo disso, retorno à superfície impossível
    ciclo_critico  = (LIMITE_CRITICO - b) / a

    # Previsões para os próximos 3 ciclos
    print(f"\n  Projeção para próximos ciclos:")
    for c in [7, 8, 9]:
        projecao = a * c + b
        print(f"    Ciclo {c}: {projecao:.1f}%")

    print(f"\n  ⚠️  PONTO DE NÃO-RETORNO (reserva = {LIMITE_CRITICO}%)")
    print(f"      Estimativa: ciclo {ciclo_critico:.1f}")
    print(f"      Ciclo atual: 6 → restam aproximadamente {ciclo_critico - 6:.1f} ciclos")

    # Influência na decisão do sistema
    ciclos_restantes = ciclo_critico - 6
    if ciclos_restantes < 3:
        print(f"\n  🔴 DECISÃO INFLUENCIADA: tempo crítico — iniciar subida imediatamente")
        fila_alertas.append({
            "nivel": "CRÍTICO",
            "msg": f"Ponto de não-retorno em {ciclos_restantes:.1f} ciclos",
            "acao": "Iniciar protocolo de emergência — subida para superfície"
        })
    elif ciclos_restantes < 5:
        print(f"\n  🟡 DECISÃO INFLUENCIADA: desligar sistemas secundários para estender missão")
    else:
        print(f"\n  🟢 Margem de tempo adequada — manter operação monitorada")

    return ciclo_critico

# 8. LOG DE EVENTOS (PILHA)

def exibir_log_eventos():
    """
    Exibe o log de eventos usando a pilha — do mais recente ao mais antigo.
    O topo da pilha (log_eventos[-1]) é o evento mais recente.
    """
    separador("LOG DE EVENTOS — PILHA (mais recente → mais antigo)")
    print()
    # Iterando da pilha de cima para baixo (reverso)
    for evento in reversed(log_eventos):
        icone = "🔴" if evento["tipo"] == "CRÍTICO" else \
                "🟡" if evento["tipo"] in ["ALERTA", "ERRO"] else \
                "🔵" if evento["tipo"] == "BOOT" else "⚪"
        print(f"  {icone} [{evento['tempo']}] [{evento['tipo']}] {evento['desc']}")

# 9 - RECOMENDAÇÕES TÉCNICAS PRIORIZADAS

def gerar_recomendacoes(diagnostico, ciclo_critico):
    """
    Gera recomendações técnicas priorizadas com base no diagnóstico
    e na previsão energética.
    """
    separador("RECOMENDAÇÕES TÉCNICAS PRIORIZADAS")

    recomendacoes = []

    # Prioridade CRÍTICA
    if diagnostico["critico"]:
        recomendacoes.append({
            "prioridade": 1,
            "nivel": "CRÍTICA",
            "acao": "Manter suporte à vida e habitat em operação máxima"
        })
        recomendacoes.append({
            "prioridade": 2,
            "nivel": "CRÍTICA",
            "acao": "Ativar comunicação de emergência via retransmissor no gelo"
        })
        recomendacoes.append({
            "prioridade": 3,
            "nivel": "CRÍTICA",
            "acao": f"Iniciar contagem regressiva para subida — ponto crítico em ciclo {ciclo_critico:.1f}"
        })

    # Prioridade ALTA
    recomendacoes.append({
        "prioridade": 4,
        "nivel": "ALTA",
        "acao": "Desligar laboratório e sistemas científicos não essenciais"
    })
    recomendacoes.append({
        "prioridade": 5,
        "nivel": "ALTA",
        "acao": "Redirecionar energia para baterias de reserva e propulsão"
    })

    # Prioridade MÉDIA
    recomendacoes.append({
        "prioridade": 6,
        "nivel": "MÉDIA",
        "acao": "Registrar dados científicos coletados na memória de longo prazo"
    })
    recomendacoes.append({
        "prioridade": 7,
        "nivel": "MÉDIA",
        "acao": "Agendar diagnóstico de sensor de pressão na próxima janela de manutenção"
    })

    print()
    for rec in recomendacoes:
        icone = "🔴" if rec["nivel"] == "CRÍTICA" else \
                "🟠" if rec["nivel"] == "ALTA" else "🟡"
        print(f"  [{rec['prioridade']}] {icone} [{rec['nivel']}] {rec['acao']}")

# 10 - HIERARQUIA DA MISSÃO

def exibir_hierarquia():
    """
    Exibe a hierarquia de sistemas da missão em formato de árvore.
    Usa o dicionário 'hierarquia' que representa a estrutura em árvore.
    """
    separador("HIERARQUIA DE SISTEMAS")
    print()
    for sistema, subsistemas in hierarquia.items():
        status_sistema = modulos.get(sistema, 1)
        icone = "🟢" if status_sistema else "🔴"
        print(f"  {icone} {sistema.upper()}")
        for sub, status in subsistemas.items():
            icone_sub = "  ├─ 🟢" if status else "  ├─ 🔴"
            print(f"  {icone_sub} {sub}: {'OK' if status else 'FALHA'}")
        print()

# 11 - FUNÇÃO PRINCIPAL — ORQUESTRA TODO O SISTEMA

def main():
    print("\n" + "|" * 60)
    print("  LEVIATHAN-7 | SISTEMA DE MONITORAMENTO OPERACIONAL")
    print("  Missão Europa — Oceano Subsuperficial de Júpiter")
    print("  Profundidade estimada: 28.400 metros")
    print("  Status: PÓS-IMPACTO | Ciclo 6 de operação")
    print("|" * 60)

    # Passo 1: Ler e interpretar os dados
    dados = interpretar_dados()

    # Passo 2: Exibir status dos módulos
    exibir_status_modulos()

    # Passo 3: Exibir hierarquia de sistemas
    exibir_hierarquia()

    # Passo 4: Diagnóstico com regras lógicas
    diagnostico = diagnosticar_missao(dados)

    # Passo 5: Gerar alertas automáticos
    gerar_alertas(dados, diagnostico)

    # Passo 6: Análise e previsão energética (regressão linear)
    ciclo_critico = prever_energia()

    # Passo 7: Log de eventos (pilha)
    exibir_log_eventos()

    # Passo 8: Recomendações priorizadas
    gerar_recomendacoes(diagnostico, ciclo_critico)

    # Resumo final
    separador("RESUMO FINAL DA MISSÃO")
    status = "🔴 CRÍTICO" if diagnostico["critico"] else \
             "🟡 ALERTA"  if diagnostico["alerta"]  else "🟢 NORMAL"
    print(f"\n  Status operacional  : {status}")
    print(f"  Reserva energética  : {dados['reserva']}%")
    print(f"  Ciclos até colapso  : {ciclo_critico - dados['ciclo']:.1f} ciclos estimados")
    print(f"  Alertas gerados     : {len(fila_alertas)}")
    print(f"  Eventos no log      : {len(log_eventos)}")
    print(f"\n  Próxima janela de comunicação: T+03:00")
    print(f"  Aguardando instruções da Terra...\n")
    print("|" * 60 + "\n")

# Ponto de entrada do programa
if __name__ == "__main__":
    main()
