import requests
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
DB_NAME = "movies.db"


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['email'])
    return None


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    query = request.args.get("q")
    movies = []
    trending = []
    popular = []

    if query:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}"
        response = requests.get(url)
        
        if response.status_code == 200:
            movies = response.json().get("results", [])
    else:
        trending_url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"
        trending_response = requests.get(trending_url)
        if trending_response.status_code == 200:
            trending = trending_response.json().get("results", [])[:8]
        
        popular_url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}"
        popular_response = requests.get(popular_url)
        if popular_response.status_code == 200:
            popular = popular_response.json().get("results", [])[:8]

    return render_template("index.html", movies=movies, trending=trending, popular=popular, 
                         image_base=TMDB_IMAGE_BASE, query=query)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        if not username or not email or not password or not confirm_password:
            flash("All fields are required!", "error")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("Password must be at least 6 characters long!", "error")
            return render_template("register.html")
        
        # Check if user exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash("Username or email already exists!", "error")
            conn.close()
            return render_template("register.html")
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        conn.close()
        
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            flash("Please enter both username and password!", "error")
            return render_template("login.html")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['email'])
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            
            # Redirect to the page they were trying to access, or home
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect("/")
        else:
            flash("Invalid username or password!", "error")
            return render_template("login.html")
    
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect("/")


@app.route("/watchlist/add", methods=["POST"])
@login_required
def add_to_watchlist():
    movie_id = request.form.get("movie_id")
    title = request.form.get("title")
    poster_path = request.form.get("poster_path")
    release_date = request.form.get("release_date")
    vote_average = request.form.get("vote_average")
    
    # Fetch full movie details to get genres
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    movie_response = requests.get(movie_url)
    genres = ""
    
    if movie_response.status_code == 200:
        movie_data = movie_response.json()
        genre_list = [g['name'] for g in movie_data.get('genres', [])]
        genres = ", ".join(genre_list)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO watchlist (user_id, tmdb_id, title, poster_path, release_date, genres, vote_average) VALUES (?, ?, ?, ?, ?, ?, ?)", 
            (current_user.id, movie_id, title, poster_path, release_date, genres, vote_average)
        )
        conn.commit()
        flash(f'"{title}" added to your watchlist!', 'success')

    except sqlite3.IntegrityError:
        flash(f'"{title}" is already in your watchlist!', 'info')

    finally:
        conn.close()

    return redirect(request.referrer or '/')


@app.route("/watchlist")
@login_required
def show_watchlist():
    genre_filter = request.args.get("genre")
    status_filter = request.args.get("status")
    sort_by = request.args.get("sort", "date_added_desc")
    search_query = request.args.get("q")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query based on filters - only show current user's movies
    query = "SELECT * FROM watchlist WHERE user_id = ?"
    params = [current_user.id]
    
    if genre_filter:
        query += " AND genres LIKE ?"
        params.append(f"%{genre_filter}%")
    
    if status_filter == "watched":
        query += " AND watched = 1"
    elif status_filter == "unwatched":
        query += " AND watched = 0"
    
    if search_query:
        query += " AND title LIKE ?"
        params.append(f"%{search_query}%")
    
    # Add sorting
    if sort_by == "title_asc":
        query += " ORDER BY title ASC"
    elif sort_by == "title_desc":
        query += " ORDER BY title DESC"
    elif sort_by == "year_asc":
        query += " ORDER BY release_date ASC"
    elif sort_by == "year_desc":
        query += " ORDER BY release_date DESC"
    elif sort_by == "rating_asc":
        query += " ORDER BY personal_rating ASC NULLS FIRST"
    elif sort_by == "rating_desc":
        query += " ORDER BY personal_rating DESC NULLS LAST"
    elif sort_by == "date_added_asc":
        query += " ORDER BY date_added ASC"
    else:  # date_added_desc (default)
        query += " ORDER BY date_added DESC"
    
    cursor.execute(query, params)
    my_movies = cursor.fetchall()
    
    # Get all unique genres for filter dropdown (only current user's movies)
    cursor.execute("SELECT DISTINCT genres FROM watchlist WHERE user_id = ? AND genres IS NOT NULL AND genres != ''", (current_user.id,))
    all_genres_raw = cursor.fetchall()
    
    genres_set = set()
    for row in all_genres_raw:
        if row['genres']:
            for genre in row['genres'].split(', '):
                genres_set.add(genre.strip())
    
    all_genres = sorted(list(genres_set))
    
    # Get statistics (only current user's movies)
    cursor.execute("SELECT COUNT(*) as total FROM watchlist WHERE user_id = ?", (current_user.id,))
    total_movies = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as watched FROM watchlist WHERE user_id = ? AND watched = 1", (current_user.id,))
    watched_count = cursor.fetchone()['watched']
    
    unwatched_count = total_movies - watched_count

    conn.close()
    
    return render_template("watchlist.html", 
                         watchlist=my_movies, 
                         image_base=TMDB_IMAGE_BASE,
                         all_genres=all_genres,
                         selected_genre=genre_filter,
                         selected_status=status_filter,
                         selected_sort=sort_by,
                         search_query=search_query,
                         total_movies=total_movies,
                         watched_count=watched_count,
                         unwatched_count=unwatched_count)


@app.route("/watchlist/remove", methods=["POST"])
@login_required
def remove_from_watchlist():
    movie_id = request.form.get("movie_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT title FROM watchlist WHERE tmdb_id = ? AND user_id = ?", (movie_id, current_user.id))
    movie = cursor.fetchone()
    
    cursor.execute("DELETE FROM watchlist WHERE tmdb_id = ? AND user_id = ?", (movie_id, current_user.id))
    conn.commit()
    conn.close()
    
    if movie:
        flash(f'"{movie["title"]}" removed from your watchlist!', 'success')
    
    return redirect(request.referrer or '/watchlist')


@app.route("/watchlist/toggle", methods=["POST"])
@login_required
def toggle_watched():
    movie_id = request.form.get("movie_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT watched, title FROM watchlist WHERE tmdb_id = ? AND user_id = ?", (movie_id, current_user.id))
    movie = cursor.fetchone()
    
    if movie:
        new_status = 0 if movie['watched'] == 1 else 1
        cursor.execute("UPDATE watchlist SET watched = ? WHERE tmdb_id = ? AND user_id = ?", (new_status, movie_id, current_user.id))
        conn.commit()
        
        status_text = "watched" if new_status == 1 else "unwatched"
        message = f'"{movie["title"]}" marked as {status_text}!'
        
        conn.close()
        return jsonify({'success': True, 'message': message, 'new_status': new_status})
    
    conn.close()
    return jsonify({'success': False, 'message': 'Movie not found'})


@app.route("/watchlist/rate", methods=["POST"])
@login_required
def rate_movie():
    movie_id = request.form.get("movie_id")
    rating = request.form.get("rating")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT title FROM watchlist WHERE tmdb_id = ? AND user_id = ?", (movie_id, current_user.id))
    movie = cursor.fetchone()
    
    if movie and rating:
        cursor.execute("UPDATE watchlist SET personal_rating = ? WHERE tmdb_id = ? AND user_id = ?", (rating, movie_id, current_user.id))
        conn.commit()
        message = f'Rated "{movie["title"]}" {rating} stars!'
        
        conn.close()
        return jsonify({'success': True, 'message': message})
    
    conn.close()
    return jsonify({'success': False, 'message': 'Error rating movie'})


@app.route("/watchlist/notes", methods=["POST"])
@login_required
def update_notes():
    movie_id = request.form.get("movie_id")
    notes = request.form.get("notes")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT title FROM watchlist WHERE tmdb_id = ? AND user_id = ?", (movie_id, current_user.id))
    movie = cursor.fetchone()
    
    if movie:
        cursor.execute("UPDATE watchlist SET notes = ? WHERE tmdb_id = ? AND user_id = ?", (notes, movie_id, current_user.id))
        conn.commit()
        message = f'Notes updated for "{movie["title"]}"!'
        
        conn.close()
        return jsonify({'success': True, 'message': message})
    
    conn.close()
    return jsonify({'success': False, 'message': 'Error updating notes'})

@app.route("/movie/<int:movie_id>")
def movie_details(movie_id):
    # Fetch movie details from TMDB API
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits,videos"
    response = requests.get(movie_url)
    
    if response.status_code != 200:
        flash("Movie not found!", "error")
        return redirect("/")
    
    movie = response.json()
    
    # Get cast (top 10)
    cast = movie.get('credits', {}).get('cast', [])[:10]
    
    # Get director
    crew = movie.get('credits', {}).get('crew', [])
    director = next((person for person in crew if person['job'] == 'Director'), None)
    
    # Get trailer
    videos = movie.get('videos', {}).get('results', [])
    trailer = next((video for video in videos if video['type'] == 'Trailer' and video['site'] == 'YouTube'), None)
    
    # Check if movie is in watchlist (only if user is logged in)
    watchlist_entry = None
    if current_user.is_authenticated:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE tmdb_id = ? AND user_id = ?", (movie_id, current_user.id))
        watchlist_entry = cursor.fetchone()
        conn.close()
    
    return render_template("movie_details.html", 
                         movie=movie, 
                         cast=cast,
                         director=director,
                         trailer=trailer,
                         watchlist_entry=watchlist_entry,
                         image_base=TMDB_IMAGE_BASE)


@app.route("/stats")
@login_required
def statistics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total movies (only current user)
    cursor.execute("SELECT COUNT(*) as total FROM watchlist WHERE user_id = ?", (current_user.id,))
    total_movies = cursor.fetchone()['total']
    
    # Watched vs unwatched
    cursor.execute("SELECT COUNT(*) as watched FROM watchlist WHERE user_id = ? AND watched = 1", (current_user.id,))
    watched_count = cursor.fetchone()['watched']
    unwatched_count = total_movies - watched_count
    
    # Average personal rating
    cursor.execute("SELECT AVG(personal_rating) as avg_rating FROM watchlist WHERE user_id = ? AND personal_rating IS NOT NULL", (current_user.id,))
    avg_rating_result = cursor.fetchone()['avg_rating']
    avg_rating = round(avg_rating_result, 1) if avg_rating_result else 0
    
    # Movies by genre
    cursor.execute("SELECT genres FROM watchlist WHERE user_id = ? AND genres IS NOT NULL AND genres != ''", (current_user.id,))
    all_movies_genres = cursor.fetchall()
    
    genre_counts = {}
    for row in all_movies_genres:
        if row['genres']:
            for genre in row['genres'].split(', '):
                genre = genre.strip()
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Movies by year
    cursor.execute("SELECT release_date FROM watchlist WHERE user_id = ? AND release_date IS NOT NULL AND release_date != ''", (current_user.id,))
    all_dates = cursor.fetchall()
    
    year_counts = {}
    for row in all_dates:
        if row['release_date']:
            year = row['release_date'][:4]
            year_counts[year] = year_counts.get(year, 0) + 1
    
    sorted_years = sorted(year_counts.items(), key=lambda x: x[0], reverse=True)
    
    # Recent additions
    cursor.execute("SELECT title, date_added FROM watchlist WHERE user_id = ? ORDER BY date_added DESC LIMIT 5", (current_user.id,))
    recent_additions = cursor.fetchall()
    
    # Top rated movies (personal ratings)
    cursor.execute("SELECT title, personal_rating FROM watchlist WHERE user_id = ? AND personal_rating IS NOT NULL ORDER BY personal_rating DESC LIMIT 5", (current_user.id,))
    top_rated = cursor.fetchall()
    
    conn.close()
    
    return render_template("stats.html",
                         total_movies=total_movies,
                         watched_count=watched_count,
                         unwatched_count=unwatched_count,
                         avg_rating=avg_rating,
                         top_genres=top_genres,
                         sorted_years=sorted_years,
                         recent_additions=recent_additions,
                         top_rated=top_rated)



@app.route("/watchlist/stats")
@login_required
def get_watchlist_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM watchlist WHERE user_id = ?", (current_user.id,))
    total_movies = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as watched FROM watchlist WHERE user_id = ? AND watched = 1", (current_user.id,))
    watched_count = cursor.fetchone()['watched']
    
    unwatched_count = total_movies - watched_count
    
    conn.close()
    
    return jsonify({
        'total_movies': total_movies,
        'watched_count': watched_count,
        'unwatched_count': unwatched_count
    })


if __name__ == "__main__":
    app.run(debug=True)