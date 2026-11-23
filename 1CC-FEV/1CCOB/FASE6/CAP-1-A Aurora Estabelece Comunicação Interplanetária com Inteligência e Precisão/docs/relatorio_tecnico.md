# Relatório Técnico — SCIC: Sistema de Comunicação Interplanetária da Colônia Aurora Siger

**Atividade Integradora** · Equipe: _[nomes e RMs dos integrantes]_ · Outubro de 2026

> Todos os números deste relatório foram obtidos executando a opção 11 do menu (demonstração completa) de `codigo_fonte.py` sobre o arquivo `dados_aurora_siger.json`. A saída completa está em `saida_demo.txt` e os gráficos em `graficos_ou_imagens/`.

---

## 1. Contexto da solução

A colônia Aurora Siger depende de duas camadas de comunicação:

1. **Rede interna** entre os 12 módulos (habitação, agricultura, laboratório, suporte médico, comando, controle ambiental etc.), com latências de dezenas de milissegundos;
2. **Enlace interplanetário** com a Terra, feito pela antena da Comunicação Interplanetária e apoiado pelo Relé Orbital, cuja latência é dominada pelo atraso da luz — cerca de **13 minutos** nos ciclos simulados.

O SCIC é um protótipo em Python, operado por menu no terminal, que organiza as leituras desses enlaces, mede o quanto as previsões de latência erram, treina um modelo simples de previsão, prioriza alertas com um **heap máximo** e permite localizar módulos, sensores e comandos por prefixo com uma **trie**. O objetivo é apoiar a decisão da equipe de operação, nunca substituí-la.

## 2. Descrição dos dados

A base `dados_aurora_siger.json` foi construída pela equipe com o script `gerar_dados.py` (semente fixa, portanto reproduzível). São **121 registros**: 12 módulos × 10 ciclos (sóis 101 a 110), mais um registro duplicado inserido de propósito.

**Formato JSON.** O arquivo é um objeto com metadados da colônia (`colonia`, `descricao`, `unidades`, `total_registros`) e a lista `registros`, em que cada leitura é um dicionário. O SCIC lê o arquivo com o módulo `json` do Python e converte a lista de dicionários em um DataFrame do Pandas. Valores ausentes aparecem como `null` e viram `NaN` no DataFrame. O JSON foi escolhido porque guarda, no mesmo arquivo, os dados e o contexto deles (como as unidades), e porque é o formato mais comum em telemetria de dispositivos IoT. No cadastro de um novo registro, o sistema lê a base, acrescenta o dicionário à lista e regrava o arquivo.

```json
{
  "colonia": "Aurora Siger",
  "unidades": {"latencia": "ms", "tensao": "V", "corrente": "A", "...": "..."},
  "total_registros": 121,
  "registros": [
    {"ciclo": 1, "modulo": "Habitação Alfa", "codigo_sensor": "0x1001",
     "latencia_prevista_ms": 56.81, "latencia_observada_ms": 48.41,
     "status": "ativo", "prioridade": 2, "...": "..."}
  ]
}
```

| Campo | Descrição |
|---|---|
| `ciclo`, `sol`, `data_registro` | Momento da leitura |
| `modulo`, `tipo`, `essencial` | Identificação do módulo; `essencial = 1` para suporte à vida, médico, comando, energia e comunicação |
| `codigo_sensor` | Identificador hexadecimal de 16 bits (`0x40xx` = Suporte Médico) |
| `distancia_m` | Distância do módulo ao nó central |
| `carga_trafego_mbps`, `qualidade_sinal` | Tráfego e qualidade do sinal (0 a 1, equivalente a um RSSI normalizado) |
| `tensao_v`, `corrente_a` | Leituras elétricas do transmissor |
| `latencia_prevista_ms` | Estimativa de engenharia (só considera tráfego) |
| `latencia_observada_ms` | Latência medida |
| `status`, `prioridade`, `mensagem_alerta` | Estado operacional, prioridade do operador (1–5) e mensagem resumida |

**Situações inseridas propositalmente** para testar o sistema: picos de latência, sobrecorrente em transmissores, manutenções programadas, uma **degradação gradual no Relé Orbital** (+1,6 ms por ciclo) e problemas de qualidade de dados.

**Limpeza com Pandas** (opção 1 do menu):

| Problema | Tratamento | Justificativa |
|---|---|---|
| 1 registro duplicado | `drop_duplicates()` | Contaria o mesmo evento duas vezes |
| 1 latência observada ausente | Registro descartado | Sem ela não há como avaliar o enlace |
| 1 qualidade de sinal ausente | Mediana da coluna | A mediana não é puxada por valores extremos |
| 1 corrente ausente | Mediana da coluna | Mesmo motivo |

Resultado: **119 registros válidos**. Após a limpeza, o sistema cria colunas derivadas: potência (`P = V·I`), resistência equivalente (`R = V/I`), erro absoluto, erro relativo e faixa de erro.

## 3. Indicadores de comunicação

| Indicador | Valor |
|---|---|
| Latência média dos enlaces internos | 39,29 ms |
| Latência média do enlace com a Terra | 13,06 min |
| Disponibilidade (registros com status ativo) | 84,0 % |
| Registros com latência acima do previsto | 28,6 % |
| Potência média dos transmissores por ciclo | 741,4 W (≈ 18,3 kWh por sol) |

O sistema também calcula, por módulo, a latência média, o erro absoluto médio e o erro relativo médio (com `groupby` do Pandas), além da potência e da energia gasta por sol em cada transmissor. Os transmissores de comunicação (Central, Interplanetária e Relé) consomem cerca de 170 W cada, bem mais que os outros módulos, o que já indica onde a gestão de energia tem mais impacto.

## 4. Análise de erros numéricos

### 4.1 Erro absoluto e erro relativo

- **Erro absoluto:** `|latência observada − latência prevista|`, em ms.
- **Erro relativo:** `erro absoluto / latência observada`.

O caso que mais justifica o erro relativo aparece nos próprios dados:

| Módulo | Erro absoluto médio | Erro relativo médio |
|---|---|---|
| Laboratório Geológico | 2,09 ms | 6,5 % |
| Comunicação Interplanetária | 428,89 ms | **0,055 %** |

Em valor absoluto, o enlace com a Terra parece 205 vezes pior. Em termos relativos, porém, ele é o **mais preciso** da colônia: errar 0,4 s em 13 minutos é desprezível. Sem o erro relativo, a equipe concentraria esforços no enlace errado.

![Erro relativo por módulo](graficos_ou_imagens/02_erro_relativo_por_modulo.png)

### 4.2 Quando o erro é aceitável ou preocupante

A equipe definiu três faixas de tolerância:

| Faixa | Erro relativo | Registros |
|---|---|---|
| Aceitável | até 10 % | 49 |
| Atenção | 10 % a 25 % | 39 |
| Crítico | acima de 25 % | 31 |

Dois cuidados surgiram da análise:

1. **Sentido do erro importa.** Dos 31 registros críticos, **23 são superestimativas** (latência observada menor que a prevista). Isso não é falha do enlace; indica apenas que a estimativa de engenharia é ruim para módulos próximos ao nó central. Por isso o SCIC só gera **alerta** quando a latência observada está **acima** da prevista.
2. **Denominador pequeno infla o erro relativo.** Comando Operacional tem o maior erro relativo médio (46,6 %), mas sua latência média é de apenas 29 ms: 9 ms de diferença já representam quase metade do valor. O erro relativo deve ser lido junto com o absoluto.

O nível de exigência também depende do módulo: em Suporte Médico e Comando, até a faixa de “atenção” merece revisão; em Habitação, é tolerável.

### 4.3 Ponto flutuante e arredondamento

- `0.1 + 0.2` resulta em `0.30000000000000004` no Python. Por isso as comparações usam `math.isclose`, e não `==`.
- Somar `0.1` dez vezes resulta em `0.9999999999999999`, e não em `1.0`. Isso acontece porque 0,1 não tem representação exata em binário (é uma dízima periódica em base 2), e o pequeno erro de cada soma vai se acumulando.
- A base armazena latências com 2 casas decimais. O erro de arredondamento, de no máximo 0,005 ms, é desprezível perto dos erros de previsão, que ficam na casa de vários milissegundos.

### 4.4 Simulação com o método de Euler

Para estimar quanto tempo um enlace leva para se recuperar após um pico, o sistema resolve numericamente a equação

`dL/dt = −k·(L − L_eq)`, com `k = 0,35/h`,

partindo do maior pico da base (Energia Solar, 121,69 ms) até o equilíbrio (42,38 ms, a mediana em operação normal). O resultado é comparado com a solução exata, `L(t) = L_eq + (L0 − L_eq)·e^(−kt)`:

| Passo h | L(12 h) por Euler | Erro absoluto | Erro relativo |
|---|---|---|---|
| 2,0 h | 42,44 ms | 1,13 ms | 2,60 % |
| 1,0 h | 42,83 ms | 0,74 ms | 1,69 % |
| 0,5 h | 43,16 ms | 0,41 ms | 0,93 % |
| 0,1 h | 43,48 ms | 0,09 ms | 0,20 % |

Ao dividir o passo pela metade, o erro também cai aproximadamente pela metade, o que caracteriza um método de 1ª ordem. Pelo modelo, o enlace volta a ficar a menos de 10 % do normal em cerca de **8,4 horas**. Se isso não acontecer, o operador deve acionar a rota redundante.

![Euler](graficos_ou_imagens/04_simulacao_euler.png)

## 5. Modelo simples de previsão

**Objetivo:** prever a latência dos **enlaces internos** a partir de carga de tráfego, distância, qualidade do sinal e potência. O enlace com a Terra fica de fora porque sua latência é determinada pela distância planetária, calculada por efemérides, e não pelo tráfego.

**Divisão dos dados (109 registros):** 60 % treino (65), 20 % validação (22) e 20 % teste (22), com `random_state = 42`.

Foram comparados dois modelos de **regressão linear** (`LinearRegression` do scikit-learn): o modelo A usa só a carga de tráfego, e o modelo B usa as 4 variáveis.

**Comparação na validação:**

| Modelo | MAE | MSE | RMSE | R² |
|---|---|---|---|---|
| A: regressão linear (só carga) | 9,96 | 443,04 | 21,05 | 0,51 |
| B: regressão linear (4 variáveis) | **7,54** | **247,18** | **15,72** | **0,73** |

O modelo B foi melhor em todas as métricas e foi o escolhido. Depois ele foi treinado de novo com treino + validação e avaliado **uma única vez** no teste. O conjunto de teste fica separado até o fim para que o resultado não seja "viciado" pela escolha do modelo.

**Resultado no teste:**

| Previsão | MAE | MSE | RMSE | R² |
|---|---|---|---|---|
| Estimativa de engenharia (campo da base) | 6,65 ms | 103,03 | 10,15 ms | 0,53 |
| Regressão linear (4 variáveis) | **5,13 ms** | **42,83** | **6,54 ms** | **0,81** |

O modelo reduz o MAE em **23 %** em relação à estimativa usada até então.

![Modelo](graficos_ou_imagens/03_modelo_real_vs_previsto.png)

### Interpretação das métricas

- **MAE = 5,1 ms:** em média, o modelo erra cerca de 5 ms por leitura. É a métrica mais fácil de comunicar aos operadores.
- **RMSE = 6,5 ms:** eleva os erros ao quadrado e, por isso, pesa mais os erros grandes.
- **RMSE/MAE:** no teste, a razão é 1,28, indicando erros parecidos entre si. Na **validação**, porém, a razão chega a **2,09**, porque os picos de latência caíram nesse conjunto. Uma diferença grande entre RMSE e MAE mostra que poucos registros têm erros muito maiores que os demais.
- **R² = 0,81:** o modelo explica 81 % da variação da latência. Isso **não** significa que ele seja perfeito: o maior erro individual no teste foi de 12,2 ms (2,4 vezes o MAE), e o modelo não consegue prever picos repentinos, que são justamente os eventos mais importantes.
- **Um único número não basta.** O mesmo modelo teve RMSE de 15,7 ms na validação e de 6,5 ms no teste. Com uma base pequena, o resultado depende bastante de quais registros caem em cada conjunto.
- **Coeficientes:** a qualidade do sinal tem o maior efeito (−82 ms por unidade: sinal pior significa mais latência), seguida da carga (+0,98 ms por Mbps). A potência praticamente não influencia e poderia ser removida.

Conclusão: o modelo é útil como **referência do comportamento normal**. Os picos são tratados pelos **alertas**, e não pela previsão.

## 6. Priorização de alertas com heap

**Representação:** cada alerta é um dicionário `{pontuacao, modulo, ciclo, codigo, erro_rel, mensagem}`. Vira alerta todo registro com `status = alerta` **ou** com latência observada acima da prevista e erro relativo maior que 25 %. Na base, são **14 alertas**.

**Critério de prioridade:**

```
pontuação = 10 × prioridade do operador (1–5)
          + 15 se o módulo é essencial
          + 20 se o status é "alerta"
          + 0,5 × erro relativo (%) (limitado a 100 %)
          + até 5 pontos por recência
```

**Estrutura:** a classe `HeapAlertas` implementa um **heap máximo** sobre uma lista. O pai do nó `i` fica em `(i−1)//2` e os filhos em `2i+1` e `2i+2`. A inserção usa **heapify-up** (método `subir`: o elemento sobe enquanto for maior que o pai) e a remoção usa **heapify-down** (método `descer`: a raiz é substituída pelo último elemento, que desce trocando de lugar com o maior filho).

**Seleção do mais urgente:** `ver_maior()` consulta a raiz em O(1); `remover_maior()` remove a raiz em O(log n). Os 5 primeiros atendimentos foram:

| # | Pontuação | Módulo | Ciclo | Mensagem |
|---|---|---|---|---|
| 1 | 115,2 | Controle Ambiental | 2 | Pico de latência (erro de 58 %) |
| 2 | 114,0 | Comando Operacional | 10 | Pico de latência |
| 3 | 112,3 | Energia Solar | 1 | Pico de latência |
| 4 | 104,2 | Comando Operacional | 4 | Pico de latência |
| 5 | 100,2 | Relé Orbital | 9 | Sobrecorrente no transmissor |

**Vantagem sobre uma lista simples:** com 10 mil alertas, atender os mil mais urgentes levou cerca de **0,008 s com o heap** e cerca de **0,74 s com uma lista** que procura o maior a cada atendimento (O(n) por busca). Os tempos mudam de um computador para outro, mas o heap continua sendo muito mais rápido. Em uma colônia onde leituras chegam continuamente, o heap mantém o alerta mais urgente sempre no topo, sem reordenar toda a fila a cada nova leitura.

## 7. Busca por prefixo com trie

A classe `Trie` indexa **nomes de módulos** (e cada palavra do nome), **códigos de sensor**, **palavras-chave das mensagens de alerta** e **comandos** cadastrados, totalizando 608 nós. Antes de entrar na trie, as chaves passam pela função `tirar_acentos`, que deixa tudo em minúsculas e sem acento, para que `com` encontre “Comunicação”. A busca desce a árvore letra por letra e depois usa uma função recursiva (`coletar`) para juntar tudo que está abaixo do nó do prefixo.

| Prefixo | Resultado |
|---|---|
| `com` | Comando Operacional, Comunicação Central, Comunicação Interplanetária e os comandos `comando_*` |
| `con` | Controle Ambiental, `consultar_status`, `consultar_alertas`, `controle_backup_dados` |
| `0x40` | Os 10 sensores do Suporte Médico |
| `pico` | Mensagem “Pico de latência no enlace” |

O enunciado sugere que `com` retornaria também “Controle”. Na trie isso não acontece, porque “Controle” começa com `con`. O prefixo comum aos dois é `co`.

**Por que a trie é adequada:** o custo para chegar ao nó do prefixo é O(m), em que m é o tamanho do prefixo, e não depende do número de registros. Uma busca linear compararia o prefixo com todas as cerca de 139 chaves. Como os códigos de sensor começam com o número do módulo, um prefixo como `0x80` lista instantaneamente todos os sensores do Controle Ambiental. No fluxo integrado (opção 9), a trie é usada justamente para localizar os sensores do módulo que está no topo do heap.

## 8. Dispositivos, bases numéricas e eletricidade

**Entrada (simulada):** sensores de latência (ping) nos roteadores, medidor de qualidade de sinal (RSSI), sensores de tensão e corrente nos transmissores e teclado do operador (cadastro manual).
**Saída:** terminal da sala de comando, gráficos e relatório, além de um LED ou sirene de alerta crítico (conceitual) acionado pelo topo do heap.
**Interfaces (conceituais):** rede cabeada e Wi-Fi entre módulos, rádio do Relé Orbital e antena para a Terra, USB ou Bluetooth para calibração de sensores.

**Bases numéricas:** o código `0x401D` do Suporte Médico é convertido manualmente, por somas de potências de 16, para **16413** em decimal e, por divisões sucessivas, para **01000000 00011101** em binário. Os resultados são conferidos com `int()` e `bin()`. Os dois primeiros dígitos hexadecimais (`40` = 64) identificam o módulo, e os dois últimos (`1D` = 29) identificam o sensor.

**Eletricidade:**
- Potência do transmissor: `P = V × I`. Por exemplo, o Relé Orbital no ciclo 1 tem 46,78 V × 3,183 A = **148,9 W**.
- Lei de Ohm: `R = V / I` = **14,70 Ω** de resistência equivalente.
- Energia por sol: os três transmissores de comunicação consomem cerca de 4,2 kWh cada.
- Detecção de **sobrecorrente**: 5 leituras ficaram mais de 25 % acima da corrente média do tipo de módulo, todas com status de alerta. Uma delas foi a do Relé Orbital no ciclo 9, com 4,65 A e 222 W.
- LED do painel: `R = (5 V − 2 V) / 0,02 A = 150 Ω`, dissipando 0,06 W.

## 9. Gerenciamento inteligente da comunicação

A discussão parte dos resultados do próprio SCIC:

- **Sensores e medidores inteligentes:** cada registro do JSON representa o pacote que um nó IoT de cada módulo enviaria por ciclo, com ping, RSSI, tensão e corrente.
- **Monitoramento contínuo:** comparar a latência observada com a prevista, ciclo a ciclo, separou o ruído normal (49 leituras aceitáveis) das anomalias (8 leituras acima do previsto com erro crítico). O monitoramento também revelou que a própria estimativa de engenharia precisava ser substituída pelo modelo.
- **Automação com supervisão:** o heap escolhe o alerta mais urgente e o SCIC **sugere** um comando, como `comando_redirecionar_rele` para picos ou `comando_reduzir_potencia` para sobrecorrente. A execução depende sempre da confirmação de um operador.
- **Redundância e armazenamento:** módulos essenciais com erro alto, como Comando Operacional e Controle Ambiental, devem ter rota alternativa pelo Relé Orbital e réplica de dados no Armazenamento. O sistema cruza essa decisão com a manutenção preditiva: como o relé está se degradando, a sugestão vem acompanhada de um aviso para confirmar a capacidade antes de redirecionar o tráfego.
- **Manutenção preditiva:** o SCIC ajusta uma reta (`np.polyfit`) ao **desvio** entre latência observada e prevista em operação normal. Usar o desvio, e não a latência bruta, evita confundir variações esperadas, como a mudança da distância Terra–planeta, com desgaste real. O **Relé Orbital** apresenta piora de **+1,48 ms por ciclo**, enquanto os demais módulos ficam abaixo de 0,2. A inspeção pode ser agendada **antes** de uma falha, mesmo sem nenhum alerta disparado pela tendência.

![Manutenção preditiva](graficos_ou_imagens/05_tendencia_rele_orbital.png)

- **Redes inteligentes e microrredes:** os transmissores consomem cerca de 18,3 kWh por sol. Os módulos de comunicação são os maiores consumidores, com cerca de 4,2 kWh por sol cada. Integrar o SCIC à microrrede permitiria reduzir a potência de transmissão em ciclos de baixo tráfego e avisar o barramento de energia sobre leituras de sobrecorrente antes que haja sobrecarga.

## 10. Reflexão social, cultural e sustentável

- **Uso eficiente da comunicação e sustentabilidade:** os dados mostram que os transmissores de comunicação concentram a maior parte do consumo de energia. Um sistema que prioriza alertas e ajusta a potência conforme a demanda reduz desperdício de energia, um recurso escasso em uma colônia. A manutenção preditiva também prolonga a vida útil dos equipamentos e evita trocas emergenciais.
- **Conhecimentos tradicionais e respeito à natureza:** muitos povos indígenas manejam recursos observando ciclos naturais e retirando apenas o necessário, com atenção ao longo prazo. O SCIC adota uma lógica parecida ao acompanhar tendências ao longo dos ciclos, em vez de reagir só a crises, e ao tratar a energia como algo a ser preservado para as próximas gerações da colônia.
- **Transparência nas decisões baseadas em dados:** a pontuação do heap é uma fórmula aberta e explicada neste relatório, e não uma caixa-preta. Qualquer membro da colônia pode entender por que o Controle Ambiental foi atendido antes da Habitação.
- **Responsabilidade humana:** o modelo tem R² de 0,81, mas não prevê picos súbitos. Por isso o SCIC apenas sugere ações; quem decide é a equipe de operação. O caso do Relé Orbital mostra o risco de automatizar sem supervisão: uma regra fixa teria redirecionado o tráfego para um equipamento em degradação.
- **Diversidade e linguagem:** as prioridades consideram a função do módulo (suporte à vida, saúde), e não quem o ocupa. Nenhuma Habitação é privilegiada sobre outra. As mensagens do sistema usam linguagem técnica e neutra, e a busca ignora acentos, para que pessoas com teclados ou hábitos de escrita diferentes encontrem os mesmos registros.

## 11. Limitações e possíveis melhorias

**Limitações:**
- Os dados são **simulados** e a base é pequena (119 registros), por isso as métricas variam conforme a divisão treino/teste.
- O modelo é linear e não antecipa picos súbitos.
- Os pesos da pontuação do heap foram definidos pela equipe, sem calibração com especialistas.
- O enlace com a Terra é previsto apenas por efemérides simplificadas.
- Os tempos de comparação entre heap e lista variam conforme o computador.

**Melhorias:**
- Coletar mais ciclos e dados reais de sensores.
- Incluir a latência do ciclo anterior como variável do modelo.
- Testar outros modelos e comparar com métricas como AIC/BIC ou com Grid Search.
- Usar validação cruzada para ter métricas mais estáveis com poucos dados.
- Atualizar a fila de prioridade em tempo real, conforme as leituras chegam.
- Revisar os pesos da pontuação com a equipe médica e de suporte à vida.
- Criar um painel de supervisão.
- Integrar com a microrrede para controle automático de potência, sempre sujeito à aprovação humana.
