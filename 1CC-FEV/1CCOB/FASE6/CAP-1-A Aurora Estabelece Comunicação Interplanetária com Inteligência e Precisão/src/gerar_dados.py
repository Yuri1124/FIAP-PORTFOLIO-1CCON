import json

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)


MODULOS = [
    ("Habitação Alfa",              "habitacao",      0, 320,  0x10),
    ("Habitação Beta",              "habitacao",      0, 540,  0x11),
    ("Agricultura Hidropônica",     "agricultura",    0, 880,  0x20),
    ("Laboratório Geológico",       "laboratorio",    0, 1450, 0x30),
    ("Suporte Médico",              "suporte_medico", 1, 260,  0x40),
    ("Armazenamento de Dados",      "armazenamento",  0, 150,  0x50),
    ("Comunicação Central",         "comunicacao",    1, 0,    0x60),
    ("Comunicação Interplanetária", "comunicacao",    1, 2100, 0x61),
    ("Comando Operacional",         "comando",        1, 90,   0x70),
    ("Controle Ambiental",          "suporte_vida",   1, 410,  0x80),
    ("Energia Solar",               "energia",        1, 1200, 0x90),
    ("Relé Orbital",                "comunicacao",    1, 1800, 0x62),
]

# Tensão nominal (V) e corrente típica (A) do transmissor de cada tipo
ELETRICA = {
    "habitacao": (12.0, 0.8), "agricultura": (12.0, 1.1),
    "laboratorio": (24.0, 1.4), "suporte_medico": (24.0, 1.0),
    "armazenamento": (12.0, 2.0), "comunicacao": (48.0, 3.5),
    "comando": (24.0, 1.6), "suporte_vida": (24.0, 1.2),
    "energia": (48.0, 0.9),
}

N_CICLOS = 10
SOL_INICIAL = 101

registros = []
for ciclo in range(1, N_CICLOS + 1):
    for idx, (nome, tipo, essencial, dist, mod_id) in enumerate(MODULOS):
        carga = rng.uniform(5, 60)                     # Mbps
        qualidade = np.clip(rng.normal(0.85, 0.08), 0.4, 1.0)
        tensao_nom, corr_nom = ELETRICA[tipo]
        tensao = tensao_nom * rng.normal(1.0, 0.02)
        corrente = corr_nom * rng.normal(1.0, 0.08)

        if nome == "Comunicação Interplanetária":

            atraso_luz_ms = (12.6 + 0.08 * ciclo) * 60_000
            observada = atraso_luz_ms + rng.normal(900, 250)
            prevista = (12.6 + 0.08 * ciclo) * 60_000 + 500
        else:
            base = 8.0
            ruido = rng.normal(0, 2.5)
            observada = (base + 0.9 * carga + 0.004 * dist
                         - 18 * qualidade + ruido + 15)
            prevista = base + 0.9 * carga + 6
            if nome == "Relé Orbital":

                observada += 1.6 * ciclo

        status, mensagem = "ativo", "Operação normal"

        anomalia = rng.random()
        if anomalia < 0.07 and nome != "Comunicação Interplanetária":
            observada *= rng.uniform(1.8, 2.6)
            qualidade *= 0.6
            status, mensagem = "alerta", "Pico de latência no enlace"
        elif anomalia < 0.10:
            corrente *= 1.35
            status, mensagem = "alerta", "Sobrecorrente no transmissor"
        elif anomalia < 0.14:
            status, mensagem = "manutencao", "Manutenção programada"

        prioridade = 4 if essencial else 2
        if status == "alerta":
            prioridade = min(5, prioridade + 1)

        codigo = f"0x{mod_id:02X}{(idx * 7 + ciclo) % 256:02X}"

        registros.append({
            "ciclo": ciclo,
            "sol": SOL_INICIAL + ciclo - 1,
            "data_registro": (pd.Timestamp("2026-09-01")
                              + pd.Timedelta(days=ciclo - 1)).date().isoformat(),
            "modulo": nome,
            "tipo": tipo,
            "essencial": essencial,
            "codigo_sensor": codigo,
            "distancia_m": dist,
            "carga_trafego_mbps": round(carga, 2),
            "qualidade_sinal": round(float(qualidade), 3),
            "tensao_v": round(tensao, 2),
            "corrente_a": round(corrente, 3),
            "latencia_prevista_ms": round(prevista, 2),
            "latencia_observada_ms": round(observada, 2),
            "status": status,
            "prioridade": prioridade,
            "mensagem_alerta": mensagem,
        })

df = pd.DataFrame(registros)

df.loc[17, "latencia_observada_ms"] = np.nan
df.loc[58, "qualidade_sinal"] = np.nan
df.loc[93, "corrente_a"] = np.nan
df = pd.concat([df, df.iloc[[33]]], ignore_index=True)

registros_json = json.loads(df.to_json(orient="records", force_ascii=False))

base = {
    "colonia": "Aurora Siger",
    "descricao": "Base simulada de dados operacionais e de comunicação (SCIC)",
    "unidades": {
        "latencia": "ms", "distancia": "m", "carga_trafego": "Mbps",
        "tensao": "V", "corrente": "A", "qualidade_sinal": "0 a 1",
    },
    "total_registros": len(registros_json),
    "registros": registros_json,
}
arquivo = open("dados_aurora_siger.json", "w", encoding="utf-8")
json.dump(base, arquivo, ensure_ascii=False, indent=2)
arquivo.close()
print("Base gerada:", len(df), "registros,", df["modulo"].nunique(), "módulos.")
print(df["status"].value_counts())
