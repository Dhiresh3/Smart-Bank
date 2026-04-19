import streamlit as st
import pickle
import requests

# 🎯 TMDb API Key
API_KEY = "2736a08daef7a534d3cf2d8c371e0427"

# 🧠 Cache movie data loading
@st.cache_resource
def load_data():
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

# 🖼️ Fetch poster with error handling
@st.cache_data
def movie_fetch(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path', '')
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    except requests.exceptions.RequestException as e:
        st.error("🚫 Couldn't fetch poster. Check your internet or API key.")
        st.text(str(e))
        return ""

# 🔍 Recommend movies
def recommend(movie, movies, similarity):
    if movie not in movies['title'].values:
        return [], []

    index = movies[movies['title'] == movie].index[0]
    distances = list(enumerate(similarity[index]))
    sorted_movies = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]

    recommended_titles = []
    recommended_posters = []

    for idx, _ in sorted_movies:
        movie_id = movies.iloc[idx].movie_id
        recommended_titles.append(movies.iloc[idx].title)
        recommended_posters.append(movie_fetch(movie_id))
    return recommended_titles, recommended_posters

# 🌟 UI
st.header("🎬 Movie Recommender System")

movies, similarity = load_data()
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie", movie_list)

if st.button("Show Recommendation"):
    recommendations, posters = recommend(selected_movie, movies, similarity)

    if recommendations:
        st.success("Here are your top picks!")
        st.balloons()

        tabs = st.tabs([str(i+1) for i in range(len(recommendations))])
        for tab, title, poster in zip(tabs, recommendations, posters):
            with tab:
                st.subheader(title)
                st.image(poster if poster else "https://via.placeholder.com/500x750?text=No+Poster")
    else:
        st.warning("Movie not found in the dataset.")

# 💖 Footer
st.markdown("---")
st.markdown("Created with passion by **Dhiresh** 💖")