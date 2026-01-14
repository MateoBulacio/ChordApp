# Flask app for ChordApp
# - SQLite database
# - routes: /, /login, /register, /logout
# - uses Jinja templates
from cs50 import SQL
from flask import Flask, abort, render_template, request, redirect, url_for, session, g, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os

from helpers import login_required, parse_content

# Input validation constants
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 100
MIN_PASSWORD_LENGTH = 3
MAX_TITLE_LENGTH = 200
MAX_ARTIST_NAME_LENGTH = 100
MAX_GENRE_NAME_LENGTH = 50
MAX_CONTENT_LENGTH = 10000  # Song content
MAX_SEARCH_QUERY_LENGTH = 100

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# db = SQL("sqlite:///chordapp.db")
DB_PATH = os.getenv("DB_PATH", "chordapp.db")
db = SQL(f"sqlite:///{DB_PATH}")

@app.route("/")
@login_required
def index():
    """Redirects to the songs list as the home page.

    Returns:
        Response: Flask redirect to the songs route.
    """
    # FUTURE IMPROVEMENT: Could display user dashboard or recent activity here
    return redirect(url_for("songs"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login.

    On GET, renders the login form. On POST, validates credentials and logs in the user.

    Returns:
        Response: Rendered template or redirect on success.

    Raises:
        None explicitly, but may raise Flask exceptions on invalid requests.
    """
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password") 
        if not username:
            return render_template("login.html", error="Username is required")
        if len(username) > MAX_USERNAME_LENGTH:
            return render_template("login.html", error=f"Username must be {MAX_USERNAME_LENGTH} characters or less")
        if not password:
            return render_template("login.html", error="Password is required")

        rows = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], password):
            return render_template("login.html", error="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for("index"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration.

    On GET, renders the registration form. On POST, validates input, hashes password, and inserts user into database.

    Returns:
        Response: Rendered template on error or redirect to login on success.

    Raises:
        ValueError: If username already exists (caught and handled).
    """
    if request.method == "POST":
        # Handle registration form submission
        username = request.form.get("username")
        if not username:
            return render_template("register.html", error="Username is required")
        if len(username) > MAX_USERNAME_LENGTH:
            return render_template("register.html", error=f"Username must be {MAX_USERNAME_LENGTH} characters or less")

        
        password = request.form.get("password")
        if not password:
            return render_template("register.html", error="Password is required")
        if len(password) < MIN_PASSWORD_LENGTH:
            return render_template("register.html", error=f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        if len(password) > MAX_PASSWORD_LENGTH:
            return render_template("register.html", error=f"Password must be {MAX_PASSWORD_LENGTH} characters or less")
        
        # Hash the password
        hashed_password = generate_password_hash(password)

        confirmation = request.form.get("confirmation")
        if not confirmation:
            return render_template("register.html", error="Password confirmation is required")
        if password != confirmation:
            return render_template("register.html", error="Password and confirmation do not match")

        try:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", username, hashed_password)
        except ValueError:
            return render_template("register.html", error="Username already exists")

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    """Logs out the current user by clearing the session.

    Returns:
        Response: Redirect to the login page.
    """
    session.clear()
    return redirect(url_for("login"))

@app.route("/songs")
@login_required
def songs():
    """Lists all songs from the database.

    Queries songs with artist and genre details, ordered by title.

    Returns:
        Response: Rendered songs template with song list.
    """
    songs = db.execute("SELECT songs.id, songs.title, artists.name AS artist, genres.name AS genre FROM songs JOIN artists ON songs.artist_id = artists.id JOIN genres ON songs.genre_id = genres.id ORDER BY songs.title")
    return render_template("songs.html", songs=songs)

@app.route("/songs/<int:song_id>")
@login_required
def song(song_id):
    """Lists all versions for a specific song.

    Args:
        song_id: The ID of the song to retrieve versions for.

    Returns:
        Response: Rendered song template with versions and song info.
    """
    song = db.execute("SELECT versions.id, versions.version_number, versions.creator_id, users.username, versions.created_at, ROUND(AVG(ratings.rating), 1) AS avg FROM versions JOIN users ON versions.creator_id = users.id LEFT JOIN ratings ON ratings.version_id = versions.id WHERE versions.song_id = ? GROUP BY versions.id ORDER BY avg DESC", song_id)
    song_info = db.execute("SELECT songs.id, songs.title, artists.name AS artist FROM songs JOIN artists ON songs.artist_id = artists.id WHERE songs.id = ?", song_id)
    return render_template("song.html", versions=song, song_info=song_info[0], user=session["user_id"])

@app.route("/songs/<int:song_id>/versions/<int:version_id>")
@login_required
def version(song_id, version_id):
    """Displays a specific version of a song, including parsed content and average rating.

    Args:
        song_id: The ID of the song.
        version_id: The ID of the version to display.

    Returns:
        Response: Rendered version template with details.

    Raises:
        404: If the version does not exist.
    """
    version = db.execute("SELECT users.username, versions.id, versions.version_number, versions.created_at, versions.creator_id, versions.content FROM versions JOIN users ON versions.creator_id = users.id WHERE versions.id = ?", version_id)

    song_info = db.execute("SELECT songs.id, songs.title, artists.name AS artist FROM songs JOIN artists ON songs.artist_id = artists.id WHERE songs.id = ?", song_id)

    avg_rating = db.execute("SELECT ROUND(AVG(rating), 1) AS avg FROM ratings WHERE version_id = ?", version_id)[0]["avg"]

    if not version:
        abort(404)
        
    parsed_song = parse_content(version[0]["content"])


    return render_template("version.html", version=version[0], song_info=song_info[0], avg_rating=avg_rating, parsed_song=parsed_song, user=session["user_id"])

@app.route("/songs/<int:song_id>/workstation")
@login_required
def workstation(song_id):
    """Renders the workstation for creating or editing a song version.

    Args:
        song_id: The ID of the song.

    Returns:
        Response: Rendered workstation template, or redirect/error if invalid.

    Raises:
        None explicitly, but handles song/version not found.
    """
    song_info = db.execute("SELECT songs.id, songs.title, artists.name AS artist FROM songs JOIN artists on songs.artist_id = artists.id WHERE songs.id = ?", song_id)
    if not song_info:
        flash("Song not found")
        return redirect(url_for("songs"))

    # Check if editing an existing version
    version_number = request.args.get("version_number", type=int)
    content = ""
    is_edit = False
    if version_number:
        version = db.execute("SELECT content, creator_id FROM versions WHERE version_number = ? AND song_id = ?", version_number, song_id)
        if version:
            if version[0]["creator_id"] != session["user_id"]:
                flash("You can only edit your own versions.")
                return redirect(url_for("song", song_id=song_id))
            content = version[0]["content"]
            is_edit = True
        else:
            return redirect(url_for("song", song_id=song_id))

    return render_template("workstation.html", song_info=song_info[0], content=content, version_number=version_number if is_edit else None)

@app.route("/save_version/<int:song_id>", methods=["POST"])
@login_required
def save_version(song_id):
    """Saves a new version or updates an existing one for a song.

    Args:
        song_id: The ID of the song.

    Returns:
        Response: Redirect to the version view on success, or workstation with error.
    """
    content = request.form.get("content")
    if not content:
        song_info = db.execute("SELECT songs.id, songs.title, artists.name AS artist FROM songs JOIN artists ON songs.artist_id = artists.id WHERE songs.id = ?", song_id)
        flash("Content is required")
        return render_template("workstation.html", song_info=song_info[0], content=content)
    if len(content) > MAX_CONTENT_LENGTH:
        song_info = db.execute("SELECT songs.id, songs.title, artists.name AS artist FROM songs JOIN artists ON songs.artist_id = artists.id WHERE songs.id = ?", song_id)
        flash(f"Content must be {MAX_CONTENT_LENGTH} characters or less")
        return render_template("workstation.html", song_info=song_info[0], content=content)

    version_number = request.form.get("version_number", type=int)
    if version_number:
        db.execute("UPDATE versions SET content = ? WHERE version_number = ? AND song_id = ? AND creator_id = ?", content, version_number, song_id, session["user_id"])
    else: 
        version_number = db.execute("SELECT COALESCE(MAX(version_number), 0) + 1 AS next_version FROM versions WHERE song_id = ?", song_id)[0]["next_version"]
        db.execute("INSERT INTO versions (song_id, version_number, creator_id, content) VALUES (?, ?, ?, ?)", song_id, version_number, session["user_id"], content)

    version_id = db.execute("SELECT id FROM versions WHERE song_id = ? AND version_number = ? AND creator_id = ?", song_id, version_number, session["user_id"])[0]["id"]

    return redirect(url_for("version", song_id=song_id, version_id=version_id))

@app.route("/songs/<int:song_id>/versions/<int:version_id>/delete", methods=["POST"])
@login_required
def delete_version(song_id, version_id):
    """Deletes a specific version of a song if owned by the user.

    Args:
        song_id: The ID of the song.
        version_id: The ID of the version to delete.

    Returns:
        Response: Redirect to the song's versions list.

    Raises:
        404: If the version does not exist or is not owned by the user.
    """
    version = db.execute("SELECT id FROM versions WHERE id = ? AND song_id = ? AND creator_id = ?", version_id, song_id, session["user_id"])
    if not version:
        abort(404)

    db.execute("DELETE FROM versions WHERE id = ?", version_id)
    return redirect(url_for("song", song_id=song_id))

@app.route("/songs/add_song", methods=["GET", "POST"])
@login_required
def add_song():
    """Handles adding a new song.

    On GET, renders the add song form with artist/genre suggestions. On POST, creates or retrieves artist/genre and adds the song if unique.

    Returns:
        Response: Rendered template or redirect to the song page with flash message.
    """
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        artist_name = request.form.get("artist_name", "").strip()
        genre_name = request.form.get("genre_name", "").strip()

        if not title or not artist_name or not genre_name:
            flash("All fields are required")
            artists = db.execute("SELECT name FROM artists ORDER BY name")
            genres = db.execute("SELECT name FROM genres ORDER BY name")
            return render_template("add_song.html", artists=[a["name"] for a in artists], genres=[g["name"] for g in genres])
        
        if len(title) > MAX_TITLE_LENGTH:
            flash(f"Title must be {MAX_TITLE_LENGTH} characters or less")
            artists = db.execute("SELECT name FROM artists ORDER BY name")
            genres = db.execute("SELECT name FROM genres ORDER BY name")
            return render_template("add_song.html", artists=[a["name"] for a in artists], genres=[g["name"] for g in genres])
        
        if len(artist_name) > MAX_ARTIST_NAME_LENGTH:
            flash(f"Artist name must be {MAX_ARTIST_NAME_LENGTH} characters or less")
            artists = db.execute("SELECT name FROM artists ORDER BY name")
            genres = db.execute("SELECT name FROM genres ORDER BY name")
            return render_template("add_song.html", artists=[a["name"] for a in artists], genres=[g["name"] for g in genres])
        
        if len(genre_name) > MAX_GENRE_NAME_LENGTH:
            flash(f"Genre name must be {MAX_GENRE_NAME_LENGTH} characters or less")
            artists = db.execute("SELECT name FROM artists ORDER BY name")
            genres = db.execute("SELECT name FROM genres ORDER BY name")
            return render_template("add_song.html", artists=[a["name"] for a in artists], genres=[g["name"] for g in genres])

        # Get or create artist
        artist = db.execute("SELECT id FROM artists WHERE name = ?", artist_name)
        if artist:
            artist_id = artist[0]["id"]
        else:
            artist_id = db.execute("INSERT INTO artists (name) VALUES (?)", artist_name)
        
        # Get or create genre
        genre = db.execute("SELECT id FROM genres WHERE name = ?", genre_name)
        if genre:
            genre_id = genre[0]["id"]
        else:
            genre_id = db.execute("INSERT INTO genres (name) VALUES (?)", genre_name)

        # Create song
        existing_song = db.execute("SELECT id FROM songs WHERE title = ? AND artist_id = ? AND genre_id = ?", title, artist_id, genre_id)
        if existing_song:
            flash("Song already exists!")
            return redirect(url_for("song", song_id=existing_song[0]["id"]))
        else:
            db.execute("INSERT INTO songs (title, artist_id, genre_id) VALUES (?, ?, ?)", title, artist_id, genre_id)
            song_id = db.execute("SELECT id FROM songs WHERE title = ? AND artist_id = ? AND genre_id = ?", title, artist_id, genre_id)[0]["id"]
            flash("Song added successfully!")
            return redirect(url_for("song", song_id=song_id))

    artists = db.execute("SELECT name FROM artists ORDER BY name")
    genres = db.execute("SELECT name FROM genres ORDER BY name")
    return render_template("add_song.html", artists=[a["name"] for a in artists], genres=[g["name"] for g in genres])

@app.route("/search")
@login_required
def search():
    """Searches for songs by title, artist, or genre.

    Returns:
        Response: Rendered search results template, or redirect with flash if no query.
    """
    query = request.args.get("q", "").strip()

    if not query:
        flash("Please enter a search term.")
        return redirect(url_for("songs"))
    
    if len(query) > MAX_SEARCH_QUERY_LENGTH:
        flash(f"Search query must be {MAX_SEARCH_QUERY_LENGTH} characters or less.")
        return redirect(url_for("songs"))

    like = f"%{query}%"

    results = db.execute("""
        SELECT songs.id, songs.title, artists.name AS artist, genres.name AS genre
        FROM songs
        JOIN artists ON songs.artist_id = artists.id
        JOIN genres ON songs.genre_id = genres.id
        WHERE songs.title LIKE ? OR artists.name LIKE ? OR genres.name LIKE ?
        ORDER BY artists.name, songs.title
    """, like, like, like) 

    return render_template("search_results.html", query=query, results=results)
    
@app.route("/versions/<int:version_id>/rate", methods=["POST"])
@login_required
def rate_version(version_id):
    """Rates or updates a rating for a song version.

    Args:
        version_id: The ID of the version to rate.

    Returns:
        Response: Redirect to the version page with flash message.
    """
    # Get rating from form
    rating = request.form.get("rating", type=int)

    song_id = db.execute("SELECT song_id FROM versions WHERE id = ?", version_id)[0]["song_id"]

    if not rating or rating < 1 or rating > 5:
        flash("Invalid rating. Please select a rating between 1 and 5.")
        return redirect(url_for("version", song_id=song_id, version_id=version_id))

    # Check if user has already rated this version
    if db.execute("SELECT id FROM ratings WHERE version_id = ? AND user_id = ?", version_id, session["user_id"]):
        # Update existing rating
        db.execute("UPDATE ratings SET rating = ? WHERE version_id = ? AND user_id = ?", rating, version_id, session["user_id"])
        flash("Your rating has been updated.")
    else:
        # Insert new rating
        db.execute("INSERT INTO ratings (rating, version_id, user_id) VALUES (?, ?, ?)", rating, version_id, session["user_id"])
        flash("Your rating has been added.")

    return redirect(url_for("version", song_id=song_id, version_id=version_id))

if __name__ == "__main__":
    print("Starting Flask Server...")
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
