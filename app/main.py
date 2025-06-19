
import os
import sys
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.tmdb_client import TMDBClient
from utils.data_processor import DataProcessor

load_dotenv()

API_KEY = os.getenv('TMDB_API_KEY', '42e2738ab23b0fb7344caddfdec2fa98')

tmdb_client = TMDBClient(API_KEY)
movies_data = tmdb_client.get_cached_or_fetch_movies(2015, 2024)

data_processor = DataProcessor(movies_data)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Movie Dashboard - Análise TMDB"

app.layout = dbc.Container([
    html.Div([
        html.H1("🎬 Movie Dashboard", className="display-4"),
        html.P("Análise de Dados de Filmes TMDB", className="lead")
    ], className="text-center bg-primary text-white p-4 mb-4 rounded"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-movies", className="text-primary"),
                    html.P("Total de Filmes", className="text-muted")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="avg-rating", className="text-success"),
                    html.P("Avaliação Média", className="text-muted")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="total-revenue", className="text-info"),
                    html.P("Receita Total", className="text-muted")
                ])
            ])
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4(id="top-genre", className="text-warning"),
                    html.P("Gênero Mais Popular", className="text-muted")
                ])
            ])
        ], md=3)
    ], className="mb-4"),

    dbc.Card([
        dbc.CardBody([
            html.H5("🔍 Filtros", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Intervalo de Anos:"),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=2015,
                        max=2024,
                        step=1,
                        marks={i: str(i) for i in range(2015, 2025)},
                        value=[2015, 2024],
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Avaliação Mínima:"),
                    dcc.Slider(
                        id='rating-slider',
                        min=0,
                        max=10,
                        step=0.5,
                        marks={i: str(i) for i in range(0, 11, 2)},
                        value=0,
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], md=6)
            ])
        ])
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📊 Gêneros Mais Frequentes por Ano", className="mb-3"),
                    dcc.Graph(id='genre-chart')
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🌍 Países que Mais Produzem Filmes", className="mb-3"),
                    dcc.Graph(id='countries-chart')
                ])
            ])
        ], md=6)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💰 Filmes com Melhor ROI", className="mb-3"),
                    dcc.Graph(id='roi-chart')
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💰 Gastos com Filmes por País Produtor", className="mb-3"),
                    dcc.Graph(id='spending-chart'),
                    html.Div(id='spending-info', className="mt-2")
                ])
            ])
        ], md=6)
    ], className="mb-4"),

    html.Hr(),
    html.P("Dashboard desenvolvido com Dash e dados do TMDB", 
           className="text-center text-muted")
    
], fluid=True)

@app.callback(
    [Output('total-movies', 'children'),
     Output('avg-rating', 'children'),
     Output('total-revenue', 'children'),
     Output('top-genre', 'children')],
    [Input('year-slider', 'value'),
     Input('rating-slider', 'value')]
)
def update_stats(year_range, min_rating):
    filtered_processor = data_processor.filter_data(year_range, min_rating)
    stats = filtered_processor.get_summary_stats()
    
    if not stats:
        return "0", "0.0", "$0", "N/A"
    
    total_movies = f"{stats.get('total_movies', 0):,}"
    avg_rating = f"{stats.get('avg_rating', 0):.1f}"
    total_revenue = f"${stats.get('total_revenue', 0)/1e9:.1f}B"
    top_genre = stats.get('top_genre', 'N/A')
    
    return total_movies, avg_rating, total_revenue, top_genre

@app.callback(
    Output('genre-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('rating-slider', 'value')]
)
def update_genre_chart(year_range, min_rating):
    filtered_processor = data_processor.filter_data(year_range, min_rating)
    genre_data = filtered_processor.get_genre_frequency_by_year()
    
    if genre_data.empty:
        return px.bar(title="Nenhum dado disponível")

    top_genres = genre_data.groupby('genre')['count'].sum().nlargest(10).index
    filtered_genre_data = genre_data[genre_data['genre'].isin(top_genres)]
    
    fig = px.bar(
        filtered_genre_data,
        x='year',
        y='count',
        color='genre',
        title="Top 10 Gêneros por Ano",
        labels={'count': 'Número de Filmes', 'year': 'Ano', 'genre': 'Gênero'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Número de Filmes",
        legend_title="Gênero",
        hovermode='closest',
        xaxis = dict(
            tickmode='array',
            tickvals=list(range(year_range[0], year_range[1] + 1)),
            tickangle=0
        )
    )
    
    return fig

@app.callback(
    Output('countries-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('rating-slider', 'value')]
)
def update_countries_chart(year_range, min_rating):
    filtered_processor = data_processor.filter_data(year_range, min_rating)
    countries_data = filtered_processor.get_top_producing_countries(15)
    
    if countries_data.empty:
        return px.bar(title="Nenhum dado disponível")
    
    fig = px.bar(
        countries_data,
        x='movie_count',
        y='country',
        orientation='h',
        title="Top 15 Países Produtores",
        labels={'movie_count': 'Número de Filmes', 'country': 'País'},
        color='movie_count',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_title="Número de Filmes",
        yaxis_title="País",
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

@app.callback(
    Output('roi-chart', 'figure'),
    [Input('year-slider', 'value'),
     Input('rating-slider', 'value')]
)
def update_roi_chart(year_range, min_rating):
    filtered_processor = data_processor.filter_data(year_range, min_rating)
    roi_data = filtered_processor.get_best_roi_movies(1000000, 15)
    
    if roi_data.empty:
        return px.bar(title="Nenhum dado disponível")
    
    fig = px.bar(
        roi_data,
        x='roi',
        y='title',
        orientation='h',
        title="Top 15 Filmes por ROI (%)",
        labels={'roi': 'ROI (%)', 'title': 'Filme', 'budget': 'Orçamento', 'revenue': 'Receita', 'year': 'Ano'},
        color='roi',
        color_continuous_scale='RdYlGn',
        hover_data=['budget', 'revenue', 'year']
    )
    
    fig.update_layout(
        xaxis_title="ROI (%)",
        yaxis_title="Filme",
        yaxis={'categoryorder': 'total ascending'},
        xaxis_tickformat = ".2f"
    )

    return fig

@app.callback(
    [Output('spending-chart', 'figure'),
     Output('spending-info', 'children')],
    [Input('year-slider', 'value'),
     Input('rating-slider', 'value')]
)
def update_spending_chart(year_range, min_rating):
    filtered_processor = data_processor.filter_data(year_range, min_rating)
    spending_data = filtered_processor.get_movie_spending_by_country(15)

    if spending_data.empty:
        return px.bar(title="Nenhum dado disponível"), ""

    spending_data['budget_millions'] = spending_data['total_budget'] / 1e6
    spending_data['avg_budget_millions'] = spending_data['avg_budget'] / 1e6

    fig = px.bar(
        spending_data,
        x='country',
        y='budget_millions',
        title="Gastos Totais com Filmes por País (Top 15)",
        labels={
            'budget_millions': 'Orçamento Total (Milhões $)',
            'country': 'País',
            'movie_count': 'Número de Filmes',
            'avg_budget_millions': 'Orçamento Médio (Milhões $)'
        },
        color='budget_millions',
        color_continuous_scale='Viridis',
        hover_data=['movie_count', 'avg_budget_millions']
    )

    fig.update_layout(
        xaxis_title="País",
        yaxis_title="Orçamento Total (Milhões $)",
        xaxis={'categoryorder': 'total descending'}
    )

    top_country = spending_data.iloc[0]['country'] if not spending_data.empty else "N/A"
    total_spending = spending_data['total_budget'].sum() / 1e9 if not spending_data.empty else 0

    spending_info = dbc.Alert(
        f"Total de investimentos: ${total_spending:.2f} bilhões. País com maior investimento: {top_country}",
        color="info"
    )

    return fig, spending_info

if __name__ == '__main__':
    print("Iniciando Movie Dashboard...")
    print(f"Dashboard disponível em: http://localhost:8050")
    app.run_server(debug=False, host='0.0.0.0', port=8050)
