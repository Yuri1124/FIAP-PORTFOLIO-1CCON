# Teste de facilidade de uso

> Os resultados abaixo vêm de uma simulação com 6 personas, com perfis diferentes para aplicar o roteiro de tarefas.

## Como foi aplicado

Cada persona usou o programa (`python src/sistema.py`) e fez as 6 tarefas do roteiro, sem ajuda. Para cada tarefa foram registrados se concluiu, o tempo, as tentativas extras e as dificuldades. No fim, cada persona respondeu um questionário de 1 a 5.

## Personas (sem dados pessoais)

| Persona | Faixa etária | Familiaridade com computador |
|---|---|---|
| Stefany | 18-29 | alta |
| Tatiana | 40-49 | média |
| Gabriel | 18-29 | alta |
| Marina | 50+ | baixa |
| João | 30-39 | média |
| Mateus | 18-29 | alta |

## Tarefas

| Nº | Tarefa | Concluída quando |
|---|---|---|
| 1 | Descubra se a nova carteira de identidade é paga. | Responde que a primeira via é gratuita |
| 2 | Usando só o menu de temas, encontre o número do SAMU. | Chega em Direitos > Emergências e encontra o 192 |
| 3 | Você foi demitido: até quando pode pedir o seguro-desemprego? | Encontra "até o 120º dia" |
| 4 | Depois da tarefa 3, abra um assunto relacionado. | Usa a opção "Quer ver um assunto relacionado?" |
| 5 | Pergunte como tirar passaporte e diga o que o sistema respondeu. | Entende que o sistema não tem essa informação |
| 6 | Diga de onde veio a informação da tarefa 1 e quando foi verificada. | Aponta a fonte e a data |

## Resultados por persona

Formato de cada célula: concluiu (S/N) · tempo em segundos · tentativas extras.

| Persona | T1 | T2 | T3 | T4 | T5 | T6 |
|---|---|---|---|---|---|---|
| Stefany | S · 25 · 0 | S · 30 · 0 | S · 28 · 0 | S · 12 · 0 | S · 15 · 0 | S · 20 · 0 |
| Tatiana | S · 40 · 0 | S · 55 · 1 | S · 45 · 0 | **N** · 60 · 2 | S · 20 · 0 | S · 35 · 0 |
| Gabriel | S · 20 · 0 | S · 25 · 0 | S · 30 · 0 | S · 10 · 0 | S · 12 · 0 | S · 18 · 0 |
| Marina | S · 70 · 1 | **N** · 120 · 3 | S · 80 · 1 | **N** · 90 · 2 | S · 30 · 0 | S · 60 · 1 |
| João | S · 35 · 0 | S · 45 · 1 | S · 40 · 0 | S · 20 · 0 | S · 18 · 0 | **N** · 50 · 1 |
| Mateus | S · 22 · 0 | S · 28 · 0 | S · 26 · 0 | S · 15 · 0 | S · 14 · 0 | S · 22 · 0 |

## Resultados por tarefa

| Nº | Concluíram | Tempo médio (s) | Dificuldade observada |
|---|---|---|---|
| 1 | 6 de 6 | 35,3 | Marina digitou "rg" sozinho na primeira tentativa e recebeu a resposta, mas demorou para achar "gratuita" no texto. |
| 2 | 5 de 6 | 50,5 | Tarefa mais demorada. Marina não sabia em qual tema estaria "emergência" e acabou digitando a pergunta em vez de usar o menu. Tatiana entrou primeiro em "Serviços públicos". |
| 3 | 6 de 6 | 41,5 | Sem dificuldades relevantes; a resposta longa exigiu leitura com calma. |
| 4 | 4 de 6 | 34,5 | Tatiana e Marina não perceberam que a lista "Quer ver um assunto relacionado?" pedia um número e digitaram uma pergunta nova. |
| 5 | 6 de 6 | 18,2 | Todas entenderam que o sistema não tinha a informação. |
| 6 | 5 de 6 | 34,2 | João encontrou a fonte, mas não a data. A linha "Verificado em" fica no meio de uma resposta longa. |

## Questionário (1 = discordo totalmente, 5 = concordo totalmente)

| Afirmação | Média |
|---|---|
| Foi fácil encontrar o que eu procurava. | 4,33 |
| A linguagem das respostas foi clara. | 4,50 |
| Ficou claro de onde veio cada informação. | 4,33 |
| Quando o sistema não sabia, entendi o que fazer. | 4,33 |
| Eu usaria um assistente assim de novo. | 4,50 |

## Indicadores

- **Taxa de conclusão:** 32 de 36 tarefas = **88,9%**
- **Tempo médio por tarefa:** **35,7 s**
- **Nota média de facilidade:** **4,4 de 5**

## Interpretação

- As tarefas por pergunta (1, 3 e 5) foram concluídas por todos. O aviso de "não tenho essa informação" foi entendido sem dificuldade.
- Os problemas se concentraram na navegação: achar o tema certo no menu (tarefa 2) e entender que a lista de assuntos relacionados pede um número (tarefa 4). Isso pesou mais para quem tem menos familiaridade com computador.
- A data de verificação existe em toda resposta, mas pode passar despercebida em respostas longas (tarefa 6).

## Melhorias sugeridas pelo teste

1. Escrever "Digite o número do assunto (ou 0 para voltar)" na lista de assuntos relacionados.
2. Mostrar exemplos de assuntos ao lado de cada tema do menu (ex.: "Direitos: consumidor, denúncias, emergências...").
3. Destacar fonte e data em um bloco separado no fim da resposta.

## Limitações

O teste foi simulado com personas fictícias, então mostra onde o sistema provavelmente gera dúvidas, mas não mede o comportamento de pessoas reais. O próximo passo é repetir o roteiro com usuários reais e comparar os resultados.
