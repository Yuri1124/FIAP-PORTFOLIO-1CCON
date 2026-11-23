# Telemetria - Missão Marte

Este repositório contém o desenvolvimento de um sistema automatizado de telemetria e análise de dados para uma simulação de missão espacial a Marte. O projeto abrange desde o processamento de dados brutos de sensores até a tomada de decisão para decolagem, incluindo análises de consumo energético e avaliação de riscos operacionais.

## Sobre o Projeto

Desenvolvido como uma Atividade Integradora, o sistema atua como o núcleo de controle de missão de uma nave espacial. O algoritmo avalia parâmetros críticos em tempo real e emite um veredito de segurança ("PRONTO PARA DECOLAR" ou "DECOLAGEM ABORTADA"), garantindo a integridade da tripulação e do equipamento.

### Principais Funcionalidades

* **Processamento de Telemetria:** Leitura e estruturação de dados históricos de sensores (temperatura, pressão de tanques, status de módulos) a partir de arquivos `.csv`.
* **Algoritmo de Verificação (GO/NO-GO):** Lógica de validação baseada em limites de segurança predefinidos para sistemas vitais (Propulsão, Suporte de Vida, etc.).
* **Análise Energética:** Cálculo de autonomia da nave, considerando a capacidade total das baterias, perdas energéticas do sistema e estimativa de consumo durante a decolagem e cruzeiro.
* **Visualização de Dados:** Geração de gráficos de evolução da capacidade energética ao longo dos dias de missão.
* **Avaliação de Risco:** Integração de análise assistida por Inteligência Artificial para classificar anomalias (como a depleção multissistêmica de pressão detectada nos dados) e sugerir ações corretivas.

## Tecnologias Utilizadas

O projeto foi construído no ecossistema de dados do Python:

* **Python 3.x**
* **Pandas:** Para ingestão, limpeza e manipulação do dataset de telemetria.
* **Matplotlib:** Para a renderização dos gráficos de análise energética.
* **Jupyter Notebook:** Como ambiente interativo para desenvolvimento e documentação executável do código.

## Estrutura do Repositório

* `telemetria_marte.ipynb`: O notebook principal contendo todo o script Python, desde a importação do CSV até a geração dos gráficos de energia.
* `nave_marte.csv`: O dataset simulado com os registros cronológicos dos sensores da nave.
