import re
import unicodedata

PONTUACAO_MINIMA = 3

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "de", "da", "do", "das", "dos", "em", "no", "na",
    "nos", "nas", "por", "para", "pra", "com", "e", "ou", "que", "qual", "quais", "como",
    "onde", "quando", "quem", "se", "eu", "me", "meu", "minha", "seu", "sua", "isso",
    "esse", "essa", "ao", "tem", "tenho", "posso", "ta", "preciso", "sobre", "mais",
    "ja", "nao", "sim", "ser", "foi", "estou", "algum", "alguma", "quero", "queria",
    "saber", "consigo", "pode", "pelo", "pela", "ele", "ela", "esta",
}

SINONIMOS = {
    "rg": ["identidade"],
    "demitido": ["demissao", "desemprego"],
    "demitida": ["demissao", "desemprego"],
    "desempregado": ["desemprego"],
    "votar": ["eleitor", "titulo"],
    "advogado": ["defensoria", "juridica"],
    "ambulancia": ["samu"],
    "fogo": ["incendio", "bombeiros"],
    "loja": ["consumidor", "empresa"],
    "apanha": ["violencia"],
    "agredida": ["violencia", "mulher"],
}

SUFIXOS = ["ar", "er", "ir", "as", "es", "os", "a", "e", "o", "s"]


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return " ".join(texto.split())


def radical(palavra):
    # Corta terminações simples para juntar plural e conjugação (denuncio/denunciar -> denunci)
    if len(palavra) <= 4 or palavra.isdigit():
        return palavra
    for sufixo in SUFIXOS:
        if palavra.endswith(sufixo) and len(palavra) - len(sufixo) >= 4:
            return palavra[:-len(sufixo)]
    return palavra


def palavras(texto, usar_sinonimos=True):
    resultado = set()
    for p in normalizar(texto).split():
        if p in STOPWORDS:
            continue
        resultado.add(radical(p))
        if usar_sinonimos and p in SINONIMOS:
            for s in SINONIMOS[p]:
                resultado.add(radical(s))
    return resultado


def criar_indice(registros):
    indice = {}
    for r in registros:
        texto = r["titulo"] + " " + " ".join(r["palavras_chave"]) + " " + " ".join(r.get("perguntas_exemplo", []))
        r["_palavras"] = palavras(texto, usar_sinonimos=False)
        r["_chaves"] = [palavras(k, usar_sinonimos=False) for k in r["palavras_chave"]]
        for p in r["_palavras"]:
            indice.setdefault(p, set()).add(r["id"])
    return indice


def pontuar(pergunta, registros, indice):
    termos = palavras(pergunta)

    candidatos = set()
    for t in termos:
        candidatos |= indice.get(t, set())

    ranking = []
    for rid in candidatos:
        r = registros[rid]
        pontos = 0
        # palavra-chave inteira presente na pergunta vale mais
        for chave in r["_chaves"]:
            if chave and chave <= termos:
                pontos += 2 + len(chave)
        # termo que só aparece neste registro vale 2, termo comum vale 1
        for t in termos & r["_palavras"]:
            pontos += 2 if len(indice[t]) == 1 else 1
        ranking.append((rid, pontos))

    ranking.sort(key=lambda x: (-x[1], x[0]))
    return ranking


def remover_dados_pessoais(texto):
    padroes = [
        r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",          # CPF
        r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",                 # e-mail
        r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b",            # telefone
    ]
    novo = texto
    for padrao in padroes:
        novo = re.sub(padrao, " ", novo)
    return novo, novo != texto


def buscar(pergunta, registros, indice):
    """Retorna um dicionário com status: ok, ambigua, sem_resposta ou invalida."""
    if not pergunta or not pergunta.strip():
        return {"status": "invalida", "motivo": "vazia", "privacidade": False}

    pergunta, privacidade = remover_dados_pessoais(pergunta.strip()[:300])
    relevantes = [p for p in normalizar(pergunta).split() if p not in STOPWORDS]
    if not relevantes:
        return {"status": "invalida", "motivo": "sem_palavras", "privacidade": privacidade}

    ranking = pontuar(pergunta, registros, indice)
    resultado = {"privacidade": privacidade, "ranking": ranking[:5]}

    # uma palavra só que aparece em vários registros (ex.: "cpf")
    if len(relevantes) == 1 and len(ranking) > 1:
        resultado.update(status="ambigua", opcoes=[rid for rid, _ in ranking[:4]])
        return resultado

    if not ranking or ranking[0][1] < PONTUACAO_MINIMA:
        resultado["status"] = "sem_resposta"
        return resultado

    melhor = ranking[0][1]
    proximos = [rid for rid, pts in ranking if pts >= melhor * 0.85]
    if len(proximos) > 1:
        resultado.update(status="ambigua", opcoes=proximos[:4])
        return resultado

    resultado.update(status="ok", id=ranking[0][0])
    return resultado
