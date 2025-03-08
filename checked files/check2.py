from flask import Flask, request, render_template, send_from_directory
import os
import zipfile
import shutil
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def home():
    return render_template('iid.html', job_description="")

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading {docx_path}: {e}")
        return ""

def process_resume(file_path):
    if file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    return ""

def extract_resumes_from_zip(zip_path, extract_folder):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")

def rank_resumes(job_desc, resumes):
    texts = [job_desc] + resumes
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    ranked = sorted(zip(resumes, similarities[0]), key=lambda x: x[1], reverse=True)
    return ranked

@app.route('/upload', methods=['POST'])
def upload():
    job_description = request.form['job_desc']
    top_n = int(request.form['top_n'])
    uploaded_files = request.files.getlist('resumes')
    extracted_texts = []
    filenames = []
    
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    for file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        if file.filename.endswith('.zip'):
            extract_folder = os.path.join(UPLOAD_FOLDER, 'extracted')
            os.makedirs(extract_folder, exist_ok=True)
            extract_resumes_from_zip(file_path, extract_folder)
            
            for root, _, files in os.walk(extract_folder):
                for extracted_file in files:
                    full_path = os.path.join(root, extracted_file)
                    extracted_texts.append(process_resume(full_path))
                    filenames.append(extracted_file)
        else:
            extracted_texts.append(process_resume(file_path))
            filenames.append(file.filename)
    
    ranked = rank_resumes(job_description, extracted_texts)
    ranked_resumes = list(zip(filenames, [score for _, score in ranked]))[:top_n]
    
    return render_template('index.html', ranked_resumes=ranked_resumes, job_description=job_description)

@app.route('/reset_jd', methods=['POST'])
def reset_jd():
    return render_template('index.html', job_description="")

if __name__ == '__main__':
    app.run(debug=True)
