from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_resumes(job_desc, resumes, filenames, top_n):
    if not resumes:
        return []

    texts = [job_desc] + resumes
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    ranked = sorted(zip(filenames, similarities[0]), key=lambda x: x[1], reverse=True)
    
    return ranked[:top_n]
