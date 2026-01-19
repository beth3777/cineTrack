import requests



API_KEY = "4c5081a829ff7e5483c442cd95941a5f"

def search_movie(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
    response = requests.get(url)

    if response.status_code == 200:
        movie_data = response.json()
        print(movie_data["results"][0]["overview"])
    else :
        print(f"failed to retrieve data{response.status_code}")


movie_title = "Stranger Things" 
search_movie(movie_title)