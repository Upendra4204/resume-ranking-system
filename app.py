from flask import Flask, request, render_template
import os
import shutil
from config import UPLOAD_FOLDER, TOP_N_DEFAULT
from resume_processing import process_resumes, extract_resumes_from_zip
from ranking import rank_resumes

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')  

    job_description = request.form['job_desc_embedding'] 
    top_n = int(request.form.get('top_n', TOP_N_DEFAULT))
    uploaded_files = request.files.getlist('resumes')

    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filenames, extracted_texts = process_resumes(uploaded_files, UPLOAD_FOLDER)

    ranked = rank_resumes(job_description, extracted_texts, filenames, top_n)
    ranked_resumes = [(filename, round(score, 2)) for filename, score in ranked]

    return render_template('index.html', ranked_resumes=ranked_resumes, total_resumes=len(filenames), job_description=job_description)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # Use PORT from HF or default to 7860
    app.run(host="0.0.0.0", port=port)

