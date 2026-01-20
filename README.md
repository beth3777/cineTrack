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
