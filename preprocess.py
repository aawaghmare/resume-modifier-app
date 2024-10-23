import google.generativeai as genai
import markdown  # Ensure this is imported for converting to markdown
import os
import PyPDF2
import docx

# Define allowed file extensions for uploads
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


# Function to process the resume and job description, and store the resume, cover letter, recruiter feedback, and career coach advice separately
def process_resume_and_cover_letter(resume_path, job_desc_path):
    # Read the resume and job description files
    resume_content = markdown_format(resume_path)
    job_description_content = read_file(job_desc_path)

    # Create the prompt for the generative model to modify the resume and create a cover letter
    prompt = f"""
    I have a resume formatted in Markdown and a job description. Please modify my resume 
    to better align with the job requirements while maintaining a professional, concise, 
    and polished tone. Focus on tailoring my skills, experiences, and achievements 
    to highlight the most relevant points for the position.

    ### Important: 
    - Retain specific keywords, tools, and relevant terms from both the original resume and the job description. Avoid generalizing or oversimplifying key technical content.
    
    ### Here is my resume in Markdown:
    {resume_content}
    
    ### Here is the job description:
    {job_description_content}
    
    Please modify the resume to:
    - Use keywords and phrases from the job description, optimizing it for Applicant Tracking Systems (ATS).
    - Adjust the bullet points under each role to emphasize relevant skills and achievements, including quantifiable results where possible.
    - If the bullet points do not already include quantifiable results, suggest improvements to convert them into quantifiable statements that highlight specific achievements or contributions.
    - Ensure all required qualifications and experiences mentioned in the job description are matched in my resume.
    - Maintain clarity, conciseness, and professionalism, keeping formatting clean and readable.
    - Ensure the resume retains my unique qualifications while aligning with the job description.
    - At the end of the output, include a professional and tailored cover letter that highlights why I'm the best fit for the role.
    
    Additionally, please:
    - Act as a recruiter (be a tough recruiter) and provide honest detailed feedback on the modified resume without any bias in 4-5 lines and mention Strengths & Areas of improvements.
    - Act as a career coach and offer advice on how to effectively pursue similar job opportunities.
    - Clearly separate the resume, cover letter, recruiter feedback, and career coach advice by using headings: "Resume", "Cover Letter", "Recruiter Feedback", and "Career Coach Advice".

    Return the updated resume, cover letter, recruiter feedback, and career coach advice in Markdown format.
    """

    # Assuming the generative AI model is already set up
    model = genai.GenerativeModel("gemini-1.5-flash")  # Replace with actual model
    response = model.generate_content(prompt)  # Generate response from the AI model
    
    # Extract the generated text
    generated_content = response.text

    # Initialize variables for each section
    resume_text = ""
    cover_letter = ""
    recruiter_feedback = ""
    career_coach_advice = ""

    # Split the generated content into the relevant sections
    if "Resume" in generated_content:
        sections = generated_content.split("Resume", 1)
        resume_text = sections[1].split("Cover Letter", 1)[0].strip()  # Extract resume text

        if "Cover Letter" in sections[1]:
            cover_letter = sections[1].split("Cover Letter", 1)[1].split("Recruiter Feedback", 1)[0].strip()  # Extract cover letter

        if "Recruiter Feedback" in sections[1]:
            recruiter_feedback = sections[1].split("Recruiter Feedback", 1)[1].split("Career Coach Advice", 1)[0].strip()  # Extract recruiter feedback

        if "Career Coach Advice" in sections[1]:
            career_coach_advice = sections[1].split("Career Coach Advice", 1)[1].strip()  # Extract career coach advice

    return resume_text, cover_letter, recruiter_feedback, career_coach_advice  # Return all sections
