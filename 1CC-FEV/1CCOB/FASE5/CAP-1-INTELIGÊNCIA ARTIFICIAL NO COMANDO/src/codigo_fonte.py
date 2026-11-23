import json
from datetime import datetime

# 1. CONFIGURACAO DE ARQUIVOS
ARQUIVO_JSON = "dados_colonia.json"
ARQUIVO_TXT = "registros_colonia.txt"

DADOS_INICIAIS = {
    "modulos": [
        {
            "nome": "Suporte de Vida",
            "status": "ativo",
            "responsavel": "Equipe Biosuporte",
            "ultima_manutencao": "2026-08-20"
        },
        {
            "nome": "Reator de Fusao",
            "status": "ativo",
            "responsavel": "Equipe Engenharia",
            "ultima_manutencao": "2026-08-15"
        },
        {
            "nome": "Hidroponia Central",
            "status": "manutencao",
            "responsavel": "Equipe Agricultura",
            "ultima_manutencao": "2026-09-01"
        }
    ],
    "alertas": [
        {
            "id": 1,
            "modulo": "Reator de Fusao",
            "tipo_ocorrencia": "Falha Critica",
            "prioridade": "Alta",
            "data": "2026-09-01",
            "seguro": False,
            "consistente": True,
            "mensagem": "Temperatura do reator acima do limite seguro operacional."
        },
        {
            "id": 2,
            "modulo": "Hidroponia Central",
            "tipo_ocorrencia": "Consumo Elevado",
            "prioridade": "Media",
            "data": "2026-09-02",
            "seguro": True,
            "consistente": False,
            "mensagem": "Consumo de agua acima da media historica do setor."
        }
    ],
    "solicitacoes": [
        {
            "id": 1,
            "tripulante": "Comandante Ihara",
            "setor": "Engenharia",
            "urgente": True,
            "essencial": True,
            "descricao": "Solicito verificacao imediata do sistema de refrigeracao do reator."
        },
        {
            "id": 2,
            "tripulante": "Tecnica Alave",
            "setor": "Lazer",
            "urgente": False,
            "essencial": False,
            "descricao": "Solicito ajuste de iluminacao no modulo de convivencia."
        }
    ],
    "historico_respostas": []
}


# 2. FUNCOES UTILITARIAS
def agora():
    """Retorna a data e hora atuais formatadas como texto."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def perguntar_sim_nao(pergunta):
    """Faz uma pergunta de sim/nao ao usuario e devolve um valor booleano."""
    resposta = input(f"{pergunta} (s/n): ").strip().lower()
    return resposta == "s"


# 3. INICIALIZACAO DOS ARQUIVOS (uso do modo 'x' - criacao exclusiva)
def inicializar_arquivos():
    """
    Garante que os arquivos de dados existam antes do sistema ser utilizado.

    Utiliza o modo 'x' (criacao exclusiva): se o arquivo ja existir, o Python
    lanca FileExistsError automaticamente. Essa excecao e tratada para que o
    programa simplesmente preserve os dados ja gravados em execucoes
    anteriores, em vez de sobrescreve-los.
    """
    try:
        with open(ARQUIVO_JSON, "x", encoding="utf-8") as arquivo:
            json.dump(DADOS_INICIAIS, arquivo, ensure_ascii=False, indent=4)
        print(f"[INFO] Arquivo '{ARQUIVO_JSON}' criado com dados iniciais.")
    except FileExistsError:
        pass

    try:
        with open(ARQUIVO_TXT, "x", encoding="utf-8") as arquivo:
            linhas_iniciais = [
                "==================================================\n",
                "REGISTROS OPERACIONAIS - NUCLEO COGNITIVO AURORA SIGER\n",
                "==================================================\n",
                f"[{agora()}] SISTEMA - Nucleo Cognitivo inicializado pela primeira vez.\n"
            ]
            arquivo.writelines(linhas_iniciais)
        print(f"[INFO] Arquivo '{ARQUIVO_TXT}' criado com registro inicial.")
    except FileExistsError:
        pass


# 4. MANIPULACAO DO ARQUIVO JSON (dicionarios em Python)
def carregar_dados():
    """Le (modo 'r') e carrega o conteudo do arquivo JSON como um dicionario Python."""
    with open(ARQUIVO_JSON, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    return dados


def salvar_dados(dados):
    """Grava (modo 'w') o dicionario Python de volta no arquivo JSON, sobrescrevendo-o."""
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)


# 5. MANIPULACAO DO ARQUIVO DE TEXTO (logs / registros)
def registrar_log(categoria, mensagem):
    """
    Adiciona uma nova linha ao arquivo de registros usando o modo 'a+'
    (acrescentar e permitir leitura no mesmo bloco 'with').

    Apos gravar a nova linha, o cursor do arquivo e reposicionado no inicio
    com seek(0) e todo o conteudo e lido com readlines(), apenas para
    confirmar que a gravacao foi realizada com sucesso.
    """
    linha = f"[{agora()}] {categoria.upper()} - {mensagem}\n"
    with open(ARQUIVO_TXT, "a+", encoding="utf-8") as arquivo:
        arquivo.write(linha)
        arquivo.seek(0)
        _ = arquivo.readlines()
    print(f"[LOG REGISTRADO] {linha.strip()}")


def exibir_registros_texto():
    """Exibe o conteudo do arquivo de registros na tela."""
    print("\n----- REGISTROS SALVOS (registros_colonia.txt) -----")
    with open(ARQUIVO_TXT, "r", encoding="utf-8") as arquivo:
        primeira_linha = arquivo.readline()
        print(f"Cabecalho: {primeira_linha.strip()}")
        demais_linhas = arquivo.readlines()
    for indice, linha in enumerate(demais_linhas, start=1):
        texto_linha = linha.strip()
        if texto_linha:
            print(f"{indice:02d}. {texto_linha}")
    print("-----------------------------------------------------\n")


# 6. CADASTRO DE REGISTROS DA COLONIA
def cadastrar_modulo():
    dados = carregar_dados()
    print("\n--- Cadastro de Modulo da Colonia ---")
    nome = input("Nome do modulo: ").strip()
    status = input("Status (ativo/inativo/manutencao): ").strip().lower()
    responsavel = input("Equipe responsavel: ").strip()

    novo_modulo = {
        "nome": nome,
        "status": status,
        "responsavel": responsavel,
        "ultima_manutencao": agora()[:10]
    }
    dados["modulos"].append(novo_modulo)
    salvar_dados(dados)
    registrar_log("cadastro", f"Modulo '{nome}' cadastrado com status '{status}'.")
    print("Modulo cadastrado com sucesso!\n")


def cadastrar_alerta():
    dados = carregar_dados()
    print("\n--- Cadastro de Alerta Operacional ---")
    modulo = input("Modulo afetado: ").strip()
    tipo_ocorrencia = input("Tipo de ocorrencia: ").strip()
    prioridade = input("Prioridade (Alta/Media/Baixa): ").strip()
    seguro = perguntar_sim_nao("O modulo esta seguro?")
    consistente = perguntar_sim_nao("Os dados do modulo estao consistentes?")
    mensagem = input("Mensagem resumida do problema: ").strip()

    novo_id = max([a["id"] for a in dados["alertas"]], default=0) + 1
    novo_alerta = {
        "id": novo_id,
        "modulo": modulo,
        "tipo_ocorrencia": tipo_ocorrencia,
        "prioridade": prioridade,
        "data": agora()[:10],
        "seguro": seguro,
        "consistente": consistente,
        "mensagem": mensagem
    }
    dados["alertas"].append(novo_alerta)
    salvar_dados(dados)
    registrar_log("alerta", f"Novo alerta cadastrado (ID {novo_id}) no modulo '{modulo}'.")
    print("Alerta cadastrado com sucesso!\n")


def cadastrar_solicitacao():
    dados = carregar_dados()
    print("\n--- Cadastro de Solicitacao da Tripulacao ---")
    tripulante = input("Nome do tripulante: ").strip()
    setor = input("Setor: ").strip()
    urgente = perguntar_sim_nao("A solicitacao e urgente?")
    essencial = perguntar_sim_nao("O setor e considerado essencial?")
    descricao = input("Descricao da solicitacao: ").strip()

    novo_id = max([s["id"] for s in dados["solicitacoes"]], default=0) + 1
    nova_solicitacao = {
        "id": novo_id,
        "tripulante": tripulante,
        "setor": setor,
        "urgente": urgente,
        "essencial": essencial,
        "descricao": descricao
    }
    dados["solicitacoes"].append(nova_solicitacao)
    salvar_dados(dados)
    registrar_log("solicitacao", f"Nova solicitacao cadastrada (ID {novo_id}) por '{tripulante}'.")
    print("Solicitacao cadastrada com sucesso!\n")


def consultar_registros_salvos():
    dados = carregar_dados()
    print("\n----- DADOS SALVOS (dados_colonia.json) -----")
    print(f"Modulos cadastrados: {len(dados['modulos'])}")
    for m in dados["modulos"]:
        print(f"  - {m['nome']} | status: {m['status']} | responsavel: {m['responsavel']}")

    print(f"\nAlertas cadastrados: {len(dados['alertas'])}")
    for a in dados["alertas"]:
        print(f"  - ID {a['id']} | {a['modulo']} | {a['tipo_ocorrencia']} | prioridade: {a['prioridade']}")

    print(f"\nSolicitacoes cadastradas: {len(dados['solicitacoes'])}")
    for s in dados["solicitacoes"]:
        print(f"  - ID {s['id']} | {s['tripulante']} | setor: {s['setor']} | urgente: {s['urgente']}")

    exibir_registros_texto()


# 7. REGRA LOGICA E SIMPLIFICACAO BOOLEANA

def validar_bloqueio_original(seguro, consistente):
    """Expressao original: BLOQUEIO = NOT (SEGURO AND CONSISTENTE)."""
    return not (seguro and consistente)


def validar_bloqueio_simplificado(seguro, consistente):
    """Expressao simplificada por De Morgan: BLOQUEIO = (NOT SEGURO) OR (NOT CONSISTENTE)."""
    return (not seguro) or (not consistente)


def demonstrar_simplificacao_booleana():
    print("\n--- Demonstracao da Regra Logica e Simplificacao Booleana ---")
    print("Expressao original:      BLOQUEIO = NOT (SEGURO AND CONSISTENTE)")
    print("Expressao simplificada:  BLOQUEIO = (NOT SEGURO) OR (NOT CONSISTENTE)\n")
    print(f"{'SEGURO':<8}{'CONSISTENTE':<14}{'ORIGINAL':<12}{'SIMPLIFICADA':<14}")
    for seguro in (True, False):
        for consistente in (True, False):
            original = validar_bloqueio_original(seguro, consistente)
            simplificada = validar_bloqueio_simplificado(seguro, consistente)
            print(f"{str(seguro):<8}{str(consistente):<14}{str(original):<12}{str(simplificada):<14}")
    print("\nAs colunas ORIGINAL e SIMPLIFICADA sao identicas em todas as linhas,")
    print("comprovando que o Teorema de De Morgan preserva o resultado logico.\n")


# 8. ENGENHARIA DE PROMPTS
def prompt_zero_shot_resumo_alerta(alerta):
    """
    Prompt Zero-shot: nenhum exemplo de entrada/saida e fornecido, apenas a
    instrucao direta e o dado a ser processado.
    """
    return (
        "Resuma o alerta operacional abaixo em ate duas frases, destacando "
        "o modulo afetado e o nivel de prioridade.\n\n"
        f"Alerta: {alerta['mensagem']}\n"
        f"Modulo: {alerta['modulo']} | Prioridade: {alerta['prioridade']}"
    )


def prompt_few_shot_classificar_solicitacao(solicitacao):
    """
    Prompt Few-shot: fornece exemplos de entrada/saida antes da solicitacao
    real, orientando o modelo sobre o padrao de classificacao esperado.
    """
    return (
        "Classifique a solicitacao da tripulacao como 'PRIORITARIA' ou 'NORMAL'.\n\n"
        "Exemplo 1:\n"
        "Solicitacao: 'Vazamento de oxigenio no setor de engenharia.'\n"
        "Classificacao: PRIORITARIA\n\n"
        "Exemplo 2:\n"
        "Solicitacao: 'Gostaria de trocar a cor da iluminacao do meu quarto.'\n"
        "Classificacao: NORMAL\n\n"
        f"Solicitacao: '{solicitacao['descricao']}'\n"
        "Classificacao:"
    )


def gerar_prompt_resposta_padronizada(alerta, bloqueio):
    """
    Prompt para gerar uma resposta padronizada ao centro de controle,
    utilizando raciocinio em etapas (Chain-of-Thought) antes da conclusao.
    """
    return (
        "Voce e o assistente do Nucleo Cognitivo da Aurora Siger.\n"
        "Pense passo a passo antes de responder:\n"
        "1) Verifique se o modulo esta seguro.\n"
        "2) Verifique se os dados do modulo sao consistentes.\n"
        "3) Aplique a regra: BLOQUEIO = (NOT SEGURO) OR (NOT CONSISTENTE).\n"
        "4) Gere uma recomendacao objetiva para o centro de controle.\n\n"
        f"Modulo: {alerta['modulo']}\n"
        f"Seguro: {alerta['seguro']} | Consistente: {alerta['consistente']}\n"
        f"Resultado da regra: BLOQUEIO = {bloqueio}\n\n"
        "Gere a recomendacao final em uma frase objetiva."
    )


def prompt_saida_estruturada(alerta):
    """
    Prompt de saida estruturada: instrui o modelo a responder estritamente em
    formato JSON, facilitando a integracao com outros sistemas.
    """
    return (
        "Gere a resposta ESTRITAMENTE no formato JSON abaixo, sem texto adicional:\n\n"
        "{\n"
        '  "modulo": "<nome do modulo>",\n'
        '  "prioridade": "<prioridade do alerta>",\n'
        '  "acao_recomendada": "<acao recomendada em poucas palavras>"\n'
        "}\n\n"
        f"Dados do alerta: {alerta['mensagem']}"
    )


def exibir_prompts_estruturados():
    dados = carregar_dados()
    if not dados["alertas"] or not dados["solicitacoes"]:
        print("E necessario ter ao menos um alerta e uma solicitacao cadastrados.\n")
        return
    alerta = dados["alertas"][0]
    solicitacao = dados["solicitacoes"][0]

    print("\n=== EXEMPLO 1: PROMPT ZERO-SHOT (resumo de alerta) ===")
    print(prompt_zero_shot_resumo_alerta(alerta))

    print("\n=== EXEMPLO 2: PROMPT FEW-SHOT (classificacao de solicitacao) ===")
    print(prompt_few_shot_classificar_solicitacao(solicitacao))

    print("\n=== EXEMPLO 3: PROMPT COM SAIDA ESTRUTURADA (JSON) ===")
    print(prompt_saida_estruturada(alerta))
    print()


# 9. SIMULACAO DE RESPOSTA DE ASSISTENTE INTELIGENTE
def estimar_tokens(texto):
    """
    Estimativa simplificada da quantidade de tokens de um texto, apenas para
    fins didaticos (tokenizadores reais usam sub-palavras, nao palavras
    inteiras). Aqui, cada palavra e considerada aproximadamente um token.
    """
    return len(texto.split())


def simular_resposta_assistente(prompt, contexto="geral", bloqueio=None):
    """
    Simula uma resposta de um assistente de IA generativa (Large Language
    Model) sem chamar nenhuma API externa. A resposta e construida localmente
    a partir de regras simples, apenas para demonstrar a estrutura de entrada
    (prompt) e saida (resposta) de um sistema baseado em Next Token
    Prediction.
    """
    tokens_entrada = estimar_tokens(prompt)

    if contexto == "alerta":
        if bloqueio:
            resposta = ("Recomenda-se o bloqueio imediato da operacao do modulo "
                        "ate a verificacao completa de seguranca e consistencia dos dados.")
        else:
            resposta = ("O modulo pode continuar em operacao; recomenda-se apenas "
                        "monitoramento continuo dos parametros reportados.")
    else:
        resposta = "Solicitacao recebida e registrada para acompanhamento da equipe responsavel."

    tokens_saida = estimar_tokens(resposta)
    print(f"[INFO] Tokens estimados -> entrada: {tokens_entrada} | saida: {tokens_saida}")
    return resposta


def analisar_alerta_operacional():
    """
    Funcionalidade integrada de exemplo: carrega um alerta salvo em JSON,
    verifica se ele exige bloqueio usando a regra booleana simplificada, exibe
    um prompt estruturado (Chain-of-Thought) e simula a resposta do
    assistente para o centro de controle.
    """
    dados = carregar_dados()
    alertas = dados.get("alertas", [])
    if not alertas:
        print("Nenhum alerta cadastrado no momento.\n")
        return

    print("\n--- Alertas disponiveis ---")
    for alerta in alertas:
        print(f"ID {alerta['id']} - {alerta['modulo']} - {alerta['tipo_ocorrencia']}")

    try:
        id_escolhido = int(input("\nDigite o ID do alerta que deseja analisar: "))
    except ValueError:
        print("ID invalido.\n")
        return

    alerta = next((a for a in alertas if a["id"] == id_escolhido), None)
    if alerta is None:
        print("Alerta nao encontrado.\n")
        return

    bloqueio = validar_bloqueio_simplificado(alerta["seguro"], alerta["consistente"])

    print(f"\nModulo: {alerta['modulo']}")
    print(f"Ocorrencia: {alerta['tipo_ocorrencia']} | Prioridade: {alerta['prioridade']}")
    print(f"Seguro: {alerta['seguro']} | Consistente: {alerta['consistente']}")
    print(f"Resultado da regra booleana (BLOQUEIO): {bloqueio}")

    prompt = gerar_prompt_resposta_padronizada(alerta, bloqueio)
    print("\n--- Prompt estruturado gerado para o centro de controle (Chain-of-Thought) ---")
    print(prompt)

    resposta_simulada = simular_resposta_assistente(prompt, contexto="alerta", bloqueio=bloqueio)
    print("\n--- Resposta simulada do assistente ---")
    print(resposta_simulada)

    dados["historico_respostas"].append({
        "pergunta": prompt,
        "resposta_simulada": resposta_simulada,
        "tipo_prompt": "chain-of-thought"
    })
    salvar_dados(dados)
    registrar_log("analise", f"Alerta ID {id_escolhido} analisado. Bloqueio={bloqueio}.")
    print()


def demonstracao_interacao_assistente():
    """Demonstra uma interacao few-shot completa, do prompt a resposta simulada."""
    dados = carregar_dados()
    if not dados["solicitacoes"]:
        print("Nenhuma solicitacao cadastrada.\n")
        return

    print("\n--- Simulacao de Interacao com Assistente Inteligente (Few-shot) ---")
    solicitacao = dados["solicitacoes"][0]
    prompt = prompt_few_shot_classificar_solicitacao(solicitacao)
    print(prompt)

    classificacao = "PRIORITARIA" if solicitacao["urgente"] and solicitacao["essencial"] else "NORMAL"
    tokens_entrada = estimar_tokens(prompt)
    print(f"\n[INFO] Tokens estimados na entrada: {tokens_entrada}")
    print(f"Resposta simulada do assistente: {classificacao}")

    dados["historico_respostas"].append({
        "pergunta": prompt,
        "resposta_simulada": classificacao,
        "tipo_prompt": "few-shot"
    })
    salvar_dados(dados)
    registrar_log("interacao_ia", f"Solicitacao de {solicitacao['tripulante']} classificada como {classificacao}.")
    print()


# 10. DEMONSTRACAO CONCEITUAL DE OTIMIZACAO (MSE, GRADIENTE DESCENDENTE, REGULARIZACAO)
def erro_quadratico_medio(valores_reais, valores_previstos):
    n = len(valores_reais)
    soma_erros = sum((r - p) ** 2 for r, p in zip(valores_reais, valores_previstos))
    return soma_erros / n


def demonstrar_otimizacao():
    """
    Exemplo didatico e simplificado de como um parametro pode ser ajustado por
    Gradiente Descendente para minimizar o Erro Quadratico Medio (MSE), com e
    sem um termo de Regularizacao L2, usando como exemplo o consumo previsto
    de energia de um modulo em funcao das horas de operacao.
    """
    print("\n--- Demonstracao de Otimizacao: MSE e Gradiente Descendente ---")

    horas_operacao = [1, 2, 3, 4, 5]
    consumo_real = [2.1, 3.9, 6.2, 7.8, 10.1]

    taxa_aprendizado = 0.01
    fator_regularizacao = 0.1
    peso = 0.0

    print(f"{'Iteracao':<10}{'Peso':<12}{'MSE (sem reg.)':<18}{'MSE (com reg. L2)':<18}")
    for iteracao in range(1, 11):
        previsoes = [peso * h for h in horas_operacao]
        erro = erro_quadratico_medio(consumo_real, previsoes)
        erro_regularizado = erro + fator_regularizacao * (peso ** 2)

        gradiente = -2 * sum(
            (r - p) * h for r, p, h in zip(consumo_real, previsoes, horas_operacao)
        ) / len(horas_operacao)
        gradiente_regularizado = gradiente + 2 * fator_regularizacao * peso

        peso = peso - taxa_aprendizado * gradiente_regularizado

        print(f"{iteracao:<10}{peso:<12.4f}{erro:<18.4f}{erro_regularizado:<18.4f}")

    print("\nO peso do modelo se ajusta a cada iteracao na direcao que reduz o MSE.")
    print("O termo de regularizacao (L2) penaliza pesos muito altos, evitando que")
    print("o modelo se ajuste de forma extrema aos dados (overfitting).\n")


# 11. SOBRE O NCAS: MEMORIA/ARMAZENAMENTO E ETICA/DIVERSIDADE
def sobre_o_ncas():
    texto = """
=====================================================================
SOBRE O NUCLEO COGNITIVO DA AURORA SIGER (NCAS)
=====================================================================

MEMORIA, ARMAZENAMENTO E FLUXO DE DADOS
---------------------------------------------------------------------
Embora o NCAS seja construido apenas com Python, arquivos texto e JSON,
nenhum dado do sistema existe "solto" no computador. Todo registro
passa por um fluxo fisico real:

1. Quando uma funcao como salvar_dados() ou registrar_log() e chamada,
   o Python monta o conteudo em MEMORIA (RAM), de forma temporaria.
2. Em seguida, o comando de escrita (write, dump, writelines) transfere
   esse conteudo, atraves do barramento de dados do computador, ate um
   dispositivo de ARMAZENAMENTO permanente (disco/SSD), onde os
   arquivos dados_colonia.json e registros_colonia.txt ficam gravados.
3. Ao reiniciar o sistema, as funcoes carregar_dados() e a leitura do
   arquivo .txt buscam o conteudo do armazenamento, trazem os bytes de
   volta para a memoria RAM, e o Python os reconstroi como dicionarios,
   listas e strings utilizaveis pelo programa.
4. Esse ciclo (memoria -> barramento -> armazenamento -> barramento ->
   memoria) e o que garante que os alertas, modulos e solicitacoes da
   colonia continuem existindo mesmo depois que o programa e encerrado.

DIVERSIDADE, ETICA E RESPONSABILIDADE NO USO DE IA
---------------------------------------------------------------------
O NCAS simula respostas de um assistente inteligente para apoiar a
tripulacao da Aurora Siger. Mesmo em um sistema simulado, e importante
reconhecer que sistemas reais de IA generativa podem reproduzir vieses
presentes nos dados usados para treina-los. Por isso, o NCAS adota os
seguintes principios:

- As respostas simuladas evitam qualquer linguagem discriminatoria e
  tratam todos os tripulantes e setores de forma equivalente, sem
  favorecer grupos especificos.
- Equipes de desenvolvimento diversas tendem a identificar mais
  facilmente vieses e pontos cegos em sistemas de IA; por isso, a
  diversidade e tratada como um valor tecnico, e nao apenas social.
- Decisoes automatizadas (como bloquear um modulo ou priorizar uma
  solicitacao) tem impacto direto na seguranca da colonia. Por isso, o
  NCAS foi projetado para APOIAR a decisao humana, e nao substitui-la:
  toda saida do sistema deve ser revisada por um responsavel humano
  antes de qualquer acao critica ser executada.
- A responsabilidade final por qualquer acao tomada com base nas
  respostas do NCAS e sempre da equipe humana da colonia, nunca do
  sistema automatizado.
=====================================================================
"""
    print(texto)


# 12. MENU PRINCIPAL
def exibir_menu():
    print("=" * 60)
    print(" NUCLEO COGNITIVO DA AURORA SIGER (NCAS) ")
    print("=" * 60)
    print("1  - Cadastrar modulo da colonia")
    print("2  - Cadastrar alerta operacional")
    print("3  - Cadastrar solicitacao da tripulacao")
    print("4  - Consultar registros e dados salvos")
    print("5  - Analisar alerta operacional (regra + prompt + resposta)")
    print("6  - Demonstrar regra logica e simplificacao booleana")
    print("7  - Exibir prompts estruturados (zero-shot / few-shot / JSON)")
    print("8  - Simular interacao com assistente inteligente (few-shot)")
    print("9  - Demonstracao de otimizacao (MSE / Gradiente Descendente)")
    print("10 - Sobre o NCAS (memoria, armazenamento, etica e diversidade)")
    print("0  - Sair")
    print("=" * 60)


def main():
    inicializar_arquivos()
    while True:
        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            cadastrar_modulo()
        elif opcao == "2":
            cadastrar_alerta()
        elif opcao == "3":
            cadastrar_solicitacao()
        elif opcao == "4":
            consultar_registros_salvos()
        elif opcao == "5":
            analisar_alerta_operacional()
        elif opcao == "6":
            demonstrar_simplificacao_booleana()
        elif opcao == "7":
            exibir_prompts_estruturados()
        elif opcao == "8":
            demonstracao_interacao_assistente()
        elif opcao == "9":
            demonstrar_otimizacao()
        elif opcao == "10":
            sobre_o_ncas()
        elif opcao == "0":
            print("\nEncerrando o Nucleo Cognitivo da Aurora Siger. Ate logo!")
            break
        else:
            print("\nOpcao invalida. Tente novamente.\n")


if __name__ == "__main__":
    main()
