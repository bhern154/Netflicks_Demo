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
  
