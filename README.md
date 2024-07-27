![NETFLICKS](/ReadMeImages/netflicks_logo.png)

NETFLICKS is a project inspired by Netflix and uses the [OTT Details API](https://rapidapi.com/gox-ai-gox-ai-default/api/ott-details).

The goal of this project is to develop a Python full-stack web application. The stack includes Flask for the server-side framework, PostgreSQL as the database, SQLAlchemy for ORM (Object Relational Mapping), Jinja for templating in HTML, WTForms for user forms, and Bcrypt for securing user authentication with encryption.

All the movie data is sourced from the [OTT Details API](https://rapidapi.com/gox-ai-gox-ai-default/api/ott-details), and the relevant information is stored in the local database. The OTT Details API is used for various functionalities, including fetching movies by genre, retrieving movies based on user searches, and obtaining additional details when a movie is clicked on.

On top of exploring movies, NETFLICKS will give you options to watch the movie of your choice under the “Streaming Availability” options available. You can also watch trailers under the “Trailers” options available.

You can explore the SQL model or schema to see all the data collected and stored for each movie, where available.

### Database Schema

![Database Schema](/ReadMeImages/database_schema.png)

The database schema is designed around two primary components: users and movies. Users can create a watchlist, and every time they view detailed information about a movie, it is saved in their recently viewed list.

Key components include:
* **User**: Stores user details such as username, password, and email.
* **Movies**: Contains movie information like title, IMDb rating, release year, synopsis, and more.
* **Watchlist and RecentlyViewed**: Track movies that users have added to their watchlist or recently viewed.
* **Genres**: Stores different movie genres, linked to movies through the MovieGenres association table.
* **MovieImages**: Contains URLs of images related to movies.
* **People**: Represents individuals involved in movies, such as actors and directors, with their roles detailed in PeopleRoles.
* **Quotes, Reviews, Trailers, and PlotSummary**: Store movie quotes, reviews, trailer URLs, and plot summaries, respectively.
* **StreamingAvailability**: Tracks where movies are available for streaming, including the platform and country.

### Navigation

![Navigation Bar](/ReadMeImages/Nav_Bar.png)

* **NETFLICKS Logo**: Redirects to the home page.
* **SEARCH**: Provides a search bar and redirects to a results page.
* **GENRES**: Displays a dropdown of all available genres and redirects to a results page.
* **LOGIN**: Appears when not logged in and redirects to a login page.
* **MY ACCOUNT**: Appears when logged in and shows a dropdown for the user’s Watchlist, Recently Viewed, Account Details, and Logout options.

### Home Page

![Home Page](/ReadMeImages/Home_Page.png)

The home page displays up to 60 movies from 16 of the most popular genres. When the application is run for the first time, it makes 16 API calls for each genre. As more movies are added to the database through subsequent calls, the home page updates to display new movies and data.

### Details Page

![Details Page](/ReadMeImages/More_Details_Page.png)

The Details Page provides comprehensive information about each movie, including:
* **Movie Banner**: A visual banner representing the movie.
* **Released Year**: The year the movie was released.
* **Runtime**: The duration of the movie.
* **Related Genres**: The genres associated with the movie.
* **Streaming Availability**: Links to platforms where the movie is available for streaming.
* **Trailer Links**: Links to trailers for the movie.
* **Languages**: The languages in which the movie is available.
* **IMDb Rating**: The movie's rating on IMDb.
* **IMDb Votes**: The number of votes the movie has received on IMDb.
* **Film Type**: The type or category of the film (e.g., feature film, short film).
* **Synopsis**: A brief overview of the movie's plot.
* **Popular Quotes**: Notable quotes from the movie.
* **Reviews**: Reviews and critiques of the movie.
* **Long Summaries**: Extended summaries providing more detailed information about the movie's storyline.

Note: Not all movies have every piece of information available. Logged-in users can also add the movie to their Watchlist.

### Login Page

![Login Page](/ReadMeImages/Login_Page.png)

The Login Page requires users to enter their username and password to access their accounts. It also includes a link to the "Register" page for new users who wish to create an account.

### Signup Page

![Signup Page](/ReadMeImages/Sign_Up_Page.png)

The Signup Page requires new users to provide the following information to create an account:
* Username
* Password
* Email
* First Name
* Last Name

### Watchlist Page

![Watchlist Page](/ReadMeImages/Watchlist_Page.png)

The Watchlist Page displays the movies that the logged-in user has added to their watchlist. Users have the option to delete movies from the watchlist.

### Recently Viewed Page

![Recently Viewed Page](/ReadMeImages/Recently_Viewed_Page.png)

The Recently Viewed Page shows the movies that the logged-in user has recently viewed. Users can choose to clear their recently viewed movies.

## How To Run NETFLICKS Locally


**Using `psql`:** Command to create a new database.
- **`psql`**
    - **`CREATE DATABASE netflicks_db;`**: Create the PostgreSQL database.

  
**MacOS Terminal / Linux:**
  - **`git clone <url>`:** Clone the repository.
  - **`cd <repo folder>`:** Change directory to the cloned repo.
  - **`code credentials.py`:** Open the `credentials.py` file in VS Code.
    
- **Fill out your API credentials:**
  - Add your API credentials in the `credentials.py` file.
  - **`SecretKey`:** Make your own SecretKey.
  - **`APIKey`:** Create a free API key at `https://rapidapi.com/gox-ai-gox-ai-default/api/ott-details`.
    
- **Set up the Python environment:**
  - **`python3 -m venv venv`:** Create a virtual environment.
  - **`source venv/bin/activate`:** Activate the virtual environment.
  - **`pip install -r requirements.txt`:** Install the required packages.
  - **`FLASK_ENV=development FLASK_DEBUG=1 flask run`:** Run the Flask application in development mode with debugging enabled.

    
**Windows Command Prompt:**
  - **`git clone <url>`:** Clone the repository.
  - **`cd <repo folder>`:** Change directory to the cloned repo.
  - **`notepad credentials.py`:** Open the `credentials.py` file in Notepad.

- **Fill out your API credentials:**
  - Add your API credentials in the `credentials.py` file.
  - **`SecretKey`:** Make your own SecretKey.
  - **`APIKey`:** Create a free API key at `https://rapidapi.com/gox-ai-gox-ai-default/api/ott-details`.

- **Set up the Python environment:**
  - **`python -m venv venv`:** Create a virtual environment.
  - **`.\venv\Scripts\activate`:** Activate the virtual environment.
  - **`pip install -r requirements.txt`:** Install the required packages.
  - **`set FLASK_ENV=development`:** Set the environment to development mode.
  - **`set FLASK_DEBUG=1`:** Enable debugging.
  - **`flask run`:** Run the Flask application.