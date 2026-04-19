from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from nltk.stem.porter import PorterStemmer
import nltk
from nltk.stem import WordNetLemmatizer

l = WordNetLemmatizer()
movies = pd.read_csv("C:\\Users\\dhire\\OneDrive\\Desktop\\Coding1\\tmdb_5000_movies.csv", encoding="ISO-8859-1")
credits = pd.read_csv("C:\\Users\\dhire\\OneDrive\\Desktop\\Coding1\\tmdb_5000_credits.csv",encoding="ISO-8859-1")
movies = movies.merge(credits,left_on="id",right_on="movie_id")
s = ['Congrats! You won a lottery ticket. Please collect money from mentioned address!',
     'Please Share your mobile Number at our website!']
# print(s[0].split())
vect = CountVectorizer(stop_words='english')
op = vect.fit_transform(s).toarray()
# print(op)
y = pd.DataFrame(op,columns = vect.get_feature_names_out(),index = ['s[0]','s[1]']) 
# cv = CountVectorizer(stop_words='english',max_features=5000)
# vectors = cv.fit_transform(df['tags'].toarray)
# p = cv.get_feature_names_out()[0:100]

ps = PorterStemmer()
# print(ps.stem('loved'))

def stemming(text):
    y = []
    for i in  text.split():
     y.append(ps.stem(i))
    return " ".join(y)
# print(stemming("love loved loving lovely"))
print(l.lemmatize("dancing",pos='v'))