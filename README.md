# 🎬 CineTrack

A web application for tracking movies you want to watch and movies you've already watched. Built with Flask, SQLite, and the TMDB API.

## Features

### 🔐 User Authentication
- User registration and login
- Secure password hashing
- Personal watchlists for each user

### 🎥 Movie Discovery
- Search movies using TMDB API
- Browse trending movies this week
- Explore popular movies
- View detailed movie information including:
  - Cast and crew
  - Movie trailers
  - Budget and revenue
  - Release date and runtime
  - User ratings

### 📋 Watchlist Management
- Add movies to your personal watchlist
- Mark movies as watched/unwatched
- Rate movies with a 5-star system
- Add personal notes to movies
- Filter by:
  - Genre
  - Watch status
  - Search by title
- Sort by:
  - Date added
  - Title (A-Z or Z-A)
  - Release year
  - Personal rating

### 📊 Statistics Dashboard
- Total movies tracked
- Movies watched vs. unwatched
- Average personal rating
- Top genres breakdown
- Movies by release year
- Recently added movies
- Your top-rated movies

### 💫 User Experience
- Toast notifications for user actions
- Responsive design with Bootstrap
- Clean and intuitive interface

## Technologies Used

- **Backend**: Python, Flask, Flask-Login
- **Database**: SQLite
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Templating**: Jinja2
- **API**: The Movie Database (TMDB) API
- **Authentication**: Werkzeug password hashing

## Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository**
```bash
   git clone https://github.com/beth3777/cinetrack.git
   cd cinetrack
```

2. **Create a virtual environment (recommended)**
```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install flask flask-login requests
```

4. **Set up the database**
   
   Create a file named `setup_db.py`:
```python
   import sqlite3

   conn = sqlite3.connect('movies.db')
   cursor = conn.cursor()

   # Drop old tables if they exist
   cursor.execute('DROP TABLE IF EXISTS watchlist')
   cursor.execute('DROP TABLE IF EXISTS users')

   # Create users table
   cursor.execute('''
   CREATE TABLE users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT UNIQUE NOT NULL,
       email TEXT UNIQUE NOT NULL,
       password_hash TEXT NOT NULL,
       created_at TEXT DEFAULT CURRENT_TIMESTAMP
   )
   ''')

   # Create watchlist table
   cursor.execute('''
   CREATE TABLE watchlist (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       tmdb_id INTEGER NOT NULL,
       title TEXT NOT NULL,
       poster_path TEXT,
       release_date TEXT,
       genres TEXT,
       vote_average REAL,
       watched INTEGER DEFAULT 0,
       personal_rating INTEGER,
       notes TEXT,
       date_added TEXT DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(id),
       UNIQUE(user_id, tmdb_id)
   )
   ''')

   conn.commit()
   conn.close()

   print("Database created successfully!")
```

   Run the setup script:
```bash
   python setup_db.py
```

5. **Configure your TMDB API Key**
   
   The app currently uses a demo API key. For production use, get your own free API key:
   - Go to [https://www.themoviedb.org/](https://www.themoviedb.org/)
   - Create an account
   - Request an API key from your account settings
   - Replace the API key in `app.py`:
```python
     API_KEY = "your_api_key_here"
```update 

## Running the Application

1. **Start the Flask development server**
```bash
   python app.py
```

2. **Open your browser and navigate to**
```
   http://localhost:5000
```

3. **Create an account and start tracking movies!**

## Project Structure
```
cinetrack/
│
├── app.py                 # Main Flask application
├── movies.db              # SQLite database (created after setup)
├── setup_db.py           # Database setup script
│
├── templates/            # HTML templates
│   ├── index.html        # Home page with search and trending movies
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── watchlist.html    # Watchlist management page
│   ├── movie_details.html # Individual movie details page
│   └── stats.html        # Statistics dashboard
│
└── README.md             # This file
```

## Usage Guide

### Getting Started
1. **Register**: Create a new account with username, email, and password
2. **Login**: Sign in with your credentials
3. **Browse Movies**: Search for movies or browse trending/popular sections
4. **Add to Watchlist**: Click "Add to Watchlist" on any movie card

### Managing Your Watchlist
- **Mark as Watched**: Toggle the watch status of any movie
- **Rate Movies**: Click on stars to give a personal rating (1-5 stars)
- **Add Notes**: Add personal notes like "Watch with friends" or "Recommended by John"
- **Filter**: Use genre, status, and sort options to organize your list
- **Search**: Quickly find movies in your watchlist using the search bar

### Viewing Statistics
- Navigate to the Statistics page to see:
  - Total movies tracked
  - Completion percentage
  - Favorite genres
  - Movies by year
  - Your top-rated movies
- Python 3.7 or higher
- pip (Python package manager)
## Future Enhancements

Potential features for future versions:
- Export watchlist to CSV/PDF
- Share watchlists with friends
- Movie recommendations based on watchlist
- Integration with streaming services
- Advanced statistics and charts
- Email notifications for new releases
