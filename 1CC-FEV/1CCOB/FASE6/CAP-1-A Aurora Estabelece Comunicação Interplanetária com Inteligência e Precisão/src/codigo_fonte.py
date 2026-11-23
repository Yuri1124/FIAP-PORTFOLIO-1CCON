
import json
import math
import time
import random
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

ARQUIVO_DADOS = "dados_aurora_siger.json"
PASTA_GRAFICOS = "graficos_ou_imagens"

LIMITE_ACEITAVEL = 0.10
LIMITE_ATENCAO = 0.25

HORAS_POR_SOL = 24.66

COMANDOS = ["comando_reiniciar_enlace", "comando_redirecionar_rele",
            "comando_reduzir_potencia", "consultar_status", "consultar_alertas",
            "controle_backup_dados", "calibrar_sensor", "ativar_redundancia"]


# Funções auxiliares de tela

def titulo(texto):
    print()
    print("=" * 70)
    print(texto)
    print("=" * 70)


def linha():
    print("-" * 70)


def esperar_enter():
    input("\nAperte ENTER para voltar ao menu...")


def salvar_grafico(nome_arquivo):
    # cria a pasta se ela ainda não existir
    if not os.path.exists(PASTA_GRAFICOS):
        os.mkdir(PASTA_GRAFICOS)
    caminho = PASTA_GRAFICOS + "/" + nome_arquivo
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()
    print("Gráfico salvo em:", caminho)



# 1) LEITURA E LIMPEZA DOS DADOS

def ler_json():
    arquivo = open(ARQUIVO_DADOS, "r", encoding="utf-8")
    dados = json.load(arquivo)
    arquivo.close()
    return dados


def carregar_dados():
    dados = ler_json()
    print("Colônia:", dados["colonia"])
    print("Unidades usadas:", dados["unidades"])

    df = pd.DataFrame(dados["registros"])
    print("Registros lidos do arquivo:", len(df))

    repetidos = df.duplicated().sum()
    df = df.drop_duplicates()
    print("Registros duplicados removidos:", repetidos)

    print("Valores vazios por coluna:")
    vazios = df.isnull().sum()
    for coluna in df.columns:
        if vazios[coluna] > 0:
            print("  ", coluna, "->", vazios[coluna])

    df = df.dropna(subset=["latencia_observada_ms"])
    df["qualidade_sinal"] = df["qualidade_sinal"].fillna(df["qualidade_sinal"].median())
    df["corrente_a"] = df["corrente_a"].fillna(df["corrente_a"].median())

    df = df.reset_index(drop=True)
    df = calcular_colunas(df)
    print("Registros depois da limpeza:", len(df))
    return df


def classificar_erro(erro_rel):
    if erro_rel <= LIMITE_ACEITAVEL:
        return "aceitavel"
    elif erro_rel <= LIMITE_ATENCAO:
        return "atencao"
    else:
        return "critico"


def calcular_colunas(df):
    # Eletricidade: P = V * I  e  lei de Ohm: R = V / I
    df["potencia_w"] = df["tensao_v"] * df["corrente_a"]
    df["resistencia_ohm"] = df["tensao_v"] / df["corrente_a"]

    # Erro absoluto = |observado - previsto|
    df["erro_abs_ms"] = abs(df["latencia_observada_ms"] - df["latencia_prevista_ms"])
    # Erro relativo = erro absoluto / valor observado
    df["erro_rel"] = df["erro_abs_ms"] / df["latencia_observada_ms"]

    # True quando a latência foi maior do que o previsto
    df["acima_previsto"] = df["latencia_observada_ms"] > df["latencia_prevista_ms"]
    df["faixa_erro"] = df["erro_rel"].apply(classificar_erro)
    return df


def cadastrar_registro(df):
    titulo("CADASTRAR NOVO REGISTRO")
    modulos = sorted(df["modulo"].unique())
    for i in range(len(modulos)):
        print(i + 1, "-", modulos[i])

    try:
        num = int(input("Número do módulo: "))
        modulo = modulos[num - 1]
        prevista = float(input("Latência prevista (ms): "))
        observada = float(input("Latência observada (ms): "))
        carga = float(input("Carga de tráfego (Mbps): "))
        qualidade = float(input("Qualidade do sinal (0 a 1): "))
        tensao = float(input("Tensão do transmissor (V): "))
        corrente = float(input("Corrente do transmissor (A): "))
    except (ValueError, IndexError):
        print("Valor inválido, o registro não foi cadastrado.")
        return df

    status = input("Status (ativo / alerta / manutencao): ").lower()
    if status not in ["ativo", "alerta", "manutencao"]:
        print("Status desconhecido, vou considerar como 'alerta'.")
        status = "alerta"
    mensagem = input("Mensagem curta: ")
    if mensagem == "":
        mensagem = "Registro manual"

    if qualidade < 0 or qualidade > 1 or observada <= 0 or corrente <= 0:
        print("Algum valor está fora do esperado. Registro não cadastrado.")
        return df

    # pega os dados fixos do módulo (tipo, distância...) de um registro antigo
    antigo = df[df["modulo"] == modulo].iloc[0]
    ciclo = int(df["ciclo"].max()) + 1
    if int(antigo["essencial"]) == 1:
        prioridade = 4
    else:
        prioridade = 2
    if status == "alerta":
        prioridade = prioridade + 1

    novo = {
        "ciclo": ciclo,
        "sol": int(df["sol"].max()) + 1,
        "data_registro": "registro manual",
        "modulo": modulo,
        "tipo": antigo["tipo"],
        "essencial": int(antigo["essencial"]),
        "codigo_sensor": antigo["codigo_sensor"][0:4] + "FF",
        "distancia_m": int(antigo["distancia_m"]),
        "carga_trafego_mbps": carga,
        "qualidade_sinal": qualidade,
        "tensao_v": tensao,
        "corrente_a": corrente,
        "latencia_prevista_ms": prevista,
        "latencia_observada_ms": observada,
        "status": status,
        "prioridade": prioridade,
        "mensagem_alerta": mensagem,
    }

    nova_linha = calcular_colunas(pd.DataFrame([novo]))
    df = pd.concat([df, nova_linha], ignore_index=True)
    print("Registro cadastrado! Erro relativo:", round(nova_linha["erro_rel"][0] * 100, 1), "%")

    resp = input("Salvar no arquivo json? (s/n): ")
    if resp.lower() == "s":

        dados = ler_json()
        dados["registros"].append(novo)
        dados["total_registros"] = len(dados["registros"])
        arquivo = open(ARQUIVO_DADOS, "w", encoding="utf-8")
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.close()
        print("Registro salvo no arquivo", ARQUIVO_DADOS)
    return df



# 2) CONSULTA DE REGISTROS

COLUNAS_TABELA = ["ciclo", "modulo", "codigo_sensor", "latencia_prevista_ms",
                  "latencia_observada_ms", "status", "prioridade"]


def consultar_registros(df, automatico=False):
    titulo("CONSULTAR REGISTROS")
    print("1 - Resumo geral")
    print("2 - Buscar por módulo")
    print("3 - Buscar por status")
    if automatico:
        op = "1"
    else:
        op = input("Opção: ")

    if op == "1":
        print("Total de registros:", len(df))
        print("Quantidade de módulos:", df["modulo"].nunique())
        print("\nQuantidade por status:")
        print(df["status"].value_counts())
        internos = df[df["modulo"] != "Comunicação Interplanetária"]
        print("\nEstatísticas dos enlaces internos:")
        print(internos[["carga_trafego_mbps", "qualidade_sinal",
                        "latencia_observada_ms"]].describe().round(2))
        print("\nÚltimos 5 registros:")
        print(df[COLUNAS_TABELA].tail(5).to_string(index=False))
    elif op == "2":
        nome = input("Digite o nome do módulo (ou parte dele): ")
        resultado = df[df["modulo"].str.lower().str.contains(nome.lower())]
        if len(resultado) == 0:
            print("Nenhum registro encontrado.")
        else:
            print(resultado[COLUNAS_TABELA].to_string(index=False))
    elif op == "3":
        status = input("Status (ativo / alerta / manutencao): ").lower()
        resultado = df[df["status"] == status]
        if len(resultado) == 0:
            print("Nenhum registro encontrado.")
        else:
            print(resultado[COLUNAS_TABELA].to_string(index=False))
    else:
        print("Opção inválida.")



# 3) INDICADORES E ERROS NUMÉRICOS

def indicadores_e_erros(df):
    titulo("INDICADORES DE COMUNICAÇÃO E ERROS")

    internos = df[df["modulo"] != "Comunicação Interplanetária"]
    terra = df[df["modulo"] == "Comunicação Interplanetária"]

    print("Latência média dos enlaces internos: %.2f ms" % internos["latencia_observada_ms"].mean())
    print("Latência média do enlace com a Terra: %.2f minutos" % (terra["latencia_observada_ms"].mean() / 60000))
    disponibilidade = (df["status"] == "ativo").sum() / len(df)
    print("Disponibilidade (registros ativos): %.1f %%" % (disponibilidade * 100))
    acima = df["acima_previsto"].sum() / len(df)
    print("Registros com latência acima do previsto: %.1f %%" % (acima * 100))

    linha()
    print("Erro médio por módulo:")
    tabela = df.groupby("modulo")[["latencia_observada_ms", "erro_abs_ms", "erro_rel"]].mean()
    tabela["erro_rel"] = tabela["erro_rel"] * 100
    tabela = tabela.sort_values("erro_rel", ascending=False)
    tabela.columns = ["latencia_media_ms", "erro_abs_medio_ms", "erro_rel_medio_%"]
    print(tabela.round(2))

    linha()
    print("Por que usar o erro relativo?")
    lab = df[df["modulo"] == "Laboratório Geológico"]
    print("Laboratório Geológico   -> erro absoluto médio: %8.2f ms | erro relativo: %.2f %%"
          % (lab["erro_abs_ms"].mean(), lab["erro_rel"].mean() * 100))
    print("Enlace com a Terra      -> erro absoluto médio: %8.2f ms | erro relativo: %.3f %%"
          % (terra["erro_abs_ms"].mean(), terra["erro_rel"].mean() * 100))
    print("Olhando só o erro absoluto, o enlace com a Terra parece muito pior,")
    print("mas como a latência dele é de ~13 minutos, o erro relativo é bem pequeno.")
    print("O erro relativo deixa comparar módulos com escalas diferentes.")

    linha()
    print("Classificação dos registros (aceitável <= 10%, atenção <= 25%, crítico > 25%):")
    print(df["faixa_erro"].value_counts())
    criticos = df[df["faixa_erro"] == "critico"]
    abaixo = criticos[criticos["acima_previsto"] == False]
    print("Dos", len(criticos), "críticos,", len(abaixo), "têm latência MENOR que a prevista.")
    print("Isso não é falha, só quer dizer que a previsão foi exagerada.")
    print("Por isso só consideramos alerta quando a latência fica ACIMA do previsto.")
    print("Obs.: em latências pequenas (~20 ms), poucos ms já dão um erro relativo alto.")

    linha()
    print("Ponto flutuante:")
    soma = 0.1 + 0.2
    print("0.1 + 0.2 =", soma)
    print("0.1 + 0.2 == 0.3 ?", soma == 0.3)
    print("Usando math.isclose:", math.isclose(soma, 0.3))
    total = 0
    for i in range(10):
        total = total + 0.1
    print("Somando 0.1 dez vezes =", total, "(deveria ser 1.0)")
    print("Isso acontece porque 0.1 não tem representação exata em binário.")
    print("Por isso comparamos números decimais com tolerância e não com ==.")
    print("No json as latências têm 2 casas decimais, então o erro de")
    print("arredondamento é no máximo 0,005 ms, bem menor que os erros de previsão.")



# 4) SIMULAÇÃO COM O MÉTODO DE EULER

def simulacao_euler(df):
    titulo("SIMULAÇÃO DA RECUPERAÇÃO DO ENLACE - MÉTODO DE EULER")

    internos = df[df["modulo"] != "Comunicação Interplanetária"]
    maior = internos["latencia_observada_ms"].idxmax()
    modulo = df.loc[maior, "modulo"]
    L0 = df.loc[maior, "latencia_observada_ms"]
    normais = df[(df["modulo"] == modulo) & (df["status"] == "ativo")]
    L_normal = normais["latencia_observada_ms"].median()
    k = 0.35
    tempo_total = 12

    print("Módulo com o maior pico:", modulo)
    print("Latência no pico: %.2f ms | latência normal: %.2f ms" % (L0, L_normal))

    exata_final = L_normal + (L0 - L_normal) * math.exp(-k * tempo_total)
    print("\nValor exato depois de 12 h: %.4f ms" % exata_final)
    print("passo h | Euler     | erro absoluto | erro relativo")

    resultados = {}
    for h in [2, 1, 0.5, 0.1]:
        t = 0
        L = L0
        lista_t = [t]
        lista_L = [L]
        passos = int(round(tempo_total / h))
        for i in range(passos):
            L = L + h * (-k * (L - L_normal))
            t = t + h
            lista_t.append(t)
            lista_L.append(L)
        erro = abs(L - exata_final)
        print("%7s | %9.4f | %13.4f | %10.3f %%" % (h, L, erro, erro / exata_final * 100))
        resultados[h] = (lista_t, lista_L)

    print("\nQuanto menor o passo h, menor o erro (o erro cai mais ou menos pela metade")
    print("quando o passo cai pela metade).")
    horas = math.log((L0 - L_normal) / (0.10 * L_normal)) / k
    print("Pelo modelo o enlace fica perto do normal em mais ou menos %.1f horas." % horas)
    print("Se isso não acontecer, o operador deve usar a rota reserva.")

    # gráfico
    tempos = np.linspace(0, tempo_total, 100)
    exata = L_normal + (L0 - L_normal) * np.exp(-k * tempos)
    plt.figure(figsize=(8, 5))
    plt.plot(tempos, exata, "k-", label="solução exata")
    plt.plot(resultados[2][0], resultados[2][1], "o--", label="Euler h = 2")
    plt.plot(resultados[0.5][0], resultados[0.5][1], "s--", label="Euler h = 0.5")
    plt.axhline(L_normal, color="gray", linestyle=":", label="latência normal")
    plt.xlabel("Horas depois do pico")
    plt.ylabel("Latência (ms)")
    plt.title("Recuperação da latência - " + modulo)
    plt.legend()
    salvar_grafico("04_simulacao_euler.png")



# 5) MODELO DE PREVISÃO E MÉTRICAS

def calcular_metricas(y_real, y_previsto):
    mae = mean_absolute_error(y_real, y_previsto)
    mse = mean_squared_error(y_real, y_previsto)
    rmse = math.sqrt(mse)
    r2 = r2_score(y_real, y_previsto)
    return mae, mse, rmse, r2


def mostrar_metricas(nome, mae, mse, rmse, r2):
    print("%-32s MAE=%6.2f  MSE=%7.2f  RMSE=%6.2f  R²=%5.2f" % (nome, mae, mse, rmse, r2))


def modelo_previsao(df):
    titulo("MODELO DE PREVISÃO DA LATÊNCIA")
    dados = df[df["modulo"] != "Comunicação Interplanetária"]

    variaveis = ["carga_trafego_mbps", "distancia_m", "qualidade_sinal", "potencia_w"]
    X = dados[variaveis]
    y = dados["latencia_observada_ms"]

    # divisão: 60% treino, 20% validação e 20% teste
    X_resto, X_teste, y_resto, y_teste = train_test_split(X, y, test_size=0.2, random_state=42)
    X_treino, X_val, y_treino, y_val = train_test_split(X_resto, y_resto, test_size=0.25, random_state=42)
    print("Treino:", len(X_treino), "| Validação:", len(X_val), "| Teste:", len(X_teste))

    # Modelo A: só usa a carga de tráfego
    modelo_a = LinearRegression()
    modelo_a.fit(X_treino[["carga_trafego_mbps"]], y_treino)
    prev_a = modelo_a.predict(X_val[["carga_trafego_mbps"]])

    # Modelo B: usa as 4 variáveis
    modelo_b = LinearRegression()
    modelo_b.fit(X_treino, y_treino)
    prev_b = modelo_b.predict(X_val)

    print("\nComparação na VALIDAÇÃO:")
    mae_a, mse_a, rmse_a, r2_a = calcular_metricas(y_val, prev_a)
    mae_b, mse_b, rmse_b, r2_b = calcular_metricas(y_val, prev_b)
    mostrar_metricas("Modelo A (só carga)", mae_a, mse_a, rmse_a, r2_a)
    mostrar_metricas("Modelo B (4 variáveis)", mae_b, mse_b, rmse_b, r2_b)

    if rmse_b < rmse_a:
        print("O modelo B foi melhor na validação, então ele foi o escolhido.")
        escolhido = modelo_b
        colunas = variaveis
    else:
        print("O modelo A foi melhor na validação, então ele foi o escolhido.")
        escolhido = modelo_a
        colunas = ["carga_trafego_mbps"]
    print("RMSE/MAE na validação do modelo B: %.2f" % (rmse_b / mae_b))
    print("(quando essa razão é bem maior que 1, alguns registros têm erros muito")
    print("maiores que os outros - aqui são os picos de latência)")

    # treina de novo com treino + validação e testa só uma vez
    escolhido.fit(X_resto[colunas], y_resto)
    prev_teste = escolhido.predict(X_teste[colunas])

    print("\nResultado no TESTE:")
    # comparação com a latência prevista que já vinha no arquivo
    prev_antiga = dados.loc[y_teste.index, "latencia_prevista_ms"]
    mae0, mse0, rmse0, r20 = calcular_metricas(y_teste, prev_antiga)
    mae, mse, rmse, r2 = calcular_metricas(y_teste, prev_teste)
    mostrar_metricas("Previsão antiga (do arquivo)", mae0, mse0, rmse0, r20)
    mostrar_metricas("Modelo escolhido", mae, mse, rmse, r2)
    print("Redução do MAE: %.0f %%" % ((1 - mae / mae0) * 100))

    print("\nCoeficientes do modelo:")
    for i in range(len(colunas)):
        print("  %-20s %+.4f" % (colunas[i], escolhido.coef_[i]))
    print("A qualidade do sinal tem o maior efeito: sinal pior = latência maior.")
    print("A potência quase não muda nada, poderia até sair do modelo.")

    linha()
    print("Interpretação das métricas:")
    print("MAE = %.2f ms: em média o modelo erra uns %.1f ms." % (mae, mae))
    print("RMSE = %.2f ms: parecido com o MAE, mas pesa mais os erros grandes." % rmse)
    print("RMSE/MAE no teste = %.2f" % (rmse / mae))
    print("R² = %.2f: o modelo explica %.0f%% da variação da latência." % (r2, r2 * 100))
    maior_erro = max(abs(y_teste.values - prev_teste))
    print("Maior erro no teste: %.2f ms (%.1f vezes o MAE)." % (maior_erro, maior_erro / mae))
    print("Um R² alto não quer dizer que o modelo é perfeito: ele não consegue")
    print("prever picos de repente. Por isso o SCIC também usa os alertas e a")
    print("decisão final é sempre da equipe humana.")

    # gráfico real x previsto
    plt.figure(figsize=(7, 6))
    plt.scatter(y_teste, prev_teste, edgecolor="black")
    menor = min(y_teste.min(), prev_teste.min())
    maior = max(y_teste.max(), prev_teste.max())
    plt.plot([menor, maior], [menor, maior], "r--", label="previsão perfeita")
    plt.xlabel("Latência real (ms)")
    plt.ylabel("Latência prevista pelo modelo (ms)")
    plt.title("Teste: real x previsto (R² = %.2f)" % r2)
    plt.legend()
    salvar_grafico("03_modelo_real_vs_previsto.png")



# 6) HEAP PARA PRIORIZAR ALERTAS

class HeapAlertas:

    def __init__(self):
        self.lista = []

    def tamanho(self):
        return len(self.lista)

    def inserir(self, alerta):
        self.lista.append(alerta)
        self.subir(len(self.lista) - 1)

    def subir(self, i):
        while i > 0:
            pai = (i - 1) // 2
            if self.lista[i]["pontuacao"] > self.lista[pai]["pontuacao"]:
                self.lista[i], self.lista[pai] = self.lista[pai], self.lista[i]
                i = pai
            else:
                break

    def descer(self, i):
        n = len(self.lista)
        while True:
            esquerdo = 2 * i + 1
            direito = 2 * i + 2
            maior = i
            if esquerdo < n and self.lista[esquerdo]["pontuacao"] > self.lista[maior]["pontuacao"]:
                maior = esquerdo
            if direito < n and self.lista[direito]["pontuacao"] > self.lista[maior]["pontuacao"]:
                maior = direito
            if maior == i:
                break
            self.lista[i], self.lista[maior] = self.lista[maior], self.lista[i]
            i = maior

    def ver_maior(self):
        if len(self.lista) == 0:
            return None
        return self.lista[0]

    def remover_maior(self):
        if len(self.lista) == 0:
            return None
        maior = self.lista[0]
        ultimo = self.lista.pop()
        if len(self.lista) > 0:
            self.lista[0] = ultimo
            self.descer(0)
        return maior


def calcular_pontuacao(registro, ultimo_ciclo):
    # Quanto maior a pontuação, mais urgente é o alerta
    pontos = 10 * registro["prioridade"]          # prioridade do operador (1 a 5)
    if registro["essencial"] == 1:
        pontos = pontos + 15                      # módulo essencial
    if registro["status"] == "alerta":
        pontos = pontos + 20                      # status de alerta
    erro_porcento = min(registro["erro_rel"] * 100, 100)
    pontos = pontos + 0.5 * erro_porcento         # tamanho do erro
    pontos = pontos + 5 * registro["ciclo"] / ultimo_ciclo   # alertas recentes valem mais
    return round(float(pontos), 1)


def montar_heap(df):
    heap = HeapAlertas()
    ultimo_ciclo = df["ciclo"].max()
    for i in range(len(df)):
        reg = df.iloc[i]
        critico_acima = reg["acima_previsto"] and reg["erro_rel"] > LIMITE_ATENCAO
        if reg["status"] == "alerta" or critico_acima:
            if reg["status"] == "alerta":
                mensagem = reg["mensagem_alerta"]
            else:
                mensagem = "Latência acima do previsto"
            alerta = {
                "pontuacao": calcular_pontuacao(reg, ultimo_ciclo),
                "modulo": reg["modulo"],
                "ciclo": int(reg["ciclo"]),
                "codigo": reg["codigo_sensor"],
                "erro_rel": reg["erro_rel"],
                "mensagem": mensagem,
            }
            heap.inserir(alerta)
    return heap


def priorizar_alertas(df):
    titulo("PRIORIZAÇÃO DE ALERTAS COM HEAP")
    heap = montar_heap(df)
    print("Alertas inseridos no heap:", heap.tamanho())
    print("Pontuação = 10*prioridade + 15 (essencial) + 20 (status alerta)")
    print("            + 0,5*erro relativo(%) + até 5 pontos se for recente")

    print("\nComo o heap fica guardado na lista (3 primeiros níveis):")
    print("nível 0:", [a["pontuacao"] for a in heap.lista[0:1]])
    print("nível 1:", [a["pontuacao"] for a in heap.lista[1:3]])
    print("nível 2:", [a["pontuacao"] for a in heap.lista[3:7]])

    mais_urgente = heap.ver_maior()
    print("\nAlerta mais urgente:", mais_urgente["modulo"], "-", mais_urgente["mensagem"])

    print("\nOrdem de atendimento (os 8 primeiros):")
    print(" #  pontos  ciclo  módulo                        erro rel  mensagem")
    pos = 1
    while heap.tamanho() > 0:
        a = heap.remover_maior()
        if pos <= 8:
            print("%2d  %6.1f  %5d  %-28s %7.1f %%  %s" % (pos, a["pontuacao"], a["ciclo"],
                  a["modulo"], a["erro_rel"] * 100, a["mensagem"]))
        pos = pos + 1

    comparar_heap_com_lista()


def comparar_heap_com_lista():
    linha()
    print("Comparação: heap x lista comum")
    random.seed(1)
    alertas = []
    for i in range(10000):
        alertas.append({"pontuacao": random.randint(0, 1000)})

    # com heap
    inicio = time.time()
    heap = HeapAlertas()
    for a in alertas:
        heap.inserir(a)
    for i in range(1000):
        heap.remover_maior()
    tempo_heap = time.time() - inicio

    # com lista: toda vez precisa procurar o maior percorrendo tudo
    inicio = time.time()
    lista = alertas.copy()
    for i in range(1000):
        pos_maior = 0
        for j in range(len(lista)):
            if lista[j]["pontuacao"] > lista[pos_maior]["pontuacao"]:
                pos_maior = j
        lista.pop(pos_maior)
    tempo_lista = time.time() - inicio

    print("10000 alertas, atendendo os 1000 mais urgentes:")
    print("  heap : %.3f segundos" % tempo_heap)
    print("  lista: %.3f segundos" % tempo_lista)
    print("No heap, inserir e remover custam O(log n). Na lista, achar o maior")
    print("custa O(n) toda vez, porque precisa olhar todos os alertas.")



# 7) TRIE PARA BUSCA POR PREFIXO

def tirar_acentos(texto):
    texto = texto.lower()
    trocas = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
              "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ç": "c"}
    novo = ""
    for letra in texto:
        if letra in trocas:
            novo = novo + trocas[letra]
        else:
            novo = novo + letra
    return novo


class NoTrie:
    def __init__(self):
        self.filhos = {}
        self.palavras = []


class Trie:
    def __init__(self):
        self.raiz = NoTrie()
        self.qtd_nos = 1

    def inserir(self, chave, texto_resultado):
        no = self.raiz
        for letra in tirar_acentos(chave):
            if letra not in no.filhos:
                no.filhos[letra] = NoTrie()
                self.qtd_nos = self.qtd_nos + 1
            no = no.filhos[letra]
        if texto_resultado not in no.palavras:
            no.palavras.append(texto_resultado)

    def buscar(self, prefixo):
        # 1. desce na árvore letra por letra
        no = self.raiz
        for letra in tirar_acentos(prefixo):
            if letra not in no.filhos:
                return []
            no = no.filhos[letra]
        # 2. junta tudo que está abaixo desse nó
        resultados = []
        self.coletar(no, resultados)
        resultados.sort()
        return resultados

    def coletar(self, no, resultados):
        for p in no.palavras:
            if p not in resultados:
                resultados.append(p)
        for letra in no.filhos:
            self.coletar(no.filhos[letra], resultados)


def montar_trie(df):
    trie = Trie()
    for modulo in df["modulo"].unique():
        trie.inserir(modulo, "[módulo] " + modulo)
        for palavra in modulo.split():
            if len(palavra) > 2:
                trie.inserir(palavra, "[módulo] " + modulo)
    for i in range(len(df)):
        codigo = df.iloc[i]["codigo_sensor"]
        trie.inserir(codigo, "[sensor] " + codigo + " (" + df.iloc[i]["modulo"] + ")")
    for msg in df["mensagem_alerta"].unique():
        for palavra in msg.split():
            if len(palavra) > 3:
                trie.inserir(palavra, "[alerta] " + msg)
    for cmd in COMANDOS:
        trie.inserir(cmd, "[comando] " + cmd)
    return trie


def mostrar_busca(trie, prefixo):
    resultados = trie.buscar(prefixo)
    print("\nPrefixo '" + prefixo + "' ->", len(resultados), "resultado(s)")
    if len(resultados) == 0:
        print("  nada encontrado")
    for r in resultados[0:10]:
        print("  -", r)
    if len(resultados) > 10:
        print("  ... e mais", len(resultados) - 10)


def busca_trie(df, automatico=False):
    titulo("BUSCA POR PREFIXO COM TRIE")
    trie = montar_trie(df)
    print("Trie criada com", trie.qtd_nos, "nós.")
    print("A busca não liga para maiúsculas nem acentos.")

    if automatico:
        for p in ["com", "con", "0x40", "pico"]:
            mostrar_busca(trie, p)
    else:
        print("Exemplos: com, con, 0x40, 0x6, pico, sobre")
        while True:
            prefixo = input("\nDigite um prefixo (ou só ENTER para sair): ")
            if prefixo == "":
                break
            mostrar_busca(trie, prefixo)

    print("\nPor que usar trie?")
    print("Para achar o prefixo a trie anda só uma letra por vez (O(m), m = tamanho")
    print("do prefixo). Uma busca comum teria que comparar com todas as chaves.")
    print("Como o código do sensor começa com o número do módulo (0x40 = Suporte")
    print("Médico), dá para achar todos os sensores de um módulo pelo prefixo.")



# 8) DISPOSITIVOS, BASES NUMÉRICAS E ELETRICIDADE

def hex_para_decimal(texto):
    # cada dígito vale (valor do dígito) * 16 elevado à posição
    texto = texto.upper().replace("0X", "")
    digitos = "0123456789ABCDEF"
    total = 0
    posicao = 0
    for letra in reversed(texto):
        total = total + digitos.index(letra) * (16 ** posicao)
        posicao = posicao + 1
    return total


def decimal_para_binario(numero):
    # método das divisões sucessivas por 2
    if numero == 0:
        return "0"
    binario = ""
    while numero > 0:
        resto = numero % 2
        binario = str(resto) + binario
        numero = numero // 2
    return binario


def dispositivos_bases_eletricidade(df):
    titulo("DISPOSITIVOS, BASES NUMÉRICAS E ELETRICIDADE")

    print("Dispositivos de ENTRADA (simulados):")
    print("  - sensor de latência (ping) nos roteadores -> latencia_observada_ms")
    print("  - medidor de qualidade de sinal (RSSI)     -> qualidade_sinal")
    print("  - sensor de tensão e corrente              -> tensao_v, corrente_a")
    print("  - teclado do operador (cadastro manual)")
    print("Dispositivos de SAÍDA:")
    print("  - terminal / monitor da sala de comando")
    print("  - gráficos e relatório")
    print("  - LED ou sirene de alerta (ideia, ligado ao alerta mais urgente)")
    print("Interfaces de comunicação (conceitual):")
    print("  - rede cabeada e Wi-Fi entre os módulos")
    print("  - rádio do Relé Orbital e antena para a Terra")
    print("  - USB / Bluetooth para calibrar sensores")

    linha()
    print("Conversão de bases do código de um sensor:")
    codigo = df[df["modulo"] == "Suporte Médico"].iloc[0]["codigo_sensor"]
    decimal = hex_para_decimal(codigo)
    binario = decimal_para_binario(decimal)
    print("Código em hexadecimal:", codigo)
    print("Em decimal (feito na mão):", decimal, "| conferindo com int():", int(codigo, 16))
    print("Em binário (feito na mão):", binario.zfill(16), "| conferindo com bin():", bin(decimal))
    print("Os 2 primeiros dígitos hex (" + codigo[2:4] + ") indicam o módulo e os 2 últimos (" +
          codigo[4:6] + ") o número do sensor.")
    print("Exemplo: 0x" + codigo[2:4] + " = módulo", hex_para_decimal(codigo[2:4]),
          "e 0x" + codigo[4:6] + " = sensor", hex_para_decimal(codigo[4:6]))

    linha()
    print("Eletricidade dos transmissores:")
    print("Potência: P = V * I   |   Lei de Ohm: R = V / I")
    media = df.groupby("modulo")[["tensao_v", "corrente_a", "potencia_w"]].mean()
    media["energia_por_sol_wh"] = media["potencia_w"] * HORAS_POR_SOL
    print(media.sort_values("potencia_w", ascending=False).round(2))

    rele = df[df["modulo"] == "Relé Orbital"].iloc[0]
    print("\nExemplo (Relé Orbital, ciclo 1):")
    print("P = %.2f V x %.3f A = %.2f W" % (rele["tensao_v"], rele["corrente_a"], rele["potencia_w"]))
    print("R = %.2f V / %.3f A = %.2f ohms" % (rele["tensao_v"], rele["corrente_a"], rele["resistencia_ohm"]))

    print("\nLeituras com corrente muito alta (mais de 25% acima da média do tipo):")
    media_tipo = df.groupby("tipo")["corrente_a"].mean()
    for i in range(len(df)):
        reg = df.iloc[i]
        if reg["corrente_a"] > 1.25 * media_tipo[reg["tipo"]]:
            print("  ciclo %2d | %-28s | %.3f A | %.1f W | status: %s"
                  % (reg["ciclo"], reg["modulo"], reg["corrente_a"], reg["potencia_w"], reg["status"]))

    print("\nResistor do LED de alerta do painel:")
    v_fonte = 5.0
    v_led = 2.0
    i_led = 0.02
    r = (v_fonte - v_led) / i_led
    print("R = (5 V - 2 V) / 0,02 A = %.0f ohms (usaria um resistor de 150 ohms)" % r)



# 9) ANALISAR ALERTAS DE COMUNICAÇÃO (junta tudo)

def tendencia_por_modulo(df):
    ativos = df[df["status"] == "ativo"]
    tendencias = {}
    for modulo in ativos["modulo"].unique():
        dados_mod = ativos[ativos["modulo"] == modulo]
        desvio = dados_mod["latencia_observada_ms"] - dados_mod["latencia_prevista_ms"]
        inclinacao, intercepto = np.polyfit(dados_mod["ciclo"], desvio, 1)
        tendencias[modulo] = inclinacao
    return tendencias


def sugerir_acao(alerta, tendencias):
    if "Sobrecorrente" in alerta["mensagem"]:
        return "comando_reduzir_potencia e verificar o transmissor"
    if tendencias["Relé Orbital"] > 0.8:
        return ("comando_redirecionar_rele, MAS o Relé Orbital está piorando a cada ciclo,"
                " confirmar se ele aguenta antes de redirecionar")
    return "comando_redirecionar_rele (usar o Relé Orbital como rota reserva)"


def analisar_alertas(df):
    titulo("ANALISAR ALERTAS DE COMUNICAÇÃO")
    print("1) Base carregada com", len(df), "registros")

    acima = df[(df["acima_previsto"] == True) & (df["erro_rel"] > LIMITE_ATENCAO)]
    print("\n2) Registros com latência acima do previsto e erro crítico:", len(acima))
    print(acima[["ciclo", "modulo", "latencia_prevista_ms", "latencia_observada_ms",
                 "erro_abs_ms"]].round(2).to_string(index=False))

    print("\n3) Alertas mais urgentes (heap):")
    heap = montar_heap(df)
    primeiro = heap.ver_maior()
    for i in range(5):
        a = heap.remover_maior()
        print("   %d. [%.1f] %s (ciclo %d, %s) - %s" % (i + 1, a["pontuacao"], a["modulo"],
              a["ciclo"], a["codigo"], a["mensagem"]))

    prefixo = primeiro["codigo"][0:4]
    print("\n4) Sensores do módulo mais urgente (trie, prefixo '" + prefixo + "'):")
    trie = montar_trie(df)
    for r in trie.buscar(prefixo)[0:5]:
        print("   -", r)

    tendencias = tendencia_por_modulo(df)
    print("\n5) Ação sugerida (precisa ser confirmada pelo operador):")
    print("  ", sugerir_acao(primeiro, tendencias))



# 10) ANÁLISE FINAL E GRÁFICOS

def gerar_graficos(df):
    internos = df[df["modulo"] != "Comunicação Interplanetária"]

    # Gráfico 1: latência prevista x observada
    plt.figure(figsize=(8, 6))
    cores = {"ativo": "blue", "alerta": "red", "manutencao": "orange"}
    for status in cores:
        parte = internos[internos["status"] == status]
        plt.scatter(parte["latencia_prevista_ms"], parte["latencia_observada_ms"],
                    color=cores[status], label=status)
    plt.plot([0, 130], [0, 130], "k--", label="prevista = observada")
    plt.xlabel("Latência prevista (ms)")
    plt.ylabel("Latência observada (ms)")
    plt.title("Latência prevista x observada (enlaces internos)")
    plt.legend()
    salvar_grafico("01_prevista_vs_observada.png")

    # Gráfico 2: erro relativo médio por módulo (com seaborn)
    erro = df.groupby("modulo")["erro_rel"].mean() * 100
    erro = erro.sort_values(ascending=False).reset_index()
    plt.figure(figsize=(9, 6))
    sns.barplot(data=erro, x="erro_rel", y="modulo", color="steelblue")
    plt.axvline(10, color="orange", linestyle="--", label="limite aceitável (10%)")
    plt.axvline(25, color="red", linestyle="--", label="limite de atenção (25%)")
    plt.xlabel("Erro relativo médio (%)")
    plt.ylabel("")
    plt.title("Erro relativo médio da latência por módulo")
    plt.legend()
    salvar_grafico("02_erro_relativo_por_modulo.png")

    # Gráfico 5: tendência do Relé Orbital (manutenção preditiva)
    ativos = df[df["status"] == "ativo"]
    rele = ativos[ativos["modulo"] == "Relé Orbital"]
    desvio = rele["latencia_observada_ms"] - rele["latencia_prevista_ms"]
    a, b = np.polyfit(rele["ciclo"], desvio, 1)
    plt.figure(figsize=(8, 5))
    plt.scatter(rele["ciclo"], desvio, color="red", label="desvio medido")
    plt.plot(rele["ciclo"], a * rele["ciclo"] + b, "r-", label="tendência: %+.2f ms por ciclo" % a)
    plt.axhline(0, color="black")
    plt.xlabel("Ciclo (sol)")
    plt.ylabel("Observada - prevista (ms)")
    plt.title("Manutenção preditiva - Relé Orbital")
    plt.legend()
    salvar_grafico("05_tendencia_rele_orbital.png")


def analise_final(df):
    titulo("ANÁLISE FINAL E GERENCIAMENTO INTELIGENTE")
    print("Gerando gráficos...")
    gerar_graficos(df)

    print("\nResumo:")
    print("- Disponibilidade geral: %.1f %%" % ((df["status"] == "ativo").mean() * 100))
    print("- Alertas registrados:", (df["status"] == "alerta").sum())
    erro_modulo = df.groupby("modulo")["erro_rel"].mean().sort_values(ascending=False)
    print("- Módulo com maior erro relativo médio: %s (%.1f %%)"
          % (erro_modulo.index[0], erro_modulo.iloc[0] * 100))
    heap = montar_heap(df)
    a = heap.ver_maior()
    print("- Alerta mais urgente:", a["modulo"], "ciclo", a["ciclo"], "-", a["mensagem"])

    linha()
    print("Gerenciamento inteligente da comunicação, a partir dos resultados:")
    print("* Sensores inteligentes: cada registro do json é como um pacote que um")
    print("  sensor IoT do módulo mandaria a cada ciclo (ping, sinal, tensão, corrente).")
    print("* Monitoramento contínuo: comparando previsto x observado a cada ciclo,")
    print("  o sistema achou", (df["faixa_erro"] == "critico").sum(), "leituras na faixa crítica.")
    print("* Automação: o heap escolhe o alerta mais urgente e o sistema sugere um")
    print("  comando, mas quem confirma é o operador.")
    print("* Redundância: módulos essenciais com erro alto precisam de rota reserva")
    print("  (Relé Orbital) e cópia dos dados no Armazenamento.")

    print("* Manutenção preditiva - tendência do desvio (ms por ciclo):")
    tendencias = tendencia_por_modulo(df)
    ordem = sorted(tendencias, key=tendencias.get, reverse=True)
    for modulo in ordem[0:3]:
        aviso = ""
        if tendencias[modulo] > 0.8:
            aviso = "  <- agendar inspeção antes de falhar"
        print("    %-28s %+.2f%s" % (modulo, tendencias[modulo], aviso))

    energia_kwh = df.groupby("ciclo")["potencia_w"].sum().mean() * HORAS_POR_SOL / 1000
    print("* Microrrede: os transmissores gastam uns %.1f kWh por sol. Os módulos de" % energia_kwh)
    print("  comunicação são os que mais gastam, então reduzir a potência quando o")
    print("  tráfego está baixo economiza energia.")

    linha()
    print("Limitações: os dados são simulados e o modelo não prevê picos de")
    print("repente. As decisões finais ficam com a equipe humana da colônia.")



# 11) DEMONSTRAÇÃO COMPLETA

def demonstracao(df):
    consultar_registros(df, automatico=True)
    indicadores_e_erros(df)
    simulacao_euler(df)
    modelo_previsao(df)
    priorizar_alertas(df)
    busca_trie(df, automatico=True)
    dispositivos_bases_eletricidade(df)
    analisar_alertas(df)
    analise_final(df)



# MENU PRINCIPAL

def menu():
    titulo("SCIC - SISTEMA DE COMUNICAÇÃO INTERPLANETÁRIA DA COLÔNIA AURORA SIGER")
    print("Carregando os dados...")
    df = carregar_dados()

    while True:
        print()
        linha()
        print(" 1 - Recarregar dados / cadastrar novo registro")
        print(" 2 - Consultar registros")
        print(" 3 - Indicadores e erros numéricos")
        print(" 4 - Simulação de recuperação do enlace (Euler)")
        print(" 5 - Modelo de previsão e métricas")
        print(" 6 - Priorizar alertas (heap)")
        print(" 7 - Buscar por prefixo (trie)")
        print(" 8 - Dispositivos, bases numéricas e eletricidade")
        print(" 9 - Analisar alertas de comunicação")
        print("10 - Análise final e gráficos")
        print("11 - Demonstração completa (roda tudo)")
        print(" 0 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "0":
            print("Saindo do SCIC. Até mais!")
            break
        elif opcao == "1":
            escolha = input("a - recarregar o arquivo | b - cadastrar registro: ")
            if escolha.lower() == "b":
                df = cadastrar_registro(df)
            else:
                df = carregar_dados()
        elif opcao == "2":
            consultar_registros(df)
        elif opcao == "3":
            indicadores_e_erros(df)
        elif opcao == "4":
            simulacao_euler(df)
        elif opcao == "5":
            modelo_previsao(df)
        elif opcao == "6":
            priorizar_alertas(df)
        elif opcao == "7":
            busca_trie(df)
        elif opcao == "8":
            dispositivos_bases_eletricidade(df)
        elif opcao == "9":
            analisar_alertas(df)
        elif opcao == "10":
            analise_final(df)
        elif opcao == "11":
            demonstracao(df)
        else:
            print("Opção inválida! Digite um número de 0 a 11.")
            continue
        esperar_enter()


menu()
