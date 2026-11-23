# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/">
  <img src="../../../assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" width="40%">
</a>
</p>

<br>

# Citizen Assist AI

## Nome do grupo

Equipe 16 (projeto individual)

## 👨‍🎓 Integrante:
- Yuri Eurich - RM 569285

## 👩‍🏫 Professores:

### Tutor(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

## 📜 Descrição

### Problema e público

Muitas pessoas têm dificuldade para encontrar orientações confiáveis sobre documentos, serviços públicos e direitos, porque as informações ficam espalhadas em vários sites e usam termos difíceis. O projeto pensa principalmente em quem tem pouca familiaridade com portais do governo: jovens tirando os primeiros documentos, trabalhadores demitidos, famílias de baixa renda e pessoas que precisam de um canal de denúncia.

### Solução

O Citizen Assist AI é um assistente de texto em Python. A pessoa pode digitar uma pergunta ou escolher um tema no menu, e o programa procura a orientação em uma base de dados com informações conferidas em sites oficiais. A resposta mostra um resumo, o passo a passo, a fonte, o link e a data em que a informação foi verificada. Quando a pergunta não está na base, o assistente avisa em vez de inventar uma resposta.

### Temas

| Tema | Assuntos |
|---|---|
| Documentos | CIN (novo RG), CPF, situação do CPF, primeiro título de eleitor, 2ª via do título, Carteira de Trabalho Digital |
| Serviços públicos | Conta gov.br, Cartão SUS, Cadastro Único, seguro-desemprego |
| Direitos e orientações comunitárias | Consumidor.gov.br, Disque 100, Ligue 180, números de emergência, Defensoria Pública, Lei de Acesso à Informação |

## 📁 Estrutura de pastas

- **`data/`**
  - `base_conhecimento.json`: as 16 orientações e a lista de temas
  - `perguntas_teste.json`: as 24 perguntas usadas nos testes
- **`docs/`**
  - `prompts.md`: os dois modelos de resposta e a comparação entre eles
  - `resultados_testes.csv`: resultado de cada teste
  - `teste_usabilidade.md`: roteiro e resultado do teste com usuário
  - `uso_ia.md`: como a IA foi usada no desenvolvimento
- **`src/`**
  - `sistema.py`: programa principal (leitura da base, respostas e menu)
  - `busca.py`: funções de busca
  - `avaliacao.py`: roda os testes e calcula os indicadores
- **`README.md`**: este arquivo

## Base de conhecimento

A base fica em `data/base_conhecimento.json`. Cada registro tem:

| Campo | Descrição |
|---|---|
| `id` | código do registro (ex.: `DOC-01`) |
| `tema` e `subtema` | onde o assunto fica no menu |
| `titulo` | nome do assunto |
| `palavras_chave` | palavras usadas na busca |
| `perguntas_exemplo` | jeitos comuns de perguntar |
| `orientacao` | resumo da orientação |
| `passos` | passo a passo |
| `referencia` | nome da fonte e link |
| `data_verificacao` | data em que a fonte foi conferida |
| `requer_confirmacao` e `aviso` | avisos para a pessoa confirmar no canal oficial |
| `relacionados` | assuntos ligados a este |

Os campos `id`, `tema`, `subtema`, `titulo`, `palavras_chave`, `orientacao`, `referencia` e `data_verificacao` são obrigatórios. Se algum faltar, o registro é ignorado e o programa mostra um aviso. O programa também trata arquivo inexistente, vazio ou com JSON inválido.

Para adicionar ou corrigir uma orientação, basta editar o JSON e usar a opção 6 do menu ("Recarregar a base"), sem mexer no código.

As informações foram conferidas em 18/11/2026 em fontes como gov.br, Receita Federal, TSE, Ministério da Saúde, Ministério dos Direitos Humanos, Ministério da Justiça e a Constituição Federal. O link de cada uma está no próprio registro.

## Estruturas de dados e busca

- **Dicionário `id -> registro`**: para achar um registro direto pelo código.
- **Índice invertido** (dicionário `palavra -> conjunto de ids`): mostra quais registros têm cada palavra, assim a busca não precisa olhar a base inteira.
- **Hierarquia tema → subtema → registro**: usada no menu "Navegar por temas".
- **Grafo de assuntos relacionados**: cada registro é um nó e o campo `relacionados` cria as ligações. Ex.: *Seguro-desemprego* está ligado à *Carteira de Trabalho Digital*, que está ligada à *Conta gov.br*, porque o pedido é feito no app da carteira, que usa a conta gov.br. Depois de cada resposta, o programa oferece esses assuntos para continuar. No mapa da base (opção 3), uma busca em largura (BFS) mostra os assuntos com ligação direta e indireta.

**Como a busca funciona** (`src/busca.py`):

1. Deixa a pergunta em minúsculas, tira acentos e pontuação.
2. Remove palavras que não ajudam (como, meu, de...), corta terminações simples para juntar formas parecidas (*denuncio* e *denunciar*) e acrescenta alguns sinônimos (*rg* → *identidade*).
3. Usa o índice para pegar só os registros que têm alguma palavra da pergunta.
4. Dá pontos para cada registro:
   - se todas as palavras de uma palavra-chave estão na pergunta: 2 pontos + 1 por palavra;
   - para cada palavra em comum: 2 pontos se só aquele registro tem a palavra, 1 ponto se outros também têm.
5. Decide a resposta:
   - pergunta vazia ou sem palavras → entrada inválida;
   - uma palavra só que aparece em mais de um registro (ex.: "cpf") → pergunta ambígua, o programa mostra as opções;
   - maior pontuação menor que 3 → sem resposta;
   - dois ou mais registros com pontuação próxima (85% da maior ou mais) → pergunta ambígua;
   - se não → mostra o registro com mais pontos.

## Modelos de resposta (prompts)

O projeto não usa um modelo de IA externo. Os prompts são instruções que o código segue para montar a resposta, e podem ser trocados na opção 4 do menu:

- **Modelo A (direto):** só a orientação e a fonte.
- **Modelo B (estruturado):** título, resumo, passo a passo, fonte, link, data de verificação, aviso, assuntos relacionados e aviso de que não é canal oficial. Quando não tem resposta, explica o motivo e sugere temas.

Nas 24 perguntas de teste, o modelo B atendeu todos os itens pedidos no enunciado (112 de 112) e o modelo A atendeu 32 de 112. O modelo B é mais longo, mas é mais claro e consistente, por isso é o padrão. Detalhes em `docs/prompts.md`.

## Testes e resultados

Os testes estão em `data/perguntas_teste.json` e rodam com `python src/avaliacao.py`. São 24 perguntas: 6 diretas, 10 escritas de outro jeito, 3 fora dos temas, 4 de limitação (vazia, só "???", e duas ambíguas) e 1 com dado pessoal.

| ID | Pergunta | Esperado | Obtido | Resultado |
|---|---|---|---|---|
| T01 | Como tiro a nova carteira de identidade? | DOC-01 | DOC-01 | Acerto |
| T02 | Como faço meu CPF? | DOC-02 | DOC-02 | Acerto |
| T03 | Qual o número do SAMU? | DIR-04 | DIR-04 | Acerto |
| T04 | Como peço o seguro-desemprego? | SER-04 | SER-04 | Acerto |
| T05 | Onde me inscrevo no Cadastro Único? | SER-03 | SER-03 | Acerto |
| T06 | Como funciona o Disque 100? | DIR-02 | DIR-02 | Acerto |
| T07 | Perdi meu título, consigo outro? | DOC-05 | DOC-05 | Acerto |
| T08 | Fui mandado embora, tenho direito a algum dinheiro do governo? | SER-04 | sem resposta | **Erro** |
| T09 | Quero reclamar de uma loja que não trocou meu produto | DIR-01 | DIR-01 | Acerto |
| T10 | Não tenho grana pra pagar advogado | DIR-05 | DIR-05 | Acerto |
| T11 | o rg novo é de graça? | DOC-01 | DOC-01 | Acerto |
| T12 | minha vizinha apanha do marido, onde denuncio? | DIR-03 | DIR-02 | **Erro** |
| T13 | Como vejo o número do meu cartão do SUS? | SER-02 | SER-02 | Acerto |
| T14 | meu cpf ta suspenso | DOC-03 | DOC-03 | Acerto |
| T15 | Como peço uma informação para um órgão do governo? | DIR-06 | DIR-06 | Acerto |
| T16 | Pra quem ligo quando tem fogo em casa? | DIR-04 | DIR-04 | Acerto |
| T17 | Como tiro passaporte? | sem resposta | sem resposta | Acerto |
| T18 | Qual a previsão do tempo para amanhã? | sem resposta | sem resposta | Acerto |
| T19 | Como renovar a CNH? | sem resposta | sem resposta | Acerto |
| T20 | (vazia) | inválida | inválida | Acerto |
| T21 | ??? | inválida | inválida | Acerto |
| T22 | cpf | ambígua | ambígua | Acerto |
| T23 | título | ambígua | ambígua | Acerto |
| T24 | meu cpf é 123.456.789-09, ele está suspenso? | DOC-03 | DOC-03 | Acerto |

**Indicadores:**

- Taxa de acerto: **22 de 24 = 91,7%**
- Tempo médio de consulta: **cerca de 0,02 ms** (média de 100 execuções de cada pergunta; muda um pouco a cada vez que roda)
- Facilidade de uso: *preencher depois do teste com usuário (ver `docs/teste_usabilidade.md`)*

**Interpretação:**

- Acertou todas as perguntas diretas, as fora dos temas e os casos de limitação. Nas perguntas fora da base, o programa não inventou resposta.
- Na primeira versão da busca, a taxa era de 17 de 24 (70,8%). Ela errava, por exemplo, "meu cpf ta suspenso", porque procurava a expressão "cpf suspenso" exatamente igual. Mudei a busca para aceitar as palavras da palavra-chave em qualquer posição, cortar terminações das palavras e dar mais peso a palavras que só aparecem em um registro.
- Os 2 erros que sobraram são de linguagem informal. "Mandado embora" não está na base, então o programa respondeu que não sabia, o que é um erro sem risco. Já a pergunta sobre violência doméstica foi para o Disque 100 em vez do Ligue 180. O Disque 100 também recebe denúncias e a resposta manda ligar 190 em caso de perigo, mas o canal mais adequado seria o 180, então esse é o erro mais importante para corrigir.

**Limitações da avaliação:** usei as mesmas perguntas para ajustar a busca e para medir o resultado, então a taxa final provavelmente está um pouco otimista. Além disso, 24 perguntas é pouco: cada erro muda a taxa em cerca de 4 pontos.

## Exemplos

Pergunta com resposta:

```text
Pergunta: Como peço o seguro-desemprego?
== Solicitar o seguro-desemprego ==
Resumo: O trabalhador formal dispensado sem justa causa pode pedir o seguro-desemprego
do 7º ao 120º dia após a demissão (para empregado doméstico, do 7º ao 90º dia). [...]
Passo a passo:
  1. Pegue com o empregador o número do requerimento do seguro-desemprego.
  2. Entre no app Carteira de Trabalho Digital ou no gov.br.
  3. Vá em 'Benefícios' > 'Seguro-desemprego' e conclua o pedido.
  4. Acompanhe o andamento pelo mesmo canal.
Fonte: gov.br - Solicitar o Seguro-Desemprego
Link: https://www.gov.br/pt-br/servicos/solicitar-o-seguro-desemprego
Verificado em: 18/11/2026
Atenção: O direito depende de tempo mínimo trabalhado e outras condições. Confirme as
regras no serviço oficial antes de contar com o benefício.
Próximos assuntos: [DOC-06] Obter a Carteira de Trabalho Digital; [SER-01] Criar a conta
gov.br e entender os níveis; [DIR-05] Conseguir assistência jurídica gratuita (Defensoria Pública)
Este assistente não é um canal oficial e não substitui o atendimento do órgão responsável.
```

Pergunta ambígua:

```text
Pergunta: cpf
Sua pergunta combina com mais de um assunto. Qual deles você procura?
  [DOC-02] Fazer a inscrição no CPF
  [DOC-03] Consultar ou regularizar a situação do CPF
Digite o código (ex.: DOC-01) ou escreva a pergunta de outro jeito.
```

Pergunta fora da base:

```text
Pergunta: Como tiro passaporte?
Não tenho uma orientação verificada sobre isso, então prefiro não responder para não
passar informação errada.
Assuntos parecidos: [DOC-01] Emitir a Carteira de Identidade Nacional (CIN); [...]
Temas disponíveis: Documentos, Serviços públicos, Direitos e orientações comunitárias.
Para outros assuntos, procure o portal gov.br ou o órgão responsável.
```

Entradas inválidas:

```text
Pergunta: (Enter sem digitar nada)
Você não digitou nenhuma pergunta.
Exemplo: 'Como faço meu CPF?' ou escolha um tema no menu.

Escolha: 9
Opção inexistente: '9'.
```

## Clareza, acessibilidade, privacidade e informação não oficial

- As respostas usam frases curtas e passo a passo numerado.
- A interface é só texto e funciona com números, o que ajuda quem usa leitor de tela. Dá para chegar na mesma informação pela pergunta ou pelo menu.
- O programa não pede dados pessoais. Se a pessoa digitar CPF, e-mail ou telefone, esses dados são apagados antes da busca, e nenhuma pergunta é salva.
- Toda resposta avisa que o assistente não é um canal oficial, e cada orientação mostra a fonte e a data de verificação.

## 📎 Links e Observações

### 🔗 Links do Projeto

* **[Vídeo de apresentação no YouTube](https://youtu.be/NR2zihVkgIQ)** - demonstração do funcionamento e explicação do projeto.

### 🧠 Decisões Técnicas

> Usei só Python, sem bibliotecas externas, para facilitar a execução. A base fica em JSON para poder ser editada sem mexer no código. Escolhi uma busca por pontuação em vez de um modelo de IA porque o resultado é previsível, dá para explicar e não corre o risco de inventar informação. O uso de IA no desenvolvimento está descrito em `docs/uso_ia.md`.

### 📢 Observações Gerais

* **Participação na Competição:** [ ] Sim, aceito participar / [ ] Não vou participar.

## 🔧 Como executar o código

**Pré-requisitos:** Python 3.8 ou mais recente e Git. Não é preciso instalar bibliotecas: o projeto usa só a biblioteca padrão do Python.

1. Clone o repositório e entre na pasta do projeto:

```bash
git clone https://github.com/SEU_USUARIO/FIAP-PORTFOLIO-1CCON.git
cd FIAP-PORTFOLIO-1CCON/1CC-XXX/TURMA/GLOBAL-SOLUTION-2
```

2. Execute o assistente:

```bash
python src/sistema.py
```

3. (Opcional) Rode os testes e recalcule os indicadores:

```bash
python src/avaliacao.py
```

No Linux ou macOS, use `python3` se o comando `python` não funcionar.

## Conclusões, limitações e melhorias

O projeto mostrou que dá para montar um assistente útil só com listas, dicionários, leitura de arquivos, condicionais e um algoritmo de busca simples, desde que a base seja bem organizada e o programa saiba dizer quando não tem a resposta.

**Limitações:** a base tem só 16 orientações e regras que mudam por estado aparecem apenas como aviso. A busca depende das palavras cadastradas e não entende bem gírias, e as informações precisam ser revisadas de tempos em tempos.

**Melhorias possíveis:**

1. Adicionar mais sinônimos e expressões populares (ex.: "mandado embora") e priorizar o Ligue 180 quando a pergunta falar de violência contra mulher.
2. Guardar, sem dados pessoais, as perguntas que ficaram sem resposta, para saber quais temas incluir.
3. Avisar quando um registro estiver há muito tempo sem verificação.
4. Testar com perguntas novas, escritas por outras pessoas.

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI">TEMPLATE - FIAP PORTFÓLIO AI</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">FIAP</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
