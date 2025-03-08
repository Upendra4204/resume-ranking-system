import os
import zipfile
import docx

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(docx_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error reading {docx_path}: {e}")
        return ""

def process_resume(file_path):
    """Processes a single resume file and extracts text."""
    if file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    return ""

def extract_resumes_from_zip(zip_path, extract_folder):
    """Extracts resumes from a ZIP file."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
    except Exception as e:
        print(f"Error extracting ZIP file: {e}")

def process_resumes(uploaded_files, upload_folder):
    """Processes uploaded resumes, extracting text from DOCX files and ZIP archives."""
    extracted_texts = []
    filenames = []

    for file in uploaded_files:
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        if file.filename.endswith('.zip'):
            extract_folder = os.path.join(upload_folder, 'extracted')
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

    return filenames, extracted_texts
