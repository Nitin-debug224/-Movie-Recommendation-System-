import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = '1a542ade879eb426981483d0f22fa150'
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Setup Session with Retries
def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = get_session()

def get_headers():
    return {
        "accept": "application/json",
        "User-Agent": "CineMatchPlus/1.0"
    }

def get_params():
    return {'api_key': API_KEY, 'language': 'en-US'}

def get_image_url(path):
    if not path:
        return "https://via.placeholder.com/500x750?text=No+Image"
    return f"{IMAGE_BASE_URL}{path}"

def make_request(url, params=None):
    try:
        final_params = get_params()
        if params:
            final_params.update(params)
            
        # verify=False is used here to bypass local SSL issues (e.g. proxies/firewalls)
        # In a production environment, this should be True or properly configured.
        response = session.get(url, params=final_params, headers=get_headers(), timeout=15, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return {}

def get_popular_movies():
    url = f"{BASE_URL}/movie/popular"
    data = make_request(url)
    return data.get('results', [])

def get_trending_movies():
    url = f"{BASE_URL}/trending/movie/week"
    data = make_request(url)
    return data.get('results', [])

def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    data = make_request(url, {'query': query})
    results = data.get('results', [])
    
    # Filter out movies with no release date and sort by release date
    results = [m for m in results if m.get('release_date')]
    results.sort(key=lambda x: x['release_date'])
    
    return results

def get_recommendations(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/recommendations"
    data = make_request(url)
    return data.get('results', [])

def get_movies_by_actor(actor_name, genre_ids=None, runtime_min=None, runtime_max=None):
    # First search for the actor to get ID
    search_url = f"{BASE_URL}/search/person"
    data = make_request(search_url, {'query': actor_name})
    
    results = data.get('results', [])
    if results:
        actor_id = results[0]['id']
        # Get movie credits
        credits_url = f"{BASE_URL}/person/{actor_id}/movie_credits"
        credits_data = make_request(credits_url)
        cast = credits_data.get('cast', [])
        
        # Filter by Genre
        if genre_ids:
            # genre_ids is a list of integers
            # cast member 'genre_ids' is a list of integers
            # We keep movie if it shares AT LEAST ONE genre with the user's preferences
            cast = [m for m in cast if any(g in genre_ids for g in m.get('genre_ids', []))]
            
        # Filter by Runtime (requires fetching details for each movie, which is expensive)
        # Optimization: Only fetch details for top candidates if needed, or skip runtime filter for actor search to be fast.
        # However, the user requested it. Let's do a lightweight filter if possible.
        # The 'movie_credits' endpoint DOES NOT return runtime. We would need to fetch details for each movie.
        # To avoid 100s of API calls, let's just sort by popularity first, take top 50, then filter by runtime.
        
        cast.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        candidates = cast[:50]
        
        final_list = []
        for movie in candidates:
            # If we need to filter by runtime, we must fetch details
            if runtime_min or runtime_max:
                details_url = f"{BASE_URL}/movie/{movie['id']}"
                details = make_request(details_url)
                runtime = details.get('runtime', 0)
                
                if runtime_min and runtime < runtime_min:
                    continue
                if runtime_max and runtime > runtime_max:
                    continue
                
                # Update movie object with exact runtime if needed, but we just push the original movie object
                final_list.append(movie)
            else:
                final_list.append(movie)
                
        return final_list[:20] # Return top 20
    return []

def get_genres():
    url = f"{BASE_URL}/genre/movie/list"
    data = make_request(url)
    return {g['id']: g['name'] for g in data.get('genres', [])}

def get_movies_by_genre(genre_ids, sort_by='popularity.desc', min_vote_count=0, runtime_min=None, runtime_max=None):
    url = f"{BASE_URL}/discover/movie"
    # genre_ids should be a comma separated string or list of ints
    if isinstance(genre_ids, list):
        genre_ids = "|".join(str(g) for g in genre_ids)
        
    params = {
        'with_genres': genre_ids,
        'sort_by': sort_by,
        'vote_count.gte': min_vote_count
    }
    
    if runtime_min:
        params['with_runtime.gte'] = runtime_min
    if runtime_max:
        params['with_runtime.lte'] = runtime_max
        
    data = make_request(url, params)
    return data.get('results', [])
