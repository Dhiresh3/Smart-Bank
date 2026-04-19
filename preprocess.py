import pandas as pd
import ast
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

# Load data
movies = pd.read_csv("C:/Users/dhire/OneDrive/Desktop/Coding1/tmdb_5000_movies.csv", encoding="ISO-8859-1")
credits = pd.read_csv("C:/Users/dhire/OneDrive/Desktop/Coding1/tmdb_5000_credits.csv", encoding="ISO-8859-1")

movies = movies.merge(credits, left_on="id", right_on="movie_id")
movies = movies[['movie_id', 'title_x', 'crew', 'genres', 'keywords', 'overview', 'cast']]
movies.rename(columns={'title_x': 'title'}, inplace=True)

# Clean data
for col in ['genres', 'keywords', 'cast', 'crew']:
    movies[col] = movies[col].apply(convert)
    movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])

movies['tag'] = movies['cast'] + movies['crew'] + movies['genres'] + movies['keywords']
new = movies[['movie_id', 'title', 'tag']]

# Vectorization
cv = CountVectorizer(stop_words='english', max_features=5000)
vectors = cv.fit_transform(new['tag'].apply(lambda x: ' '.join(x))).toarray()
similarity = cosine_similarity(vectors)

# Save data
pickle.dump(new, open('movie_list.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))