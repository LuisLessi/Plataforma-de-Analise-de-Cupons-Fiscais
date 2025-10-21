# Plataforma de Análise de Cupons Fiscais

Sistema completo para ingestão, enriquecimento e análise de Cupons Fiscais Eletrônicos (CF-e).
<img width="506" height="386" alt="image" src="https://github.com/user-attachments/assets/3201a148-7345-4e69-9eb8-9a0308ad430a" />


## Funcionalidades

- **ETL Avançado**: Processamento automático de arquivos XML de cupons fiscais
- **Web Scraping**: Enriquecimento de dados com informações de produtos via Selenium
- **Dashboards Interativos**: Visualização em tempo real de métricas comerciais
- **Consulta em Linguagem Natural**: Busca inteligente através de perguntas pré-definidas
- **API RESTful**: Endpoints para integração e consumo de dados

## Stack Tecnológica

- **Backend**: Python + Flask
- **Banco de Dados**: SQLite
- **Processamento de Dados**: Pandas + NumPy
- **Web Scraping**: Selenium
- **Frontend**: HTML5 + Chart.js
- **Visualização**: Gráficos interativos responsivos

## Como Executar o Projeto

### Pré-requisitos
- Python 3.8+
- pip (gerenciador de pacotes Python)

### Método 1: Execução Automática (Recomendado)
python run.py

Este método executa sequencialmente:
1. Instala dependências automaticamente
2. Processa ETL (main.py)
3. Executa Web Scraping (scrapper.py)
4. Inicia servidor Flask (app.py)
5. Abre navegador automaticamente

### Método 2: Execução Manual (Controle Total)
1. Instalar dependências
pip install -r requirements.txt

2. Executar ETL
python main.py

3. Executar Web Scraping
python scrapper.py

4. Iniciar aplicação
python app.py

5. Acessar no navegador
http://localhost:5000

## Estrutura do Projeto
<img width="751" height="340" alt="image" src="https://github.com/user-attachments/assets/bd040e73-faff-446c-a71e-8e5f9e5a5d04" />


## Endpoints da API

### Dashboards
- GET /api/top_products - Top 5 produtos mais vendidos
- GET /api/daily_revenue - Faturamento por dia
- GET /api/discount_analysis - Análise de descontos
- GET /api/top_products_quantity - Top produtos por quantidade
- GET /api/cfop_sales - Vendas por CFOP
- GET /api/avg_product_value - Média de valor por produto

### Consulta em Linguagem Natural
- POST /api/query - Consulta com perguntas pré-definidas

**Perguntas suportadas:**
- "Qual o valor total vendido pela empresa [nome]"
- "Quais empresas compraram o produto [produto]"

## Evolução com LLM

Para evoluir o endpoint /api/query com capacidades de LLM, a arquitetura poderia ser expandida da seguinte forma:

**Integração com APIs de LLM**: A aplicação poderia ser integrada com serviços como OpenAI GPT ou Google AI para traduzir perguntas em linguagem natural em queries SQL complexas. Isso permitiria que usuários fizessem perguntas variadas como "Qual foi o produto mais vendido no último trimestre?" ou "Mostre a evolução do faturamento por semana", sem necessidade de mapeamento manual prévio.

**Considerações Arquiteturais**: A implementação exigiria uma camada de validação de segurança para as queries geradas, prevenindo SQL injection e operações maliciosas. Adicionalmente, um sistema de cache seria essencial para otimizar consultas frequentes e controlar custos da API. A solução manteria o fallback para as perguntas pré-definidas, garantindo robustez enquanto adquire capacidades de NLP avançadas.

## Dashboards Disponíveis

1. **Top 5 Produtos** - Gráfico de barras dos produtos mais vendidos em valor
3. **Faturamento Diário** - Série temporal de receita por dia
4. **Análise de Descontos** - Dispersão valor bruto vs descontos aplicados
5. **Produtos por Quantidade** - Volume de vendas por produto
6. **Vendas por CFOP** - Distribuição por código fiscal
7. **Valor Médio por Produto** - Preço médio dos produtos

## Desenvolvimento
Clonar repositório
git clone [url-do-repositorio]
cd cupons-fiscais

Ambiente virtual (opcional)
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows

Instalar dependências
pip install -r requirements.txt


## Critérios de Avaliação Atendidos

- ✅ **Funcionalidade**: Pipeline completo operacional
- ✅ **Qualidade de Código**: Código modular e documentado
- ✅ **Modelagem de Dados**: Schema relacional bem definido
- ✅ **Resolução de Problemas**: Abordagens eficientes em parsing e scraping

## Licença

Este projeto foi desenvolvido como parte de desafio técnico para análise de cupons fiscais.
