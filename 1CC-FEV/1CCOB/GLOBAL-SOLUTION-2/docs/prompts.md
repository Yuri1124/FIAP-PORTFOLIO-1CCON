# Modelos de prompt

O projeto não chama nenhuma IA externa. Os prompts abaixo são as instruções que o código segue para montar as respostas (funções `resposta_modelo_a` e `resposta_modelo_b` em `src/sistema.py`).

## Modelo A - direto

> Você é um assistente de informações. Responda à pergunta usando a orientação encontrada na base e informe a fonte ao final.

Exemplo:

```text
O trabalhador formal dispensado sem justa causa pode pedir o seguro-desemprego do 7º ao 120º dia [...]
Fonte: gov.br - Solicitar o Seguro-Desemprego (https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego)
```

Sem resposta: `Não encontrei resposta para essa pergunta.`

## Modelo B - estruturado (usado por padrão)

> Você é o Citizen Assist AI, um assistente de orientação cidadã não oficial. Use somente a base verificada. Responda com: título, resumo simples, passo a passo, fonte com link, data da verificação, aviso quando precisar confirmar e assuntos relacionados. Nunca invente prazos ou documentos e não peça dados pessoais. Se a pergunta não estiver na base, diga isso e sugira os temas disponíveis.

O exemplo completo está no README.

## Comparação

Para comparar, o `src/avaliacao.py` confere se cada resposta tem os itens pedidos no enunciado:

- quando há resposta: fonte, link, data de verificação, aviso, assuntos relacionados e passo a passo;
- quando não há resposta (vazia, ambígua ou fora da base): se explica o problema e se sugere outro caminho.

| | Modelo A | Modelo B |
|---|---|---|
| Itens atendidos nas 24 perguntas | 32 de 112 | 112 de 112 |
| Tamanho da resposta do seguro-desemprego | 57 palavras | 172 palavras |

**Conclusão:** o modelo B é maior, mas fica mais claro porque separa resumo, passos e fonte em linhas diferentes. Ele também sempre mostra a data e o aviso de canal não oficial. A maior diferença aparece quando o programa não tem a resposta: o modelo A só diz "Não encontrei", e o B explica o motivo e mostra outros temas. Por isso o B é o padrão.

Essa comparação só verifica se os itens aparecem na resposta, não se a pessoa entendeu melhor. Para isso existe o teste com usuário (`docs/teste_usabilidade.md`).
