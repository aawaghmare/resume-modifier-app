# Replace this with your actual Gemini API key
API_KEY = "AIzaSyDGmQpZ-1u4pIqErhLjQ9P0zIG3f8g6Lzk"

import google.generativeai as genai
import os

genai.configure(api_key=API_KEY)

from flask import Flask, render_template_string, request
from markupsafe import Markup
import os
import markdown
from werkzeug.serving import run_simple
import markdown2
import PyPDF2
import docx
import re

app = Flask(__name__)

# Define the upload folder and allowed extensions for resumes and job descriptions
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}

# Check if the uploaded file is allowed (based on file extension)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to read a file based on its extension and handle encoding errors
def read_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    
    if ext == 'pdf':
        return read_pdf(file_path)  # Call the PDF reader function
    elif ext == 'docx':
        return read_docx(file_path)  # Call the DOCX reader function
    else:  # For txt and md files
        try:
            # Try reading the file as UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # If UTF-8 decoding fails, fallback to another encoding like ISO-8859-1 (Latin-1)
            with open(file_path, 'r', encoding='ISO-8859-1') as f:
                return f.read()
            
# Function to read the contents of a PDF file
def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()  # Extract text from each page
    return text

# Function to read the contents of a DOCX file
def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to create the any resume input file into markdown format use gen ai for that

def markdown_format(resume_path):
    """
    Function to convert the content of a resume file into markdown format using generative AI.
    """
    # Step 1: Use the read_file function to read the resume content
    resume_content = read_file(resume_path)

    # Step 2: Create the prompt for the generative AI model
    prompt = f'''
    Convert the following resume content into Markdown format. Ensure that:
    - Section headings are formatted as headings.
    - Bullet points are properly represented as lists.
    - Maintain the overall structure and hierarchy of the content.
    
    Resume Content:
    {resume_content}
    '''

# Step 3: Generate markdown using AI model (assuming genai model is initialized)
    model = genai.GenerativeModel("gemini-1.5-flash")  # Replace with actual model
    resume_response = model.generate_content(prompt)  # Generate response from the AI model

    # Step 4: Return the generated markdown content
    return resume_response.text  # Assuming `text` holds the generated markdown content



# Main route for uploading and processing resumes
@app.route('/', methods=['GET', 'POST'])
def index():
    processed_resume = ""
    html_original_resume_content = ""
    resume_path = ""
    job_desc_path = ""
    html_cover_letter_content = ""

    if request.method == 'POST':
        try:
            # Check if retrying or uploading new files
            if 'retry' in request.form and 'resume_path' in request.form and 'job_desc_path' in request.form:
                resume_path = request.form['resume_path']
                job_desc_path = request.form['job_desc_path']
            else:
                # Handle new file uploads
                resume_file = request.files.get('resume')
                job_desc_file = request.files.get('job_description')

                if resume_file and allowed_file(resume_file.filename) and job_desc_file and allowed_file(job_desc_file.filename):
                    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
                    job_desc_path = os.path.join(app.config['UPLOAD_FOLDER'], job_desc_file.filename)

                    resume_file.save(resume_path)
                    job_desc_file.save(job_desc_path)

            # Read the original resume and job description
            original_resume_content = markdown_format(resume_path)
            job_description_content = read_file(job_desc_path)

            # Convert to HTML for display
            html_original_resume_content = markdown.markdown(original_resume_content)

            # Process resume and cover letter with AI
            processed_resume, cover_letter, recruiter_feedback, career_coach_advice = process_resume_and_cover_letter(resume_path, job_desc_path)
            html_resume_content = markdown.markdown(processed_resume)

            #Calculate the similarity score with the modified resume
            modified_resume_score = round(calculate_semantic_similarity(processed_resume, job_description_content) * 100)     
            
            # Convert cover letter to HTML if generated
            html_cover_letter_content = markdown.markdown(cover_letter) if cover_letter else ""

            # Convert recruiter feedback to HTML if generated
            html_recruiter_feedback_content = markdown.markdown(recruiter_feedback) if recruiter_feedback else ""
            
            # Convert career coach advice to HTML if generated
            html_career_coach_advice_content = markdown.markdown(career_coach_advice) if career_coach_advice else ""
            
            # Render the result form
            return render_template_string('result.html', 
            resume_content=Markup(html_resume_content), 
            cover_letter_content=Markup(html_cover_letter_content), 
            recruiter_feedback_content=Markup(html_recruiter_feedback_content), 
            career_coach_advice_content=Markup(html_career_coach_advice_content), 
            resume_path=resume_path, 
            job_desc_path=job_desc_path, 
            modified_resume_score=modified_resume_score)
        
        except Exception as e:
            return f"Error: {e}"
    # Render the initial form for uploading a resume and job description
    return render_template_string('index.html')



# Run the Flask application on localhost at port 5001
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Create the upload directory if it doesn't exist
    run_simple('localhost', 5001, app)  # Run the Flask development server
            
