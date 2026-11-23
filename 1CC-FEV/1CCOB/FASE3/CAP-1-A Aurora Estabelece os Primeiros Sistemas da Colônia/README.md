# Sistema Inteligente de Colônia Espacial — Marte Base Alpha

---

## Sobre o Projeto

Este sistema simula o funcionamento inteligente de uma colônia em Marte.  
Ele organiza os dados da colônia, toma decisões automáticas, prevê geração de energia eólica usando regressão linear e analisa o balanço energético.

Todo o sistema foi desenvolvido em **Python puro**, sem bibliotecas externas, usando apenas conceitos básicos da disciplina: listas, dicionários, funções e estruturas de decisão.

---

## Estrutura do Código

```
colonia_marte/
└── colonia.py        <- arquivo principal (todos os módulos)
```

O arquivo está dividido em **5 módulos** (cada um em sua seção):

| Módulo | O que faz |
|--------|-----------|
| **Módulo 1** – Dados da Colônia | Organiza dados em listas, dicionários e hierarquia |
| **Módulo 2** – Tomada de Decisões | Regras com `if/elif/else` e operadores lógicos |
| **Módulo 3** – Previsão (Regressão) | Estima energia eólica a partir do histórico de vento |
| **Módulo 4** – Análise de Energia | Compara geração x consumo e gera recomendação |
| **Módulo 5** – Relatório Completo | Integra todos os módulos e exibe o resultado |

---

## Como Executar

1. Certifique-se de ter o **Python 3** instalado
2. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/colonia-marte.git
   cd colonia-marte
   ```
3. Execute o arquivo principal:
   ```bash
   python colonia.py
   ```

Não é necessário instalar nenhuma biblioteca externa.

---

## Exemplos de Entrada e Saída

### Cenário 1 — Energia baixa, consumo alto (alerta)

**Entrada:**
```
energia = 40%
consumo = 70 unidades
geracao = 40 unidades
velocidade_vento = 11 km/h
```

**Saída:**
```
DECISAO AUTOMATICA:
   ALERTA: Energia < 50% e consumo alto -> Ativar MODO ECONOMIA

STATUS DOS SISTEMAS:
   oxigenio            : LIGADO (prioridade CRITICA)
   temperatura         : LIGADO (prioridade CRITICA)
   laboratorio         : DESLIGADO (economia)
   entretenimento      : DESLIGADO (economia)

ANALISE ENERGETICA:
   ALERTA: Consumo maior que geracao!
      Deficit de 30 unidades -> Reduzir consumo ou aumentar geracao

PREVISAO EOLICA:
   Vento = 11 km/h -> Energia prevista ≈ 27.3 unidades
```

---

### Cenário 2 — Sistema estável, geração alta (sugestão de armazenamento)

**Entrada:**
```
energia = 85%
consumo = 30 unidades
geracao = 80 unidades
velocidade_vento = 18 km/h
```

**Saída:**
```
DECISAO AUTOMATICA:
   NORMAL: Sistema estavel -> Operacao padrao

ANALISE ENERGETICA:
   SUGESTAO: Geracao muito acima do consumo!
      Excedente de 50 unidades -> Armazenar energia nas baterias

PREVISAO EOLICA:
   Vento = 18 km/h -> Energia prevista ≈ 44.9 unidades
```

---

### Cenário 3 — Situação crítica

**Entrada:**
```
energia = 15%
consumo = 75 unidades
geracao = 20 unidades
velocidade_vento = 5 km/h
```

**Saída:**
```
DECISAO AUTOMATICA:
   CRITICO: Energia critica + consumo alto -> Desligar sistemas nao essenciais IMEDIATAMENTE

STATUS DOS SISTEMAS:
   oxigenio   : LIGADO (prioridade CRITICA)   <- nunca desliga!
   temperatura: LIGADO (prioridade CRITICA)   <- nunca desliga!
   laboratorio: DESLIGADO (economia)

ANALISE ENERGETICA:
   ALERTA: Consumo maior que geracao!
      Deficit de 55 unidades -> Reduzir consumo ou aumentar geracao
```

---

## Conceitos Aplicados

### Estruturas de Dados
- **Dicionário (chave-valor):** armazena energia, consumo, clima e sistemas
- **Lista:** histórico de velocidade do vento e energia gerada
- **Hierarquia:** `sistemas -> energetico -> solar / eolico`

### Lógica de Decisão
- Regras simples com `if / elif / else`
- Condições combinadas com `and` (ex: `energia < 50 and consumo > 70`)
- Priorização: sistemas críticos nunca são desligados

### Regressão Linear
- Fórmula da reta: `y = a*x + b`
- Calculada manualmente com somatórios (sem bibliotecas externas)
- Usada para prever energia eólica a partir da velocidade do vento

### Análise Energética
- Comparação direta: `geracao vs consumo`
- Três situações: déficit / equilíbrio / excedente
- Recomendação gerada automaticamente

---


