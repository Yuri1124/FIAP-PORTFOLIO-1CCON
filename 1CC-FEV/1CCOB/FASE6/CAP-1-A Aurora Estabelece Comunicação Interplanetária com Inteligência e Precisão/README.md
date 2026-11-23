# SCIC — Sistema de Comunicação Interplanetária da Colônia Aurora Siger

Protótipo em Python que organiza os dados operacionais e de comunicação da colônia Aurora Siger. O sistema calcula o erro das previsões de latência, treina e avalia um modelo simples de previsão, prioriza alertas críticos com **heap**, busca registros por prefixo com **trie** e relaciona tudo com dispositivos de entrada e saída, bases numéricas e eletricidade básica.

Equipe: _[nomes e RMs]_

## Arquivos da entrega

| Arquivo | Conteúdo |
|---|---|
| `codigo_fonte.py` | **Arquivo principal**: menu no terminal com todas as funcionalidades |
| `dados_aurora_siger.json` | Base simulada: 12 módulos × 10 ciclos (121 registros) |
| `relatorio_tecnico.md` | Relatório técnico completo, com os resultados da execução |
| `README.md` | Este arquivo |
| `link_video.txt` | Link do vídeo no YouTube (não listado) |
| `graficos_ou_imagens/` | Gráficos gerados pelas opções 4, 5 e 10 do menu |
| `gerar_dados.py` | Script auxiliar que gerou o JSON (semente fixa). **Não** é necessário executá-lo |
| `saida_demo.txt` | Exemplo de saída da opção 11 (demonstração completa) |
| `roteiro_video.md` | Roteiro sugerido para o vídeo de 5 minutos |

## Dependências

Python 3.9 ou superior e as bibliotecas estudadas na fase:

```bash
pip install numpy pandas matplotlib seaborn scikit-learn
```

O módulo `json` já vem com o Python. Nenhuma biblioteca adicional foi usada. O heap e a trie foram implementados pela equipe, sem usar `heapq` nem bibliotecas prontas.

## Como executar

```bash
python codigo_fonte.py
```

Mantenha `dados_aurora_siger.json` na mesma pasta de `codigo_fonte.py` e execute o comando dentro dessa pasta.

Para ver tudo funcionando de uma vez, escolha a **opção 11 (demonstração completa)**.

## Menu

| Opção | Funcionalidade |
|---|---|
| 1 | Recarregar a base (com limpeza de duplicados e valores vazios) **ou cadastrar** um novo registro, com opção de salvá-lo no JSON |
| 2 | Consultar registros: resumo geral, busca por módulo ou por status |
| 3 | Indicadores de comunicação, erro absoluto e relativo, faixas de tolerância e ponto flutuante |
| 4 | Simulação da recuperação do enlace pelo método de Euler, comparada com a solução exata |
| 5 | Modelo de previsão de latência (regressão linear), treino/validação/teste e métricas MAE, MSE, RMSE e R² |
| 6 | Priorização de alertas com heap máximo (heapify-up e heapify-down) e comparação com lista comum |
| 7 | Busca por prefixo com trie (módulos, códigos de sensor, alertas e comandos) |
| 8 | Dispositivos de entrada e saída, conversão hexadecimal/decimal/binário, P = V·I e lei de Ohm |
| 9 | **Analisar alertas de comunicação**: junta dados, erros, heap e trie e sugere uma ação |
| 10 | Análise final, gerenciamento inteligente (manutenção preditiva, redundância, microrrede) e gráficos |
| 11 | Demonstração completa (roda as opções 2 a 10 em sequência) |
| 0 | Sair |

### Exemplos de uso

- Na opção 7, digite `com` para listar Comando Operacional, Comunicação Central, Comunicação Interplanetária e os comandos `comando_*`.
- Ainda na opção 7, digite `0x40` para listar todos os sensores do Suporte Médico.
- A opção 9 mostra o alerta mais urgente, os sensores desse módulo e a ação sugerida para o operador confirmar.

## Observações

- Os dados são **simulados** (veja `gerar_dados.py`), e os resultados são sempre os mesmos.
- Os tempos da comparação entre heap e lista mudam de um computador para outro.
- Os gráficos não abrem em janela: eles são salvos na pasta `graficos_ou_imagens/`.
