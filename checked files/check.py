import os
import numpy as np
import docx
import PyPDF2
from flask import Flask, request, render_template
from scipy.spatial.distance import cosine
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load BERT Model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute Cosine Similarity
def compute_similarity(job_embedding, resume_embeddings):
    scores = [(file, 1 - cosine(job_embedding, embedding)) for file, embedding in resume_embeddings]
    return sorted(scores, key=lambda x: x[1], reverse=True)

def get_top_n_resumes(job_embedding, resume_embeddings, top_n=5):
    ranked_resumes = compute_similarity(job_embedding, resume_embeddings)
    return ranked_resumes[:top_n]

# Extract text from resumes
def extract_text_from_resume(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + " "
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + " "
    return text.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    ranked_resumes = []
    if request.method == 'POST':
        job_description = request.form['job_desc_embedding']  # Get job description text
        job_desc_embedding = embedding_model.encode(job_description)  # Convert text to embedding
        
        # Handle file upload
        uploaded_files = request.files.getlist('resumes')
        resume_embeddings = []
        
        for file in uploaded_files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text from resume and generate embedding
            resume_text = extract_text_from_resume(filepath)
            if resume_text:
                embedding = embedding_model.encode(resume_text)  # Convert text to embedding
                resume_embeddings.append((filename, embedding))
        
        ranked_resumes = get_top_n_resumes(job_desc_embedding, resume_embeddings, top_n=5)
    
    return render_template('index.html', ranked_resumes=ranked_resumes)

if __name__ == '__main__':
    app.run(debug=True)
