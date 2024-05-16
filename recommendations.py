import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

def recommend_papers(input_query):
    data_path = "updated_data.csv"
    history_path = "history.txt"
    data_df = pd.read_csv(data_path)

    with open(history_path, 'r') as file:
        history_titles = file.readlines()
    history_titles = [title.strip() for title in history_titles]

    all_titles = list(data_df['title'])
    combined_titles = all_titles + history_titles

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_titles)

    knn_model = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='cosine')
    knn_model.fit(tfidf_matrix)

    input_vector = vectorizer.transform([input_query])
    distances, indices = knn_model.kneighbors(input_vector, return_distance=True)
    recommended_indices = indices[0][1:]  # Exclude the input paper itself
    recommended_papers = [combined_titles[idx] for idx in recommended_indices]
    for idx, paper in enumerate(recommended_papers, 1):
        title = paper
        authors = data_df.loc[data_df['title'] == paper, 'authors'].values[0]
        year = data_df.loc[data_df['title'] == paper, 'year'].values[0]
        print(f"{idx}. Title: {title}\n   Author(s): {authors}\n   Year: {year}")

if len(sys.argv) < 2:
    print("Usage: python main.py <input_query>")
    sys.exit(1)

input_query = ' '.join(sys.argv[1:])
recommend_papers(input_query)
