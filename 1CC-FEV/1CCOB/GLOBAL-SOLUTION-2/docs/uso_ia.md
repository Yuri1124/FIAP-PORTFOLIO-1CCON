# Uso de IA

## Ferramenta

Usei o **Claude** (Anthropic) como apoio durante o desenvolvimento. O programa em si não usa IA: as respostas saem só da base `data/base_conhecimento.json`, escolhidas pela busca em `src/busca.py`.

## Onde a IA ajudou

- Encontrar páginas oficiais sobre cada tema e resumir o conteúdo.
- Sugerir como organizar o código e a busca.
- Escrever e comparar os dois modelos de prompt.
- Sugerir perguntas de teste.
- Revisar os textos.

## Validação que fiz

1. **Conferi as fontes.** Comparei cada orientação com o site oficial do campo `referencia`. Encontrei e corrigi dois erros nos textos sugeridos:
   - Cartão SUS: o texto dizia que dava para fazer o cartão pelo app Meu SUS Digital. O site do Ministério da Saúde diz que o app não emite cartão novo; isso é feito em uma unidade de saúde.
   - Conta gov.br: o texto dizia que a CIN levava ao nível ouro. O site oficial fala em validação biométrica em base do governo ou certificado digital.
2. **Rodei os testes.** A primeira versão da busca acertava 17 de 24 perguntas. Ajustei a busca e cheguei a 22 de 24. Deixei os 2 erros registrados no README em vez de mudar a base só para acertar o teste.
3. **Testei o programa à mão**, incluindo entrada vazia, opção inexistente e arquivo da base ausente, vazio ou com erro.
4. **Entendi o código** e consigo explicar cada parte.

## Cuidados

A IA pode errar ou usar informação desatualizada. Por isso cada orientação tem link e data de verificação, e a base deve ser revisada de tempos em tempos.
