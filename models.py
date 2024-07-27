from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database and create tables if they don't already exist."""
    db.app = app
    db.init_app(app)

    with app.app_context():
        try:
            # Query to check if the 'movies' table exists
            result = db.session.execute(text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'movies'
                );
                """
            ))
            table_exists = result.scalar()

            if table_exists:
                print("Table 'movies' already exists.")
            else:
                # If the 'movies' table does not exist, create all tables
                print("Table 'movies' does not exist. Creating tables...")
                db.create_all()
        except OperationalError as e:
            # Handle operational errors
            print(f"OperationalError: {e}")

# User Model
class User(db.Model):
    __tablename__ = "Users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(pwd)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct."""
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False

    def __repr__(self):
        return f"<User id={self.user_id} username={self.username} email={self.email}>"

# Movies Model
class Movies(db.Model):
    __tablename__ = 'movies'
    imdbid = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(255))
    imdbrating = db.Column(db.Numeric(3, 1))
    released = db.Column(db.Integer)
    synopsis = db.Column(db.Text)
    type = db.Column(db.String(20))
    runtime = db.Column(db.String(20))
    language = db.Column(db.String(50))
    numvotes = db.Column(db.Integer)
    api_called = db.Column(db.Boolean, default=False)

    images = relationship("MovieImages", backref="movie")
    summary = relationship("PlotSummary", backref="movie")
    streaming_availability = relationship("StreamingAvailability", backref="movie")
    trailers = relationship("Trailers", backref="movie")
    quotes = relationship("Quotes", backref="movie")
    reviews = relationship("Reviews", backref="movie")
    genres = relationship("Genres", secondary="moviegenres", back_populates="movies")

    def __repr__(self):
        return f"<Movies imdbid={self.imdbid} title={self.title}>"

# Watchlist Model
class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    watchlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'), nullable=False)

    def __repr__(self):
        return f"<Watchlist id={self.watchlist_id} user_id={self.user_id} imdbid={self.imdbid}>"

# RecentlyViewed Model
class RecentlyViewed(db.Model):
    __tablename__ = 'recentlyviewed'
    recently_viewed_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'), nullable=False)

    def __repr__(self):
        return f"<RecentlyViewed id={self.recently_viewed_id} user_id={self.user_id} imdbid={self.imdbid}>"

# Genres Model
class Genres(db.Model):
    __tablename__ = 'genres'
    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre_name = db.Column(db.String(50), unique=True)

    movies = relationship("Movies", secondary="moviegenres", back_populates="genres")

    def __repr__(self):
        return f"<Genres id={self.genre_id} genre_name={self.genre_name}>"

# MovieGenres Model
class MovieGenres(db.Model):
    __tablename__ = 'moviegenres'
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'), primary_key=True)

    def __repr__(self):
        return f"<MovieGenres imdbid={self.imdbid} genre_id={self.genre_id}>"

# MovieImages Model
class MovieImages(db.Model):
    __tablename__ = 'movieimages'
    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'))
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f"<MovieImages id={self.image_id} imdbid={self.imdbid} image_url={self.image_url}>"

# People Model
class People(db.Model):
    __tablename__ = 'people'
    peopleid = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255))

    def __repr__(self):
        return f"<People id={self.peopleid} name={self.name}>"

# PeopleRoles Model
class PeopleRoles(db.Model):
    __tablename__ = 'peopleroles'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    peopleid = db.Column(db.String(20), db.ForeignKey('people.peopleid'))
    role = db.Column(db.String(50))

    def __repr__(self):
        return f"<PeopleRoles id={self.role_id} peopleid={self.peopleid} role={self.role}>"

# MoviePeople Model
class MoviePeople(db.Model):
    __tablename__ = 'moviepeople'
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'), primary_key=True)
    peopleid = db.Column(db.String(20), db.ForeignKey('people.peopleid'), primary_key=True)
    category = db.Column(db.String(50), primary_key=True)
    job = db.Column(db.String(255))
    characters = db.Column(db.JSON)

    def __repr__(self):
        return f"<MoviePeople imdbid={self.imdbid} peopleid={self.peopleid} category={self.category} job={self.job}>"

# Quotes Model
class Quotes(db.Model):
    __tablename__ = 'quotes'
    quote_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'))
    quote = db.Column(db.Text)

    def __repr__(self):
        return f"<Quotes id={self.quote_id} imdbid={self.imdbid} quote={self.quote}>"

# Reviews Model
class Reviews(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'))
    review = db.Column(db.Text)

    def __repr__(self):
        return f"<Reviews id={self.review_id} imdbid={self.imdbid} review={self.review}>"

# Trailers Model
class Trailers(db.Model):
    __tablename__ = 'trailers'
    trailer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'))
    trailer_url = db.Column(db.String(255))

    def __repr__(self):
        return f"<Trailers id={self.trailer_id} imdbid={self.imdbid} trailer_url={self.trailer_url}>"

# PlotSummary Model
class PlotSummary(db.Model):
    __tablename__ = 'plotsummary'
    summary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'))
    summary = db.Column(db.Text)

    def __repr__(self):
        return f"<PlotSummary id={self.summary_id} imdbid={self.imdbid} summary={self.summary}>"

# StreamingAvailability Model
class StreamingAvailability(db.Model):
    __tablename__ = 'streamingavailability'
    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imdbid = db.Column(db.String(20), db.ForeignKey('movies.imdbid'))
    country = db.Column(db.String(50))
    platform = db.Column(db.String(50))
    link = db.Column(db.String(255))

    def __repr__(self):
        return f"<StreamingAvailability id={self.availability_id} imdbid={self.imdbid} country={self.country} platform={self.platform}> link={self.link}"