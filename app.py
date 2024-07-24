from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Movies, Watchlist, RecentlyViewed, Genres, MovieGenres, MovieImages, People, PeopleRoles, MoviePeople, Quotes, Reviews, Trailers, PlotSummary, StreamingAvailability
from forms import RegisterForm, LoginForm, SearchForm
from sqlalchemy.exc import IntegrityError
import requests
import time
from credentials import SecretKey, APIKey

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///movies_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SecretKey
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

# Uncomment the line below if you want to see the debug toolbar
# toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/home')

@app.route('/home')
def home():

    if not Movies.query.first():
        setup_home_page()

    latest_movies = (db.session.query(Movies)
          .join(MovieImages, Movies.imdbid == MovieImages.imdbid)
          .filter(Movies.type == 'movie')
          .order_by(Movies.numvotes.asc())
          .order_by(Movies.released.desc())
          .limit(100)
          .all())

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
    
    return render_template('home.html', movie_data=movie_data)

def get_movies_from_genre(genre):
        
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

    get_genre_recommendations('Action', 1)
    time.sleep(2)
    get_genre_recommendations('Adventure', 1)
    time.sleep(2)
    get_genre_recommendations('Animation', 1)
    time.sleep(2)
    get_genre_recommendations('Comedy', 1)
    time.sleep(2)
    get_genre_recommendations('Crime', 1)
    time.sleep(2)
    get_genre_recommendations('Drama', 1)
    time.sleep(2)
    get_genre_recommendations('Family', 1)
    time.sleep(2)
    get_genre_recommendations('Fantasy', 1)
    time.sleep(2)
    get_genre_recommendations('Horror', 1)
    time.sleep(2)
    get_genre_recommendations('Mystery', 1)
    time.sleep(2)
    get_genre_recommendations('Romance', 1)
    time.sleep(2)
    get_genre_recommendations('Sci-Fi', 1)
    time.sleep(2)
    get_genre_recommendations('Sport', 1)
    time.sleep(2)
    get_genre_recommendations('Thriller', 1)
    time.sleep(2)
    get_genre_recommendations('War', 1)
    time.sleep(2)

    return 

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

        flash('Welcome! Successfully Created Your Account!', "success")

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
    flash("Goodbye!", "info")
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

# ------------------------- API CALLS -------------------------


@app.route('/api/genre/<string:genre>/<string:page>', methods=["GET", "POST"])
def get_genre_results(genre, page):

    results = get_genre_recommendations(genre, page)

    movies = (db.session.query(Movies)
          .join(MovieGenres, Movies.imdbid == MovieGenres.imdbid)
          .join(Genres, MovieGenres.genre_id == Genres.genre_id)
          .join(MovieImages, Movies.imdbid == MovieImages.imdbid)
          .filter(Movies.imdbid.in_(results))  # Filter by IMDb IDs
          .all())

    return render_template('genre_results.html', genre=genre, page=page, movies=movies)

# -------- SEARCH FOR MOVIE --------
@app.route('/api/search', methods=["POST"])
def get_search_results():

    search = request.form["search"]

    try:
        url = f'https://ott-details.p.rapidapi.com/search?title={search}&page=1'
        headers = {
            'X-RapidAPI-Key': APIKey,
            'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        existing_imdbids = {movie.imdbid for movie in Movies.query.all()}
        search_imdbids = []

        # Insert data from the JSON response to the database
        for item in response_data.get('results', []):

            search_imdbids.append(item.get('imdbid'))

            # Check if the movie already exists in the database
            imdbid = item.get('imdbid')
            if imdbid in existing_imdbids:
                print(f"Movie with imdbid {imdbid} already exists. Skipping.")
                continue

            #Add items to the 'Movies' table
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
                movie_genre = MovieGenres(imdbid=movie.imdbid, genre_id=genre.genre_id)
                db.session.add(movie_genre)

            # Add items to the MovieImages Table
            for image_url in item.get('imageurl', []):
                # Find the index of the second to last '.'
                last_dot_index = image_url.rfind('.')
                second_last_dot_index = image_url.rfind('.', 0, last_dot_index)
                # remove the substring '_V1_UY600_CR900,0,600,900_AL_' to get the original image
                new_image_url = image_url[:second_last_dot_index + 1] + '' + image_url[last_dot_index:]
                movie_image = MovieImages(imdbid=movie.imdbid, image_url=new_image_url)
                db.session.add(movie_image)

        db.session.commit()

    except requests.exceptions.RequestException as e:
        flash(f'An error occurred while fetching data, {e}')
        return render_template('search_results.html')
    
    try:
        # Query movies filtered by search_imdbids
        movies = (db.session.query(Movies)
                .filter(Movies.imdbid.in_(search_imdbids))
                .order_by(Movies.released.desc())
                .limit(50)
                .all())
        
        return render_template('search_results.html', search=search, movies=movies)

    except Exception as e:
        flash(f'An error occurred while fetching data, {e}')

    render_template('search_results.html')

# -------- GET MOVIES BY GENRE FROM API ----------
def get_genre_recommendations(genre, page):
    result_imdbids = []

    try:
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
        flash(f'An error occurred while fetching data: {e}', "error")
    except Exception as e:
        db.session.rollback()
        flash(f'An unexpected error occurred: {e}', "error")
    
    return result_imdbids


# -------- GET MOVIES DETAILS FROM API ----------
@app.route('/movie-details-<string:imdbid>', methods=['GET'])
def get_movie_details(imdbid):
    movie = Movies.query.get(imdbid)

    # Don't call API if we already stored details in db
    if movie and movie.api_called:
        # Add to recently viewed if logged in
        add_to_recently_viewed(imdbid)
        return render_template('movie_details.html', movie=movie)

    try:
        url = f"https://ott-details.p.rapidapi.com/gettitleDetails?imdbid={imdbid}"
        headers = {
            'X-RapidAPI-Key': APIKey,
            'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        movie_data = response.json()
        title = movie_data.get('title')
        imdb_rating = movie_data.get('imdbrating')
        released = movie_data.get('released')
        synopsis = movie_data.get('synopsis')
        movie_type = movie_data.get('type')
        runtime = movie_data.get('runtime')
        language = ', '.join(movie_data.get('language', []))
        numvotes = movie_data.get('numvotes')
        images = movie_data.get('imageurl', [])
        streaming_data = movie_data.get('streamingAvailability', {}).get('country', {}).get('US', [])
        genres = movie_data.get('genre', [])

        if movie:
            movie.title = title or movie.title
            movie.imdbrating = imdb_rating or movie.imdbrating
            movie.released = released or movie.released
            movie.synopsis = synopsis or movie.synopsis
            movie.type = movie_type or movie.type
            movie.runtime = runtime or movie.runtime
            movie.language = language or movie.language
            movie.numvotes = numvotes or movie.numvotes
        else:
            movie = Movies(
                imdbid=imdbid,
                title=title,
                imdbrating=imdb_rating,
                released=released,
                synopsis=synopsis,
                type=movie_type,
                runtime=runtime,
                language=language,
                numvotes=numvotes
            )
            db.session.add(movie)
        db.session.commit()

        for image_url in images:
            if not MovieImages.query.filter_by(imdbid=imdbid, image_url=image_url).first():
                db.session.add(MovieImages(imdbid=imdbid, image_url=image_url))

        for genre_name in genres:
            genre = Genres.query.filter_by(genre_name=genre_name).first() or Genres(genre_name=genre_name)
            db.session.add(genre)
            db.session.commit()

            if not MovieGenres.query.filter_by(imdbid=imdbid, genre_id=genre.genre_id).first():
                db.session.add(MovieGenres(imdbid=imdbid, genre_id=genre.genre_id))

        for stream in streaming_data:
            platform = stream.get('platform')
            url = stream.get('url')
            if not StreamingAvailability.query.filter_by(imdbid=imdbid, platform=platform).first():
                db.session.add(StreamingAvailability(imdbid=imdbid, platform=platform, link=url))

        db.session.commit()

    except requests.exceptions.RequestException as e:
        flash(f"Error fetching movie details from API: {e}")
    except Exception as e:
        db.session.rollback()
        flash(f"Unexpected error: {e}")
    
    time.sleep(2)

    try:
        url = f"https://ott-details.p.rapidapi.com/getadditionalDetails?imdbid={imdbid}"
        headers = {
            'X-RapidAPI-Key': APIKey,
            'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        movie_data = response.json()
        title = movie_data.get('title')
        numvotes = movie_data.get('numVotes')
        plot_summary = movie_data.get('plotSummary')
        quotes = movie_data.get('quotes', [])
        reviews = movie_data.get('reviews', [])
        trailer_urls = movie_data.get('trailerUrl', [])

        if movie:
            movie.title = title or movie.title
            movie.numvotes = numvotes or movie.numvotes
            movie.api_called = True
        else:
            movie = Movies(
                imdbid=imdbid,
                title=title,
                numvotes=numvotes,
                api_called=True
            )
            db.session.add(movie)

        for person in movie_data.get('people', []):
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

        for quote_text in quotes:
            db.session.add(Quotes(imdbid=imdbid, quote=quote_text))

        for review_text in reviews:
            db.session.add(Reviews(imdbid=imdbid, review=review_text))

        for url in trailer_urls:
            db.session.add(Trailers(imdbid=imdbid, trailer_url=url))

        db.session.add(PlotSummary(imdbid=imdbid, summary=plot_summary))

        db.session.commit()

    except requests.exceptions.RequestException as e:
        flash(f"Error fetching additional movie details from API: {e}")
    except Exception as e:
        db.session.rollback()
        flash(f"Unexpected error: {e}")
    
    return render_template('movie_details.html', movie=Movies.query.get(imdbid))