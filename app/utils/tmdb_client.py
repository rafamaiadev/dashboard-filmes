import requests
import os
import time
import json
from typing import List, Dict, Optional

class TMDBClient:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        if params is None:
            params = {}

        params['api_key'] = self.api_key

        try:
            response = self.session.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None

    def get_popular_movies(self, page: int = 1, year: int = None) -> Optional[Dict]:
        params = {'page': page}
        if year:
            params['primary_release_year'] = year

        return self._make_request("/movie/popular", params)

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        return self._make_request(f"/movie/{movie_id}")

    def discover_movies(self, year: int, page: int = 1) -> Optional[Dict]:
        params = {
            'primary_release_year': year,
            'page': page,
            'sort_by': 'popularity.desc'
        }
        return self._make_request("/discover/movie", params)

    def get_genres(self) -> Optional[Dict]:
        return self._make_request("/genre/movie/list")

    def get_movies_by_year_range(self, start_year: int = 2020, end_year: int = 2024, max_pages: int = 5) -> List[Dict]:
        all_movies = []

        for year in range(start_year, end_year + 1):
            print(f"Buscando filmes de {year}...")

            for page in range(1, max_pages + 1):
                data = self.discover_movies(year, page)

                if data and 'results' in data:
                    movies = data['results']

                    for movie in movies:
                        movie['year'] = year

                        details = self.get_movie_details(movie['id'])
                        if details:
                            movie.update({
                                'budget': details.get('budget', 0),
                                'revenue': details.get('revenue', 0),
                                'runtime': details.get('runtime', 0),
                                'production_countries': details.get('production_countries', []),
                                'production_companies': details.get('production_companies', [])
                            })

                    all_movies.extend(movies)

                    time.sleep(0.25)

                    if page >= data.get('total_pages', 1):
                        break
                else:
                    break

        return all_movies

    def save_data_to_cache(self, data: List[Dict], filename: str):
        os.makedirs('data', exist_ok=True)
        with open(f'data/{filename}', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data_from_cache(self, filename: str) -> Optional[List[Dict]]:
        try:
            with open(f'data/{filename}', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def get_cached_or_fetch_movies(self, start_year: int, end_year: int) -> List[Dict]:
        cache_file = f'movies_{start_year}_{end_year}.json'

        cached_data = self.load_data_from_cache(cache_file)
        if cached_data:
            print(f"Dados carregados do cache: {len(cached_data)} filmes")
            return cached_data

        print("Cache não encontrado. Buscando dados da API...")
        movies = self.get_movies_by_year_range(start_year, end_year)

        if movies:
            self.save_data_to_cache(movies, cache_file)
            print(f"Dados salvos no cache: {len(movies)} filmes")

        return movies
