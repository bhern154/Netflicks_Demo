from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Movies, Watchlist, RecentlyViewed, Genres, MovieGenres, MovieImages, People, PeopleRoles, MoviePeople, Quotes, Reviews, Trailers, PlotSummary, StreamingAvailability
from forms import RegisterForm, LoginForm, SearchForm
from sqlalchemy.exc import IntegrityError
import requests
import time
from credentials import SecretKey, APIKey

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///netflicks_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SecretKey
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# ---- Uncomment the line below if you want to see the debug toolbar
# toolbar = DebugToolbarExtension(app)

# --------------- HOME ROUTES ---------------

@app.route('/')
def home_page():
    """Redirect the root URL to the home page."""
    return redirect('/home')

@app.route('/home')
def home():
    """Render the home page with movie data from various genres."""

    # Check if there are any movies in the database; if not, initialize the home page data.
    if not Movies.query.first():
        # Makes a call to the API for each genre to display on the home page
        setup_home_page()

    # Query to get the latest movies, joining with MovieImages to get image data.
    latest_movies = (db.session.query(Movies)
          .join(MovieImages, Movies.imdbid == MovieImages.imdbid)
          .filter(Movies.type == 'movie')
          .order_by(Movies.numvotes.asc())
          .order_by(Movies.released.desc())
          .limit(100)
          .all())

    # Fetch movies for each genre from the database
    action_movies = get_movies_from_genre('Action')
    adventure_movies = get_movies_from_genre('Adventure')
    animation_movies = get_movies_from_genre('Animation')
    comedy_movies = get_movies_from_genre('Comedy')
    crime_movies = get_movies_from_genre('Crime')
    drama_movies = get_movies_from_genre('Drama')
    family_movies = get_movies_from_genre('Family')
    fantasy_movies = get_movies_from_genre('Fantasy')
    horror_movies = get_movies_from_genre('Horror')
    mystery_movies = get_movies_from_genre('Mystery')
    romance_movies = get_movies_from_genre('Romance')
    sci_fi_movies = get_movies_from_genre('Sci-Fi')
    sport_movies = get_movies_from_genre('Sport')
    thriller_movies = get_movies_from_genre('Thriller')
    war_movies = get_movies_from_genre('War')

    # Create a dictionary to organize movie data by category.
    movie_data = {
        'LATEST ARRIVALS (2020)' : latest_movies,
        'ACTION' : action_movies,
        'ADVENTURE' : adventure_movies,
        'ANIMATION' : animation_movies,
        'COMEDY' : comedy_movies,
        'CRIME' : crime_movies,
        'DRAMA' : drama_movies,
        'FAMILY' : family_movies,
        'FANTASY' : fantasy_movies,
        'HORROR' : horror_movies,
        'MYSTERY' : mystery_movies,
        'ROMANCE' : romance_movies,
        'SCI-FI' : sci_fi_movies,
        'SPORT' : sport_movies,
        'THRILLER' : thriller_movies,
        'WAR' : war_movies
    }
    
    # Render the 'home.html' template, passing the movie data to be displayed.
    return render_template('home.html', movie_data=movie_data)

# ------------------------- API CALLS -------------------------

# Fetch and display movie results based on the selected genre and page number.
@app.route('/api/genre/<string:genre>/<string:page>', methods=["GET", "POST"])
def get_genre_results(genre, page):
    """
    Fetch and display movie results based on the selected genre and page number.

    Args:
        genre (str): The genre of the movies to display.
        page (str): The page number for paginated results.
    """

    # Get movie recommendations based on the genre and page number
    results = get_genre_recommendations(genre, page)

    # Query the database to get movie details for the recommended IMDb IDs
    movies = (db.session.query(Movies)
          .join(MovieGenres, Movies.imdbid == MovieGenres.imdbid)
          .join(Genres, MovieGenres.genre_id == Genres.genre_id)
          .join(MovieImages, Movies.imdbid == MovieImages.imdbid)
          .filter(Movies.imdbid.in_(results))  # Filter by IMDb IDs
          .all())

    # Render the 'genre_results.html' template with the movies, genre, and page data
    return render_template('genre_results.html', genre=genre, page=page, movies=movies)

# ----------------- SEARCH FOR MOVIE USING THE API -----------------
@app.route('/api/search', methods=["POST"])
def get_search_results():
    """
    Handle search requests for movies using the OTT Details API.
    """
    search = request.form["search"]  # Get search term from form

    try:
        # API request setup
        url = f'https://ott-details.p.rapidapi.com/search?title={search}&page=1'
        headers = {
            'X-RapidAPI-Key': APIKey,
            'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
        }

        # Fetch and parse API response
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # Existing IMDb IDs in database
        existing_imdbids = {movie.imdbid for movie in Movies.query.all()}
        search_imdbids = []

        # Insert new data into the database
        for item in response_data.get('results', []):
            imdbid = item.get('imdbid')
            search_imdbids.append(imdbid)

            if imdbid in existing_imdbids:
                continue  # Skip if movie already exists

            # Add movie
            movie = Movies(
                imdbid=imdbid,
                title=item.get('title'),
                imdbrating=item.get('imdbrating'),
                released=item.get('released'),
                synopsis=item.get('synopsis'),
                type=item.get('type')
            )
            db.session.add(movie)

            # Add genres
            for genre_name in item.get('genre', []):
                genre = Genres.query.filter_by(genre_name=genre_name).first()
                if not genre:
                    genre = Genres(genre_name=genre_name)
                    db.session.add(genre)
                    db.session.flush()  # Populate genre_id
                movie_genre = MovieGenres(imdbid=imdbid, genre_id=genre.genre_id)
                db.session.add(movie_genre)

            # Add images
            for image_url in item.get('imageurl', []):
                # Construct original image URL
                last_dot_index = image_url.rfind('.')
                second_last_dot_index = image_url.rfind('.', 0, last_dot_index)
                new_image_url = image_url[:second_last_dot_index + 1] + '' + image_url[last_dot_index:]
                movie_image = MovieImages(imdbid=imdbid, image_url=new_image_url)
                db.session.add(movie_image)

        db.session.commit()  # Save changes

        # Query and render movies based on search results
        movies = (db.session.query(Movies)
                .filter(Movies.imdbid.in_(search_imdbids))
                .order_by(Movies.released.desc())
                .limit(50)
                .all())
        return render_template('search_results.html', search=search, movies=movies)

    except requests.exceptions.RequestException as e:
        flash(f'An error occurred while fetching data: {e}')
    except Exception as e:
        flash(f'An error occurred: {e}')

    return render_template('search_results.html')

# -------- GET MOVIES BY GENRE FROM API ----------
def get_genre_recommendations(genre, page):
    result_imdbids = []

    try:
        # API takes blank input for New Arrivals
        if genre == 'New Arrivals':
            genre = ''

        url = 'https://ott-details.p.rapidapi.com/advancedsearch'
        querystring = {
            'start_year': '2016',
            'end_year': '2020',
            'min_imdb': '7.5',
            'genre': genre,
            'language': 'english',
            'sort': 'latest',
            'page': page
        }
        headers = {
            'X-RapidAPI-Key': APIKey,
            'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        response_data = response.json()

        existing_imdbids = {movie.imdbid for movie in Movies.query.all()}

        # Insert data from the JSON response to the database
        for item in response_data.get('results', []):
            # Check if the movie already exists in the database
            imdbid = item.get('imdbid')
            result_imdbids.append(imdbid)

            if imdbid in existing_imdbids:
                print(f"Movie with imdbid {imdbid} already exists. Skipping.")
                continue

            # Add items to the 'Movies' table
            movie = Movies(
                imdbid=item.get('imdbid'),
                title=item.get('title'),
                imdbrating=item.get('imdbrating'),
                released=item.get('released'),
                synopsis=item.get('synopsis'),
                type=item.get('type')
            )

            db.session.add(movie)

            # Add items to the Genre and MovieGenre Tables
            for genre_name in item.get('genre', []):
                genre = Genres.query.filter_by(genre_name=genre_name).first()
                if not genre:
                    genre = Genres(genre_name=genre_name)
                    db.session.add(genre)
                    # Ensure the genre_id is populated so that MovieGenre can access it
                    db.session.flush()
                if not MovieGenres.query.filter_by(imdbid=movie.imdbid, genre_id=genre.genre_id).first():
                    movie_genre = MovieGenres(imdbid=movie.imdbid, genre_id=genre.genre_id)
                    db.session.add(movie_genre)

            # Add items to the MovieImages Table
            for image_url in item.get('imageurl', []):
                # Find the index of the second to last '.'
                last_dot_index = image_url.rfind('.')
                second_last_dot_index = image_url.rfind('.', 0, last_dot_index)
                # remove the substring '_V1_UY600_CR900,0,600,900_AL_' to get the original image
                new_image_url = image_url[:second_last_dot_index + 1] + '' + image_url[last_dot_index:]
                if not MovieImages.query.filter_by(imdbid=movie.imdbid, image_url=new_image_url).first():
                    movie_image = MovieImages(imdbid=movie.imdbid, image_url=new_image_url)
                    db.session.add(movie_image)

        db.session.commit()

    except requests.exceptions.RequestException as e:
        flash(f'An error occurred while fetching data: {e}')
    except Exception as e:
        db.session.rollback()
        flash(f'An unexpected error occurred: {e}')
    
    return result_imdbids


# -------- GET MOVIE DETAILS FROM API ----------
@app.route('/movie-details-<string:imdbid>', methods=['GET'])
def get_movie_details(imdbid):
    """
    Fetch movie details using the API and display them.

    Args:
        imdbid (str): The IMDb ID of the movie.

    Returns:
        Rendered template with movie details.
    """
    movie = Movies.query.get(imdbid)

    # Don't call API if we already stored details in db
    if movie and movie.api_called:
        add_to_recently_viewed(imdbid)
        return render_template('movie_details.html', movie=movie)

    # Fetch and update primary movie details
    fetch_and_update_movie_details(imdbid)

    # wait for 2 second because API only accepts one call per second
    time.sleep(2)

    # Fetch and update additional movie details
    fetch_and_update_additional_movie_details(imdbid)

    return render_template('movie_details.html', movie=Movies.query.get(imdbid))

def fetch_and_update_movie_details(imdbid):
    """
    Fetch primary movie details from the API and update the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
    """
    try:
        url = f"https://ott-details.p.rapidapi.com/gettitleDetails?imdbid={imdbid}"
        headers = {
            'X-RapidAPI-Key': APIKey,
            'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        movie_data = response.json()

        movie = Movies.query.get(imdbid)
        if not movie:
            movie = Movies(imdbid=imdbid)
            db.session.add(movie)

        movie.title = movie_data.get('title', movie.title)
        movie.imdbrating = movie_data.get('imdbrating', movie.imdbrating)
        movie.released = movie_data.get('released', movie.released)
        movie.synopsis = movie_data.get('synopsis', movie.synopsis)
        movie.type = movie_data.get('type', movie.type)
        movie.runtime = movie_data.get('runtime', movie.runtime)
        movie.language = ', '.join(movie_data.get('language', [])) if movie_data.get('language') else movie.language
        movie.numvotes = movie_data.get('numvotes', movie.numvotes)

        update_movie_images(imdbid, movie_data.get('imageurl', []))
        update_movie_genres(imdbid, movie_data.get('genre', []))
        update_streaming_availability(imdbid, movie_data.get('streamingAvailability', {}).get('country', {}).get('US', []))

        db.session.commit()

    except requests.exceptions.RequestException as e:
        flash(f"Error fetching movie details from API: {e}")
    except Exception as e:
        db.session.rollback()
        flash(f"Unexpected error: {e}")

def fetch_and_update_additional_movie_details(imdbid):
    """
    Fetch additional movie details from the API and update the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
    """
    try:
        url = f"https://ott-details.p.rapidapi.com/getadditionalDetails?imdbid={imdbid}"
        headers = {
            'X-RapidAPI-Key': APIKey,
            'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        movie_data = response.json()

        movie = Movies.query.get(imdbid)
        if movie:
            movie.title = movie_data.get('title', movie.title)
            movie.numvotes = movie_data.get('numVotes', movie.numvotes)
            movie.api_called = True
        else:
            movie = Movies(imdbid=imdbid, title=movie_data.get('title'), numvotes=movie_data.get('numVotes'), api_called=True)
            db.session.add(movie)

        update_people_and_roles(imdbid, movie_data.get('people', []))
        update_quotes(imdbid, movie_data.get('quotes', []))
        update_reviews(imdbid, movie_data.get('reviews', []))
        update_trailers(imdbid, movie_data.get('trailerUrl', []))
        update_plot_summary(imdbid, movie_data.get('plotSummary'))

        db.session.commit()

    except requests.exceptions.RequestException as e:
        flash(f"Error fetching additional movie details from API: {e}")
    except Exception as e:
        db.session.rollback()
        flash(f"Unexpected error: {e}")

def update_movie_images(imdbid, images):
    """
    Update movie images in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        images (list): List of image URLs.
    """
    for image_url in images:
        if not MovieImages.query.filter_by(imdbid=imdbid, image_url=image_url).first():
            db.session.add(MovieImages(imdbid=imdbid, image_url=image_url))

def update_movie_genres(imdbid, genres):
    """
    Update movie genres in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        genres (list): List of genre names.
    """
    for genre_name in genres:
        genre = Genres.query.filter_by(genre_name=genre_name).first()
        if not genre:
            genre = Genres(genre_name=genre_name)
            db.session.add(genre)
            db.session.commit()

        if not MovieGenres.query.filter_by(imdbid=imdbid, genre_id=genre.genre_id).first():
            db.session.add(MovieGenres(imdbid=imdbid, genre_id=genre.genre_id))

def update_streaming_availability(imdbid, streaming_data):
    """
    Update streaming availability in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        streaming_data (list): List of streaming availability information.
    """
    for stream in streaming_data:
        platform = stream.get('platform')
        url = stream.get('url')
        if not StreamingAvailability.query.filter_by(imdbid=imdbid, platform=platform).first():
            db.session.add(StreamingAvailability(imdbid=imdbid, platform=platform, link=url))

def update_people_and_roles(imdbid, people):
    """
    Update people and their roles in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        people (list): List of people involved in the movie.
    """
    for person in people:
        peopleid = person.get('peopleid')
        existing_person = People.query.get(peopleid)
        if not existing_person:
            new_person = People(peopleid=peopleid, name="Unknown")
            db.session.add(new_person)
            db.session.commit()

        if not PeopleRoles.query.filter_by(peopleid=peopleid, role=person.get('category')).first():
            db.session.add(PeopleRoles(peopleid=peopleid, role=person.get('category')))

        if not MoviePeople.query.filter_by(imdbid=imdbid, peopleid=peopleid, category=person.get('category')).first():
            db.session.add(MoviePeople(
                imdbid=imdbid,
                peopleid=peopleid,
                category=person.get('category'),
                job=person.get('job'),
                characters=person.get('characters')
            ))

def update_quotes(imdbid, quotes):
    """
    Update movie quotes in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        quotes (list): List of movie quotes.
    """
    for quote_text in quotes:
        db.session.add(Quotes(imdbid=imdbid, quote=quote_text))

def update_reviews(imdbid, reviews):
    """
    Update movie reviews in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        reviews (list): List of movie reviews.
    """
    for review_text in reviews:
        db.session.add(Reviews(imdbid=imdbid, review=review_text))

def update_trailers(imdbid, trailer_urls):
    """
    Update movie trailers in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        trailer_urls (list): List of trailer URLs.
    """
    for url in trailer_urls:
        db.session.add(Trailers(imdbid=imdbid, trailer_url=url))

def update_plot_summary(imdbid, plot_summary):
    """
    Update plot summary in the database.

    Args:
        imdbid (str): The IMDb ID of the movie.
        plot_summary (str): Plot summary of the movie.
    """
    db.session.add(PlotSummary(imdbid=imdbid, summary=plot_summary))

# --------------- HELPER FUNCTIONS ---------------

def get_movies_from_genre(genre):
    """Fetch a list of movies from a specific genre. Returns a list of movies from the specified genre."""
        
    # Query to fetch movies of a specific genre.
    movies = (db.session.query(Movies)
          .join(MovieGenres, Movies.imdbid == MovieGenres.imdbid)
          .join(Genres, MovieGenres.genre_id == Genres.genre_id)
          .join(MovieImages, Movies.imdbid == MovieImages.imdbid)
          .filter(Genres.genre_name == genre) 
          .order_by(Movies.numvotes.asc())
          .order_by(Movies.released.desc())
          .limit(60)
          .all())
        
    return movies

def setup_home_page():
    """Initialize the home page by fetching genre recommendations."""

    # List of genres to fetch recommendations for
    genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy', 'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War']

    # Fetch recommendations for each genre with a delay between requests
    for genre in genres:
        get_genre_recommendations(genre, 1)  # Fetch recommendations for the genre
        time.sleep(2)  # 2 second delay because the API only accepts 1 request per second

    return

# --------------- USER ROUTES ---------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        # encript the password
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        
        #redirect to form if registration info is invalid
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        
        # store the user in a session
        session['username'] = new_user.username

        flash('Welcome! Successfully Created Your Account!')

        return redirect(f'/home')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # get encripted password
        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = user.username
            return redirect(f'/home')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!")
    return redirect('/')

@app.route('/user/account')
def show_user():
   
    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')

    return render_template('user.html', user=user)
    
@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):

    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')

    db.session.delete(user)
    db.session.commit()

    session.pop('username')
    flash('User deleted successfully!', 'info')
    return redirect('/')

@app.route('/users/watchlist/<string:imdbid>', methods=["GET", "POST"])
def add_to_watchlist(imdbid):
    """Add or remove watchlist item for the user."""

    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')
    user_id = user.user_id

    # Check if the item already exists in the watchlist
    watchlist_item = Watchlist.query.filter_by(user_id=user_id, imdbid=imdbid).first()

    if watchlist_item:
        # If the item exists, remove it from the watchlist
        db.session.delete(watchlist_item)
        db.session.commit()
        flash(f"Removed {imdbid} from your watchlist", "success")
    else:
        # If the item doesn't exist, add it to the watchlist
        new_watchlist_item = Watchlist(user_id=user_id, imdbid=imdbid)
        db.session.add(new_watchlist_item)
        db.session.commit()
        flash(f"Added {imdbid} to your watchlist", "success")

    return redirect(request.referrer or '/')

@app.route('/users/watchlist')
def user_watchlist():
    """Show a user's watchlist."""

    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')
    user_id = user.user_id

    # Query all IMDb IDs from the user's watchlist
    watchlist_imdbids = Watchlist.query.filter_by(user_id=user_id).with_entities(Watchlist.imdbid).all()

    # Extract IMDb IDs from the result
    imdbids = [item.imdbid for item in watchlist_imdbids]

    movies = (db.session.query(Movies)
          .join(MovieGenres, Movies.imdbid == MovieGenres.imdbid)
          .join(Genres, MovieGenres.genre_id == Genres.genre_id)
          .join(MovieImages, Movies.imdbid == MovieImages.imdbid)
          .filter(Movies.imdbid.in_(imdbids))  # Filter by IMDb IDs
          .all())

    return render_template('watchlist.html', movies=movies)

@app.route('/users/watchlist/empty')
def empty_user_watchlist():
    """Delete a user's watchlist."""

    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')
    user_id = user.user_id

    Watchlist.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    flash("Your watchlist has been emptied!")
    return render_template('watchlist.html')

def add_to_recently_viewed(imdbid):
    """Add movie to user's recently viewed."""

    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')
    user_id = user.user_id

    recentlyViewed_item = RecentlyViewed.query.filter_by(user_id=user_id, imdbid=imdbid).first()

    if not recentlyViewed_item:
        new_recentlyViewed_item = RecentlyViewed(user_id=user_id, imdbid=imdbid)
        db.session.add(new_recentlyViewed_item)
        db.session.commit()
    
    return

@app.route('/users/recently-viewed')
def user_recently_viewed():
    """Show a user's recently viewed."""

    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')
    user_id = user.user_id

    # Query all IMDb IDs from the user's recently viewed
    recentlyViewed_imdbids = RecentlyViewed.query.filter_by(user_id=user_id).with_entities(RecentlyViewed.imdbid).all()

    # Extract IMDb IDs from the query result
    imdbids = [item.imdbid for item in recentlyViewed_imdbids]

    # Query movies from the Movies table based on IMDb IDs
    movies = (db.session.query(Movies)
              .join(MovieGenres, Movies.imdbid == MovieGenres.imdbid)
              .join(Genres, MovieGenres.genre_id == Genres.genre_id)
              .join(MovieImages, Movies.imdbid == MovieImages.imdbid)
              .filter(Movies.imdbid.in_(imdbids))  # Filter by IMDb IDs
              .all())

    return render_template('recently_viewed.html', movies=movies)

@app.route('/users/recently-viewed/empty')
def empty_user_recentlyViewed():
    """Delete a user's recently viewed."""

    # Make sure user is logged in 
    if "username" not in session:
        flash("Please login first!", "info")
        return redirect(request.referrer or '/')
    username = session['username']
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User not found!", "error")
        return redirect(request.referrer or '/')
    user_id = user.user_id

    RecentlyViewed.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    flash("Your recenly viewed has been emptied!")
    return render_template('recently_viewed.html')