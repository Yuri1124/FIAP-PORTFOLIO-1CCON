import csv
import json
import os
import time

from sistema import iniciar, resposta_modelo_a, resposta_modelo_b, responder

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_TESTES = os.path.join(PASTA, "..", "data", "perguntas_teste.json")
ARQUIVO_CSV = os.path.join(PASTA, "..", "docs", "resultados_testes.csv")
REPETICOES = 100


def obtido(resultado):
    if resultado["status"] == "ok":
        return resultado["id"]
    return resultado["status"].upper()


def criterios(texto, status):
    # checklist com os itens pedidos no enunciado
    if status == "ok":
        itens = ["Fonte:", "http", "Verificado em", "Atenção:", "Próximos assuntos", "1. "]
        return sum(1 for item in itens if item in texto), len(itens)
    explica_limite = len(texto.split()) >= 12
    sugere_caminho = any(x in texto for x in ["Temas disponíveis", "[", "Exemplo"])
    return explica_limite + sugere_caminho, 2


def main():
    with open(ARQUIVO_TESTES, encoding="utf-8") as arq:
        testes = json.load(arq)["perguntas"]

    app = iniciar()
    linhas = []
    pontos_a = pontos_b = total_criterios = 0

    for t in testes:
        _, resultado = responder(t["pergunta"], app)
        resposta = obtido(resultado)
        acerto = resposta == t["esperado"]
        if t["categoria"] == "privacidade":
            acerto = acerto and resultado["privacidade"]

        inicio = time.perf_counter()
        for _ in range(REPETICOES):
            responder(t["pergunta"], app)
        tempo = (time.perf_counter() - inicio) / REPETICOES * 1000

        a, total = criterios(resposta_modelo_a(resultado, app["registros"]), resultado["status"])
        b, _ = criterios(resposta_modelo_b(resultado, app["registros"], app["temas"], app["grafo"]),
                         resultado["status"])
        pontos_a += a
        pontos_b += b
        total_criterios += total

        linhas.append([t["id"], t["categoria"], t["pergunta"], t["esperado"], resposta,
                       "ACERTO" if acerto else "ERRO", f"{tempo:.3f}"])

    with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as arq:
        escritor = csv.writer(arq, delimiter=";")
        escritor.writerow(["id", "categoria", "pergunta", "esperado", "obtido", "resultado", "tempo_ms"])
        escritor.writerows(linhas)

    acertos = sum(1 for l in linhas if l[5] == "ACERTO")
    tempo_medio = sum(float(l[6]) for l in linhas) / len(linhas)

    print(f"{'ID':<5}{'Esperado':<14}{'Obtido':<14}{'Resultado':<10}ms")
    for l in linhas:
        print(f"{l[0]:<5}{l[3]:<14}{l[4]:<14}{l[5]:<10}{l[6]}")

    print(f"\nTaxa de acerto: {acertos}/{len(linhas)} = {acertos / len(linhas) * 100:.1f}%")
    print(f"Tempo médio de consulta: {tempo_medio:.3f} ms")

    print("\nAcerto por categoria:")
    for cat in dict.fromkeys(l[1] for l in linhas):
        grupo = [l for l in linhas if l[1] == cat]
        ok = sum(1 for l in grupo if l[5] == "ACERTO")
        print(f"  {cat}: {ok}/{len(grupo)}")

    print(f"\nCritérios do enunciado atendidos - Modelo A: {pontos_a}/{total_criterios} | "
          f"Modelo B: {pontos_b}/{total_criterios}")
    print(f"Resultados salvos em {os.path.normpath(ARQUIVO_CSV)}")


if __name__ == "__main__":
    main()
