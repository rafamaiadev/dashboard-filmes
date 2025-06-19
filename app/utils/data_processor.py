
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter

class DataProcessor:
    
    def __init__(self, movies_data: List[Dict]):
        self.movies_data = movies_data
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        if not self.movies_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.movies_data)

        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        df['year'] = df['release_date'].dt.year
        df['budget'] = pd.to_numeric(df['budget'], errors='coerce').fillna(0)
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
        df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce').fillna(0)
        df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce').fillna(0)

        df['roi'] = np.where(df['budget'] > 0, 
                            (df['revenue'] - df['budget']) / df['budget'] * 100, 
                            0)
        
        return df
    
    def get_genre_frequency_by_year(self) -> pd.DataFrame:
        genre_year_data = []
        
        for _, movie in self.df.iterrows():
            if pd.isna(movie['year']) or not movie.get('genre_ids'):
                continue
                
            year = int(movie['year'])
            genre_ids = movie['genre_ids']
            
            genre_map = {
                28: 'Ação', 12: 'Aventura', 16: 'Animação', 35: 'Comédia',
                80: 'Crime', 99: 'Documentário', 18: 'Drama', 10751: 'Família',
                14: 'Fantasia', 36: 'História', 27: 'Terror', 10402: 'Música',
                9648: 'Mistério', 10749: 'Romance', 878: 'Ficção Científica',
                10770: 'TV Movie', 53: 'Thriller', 10752: 'Guerra', 37: 'Faroeste'
            }
            
            for genre_id in genre_ids:
                genre_name = genre_map.get(genre_id, f'Gênero {genre_id}')
                genre_year_data.append({
                    'year': year,
                    'genre': genre_name,
                    'count': 1
                })
        
        if not genre_year_data:
            return pd.DataFrame()
        
        genre_df = pd.DataFrame(genre_year_data)
        return genre_df.groupby(['year', 'genre']).sum().reset_index()
    
    def get_top_producing_countries(self, top_n: int = 15) -> pd.DataFrame:
        country_counts = Counter()
        
        for _, movie in self.df.iterrows():
            countries = movie.get('production_countries', [])
            if isinstance(countries, list):
                for country in countries:
                    if isinstance(country, dict) and 'name' in country:
                        country_counts[country['name']] += 1
        
        if not country_counts:
            return pd.DataFrame()
        
        top_countries = country_counts.most_common(top_n)
        return pd.DataFrame(top_countries, columns=['country', 'movie_count'])
    
    def get_best_roi_movies(self, min_budget: int = 1000000, top_n: int = 20) -> pd.DataFrame:
        roi_df = self.df[
            (self.df['budget'] >= min_budget) & 
            (self.df['revenue'] > 0) & 
            (self.df['roi'] > 0)
        ].copy()
        
        if roi_df.empty:
            return pd.DataFrame()
        
        roi_df = roi_df.nlargest(top_n, 'roi')[
            ['title', 'budget', 'revenue', 'roi', 'year', 'vote_average']
        ]
        
        return roi_df
    
    def get_popularity_rating_correlation(self) -> Tuple[pd.DataFrame, float]:
        corr_df = self.df[
            (self.df['popularity'] > 0) & 
            (self.df['vote_average'] > 0)
        ][['title', 'popularity', 'vote_average', 'year']].copy()
        
        if corr_df.empty:
            return pd.DataFrame(), 0
        
        correlation = corr_df['popularity'].corr(corr_df['vote_average'])
        
        return corr_df, correlation

    def get_movie_spending_by_country(self, top_n: int = 15) -> pd.DataFrame:
        country_spending = {}
        country_movie_count = {}

        for _, movie in self.df.iterrows():
            budget = movie.get('budget', 0)
            countries = movie.get('production_countries', [])

            if budget > 0 and isinstance(countries, list):
                for country in countries:
                    if isinstance(country, dict) and 'name' in country:
                        country_name = country['name']
                        if country_name not in country_spending:
                            country_spending[country_name] = 0
                            country_movie_count[country_name] = 0

                        country_spending[country_name] += budget
                        country_movie_count[country_name] += 1

        if not country_spending:
            return pd.DataFrame()

        spending_data = []
        for country, total_budget in country_spending.items():
            movie_count = country_movie_count[country]
            avg_budget = total_budget / movie_count if movie_count > 0 else 0

            spending_data.append({
                'country': country,
                'total_budget': total_budget,
                'movie_count': movie_count,
                'avg_budget': avg_budget
            })

        spending_df = pd.DataFrame(spending_data)
        spending_df = spending_df.sort_values('total_budget', ascending=False).head(top_n)

        return spending_df
    
    def get_summary_stats(self) -> Dict:
        if self.df.empty:
            return {}
        
        return {
            'total_movies': len(self.df),
            'years_range': f"{self.df['year'].min():.0f} - {self.df['year'].max():.0f}",
            'avg_rating': self.df['vote_average'].mean(),
            'total_revenue': self.df['revenue'].sum(),
            'avg_budget': self.df[self.df['budget'] > 0]['budget'].mean(),
            'top_genre': self._get_most_common_genre()
        }
    
    def _get_most_common_genre(self) -> str:
        genre_counts = Counter()
        
        for _, movie in self.df.iterrows():
            genre_ids = movie.get('genre_ids', [])
            if isinstance(genre_ids, list):
                genre_counts.update(genre_ids)
        
        if not genre_counts:
            return "N/A"
        
        genre_map = {
            28: 'Ação', 12: 'Aventura', 16: 'Animação', 35: 'Comédia',
            80: 'Crime', 99: 'Documentário', 18: 'Drama', 10751: 'Família',
            14: 'Fantasia', 36: 'História', 27: 'Terror', 10402: 'Música',
            9648: 'Mistério', 10749: 'Romance', 878: 'Ficção Científica',
            10770: 'TV Movie', 53: 'Thriller', 10752: 'Guerra', 37: 'Faroeste'
        }
        
        most_common_id = genre_counts.most_common(1)[0][0]
        return genre_map.get(most_common_id, f'Gênero {most_common_id}')
    
    def filter_data(self, year_range: List[int] = None, min_rating: float = 0) -> 'DataProcessor':
        filtered_df = self.df.copy()
        
        if year_range:
            filtered_df = filtered_df[
                (filtered_df['year'] >= year_range[0]) & 
                (filtered_df['year'] <= year_range[1])
            ]
        
        if min_rating > 0:
            filtered_df = filtered_df[filtered_df['vote_average'] >= min_rating]
        
        filtered_movies = filtered_df.to_dict('records')
        
        return DataProcessor(filtered_movies)
