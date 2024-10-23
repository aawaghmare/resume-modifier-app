import re
from sentence_transformers import SentenceTransformer, util
# Load a pre-trained sentence transformer model that supports encoding
model_scorer = SentenceTransformer ('all-mpnet-base-v2')

# Define a function for basic text preprocessing
def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text)  # Remove special characters
    text = text.lower()  # Convert to lowercase
    return text.strip()


# Define the function to calculate semantic similarity
def calculate_semantic_similarity(resume_text, jd_text):
    # Preprocess the input texts
    resume_text = preprocess_text(resume_text)
    jd_text = preprocess_text(jd_text)
    # Encode both the resume and job description into vectors
    resume_vector = model_scorer.encode(resume_text, convert_to_tensor=True)
    jd_vector = model_scorer.encode(jd_text, convert_to_tensor=True)
    
    # Compute cosine similarity between the vectors
    similarity = util.pytorch_cos_sim(resume_vector, jd_vector)
    return similarity.item()  # Convert tensor to scalar
