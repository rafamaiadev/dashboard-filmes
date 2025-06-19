
# Movie Dashboard - Análise de Dados TMDB

Dashboard interativo para análise de dados de filmes dos últimos 5 anos (2020-2024) usando a API do TMDB.

## 📊 Insights Implementados

1. **Gêneros de filmes mais frequentes** - Análise temporal dos gêneros mais populares
2. **Países que mais produzem filmes** - Ranking de produção cinematográfica por país
3. **Filmes com melhor relação custo/arrecadação** - ROI dos filmes mais lucrativos
4. **Gastos com filmes por país produtor** - Análise dos investimentos cinematográficos por país

## 🚀 Como Executar

### Usando Docker (Recomendado)

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd movie-dashboard
```

2. Configure a chave da API:
```bash
cp .env.example .env
# Edite o arquivo .env e adicione sua chave da API TMDB
```

3. Execute com Docker Compose:
```bash
docker-compose up --build
```

4. Acesse o dashboard em: http://localhost:8050

### Execução Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure a variável de ambiente:
```bash
export TMDB_API_KEY=sua_chave_aqui
```

3. Execute a aplicação:
```bash
python app/main.py
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.9+**
- **Dash** - Framework para dashboards interativos
- **Plotly** - Visualizações interativas
- **Pandas** - Manipulação de dados
- **Requests** - Consumo da API TMDB
- **Docker** - Containerização

## 📁 Estrutura do Projeto

```
movie-dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal Dash
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── tmdb_client.py   # Cliente da API TMDB
│   │   └── data_processor.py # Processamento de dados
│   └── assets/
│       └── style.css        # Estilos customizados
├── data/                    # Cache de dados (opcional)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔑 Configuração da API

1. Crie uma conta em [TMDB](https://www.themoviedb.org/)
2. Obtenha sua chave da API em Settings > API
3. Configure no arquivo `.env`:
```
TMDB_API_KEY=sua_chave_da_api_aqui
```

## 📈 Funcionalidades

- **Dashboard interativo** com múltiplas visualizações
- **Filtros dinâmicos** por ano, gênero e país
- **Gráficos responsivos** com Plotly
- **Cache de dados** para melhor performance
- **Interface moderna** com design responsivo

## 🐳 Docker

O projeto inclui configuração completa para Docker:
- Dockerfile otimizado para Python
- docker-compose.yml para fácil execução
- Volumes para persistência de dados

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos.
