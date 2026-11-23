
# SIGIC - Sistema Inteligente de Gerenciamento da Infraestrutura da Colônia

# SEÇÃO 1: ESTRUTURAS DE DADOS - MÓDULOS DA COLÔNIA

modulos = {
    "HAB": {
        "nome":        "Habitação",
        "consumo_kw":  45.0,
        "prioridade":  1,
        "capacidade":  50,
        "status":      "operacional",
        "descricao":   "Dormitórios, área de convivência e suporte de vida pessoal."
    },
    "CTR": {
        "nome":        "Centro de Controle",
        "consumo_kw":  30.0,
        "prioridade":  1,
        "capacidade":  20,
        "status":      "operacional",
        "descricao":   "Coordena todas as operações da base e comunicação interna."
    },
    "ENE": {
        "nome":        "Armazenamento de Energia",
        "consumo_kw":  10.0,
        "prioridade":  1,
        "capacidade":  500,
        "status":      "operacional",
        "descricao":   "Baterias de alta densidade e painéis solares de backup."
    },
    "AGR": {
        "nome":        "Agricultura",
        "consumo_kw":  60.0,
        "prioridade":  2,
        "capacidade":  200,
        "status":      "operacional",
        "descricao":   "Cultivo hidropônico de alimentos para a colônia."
    },
    "LAB": {
        "nome":        "Laboratório Científico",
        "consumo_kw":  35.0,
        "prioridade":  3,
        "capacidade":  15,
        "status":      "operacional",
        "descricao":   "Pesquisas em geologia marciana, biologia e química."
    },
    "COM": {
        "nome":        "Comunicação",
        "consumo_kw":  20.0,
        "prioridade":  2,
        "capacidade":  1,
        "status":      "operacional",
        "descricao":   "Antenas para contato com a Terra e satélites orbitais."
    },
    "MED": {
        "nome":        "Suporte Médico",
        "consumo_kw":  40.0,
        "prioridade":  1,
        "capacidade":  10,
        "status":      "operacional",
        "descricao":   "Enfermaria, cirurgia de emergência e farmácia."
    },
    "OXI": {
        "nome":        "Produção de Oxigênio",
        "consumo_kw":  55.0,
        "prioridade":  1,
        "capacidade":  300,
        "status":      "operacional",
        "descricao":   "Eletrólise da água e separação de CO2 da atmosfera interna."
    }
}


# SEÇÃO 2: TUPLAS - INFORMAÇÕES IMUTÁVEIS DO SISTEMA


MODULOS_IDS = ("HAB", "CTR", "ENE", "AGR", "LAB", "COM", "MED", "OXI")

COORDENADAS = {
    "HAB": (0,    100),
    "CTR": (0,    0),
    "ENE": (-120, 0),
    "AGR": (120,  0),
    "LAB": (0,   -100),
    "COM": (200,  100),
    "MED": (-80,  100),
    "OXI": (-120, -80)
}

INFO_SISTEMA = ("SIGIC", "v1.0", "Base Aurora Siger", "Marte")


# SEÇÃO 3: LISTA DE ADJACÊNCIA - O GRAFO DA COLÔNIA


ARESTAS = [
    ("HAB", "CTR", 100),
    ("HAB", "MED", 80),
    ("HAB", "OXI", 150),
    ("CTR", "ENE", 120),
    ("CTR", "AGR", 120),
    ("CTR", "LAB", 100),
    ("CTR", "COM", 200),
    ("ENE", "OXI", 80),
    ("ENE", "MED", 60),
    ("AGR", "COM", 180),
    ("LAB", "OXI", 120),
    ("MED", "HAB", 80),
    ("OXI", "ENE", 80),
]


def construir_grafo(lista_de_arestas):
    grafo = {}
    for modulo_id in MODULOS_IDS:
        grafo[modulo_id] = []
    for (a, b, peso) in lista_de_arestas:
        grafo[a].append((b, peso))
        grafo[b].append((a, peso))
    for modulo_id in grafo:
        grafo[modulo_id] = list(set(grafo[modulo_id]))
        grafo[modulo_id].sort()
    return grafo


grafo_colonia = construir_grafo(ARESTAS)



# SEÇÃO 4: ALGORITMOS DE REDE


def bfs(grafo, origem):
    visitados = []
    nivel = {}
    ja_visitado = set()
    fila = [origem]
    ja_visitado.add(origem)
    nivel[origem] = 0
    while len(fila) > 0:
        modulo_atual = fila.pop(0)
        visitados.append(modulo_atual)
        for (vizinho, peso) in grafo[modulo_atual]:
            if vizinho not in ja_visitado:
                ja_visitado.add(vizinho)
                fila.append(vizinho)
                nivel[vizinho] = nivel[modulo_atual] + 1
    return visitados, nivel


def dfs(grafo, origem):
    visitados = []
    ja_visitado = set()
    pilha = [origem]
    while len(pilha) > 0:
        modulo_atual = pilha.pop()
        if modulo_atual in ja_visitado:
            continue
        ja_visitado.add(modulo_atual)
        visitados.append(modulo_atual)
        vizinhos_ordenados = sorted(grafo[modulo_atual], reverse=True)
        for (vizinho, peso) in vizinhos_ordenados:
            if vizinho not in ja_visitado:
                pilha.append(vizinho)
    return visitados


def dijkstra(grafo, origem):
    INFINITO = float('inf')
    distancias = {}
    for modulo_id in MODULOS_IDS:
        distancias[modulo_id] = INFINITO
    distancias[origem] = 0
    predecessores = {}
    for modulo_id in MODULOS_IDS:
        predecessores[modulo_id] = None
    nao_finalizados = set(MODULOS_IDS)

    while len(nao_finalizados) > 0:
        modulo_atual = None
        menor_dist = INFINITO
        for modulo_id in nao_finalizados:
            if distancias[modulo_id] < menor_dist:
                menor_dist = distancias[modulo_id]
                modulo_atual = modulo_id
        if modulo_atual is None:
            break
        nao_finalizados.remove(modulo_atual)
        for (vizinho, peso_aresta) in grafo[modulo_atual]:
            distancia_alternativa = distancias[modulo_atual] + peso_aresta
            if distancia_alternativa < distancias[vizinho]:
                distancias[vizinho] = distancia_alternativa
                predecessores[vizinho] = modulo_atual

    return distancias, predecessores


def reconstruir_caminho(predecessores, origem, destino):
    caminho = []
    modulo_atual = destino
    while modulo_atual is not None:
        caminho.append(modulo_atual)
        modulo_atual = predecessores[modulo_atual]
    caminho.reverse()
    if len(caminho) == 0 or caminho[0] != origem:
        return []
    return caminho



# SEÇÃO 5 e 6: INTERFACE E MENU PRINCIPAL


def imprimir_linha_separadora():
    print("=" * 65)

def imprimir_titulo(texto):
    imprimir_linha_separadora()
    print(f"  {texto}")
    imprimir_linha_separadora()

def exibir_rede_colonia():
    imprimir_titulo("REDE DA COLÔNIA - LISTA DE ADJACÊNCIA")
    for modulo_id in MODULOS_IDS:
        nome_modulo = modulos[modulo_id]["nome"]
        lista_viz = ""
        for (viz, peso) in grafo_colonia[modulo_id]:
            lista_viz += f"{viz}:{peso}m  "
        print(f"  [{modulo_id}] {nome_modulo:<22} -> {lista_viz}")
    print()

def exibir_status_modulo(modulo_id):
    if modulo_id not in modulos:
        print(f"\n  ERRO: Módulo '{modulo_id}' não encontrado.\n")
        return
    m = modulos[modulo_id]
    imprimir_titulo(f"MÓDULO: {m['nome']} [{modulo_id}]")
    print(f"  Descrição   : {m['descricao']}")
    print(f"  Status      : {m['status'].upper()}")
    print(f"  Prioridade  : {m['prioridade']}")
    print(f"  Consumo     : {m['consumo_kw']} kW")
    print(f"  Capacidade  : {m['capacidade']}")
    print(f"  Vizinhos    : ", end="")
    for (viz, peso) in grafo_colonia[modulo_id]:
        print(f"{viz}({peso}m)", end="  ")
    print("\n")

def executar_dijkstra_interativo():
    imprimir_titulo("CAMINHO MÍNIMO - ALGORITMO DE DIJKSTRA")
    print("  Módulos: " + " | ".join([f"{m}={modulos[m]['nome']}" for m in MODULOS_IDS]))
    origem  = input("\n  ORIGEM  : ").strip().upper()
    destino = input("  DESTINO : ").strip().upper()
    if origem not in modulos or destino not in modulos:
        print("\n  ERRO: Módulo não encontrado.\n"); return
    if origem == destino:
        print("\n  Distância = 0 metros.\n"); return
    distancias, predecessores = dijkstra(grafo_colonia, origem)
    caminho = reconstruir_caminho(predecessores, origem, destino)
    if not caminho or distancias[destino] == float('inf'):
        print(f"\n  Não existe caminho entre {origem} e {destino}.\n"); return
    print(f"\n  Caminho: {' -> '.join(caminho)}")
    print(f"  Distância total: {distancias[destino]} metros\n")

def executar_simulacao():
    imprimir_titulo("SIMULAÇÃO OPERACIONAL")
    for mid in MODULOS_IDS:
        print(f"    {mid} - {modulos[mid]['nome']:<25}: {modulos[mid]['status'].upper()}")
    mid = input("\n  ID do módulo: ").strip().upper()
    if mid not in modulos:
        print("\n  ERRO: Módulo não encontrado.\n"); return
    print("  1=operacional  2=em alerta  3=em manutencao  4=desligado")
    op = input("  Escolha: ").strip()
    mapa = {"1":"operacional","2":"em alerta","3":"em manutencao","4":"desligado"}
    if op not in mapa:
        print("\n  Opção inválida.\n"); return
    ant = modulos[mid]["status"]
    modulos[mid]["status"] = mapa[op]
    print(f"\n  {modulos[mid]['nome']}: '{ant}' -> '{mapa[op]}'")
    if mapa[op] == "desligado" and modulos[mid]["prioridade"] == 1:
        print("  *** ALERTA CRÍTICO: módulo de prioridade 1 desligado! ***\n")

def exibir_bfs_dfs():
    imprimir_titulo("EXPLORAÇÃO DA REDE: BFS e DFS")
    origem = input("  Módulo de origem: ").strip().upper()
    if origem not in modulos:
        print("\n  ERRO.\n"); return
    v_bfs, niveis = bfs(grafo_colonia, origem)
    print(f"\n  BFS: {' -> '.join(v_bfs)}")
    v_dfs = dfs(grafo_colonia, origem)
    print(f"  DFS: {' -> '.join(v_dfs)}\n")

def main():
    imprimir_titulo("SIGIC - Base Aurora Siger | Sistema Inicializado")
    while True:
        print("\n  [1] Visualizar rede  [2] Status módulo  [3] Dijkstra")
        print("  [4] Simulação        [5] BFS/DFS         [0] Sair")
        op = input("  Opção: ").strip()
        if   op == "1": exibir_rede_colonia()
        elif op == "2":
            mid = input("  ID do módulo: ").strip().upper()
            exibir_status_modulo(mid)
        elif op == "3": executar_dijkstra_interativo()
        elif op == "4": executar_simulacao()
        elif op == "5": exibir_bfs_dfs()
        elif op == "0": print("\n  SIGIC encerrado.\n"); break
        else: print("\n  Opção inválida.\n")

if __name__ == "__main__":
    main()