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

# Create watchlist table with user_id
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