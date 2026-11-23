import json
import os
import sys
import time

from busca import buscar, criar_indice, normalizar

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_BASE = os.path.join(PASTA, "..", "data", "base_conhecimento.json")

CAMPOS_OBRIGATORIOS = ["id", "tema", "subtema", "titulo", "palavras_chave",
                       "orientacao", "referencia", "data_verificacao"]

AVISO_OFICIAL = "Este assistente não é um canal oficial e não substitui o atendimento do órgão responsável."

PROMPTS = {
    "A": "Você é um assistente de informações. Responda à pergunta usando a orientação "
         "encontrada na base e informe a fonte ao final.",
    "B": "Você é o Citizen Assist AI, um assistente de orientação cidadã não oficial. "
         "Use somente a base verificada. Responda com: título, resumo simples, passo a passo, "
         "fonte com link, data da verificação, aviso quando precisar confirmar e assuntos "
         "relacionados. Nunca invente prazos ou documentos e não peça dados pessoais. "
         "Se a pergunta não estiver na base, diga isso e sugira os temas disponíveis.",
}


# ---------- leitura da base ----------

def carregar_base(caminho=ARQUIVO_BASE):
    if not os.path.exists(caminho):
        raise ValueError("arquivo da base não encontrado: " + caminho)

    with open(caminho, encoding="utf-8") as arq:
        conteudo = arq.read()
    if not conteudo.strip():
        raise ValueError("o arquivo da base está vazio")

    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError:
        raise ValueError("o arquivo da base não é um JSON válido")

    if not dados.get("registros"):
        raise ValueError("a base não tem registros")

    registros = {}
    avisos = []
    for r in dados["registros"]:
        faltando = [c for c in CAMPOS_OBRIGATORIOS if not r.get(c)]
        if faltando:
            avisos.append(f"{r.get('id', '?')} ignorado: faltam os campos {', '.join(faltando)}")
        elif not r["referencia"].get("fonte") or not r["referencia"].get("url"):
            avisos.append(f"{r['id']} ignorado: referência sem fonte ou link")
        elif r["tema"] not in dados["temas"]:
            avisos.append(f"{r['id']} ignorado: tema '{r['tema']}' não existe")
        elif r["id"] in registros:
            avisos.append(f"{r['id']} ignorado: id repetido")
        else:
            r.setdefault("passos", [])
            r.setdefault("relacionados", [])
            r.setdefault("aviso", "")
            r.setdefault("requer_confirmacao", True)
            registros[r["id"]] = r

    if not registros:
        raise ValueError("nenhum registro válido na base")

    return dados["temas"], registros, avisos


def montar_grafo(registros):
    # grafo não direcionado: se A cita B, B também fica ligado a A
    grafo = {rid: [] for rid in registros}
    for rid, r in registros.items():
        for outro in r["relacionados"]:
            if outro not in registros:
                continue
            if outro not in grafo[rid]:
                grafo[rid].append(outro)
            if rid not in grafo[outro]:
                grafo[outro].append(rid)
    return grafo


def assuntos_proximos(grafo, inicio, profundidade=2):
    # busca em largura (BFS) a partir de um assunto
    distancia = {inicio: 0}
    fila = [inicio]
    while fila:
        atual = fila.pop(0)
        if distancia[atual] == profundidade:
            continue
        for vizinho in grafo[atual]:
            if vizinho not in distancia:
                distancia[vizinho] = distancia[atual] + 1
                fila.append(vizinho)
    del distancia[inicio]
    return distancia


# ---------- respostas ----------

def formatar_data(data):
    ano, mes, dia = data.split("-")
    return f"{dia}/{mes}/{ano}"


def resposta_modelo_a(resultado, registros):
    if resultado["status"] == "ok":
        r = registros[resultado["id"]]
        return f"{r['orientacao']}\nFonte: {r['referencia']['fonte']} ({r['referencia']['url']})"
    if resultado["status"] == "ambigua":
        return "Encontrei mais de uma resposta possível. Seja mais específico."
    if resultado["status"] == "invalida":
        return "Entrada inválida."
    return "Não encontrei resposta para essa pergunta."


def resposta_modelo_b(resultado, registros, temas, grafo):
    linhas = []
    if resultado.get("privacidade"):
        linhas.append("[Privacidade] Removi um dado pessoal (CPF, e-mail ou telefone) da sua "
                      "mensagem. Ele não é guardado e não é necessário aqui.")

    status = resultado["status"]
    if status == "ok":
        r = registros[resultado["id"]]
        linhas.append(f"== {r['titulo']} ==")
        linhas.append(f"Resumo: {r['orientacao']}")
        if r["passos"]:
            linhas.append("Passo a passo:")
            for i, passo in enumerate(r["passos"], 1):
                linhas.append(f"  {i}. {passo}")
        linhas.append(f"Fonte: {r['referencia']['fonte']}")
        linhas.append(f"Link: {r['referencia']['url']}")
        linhas.append(f"Verificado em: {formatar_data(r['data_verificacao'])}")
        aviso = r["aviso"]
        if r["requer_confirmacao"] and "confirme" not in aviso.lower():
            aviso += " Confirme os requisitos atualizados no canal oficial."
        if aviso:
            linhas.append(f"Atenção: {aviso.strip()}")
        vizinhos = grafo[r["id"]][:3]
        if vizinhos:
            nomes = "; ".join(f"[{v}] {registros[v]['titulo']}" for v in vizinhos)
            linhas.append(f"Próximos assuntos: {nomes}")
        linhas.append(AVISO_OFICIAL)

    elif status == "ambigua":
        linhas.append("Sua pergunta combina com mais de um assunto. Qual deles você procura?")
        for rid in resultado["opcoes"]:
            linhas.append(f"  [{rid}] {registros[rid]['titulo']}")
        linhas.append("Digite o código (ex.: DOC-01) ou escreva a pergunta de outro jeito.")

    elif status == "invalida":
        if resultado["motivo"] == "vazia":
            linhas.append("Você não digitou nenhuma pergunta.")
        else:
            linhas.append("Não consegui identificar palavras na sua mensagem.")
        linhas.append("Exemplo: 'Como faço meu CPF?' ou escolha um tema no menu.")

    else:
        linhas.append("Não tenho uma orientação verificada sobre isso, então prefiro não "
                      "responder para não passar informação errada.")
        parecidos = [rid for rid, _ in resultado["ranking"][:3]]
        if parecidos:
            linhas.append("Assuntos parecidos: " + "; ".join(f"[{p}] {registros[p]['titulo']}" for p in parecidos))
        linhas.append("Temas disponíveis: " + ", ".join(t["nome"] for t in temas.values()) + ".")
        linhas.append("Para outros assuntos, procure o portal gov.br ou o órgão responsável.")

    return "\n".join(linhas)


def responder(pergunta, app):
    codigo = normalizar(pergunta).upper().replace(" ", "-")
    if codigo in app["registros"]:
        resultado = {"status": "ok", "id": codigo, "privacidade": False}
    else:
        resultado = buscar(pergunta, app["registros"], app["indice"])

    if app["modelo"] == "A":
        texto = resposta_modelo_a(resultado, app["registros"])
    else:
        texto = resposta_modelo_b(resultado, app["registros"], app["temas"], app["grafo"])
    return texto, resultado


def iniciar(caminho=ARQUIVO_BASE, modelo="B"):
    temas, registros, avisos = carregar_base(caminho)
    return {
        "temas": temas,
        "registros": registros,
        "indice": criar_indice(registros.values()),
        "grafo": montar_grafo(registros),
        "modelo": modelo,
        "avisos": avisos,
        "caminho": caminho,
    }


# ---------- menu ----------

def ler(mensagem):
    try:
        return input(mensagem).strip()
    except (EOFError, KeyboardInterrupt):
        return "0"


def escolher(opcoes, titulo):
    """opcoes é uma lista de (valor, texto). Retorna o valor escolhido ou None."""
    while True:
        print(f"\n{titulo}")
        for i, (_, texto) in enumerate(opcoes, 1):
            print(f"  {i}. {texto}")
        print("  0. Voltar")
        op = ler("Escolha: ")
        if op == "0":
            return None
        if op.isdigit() and 1 <= int(op) <= len(opcoes):
            return opcoes[int(op) - 1][0]
        if not op:
            print("Você não digitou nada.")
        else:
            print(f"Opção inexistente: '{op}'.")


def mostrar(rid, app):
    texto, _ = responder(rid, app)
    print("-" * 60)
    print(texto)
    print("-" * 60)


def oferecer_relacionados(rid, app):
    while app["grafo"][rid]:
        opcoes = [(v, app["registros"][v]["titulo"]) for v in app["grafo"][rid][:4]]
        escolha = escolher(opcoes, "Quer ver um assunto relacionado?")
        if escolha is None:
            return
        mostrar(escolha, app)
        rid = escolha


def menu_pergunta(app):
    print("\nDigite sua pergunta (0 para voltar). Não informe dados pessoais.")
    while True:
        pergunta = ler("\nPergunta: ")
        if pergunta == "0":
            return
        inicio = time.perf_counter()
        texto, resultado = responder(pergunta, app)
        tempo = (time.perf_counter() - inicio) * 1000
        print("-" * 60)
        print(texto)
        print("-" * 60)
        print(f"(consulta em {tempo:.2f} ms)")
        if resultado["status"] == "ok" and app["modelo"] == "B":
            oferecer_relacionados(resultado["id"], app)
            print("\nPode fazer outra pergunta (0 para voltar).")


def menu_temas(app):
    temas, registros = app["temas"], app["registros"]
    while True:
        tema = escolher([(t, temas[t]["nome"]) for t in temas], "TEMAS")
        if tema is None:
            return
        subtemas = temas[tema]["subtemas"]
        sub = escolher(list(subtemas.items()), temas[tema]["nome"].upper())
        if sub is None:
            continue
        lista = [(rid, r["titulo"]) for rid, r in registros.items()
                 if r["tema"] == tema and r["subtema"] == sub]
        rid = escolher(lista, subtemas[sub].upper())
        if rid is None:
            continue
        mostrar(rid, app)
        oferecer_relacionados(rid, app)


def menu_mapa(app):
    temas, registros = app["temas"], app["registros"]
    for tema, info in temas.items():
        print(f"\n{info['nome']}")
        for sub, nome_sub in info["subtemas"].items():
            print(f"  {nome_sub}")
            for rid, r in registros.items():
                if r["tema"] == tema and r["subtema"] == sub:
                    print(f"    [{rid}] {r['titulo']}")
    print(f"\nTotal: {len(registros)} orientações.")

    rid = ler("\nDigite um código para ver assuntos próximos (Enter para voltar): ").upper()
    if rid in registros:
        for outro, dist in sorted(assuntos_proximos(app["grafo"], rid).items(), key=lambda x: x[1]):
            ligacao = "direta" if dist == 1 else "indireta"
            print(f"  [{outro}] {registros[outro]['titulo']} (ligação {ligacao})")
    elif rid:
        print(f"O código '{rid}' não existe.")


def menu_modelo(app):
    app["modelo"] = "A" if app["modelo"] == "B" else "B"
    print(f"\nModelo de resposta agora é o {app['modelo']}.")
    print("Instrução:", PROMPTS[app["modelo"]])


def menu_sobre(app):
    print(f"""
SOBRE
- Protótipo acadêmico - FIAP Global Solution 2026.2.
- {AVISO_OFICIAL}
- As respostas vêm só de uma base com {len(app['registros'])} orientações conferidas em fontes oficiais.
- O assistente não pede nem guarda dados pessoais e não salva as perguntas.
- Quando a informação não está na base, ele avisa em vez de inventar.""")


def menu_recarregar(app):
    try:
        novo = iniciar(app["caminho"], app["modelo"])
    except ValueError as erro:
        print(f"\nNão foi possível recarregar: {erro}")
        return
    app.update(novo)
    print(f"\nBase recarregada com {len(app['registros'])} registros.")
    for aviso in app["avisos"]:
        print(" -", aviso)


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else ARQUIVO_BASE
    try:
        app = iniciar(caminho)
    except ValueError as erro:
        print(f"Erro ao carregar a base: {erro}")
        sys.exit(1)

    for aviso in app["avisos"]:
        print("[aviso]", aviso)

    print("=" * 60)
    print(" CITIZEN ASSIST AI - orientações sobre documentos,")
    print(" serviços e direitos")
    print("=" * 60)
    print(AVISO_OFICIAL)

    opcoes = {
        "1": ("Fazer uma pergunta", menu_pergunta),
        "2": ("Navegar por temas", menu_temas),
        "3": ("Ver mapa da base", menu_mapa),
        "4": ("Trocar modelo de resposta (A/B)", menu_modelo),
        "5": ("Sobre e privacidade", menu_sobre),
        "6": ("Recarregar a base", menu_recarregar),
    }

    while True:
        print("\nMENU")
        for chave, (texto, _) in opcoes.items():
            print(f"  {chave}. {texto}")
        print("  0. Sair")
        op = ler("Escolha: ")
        if op == "0":
            print("Até logo!")
            break
        if op in opcoes:
            opcoes[op][1](app)
        elif not op:
            print("Você não digitou nada.")
        else:
            print(f"Opção inexistente: '{op}'.")


if __name__ == "__main__":
    main()
