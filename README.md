### How To Run Netflicks Locally

- **Using `psql`:** Command to create a new database.
- **MacOS Terminal:**
  - **`git clone https://github.com/bhern154/Netflicks.git`:** Clone the repository.
  - **`cd Netflicks`:** Change directory to the cloned repo.
  - **`code credentials.py`:** Open the `credentials.py` file in VS Code.
- **Fill out your API credentials:** Add your API credentials in the `credentials.py` file.
- **Set up the Python environment:**
  - **`python3 -m venv venv`:** Create a virtual environment.
  - **`source venv/bin/activate`:** Activate the virtual environment.
  - **`pip install -r requirements.txt`:** Install the required packages.
  - **`FLASK_ENV=development FLASK_DEBUG=1 flask run`:** Run the Flask application in development mode with debugging enabled.
