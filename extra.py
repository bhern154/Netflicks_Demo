# -------- GET MOVIE RECOMMENDATIONS FROM GENRE --------
# @app.route('/api/recommendations-<string:genre>', methods=['GET'])
# def get_genre_recommendations(genre):

#     try:
#         url = 'https://ott-details.p.rapidapi.com/advancedsearch'
#         querystring = {
#             'start_year': '2016',
#             'end_year': '2020',
#             'min_imdb': '7.5',
#             'genre': genre,
#             'language': 'english',
#             'sort': 'latest',
#             'page': '1'
#         }
#         headers = {
#             'X-RapidAPI-Key': APIKey,
#             'X-RapidAPI-Host': 'ott-details.p.rapidapi.com'
#         }

#         response = requests.get(url, headers=headers, params=querystring)
#         response.raise_for_status()
#         response_data = response.json()

#         existing_imdbids = {movie.imdbid for movie in Movies.query.all()}

#         # Insert data from the JSON response to the database
#         for item in response_data.get('results', []):

#             # Check if the movie already exists in the database
#             imdbid = item.get('imdbid')
#             if imdbid in existing_imdbids:
#                 print(f"Movie with imdbid {imdbid} already exists. Skipping.")
#                 continue

#             #Add items to the 'Movies' table
#             movie = Movies(
#                 imdbid=item.get('imdbid'),
#                 title=item.get('title'),
#                 imdbrating=item.get('imdbrating'),
#                 released=item.get('released'),
#                 synopsis=item.get('synopsis'),
#                 type=item.get('type')
#             )

#             db.session.add(movie)

#             # Add items to the Genre and MovieGenre Tables
#             for genre_name in item.get('genre', []):
#                 genre = Genres.query.filter_by(genre_name=genre_name).first()
#                 if not genre:
#                     genre = Genres(genre_name=genre_name)
#                     db.session.add(genre)
#                     # Ensure the genre_id is populated so that MovieGenre can access it
#                     db.session.flush()
#                 movie_genre = MovieGenres(imdbid=movie.imdbid, genre_id=genre.genre_id)
#                 db.session.add(movie_genre)

#             # Add items to the MovieImages Table
#             for image_url in item.get('imageurl', []):
#                 # Find the index of the second to last '.'
#                 last_dot_index = image_url.rfind('.')
#                 second_last_dot_index = image_url.rfind('.', 0, last_dot_index)
#                 # remove the substring '_V1_UY600_CR900,0,600,900_AL_' to get the original image
#                 new_image_url = image_url[:second_last_dot_index + 1] + '' + image_url[last_dot_index:]
#                 movie_image = MovieImages(imdbid=movie.imdbid, image_url=new_image_url)
#                 db.session.add(movie_image)

#         db.session.commit()

#         return jsonify(response_data)
#     except requests.exceptions.RequestException as e:
#         print(e)
#         return jsonify({'error': 'An error occurred while fetching data'}), 500