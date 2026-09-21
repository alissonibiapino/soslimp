# SOSLimp PDV

## Sobre o Projeto

Este projeto é um trabalho acadêmico desenvolvido por estudantes da Fatec Ipiranga, como parte das disciplinas do curso de Big Data para Negócios. Ele representa a aplicação prática de conhecimentos adquiridos em diversas áreas, incluindo:

-   **Bancos de Dados Relacionais (PostgreSQL) e não relacionais (Neo4j)**: Para a gestão transacional de vendas, produtos, categorias, explorar relações entre produtos e vendas, visando funcionalidades de recomendação.
-   **Estatística e Probabilidade**: Aplicadas na simulação de dados e na análise de padrões de vendas.
-   **Gestão de Negócios**: Refletida na modelagem do sistema de Ponto de Venda (PDV) e nas funcionalidades que apoiam a operação de uma empresa real.
-   **Engenharia de Software**: Evidenciada na arquitetura do sistema, organização do código e uso de boas práticas de desenvolvimento.
-   **Inteligência Artificial**: Integrada para fornecer recomendações de produtos e prever tendências de demanda, otimizando a experiência de venda e a gestão de estoque.

A principal ideia por trás do SOSLimp PDV é unir todos esses conhecimentos em uma lógica de negócios coesa, simulando um sistema de PDV para a empresa SOSLimp. O projeto teve início no Projeto Integrador II, com a construção do PDV, do motor de recomendação e da modelagem de banco de dados, e segue em evolução no Projeto Integrador III, com a adição de um Data Warehouse, controle de estoque e modelos preditivos de demanda.

## Tecnologias Utilizadas

O projeto SOSLimp PDV é construído com as seguintes tecnologias:

**Backend:**
-   **Python**: Linguagem de programação principal.
-   **FastAPI**: Framework web para construção da API RESTful.
-   **PostgreSQL**: Banco de dados relacional para armazenamento de dados transacionais e do Data Warehouse.
-   **Neo4j**: Banco de dados de grafos para modelagem de relações e recomendações.
-   **Docker / Docker Compose**: Para orquestração e gerenciamento dos ambientes de banco de dados.

**Frontend:**
-   **HTML5**: Estrutura das páginas web.
-   **CSS3**: Estilização e design responsivo.
-   **JavaScript**: Lógica interativa e comunicação com o backend.

**Dados, Análise e IA (Projeto Integrador III):**
-   **Data Warehouse**: Modelagem dimensional (esquema estrela) em schema dedicado do PostgreSQL, com tabela fato de vendas e dimensões de produto, tempo, loja, colaborador e forma de pagamento.
-   **Power BI**: Construção de dashboards analíticos e exploração do Data Warehouse.
-   **Pandas / NumPy**: Manipulação e agregação de dados para modelagem preditiva.
-   **scikit-learn**: Treinamento de modelos de Regressão Linear e Rede Neural (MLP) para previsão de demanda por categoria, com validação cruzada.
-   **Matplotlib**: Geração de gráficos de avaliação dos modelos (real vs. previsto, resíduos, coeficientes).
-   **Jupyter Notebook**: Ambiente de desenvolvimento da análise estatística e dos modelos preditivos.
-   **SQLAlchemy / python-dotenv**: Conexão segura do notebook de análise com o banco de dados.

**Outras Ferramentas/Conceitos:**
-   **SQL**: Para definição e manipulação do esquema do banco de dados PostgreSQL.
-   **Cypher**: Linguagem de consulta para o Neo4j.
-   **Git / GitHub**: Controle de versão e hospedagem do código.

## Novas Implementações (Projeto Integrador III)

-   **Controle de Estoque**: Gestão de estoque por produto e por loja, com registro de movimentações (entradas, saídas e ajustes) e alertas visuais quando o saldo se aproxima ou fica abaixo do mínimo definido.
-   **Data Warehouse**: Modelagem em esquema estrela, separando o banco transacional (OLTP) da camada analítica (OLAP), facilitando a construção de relatórios e dashboards.
-   **Modelo Preditivo de Demanda**: Comparação entre Regressão Linear e Rede Neural para previsão de vendas por categoria e loja, com avaliação por validação cruzada (5 folds) e geração de insights de tendência (alta, estável ou baixa) por categoria de produto.

### Equipe do Projeto

**Integrantes:**
-   Alisson Ibiapino da Silva - 2041382521023
-   Luiz Ângelo Pinto Ferreira - 2041382521017
-   Vinícius Fernandes - 2041382421023
##
- **Instituição:** Fatec Ipiranga - Pastor Enéas Tognini
- **Disciplina:** Projeto Integrador III
- **Professora orientadora:** Roberta Kelly Bondade de Caldas Cavalcanti
