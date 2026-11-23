# MGPEB - Módulo de Gerenciamento de Pouso e Estabilização de Base
# Missão Aurora Siger | Colônia em Marte

from collections import deque  # usada para implementar a fila de pouso

# 1. DEFINIÇÃO DOS MÓDULOS
# Cada módulo é representado como um dicionário com os seguintes atributos:
#   nome         : identificador do módulo
#   tipo         : categoria (habitação, energia, lab, logística, médico)
#   prioridade   : 1 (crítica) a 5 (baixa) — menor número = maior urgência
#   combustivel  : porcentagem restante (0 a 100)
#   massa        : toneladas
#   criticidade  : 'alta', 'media' ou 'baixa' — importância da carga
#   hora_orbita  : hora estimada de chegada à órbita (formato 0-23)
#   sensor_ok    : True se sensores de navegação estão íntegros
# =============================================================================

modulos_iniciais = [
    {
        "nome": "HAB-01",
        "tipo": "habitação",
        "prioridade": 1,
        "combustivel": 72,
        "massa": 18.5,
        "criticidade": "alta",
        "hora_orbita": 6,
        "sensor_ok": True,
    },
    {
        "nome": "ENE-01",
        "tipo": "energia",
        "prioridade": 2,
        "combustivel": 85,
        "massa": 12.0,
        "criticidade": "alta",
        "hora_orbita": 7,
        "sensor_ok": True,
    },
    {
        "nome": "LAB-01",
        "tipo": "laboratório",
        "prioridade": 3,
        "combustivel": 55,
        "massa": 9.8,
        "criticidade": "media",
        "hora_orbita": 9,
        "sensor_ok": True,
    },
    {
        "nome": "LOG-01",
        "tipo": "logística",
        "prioridade": 4,
        "combustivel": 30,
        "massa": 22.0,
        "criticidade": "media",
        "hora_orbita": 11,
        "sensor_ok": False,
    },
    {
        "nome": "MED-01",
        "tipo": "médico",
        "prioridade": 1,
        "combustivel": 90,
        "massa": 8.5,
        "criticidade": "alta",
        "hora_orbita": 8,
        "sensor_ok": True,
    },
    {
        "nome": "HAB-02",
        "tipo": "habitação",
        "prioridade": 2,
        "combustivel": 20,
        "massa": 17.0,
        "criticidade": "media",
        "hora_orbita": 14,
        "sensor_ok": True,
    },
    {
        "nome": "ENE-02",
        "tipo": "energia",
        "prioridade": 3,
        "combustivel": 65,
        "massa": 11.5,
        "criticidade": "alta",
        "hora_orbita": 10,
        "sensor_ok": True,
    },
]

# 2. ESTRUTURAS DE DADOS LINEARES
# =============================================================================

fila_pouso = deque()

pousados = []

em_alerta = []

historico_decisoes = []

# 3. FUNÇÃO: ORDENAÇÃO POR PRIORIDADE (Bubble Sort)
# Ordena a lista de módulos por prioridade (menor número = pousa primeiro).
# Em caso de empate, ordena pela hora de chegada à órbita.
# =============================================================================

def ordenar_por_prioridade(lista):
    """
    Bubble Sort: compara pares adjacentes e troca se necessário.
    Critério primário: prioridade (ascendente).
    Critério secundário: hora_orbita (ascendente).
    """
    n = len(lista)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            p1 = lista[j]["prioridade"]
            p2 = lista[j + 1]["prioridade"]
            h1 = lista[j]["hora_orbita"]
            h2 = lista[j + 1]["hora_orbita"]
            if p1 > p2 or (p1 == p2 and h1 > h2):
                lista[j], lista[j + 1] = lista[j + 1], lista[j]
    return lista

# 4. FUNÇÃO: BUSCA SEQUENCIAL
# Localiza o primeiro módulo que atende a um critério específico.
# =============================================================================

def buscar_por_tipo(lista, tipo_buscado):
    """Busca sequencial: percorre a lista até encontrar o tipo desejado."""
    for modulo in lista:
        if modulo["tipo"] == tipo_buscado:
            return modulo
    return None


def buscar_menor_combustivel(lista):
    """Busca o módulo com menor nível de combustível (busca de mínimo)."""
    if not lista:
        return None
    menor = lista[0]
    for modulo in lista[1:]:
        if modulo["combustivel"] < menor["combustivel"]:
            menor = modulo
    return menor

# 5. REGRAS LÓGICAS DE AUTORIZAÇÃO DE POUSO
#
# As condições abaixo simulam portas lógicas booleanas:
#
#   AUTORIZADO = (combustivel >= 25)          — NOT combustivel_critico
#              AND sensor_ok                  — sensor íntegro
#              AND (cond_atmosferica == True) — AND condição atmosférica
#              AND (area_disponivel == True)  — AND área de pouso livre
#
#   ALERTA_PRIORITARIO = (criticidade == 'alta') AND (combustivel < 25)
#       → pouso de emergência: força autorização mesmo com combustível baixo
#         se e somente se a área estiver disponível e sensores OK
# =============================================================================

def avaliar_pouso(modulo, cond_atmosferica, area_disponivel):
    """
    Avalia se o módulo pode pousar com base nas regras booleanas do MGPEB.
    Retorna uma tupla: (decisao: str, motivo: str)
    """
    combustivel_ok = modulo["combustivel"] >= 25 
    sensor_ok      = modulo["sensor_ok"]
    carga_critica  = modulo["criticidade"] == "alta" 

    emergencia = carga_critica and (modulo["combustivel"] < 25) and area_disponivel and sensor_ok

    condicoes_normais = combustivel_ok and sensor_ok and cond_atmosferica and area_disponivel

    if emergencia:
        return ("POUSO_EMERGENCIA", "Carga crítica com combustível baixo — pouso de emergência autorizado")
    elif condicoes_normais:
        return ("AUTORIZADO", "Todas as condições satisfeitas")
    else:
        razoes = []
        if not combustivel_ok:
            razoes.append(f"combustível insuficiente ({modulo['combustivel']}%)")
        if not sensor_ok:
            razoes.append("falha nos sensores de navegação")
        if not cond_atmosferica:
            razoes.append("condição atmosférica desfavorável")
        if not area_disponivel:
            razoes.append("área de pouso indisponível")
        return ("BLOQUEADO", " | ".join(razoes))


# 6. SIMULAÇÃO PRINCIPAL
# =============================================================================

def simular_operacao():
    print("=" * 60)
    print("  MGPEB — Missão Aurora Siger")
    print("  Simulação de Pouso em Marte")
    print("=" * 60)

    modulos_ordenados = ordenar_por_prioridade(list(modulos_iniciais))
    for m in modulos_ordenados:
        fila_pouso.append(m)

    print(f"\n[FILA] {len(fila_pouso)} módulos enfileirados (ordem de pouso):")
    for i, m in enumerate(fila_pouso, 1):
        print(f"  {i}. {m['nome']} | Tipo: {m['tipo']:12s} | Prior.: {m['prioridade']} | "
              f"Comb.: {m['combustivel']}% | Sensor: {'OK' if m['sensor_ok'] else 'FALHA'}")

    condicoes_ambiente = {
        "HAB-01": (True,  True),
        "ENE-01": (True,  True),
        "MED-01": (True,  True),
        "LAB-01": (True,  True),
        "ENE-02": (True,  False),
        "LOG-01": (True,  True),
        "HAB-02": (False, True),
    }

    print("\n" + "=" * 60)
    print("  PROCESSAMENTO DA FILA DE POUSO")
    print("=" * 60)

    while fila_pouso:
        modulo = fila_pouso.popleft()
        nome = modulo["nome"]
        atm, area = condicoes_ambiente.get(nome, (True, True))

        decisao, motivo = avaliar_pouso(modulo, atm, area)

        historico_decisoes.append({
            "modulo": nome,
            "decisao": decisao,
            "motivo": motivo
        })

        if decisao in ("AUTORIZADO", "POUSO_EMERGENCIA"):
            pousados.append(modulo)
            tag = "EMERGÊNCIA" if decisao == "POUSO_EMERGENCIA" else "OK"
            print(f"  ✓ [{tag}] {nome} pousou com sucesso. | {motivo}")
        else:
            em_alerta.append(modulo)
            print(f"  ✗ [BLOQUEADO] {nome} — {motivo}")

    print("\n" + "=" * 60)
    print("  BUSCAS NO SISTEMA")
    print("=" * 60)

    resultado_tipo = buscar_por_tipo(pousados, "médico")
    if resultado_tipo:
        print(f"  Módulo médico pousado: {resultado_tipo['nome']}")
    else:
        print("  Nenhum módulo médico pousado ainda.")

    critico = buscar_menor_combustivel(em_alerta)
    if critico:
        print(f"  Módulo em alerta com menor combustível: {critico['nome']} ({critico['combustivel']}%)")

    print("\n" + "=" * 60)
    print("  RESUMO FINAL")
    print("=" * 60)
    print(f"  Módulos pousados : {len(pousados)}")
    print(f"  Módulos em alerta: {len(em_alerta)}")

    print("\n  Histórico de decisões (ordem cronológica inversa — pilha):")
    temp_historico = list(historico_decisoes)
    while temp_historico:
        entrada = temp_historico.pop()
        print(f"    {entrada['modulo']:8s} -> {entrada['decisao']:20s} | {entrada['motivo']}")

    print("\n" + "=" * 60)
    print("  MODELAGEM: Altura em função do tempo de descida")
    print("  h(t) = h0 - v0*t - (1/2)*a*t^2")
    print("  h0=8000m, v0=10m/s, a=3.7m/s² (gravidade em Marte)")
    print("=" * 60)
    h0 = 8000
    v0 = 10
    a  = 3.7

    print(f"  {'Tempo(s)':>10}  {'Altura(m)':>12}  {'Retrofoguetes':>14}")
    for t in range(0, 75, 10):
        h = h0 - v0 * t - 0.5 * a * t * t
        if h < 0:
            h = 0
        retro = "ACIONAR" if h <= 500 else "aguardar"
        print(f"  {t:>10}  {h:>12.1f}  {retro:>14}")

    print("\n  Fim da simulação MGPEB.")

# PONTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    simular_operacao()