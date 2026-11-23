# 🌊 LEVIATHAN-7 — Sistema Inteligente de Monitoramento de Missão Espacial

## 🚀 Resumo do Problema e Cenário

A **Missão LEVIATHAN-7** é uma operação de exploração autônoma no oceano subsuperficial de **Europa**, lua gelada de Júpiter. Um submarino robótico mergulhou sob 30 km de gelo para coletar amostras do oceano líquido que existe abaixo — um dos ambientes mais promissores para a busca de vida extraterrestre.

No **Dia 47 da missão**, o submersível sofreu uma colisão com uma estrutura rochosa submersa desconhecida. Vários módulos foram danificados, a comunicação principal foi perdida, e o sistema embarcado foi forçado a **reinicializar** e operar de forma completamente autônoma.

O sistema desenvolvido neste projeto é responsável por:
- Diagnosticar os danos a partir dos dados de telemetria recebidos
- Classificar o estado operacional em **normal**, **alerta** ou **crítico**
- Gerar alertas automáticos priorizados
- Prever com quanto tempo de energia a missão ainda dispõe
- Recomendar ações para garantir o retorno seguro à superfície

---

## 🗂️ Estruturas de Dados Utilizadas

| Estrutura | Onde foi usada | Justificativa |
|-----------|---------------|---------------|
| **Dicionário** | `modulos`, `ambiente`, `hierarquia` | Acesso O(1) por nome do módulo — essencial para busca rápida em sistemas críticos |
| **Lista** | `leituras_energia`, `log_eventos` | Armazena séries temporais de dados; permite iteração e indexação por ciclo |
| **Matriz (lista de listas)** | `leituras_energia` | Representa leituras de múltiplas variáveis (geração, consumo, reserva) ao longo do tempo |
| **Pilha (lista com append/reversed)** | `log_eventos` | Registra eventos com acesso ao mais recente no topo — padrão LIFO |
| **Fila (deque)** | `fila_alertas` | Organiza alertas por ordem de chegada — padrão FIFO; os críticos são exibidos primeiro |
| **Dicionário de dicionários** | `hierarquia` | Representa a árvore hierárquica de sistemas e subsistemas da missão |

---

## ⚙️ Regras Lógicas Principais do Diagnóstico

### Expressão Booleana Principal

```
STATUS_CRÍTICO = (reserva < 50 AND consumo > geração)
                 OR (suporte_vida == 0)
                 OR (radiação > 10.0)

STATUS_ALERTA  = NOT STATUS_CRÍTICO AND
                 ((comunicação == 0 AND sinal < 30 AND NOT sinal > 50)
                  OR (reserva >= 50 AND reserva < 70)
                  OR laboratório == 0)

STATUS_NORMAL  = NOT STATUS_CRÍTICO AND NOT STATUS_ALERTA
```

### Regras em linguagem natural

| Regra | Condição | Ação gerada |
|-------|----------|-------------|
| Regra 1 | Reserva < 50% **E** consumo > geração | Status CRÍTICO — colapso energético iminente |
| Regra 2 | Suporte à vida falhou **OU** radiação > 10 mSv/h | Status CRÍTICO — risco à missão |
| Regra 3 | Comunicação offline **E** sinal < 30% **E NÃO** sinal > 50% | Status ALERTA — comunicação comprometida |
| Regra 4 | Reserva entre 50% e 70% | Status ALERTA — monitorar tendência energética |

### Detecção de Inconsistência
```
pressao_invalida = (pressao_casco < 0) OR (pressao_casco > 200000)
```
O sensor retornou `-9999 kPa`, valor fisicamente impossível. O sistema detecta a anomalia, **descarta o dado** e **não aciona alarme falso** de ruptura de casco.

---

## 📈 Técnica de Previsão Utilizada

**Regressão Linear Simples** — implementada manualmente em Python puro, sem bibliotecas externas.

- **Variável analisada:** reserva energética (%) ao longo dos ciclos
- **Dados:** 6 leituras históricas (ciclos 1 a 6)
- **Equação encontrada:** `reserva = -10.26 × ciclo + 111.07`
- **Resultado:** ponto de não-retorno (reserva = 20%) estimado no **ciclo 8.9**
- **Influência na decisão:** com apenas ~2.9 ciclos restantes, o sistema gera alerta CRÍTICO e recomenda início imediato do protocolo de subida

---

## ▶️ Como Executar

**Pré-requisito:** Python 3.x instalado (sem bibliotecas externas necessárias)

```bash
# Clonar o repositório
git clone https://github.com/Yuri1124/leviathan7.git
cd leviathan7

# Executar o sistema
python src/sistema.py
```

---

## 📥 Exemplo de Entrada

Os dados estão embutidos no código e espelhados no arquivo `data/dados.csv`:

```
Módulos críticos: suporte_vida=1, energia=1, comunicacao=0, habitat=1, laboratorio=0, armazenamento=1
Reserva energética atual: 47%
Geração: 70 kWh | Consumo: 122 kWh
Radiação: 7.8 mSv/h | Sinal: 23%
Pressão do casco: -9999 kPa (INVÁLIDO)
```

## 📤 Exemplo de Saída

```
Status operacional  : 🔴 CRÍTICO
Reserva energética  : 47%
Ciclos até colapso  : 2.9 ciclos estimados
Alertas gerados     : 7

[1] 🔴 [CRÍTICO] Comunicação principal OFFLINE
[2] 🔴 [CRÍTICO] Energia em colapso — reserva 47%
[3] 🟡 [ALERTA]  Sensor de pressão com falha
...
```

---

## 🛠️ Recomendações Geradas pelo Sistema

1. 🔴 **[CRÍTICA]** Manter suporte à vida e habitat em operação máxima
2. 🔴 **[CRÍTICA]** Ativar comunicação de emergência via retransmissor no gelo
3. 🔴 **[CRÍTICA]** Iniciar contagem regressiva — ponto crítico no ciclo 8.9
4. 🟠 **[ALTA]** Desligar laboratório e sistemas científicos
5. 🟠 **[ALTA]** Redirecionar energia para baterias e propulsão
6. 🟡 **[MÉDIA]** Registrar dados científicos na memória de longo prazo
7. 🟡 **[MÉDIA]** Agendar diagnóstico do sensor de pressão

---

## 🎥 Vídeo de Apresentação

[Link do YouTube — a preencher]

---

## 📚 Conclusões e Aprendizados

O projeto LEVIATHAN-7 demonstrou como conceitos fundamentais de computação — estruturas de dados, lógica booleana, algoritmos e análise de dados — podem ser aplicados em um cenário realista e crítico de operação espacial.

A principal aprendizagem foi perceber que **a escolha das estruturas de dados importa**: usar um dicionário para acesso a módulos, uma fila para alertas e uma pilha para o log não são detalhes — são decisões técnicas que impactam diretamente a eficiência e a clareza do sistema.

A previsão por regressão linear, implementada do zero sem bibliotecas, demonstrou que técnicas simples podem gerar insights operacionais valiosos quando aplicadas com raciocínio claro.
"# leviathan7" 
