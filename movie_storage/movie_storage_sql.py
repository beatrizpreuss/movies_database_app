from sqlalchemy import create_engine, text
import emoji

# Define the database URL
DB_URL = "sqlite:///_data/movies.db"

engine = create_engine(DB_URL)

# Create the movies table if it does not exist
with engine.begin() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT,
            note TEXT
        )
    """))


def list_movies():
    """Retrieve all movies from the database."""
    with engine.begin() as connection:
        result = connection.execute(text("SELECT title, year, rating FROM movies"))
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2]} for row in movies}


def add_movie(title, year, rating, poster):
    """Add a new movie to the database."""
    with engine.begin() as connection:
        try:
            connection.execute(text("INSERT INTO movies (title, year, rating, poster) VALUES (:title, :year, :rating, :poster)"),
                               {"title": title, "year": year, "rating": rating, "poster": poster})
            print(f"{emoji.emojize(':check_mark_button:')}Movie '{title}' added successfully.")
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title):
    """Delete a movie from the database."""
    try:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM movies WHERE title = :title"),
                               {"title": title})
            print(f"{emoji.emojize(':check_mark_button:')}Movie '{title}' successfully deleted.")
    except Exception as e:
        print(f"Error: {e}")


def update_movie(title, note):
    """Update a movie's note in the database."""
    try:
        with engine.begin() as connection:
            connection.execute(text("UPDATE movies SET note = :note WHERE title = :title"),
                               {"title": title, "note": note})
            print(f"{emoji.emojize(':check_mark_button:')}Movie '{title}' successfully updated.")
    except Exception as e:
        print(f"Error: {e}")


def get_movies_for_website():
    """Retrieve all movies from the database."""
    with engine.begin() as connection:
        result = connection.execute(text("SELECT title, year, rating, poster, note FROM movies"))
        movies = result.fetchall()

    return {row[0]: {"year": row[1], "rating": row[2], "poster": row[3], "note": row[4]} for row in movies}