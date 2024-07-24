DROP DATABASE IF EXISTS movies_db;

CREATE DATABASE movies_db;

\c movies_db

-- TABLES FOR MOVIES API (https://rapidapi.com/gox-ai-gox-ai-default/api/ott-details)

CREATE TABLE Movies (
    imdbid VARCHAR(20) PRIMARY KEY,
    title VARCHAR(255),
    imdbrating DECIMAL(3,1),
    released INT,
    synopsis TEXT,
    type VARCHAR(20),
    runtime VARCHAR(20),
    language VARCHAR(50),
    numVotes INT,
    API_Called BOOLEAN DEFAULT FALSE
);

CREATE TABLE Genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(50) UNIQUE
);

CREATE TABLE MovieGenres (
    imdbid VARCHAR(20),
    genre_id INT,
    PRIMARY KEY (imdbid, genre_id),
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) ,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) 
);

CREATE TABLE MovieImages (
    image_id SERIAL PRIMARY KEY,
    imdbid VARCHAR(20),
    image_url VARCHAR(255),
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) 
);

CREATE TABLE People (
    peopleid VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE PeopleRoles (
    role_id SERIAL PRIMARY KEY,
    peopleid VARCHAR(20),
    role VARCHAR(50),
    FOREIGN KEY (peopleid) REFERENCES People(peopleid) 
);

CREATE TABLE MoviePeople (
    imdbid VARCHAR(20),
    peopleid VARCHAR(20),
    category VARCHAR(50),
    job VARCHAR(255),
    characters JSON,
    PRIMARY KEY (imdbid, peopleid, category),
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) ,
    FOREIGN KEY (peopleid) REFERENCES People(peopleid) 
);

CREATE TABLE Quotes (
    quote_id SERIAL PRIMARY KEY,
    imdbid VARCHAR(20),
    quote TEXT,
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) 
);

CREATE TABLE Reviews (
    review_id SERIAL PRIMARY KEY,
    imdbid VARCHAR(20),
    review TEXT,
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) 
);

CREATE TABLE Trailers (
    trailer_id SERIAL PRIMARY KEY,
    imdbid VARCHAR(20),
    trailer_url VARCHAR(255),
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) 
);

CREATE TABLE PlotSummary (
    summary_id SERIAL PRIMARY KEY,
    imdbid VARCHAR(20),
    summary TEXT,
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) 
);

CREATE TABLE StreamingAvailability (
    availability_id SERIAL PRIMARY KEY,
    imdbid VARCHAR(20),
    country VARCHAR(50),
    platform VARCHAR(50),
    link VARCHAR(255),
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid) 
);

-- TABLES FOR USER

CREATE TABLE "Users"
(
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL
);

-- User's Watchlist
CREATE TABLE Watchlist (
    watchlist_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    imdbid VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "Users"(user_id),
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid)
);

-- User's Recently Viewed
CREATE TABLE RecentlyViewed (
    recently_viewed_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    imdbid VARCHAR(20) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES "Users"(user_id),
    FOREIGN KEY (imdbid) REFERENCES Movies(imdbid)
);