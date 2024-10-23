# Replace this with your actual Gemini API key
API_KEY = ""

import google.generativeai as genai
import os

genai.configure(api_key=API_KEY)

from flask import Flask, render_template_string, request, render_template
from markupsafe import Markup
import os
import markdown
from werkzeug.serving import run_simple
import markdown2
import re
from preprocess import process_resume_and_cover_letter, markdown_format, allowed_file, read_file
from model_scorer import calculate_semantic_similarity

#app = Flask(__name__)
app = Flask(__name__, template_folder='html_templates')


# Define the upload folder for resumes and job descriptions
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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
            return render_template('result.html', 
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
    return render_template('index.html')



# Run the Flask application on localhost at port 5001
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Create the upload directory if it doesn't exist
    run_simple('localhost', 5001, app)  # Run the Flask development server
            
