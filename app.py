import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx  # For reading .docx files
import json  # To handle JSON parsing

# Replace this with your actual API key
GEMINI_API_KEY = "AIzaSyB9FSP3kO4w1y2Ao-nzK6DzrgSqjDrjXdc"

# Configure the Gemini API directly with the API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Helper function to extract text from a PDF
def pdf_to_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()
    return text

# Helper function to extract text from a Word (.docx) file
def docx_to_text(docx_file):
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Helper function to extract text from a TXT file
def txt_to_text(txt_file):
    return txt_file.read().decode("utf-8")

# Helper function to clean the response and ensure it's valid JSON
def clean_json_response(response_text):
    # Strip backticks and any other non-JSON formatting
    cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned_text)  # Parse the cleaned text as JSON
    except json.JSONDecodeError:
        st.error("Failed to parse JSON response. The output was not valid JSON.")
        return None

# Step 1: Job description parsing using Gemini API
def parse_job_description(job_description):
    response = model.generate_content(
        f"Extract the Industry, Experience, and Skill from the Job description given below and show it in JSON format: {job_description}"
    )
    return clean_json_response(response.text)

# Step 2: Resume parsing using Gemini API
def parse_resume_text(resume_text):
    response = model.generate_content(
        f"Extract the Industry, Experience, and Skill from the candidate's resume given below and show it in JSON format: {resume_text}"
    )
    return clean_json_response(response.text)

# Step 3: Compare job description and resume using Gemini API
def compare_job_and_resume(job_desc_json, resume_json):
    response = model.generate_content(
        f"""
        Compare the following Job Description and Candidate Resume and say FIT or NOT FIT as a general heading. 
        Give a rating out of 10, and explain the assessment for Industry, Experience, and Skills in separate lines. 
        Also, explain reasons for not giving a perfect 10.
        
        Job Description:
        {job_desc_json}

        Candidate Resume:
        {resume_json}
        """
    )
    return response.text

# Streamlit app frontend
def main():
    st.title("Job Fit Analyzer")
    st.write("Upload your resume and enter a job description to see how well you fit the job.")

    # Job description input
    job_description = st.text_area("Enter Job Description", height=150)
    
    # Resume upload (support for PDF, DOCX, and TXT)
    resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    if st.button("Analyze"):
        if not job_description:
            st.error("Please enter a job description.")
        if not resume_file:
            st.error("Please upload your resume.")
        if job_description and resume_file:
            # Detect file type and extract text accordingly
            file_type = resume_file.type
            resume_text = ""
            
            if file_type == "application/pdf":
                st.write("Processing resume (PDF)...")
                resume_text = pdf_to_text(resume_file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                st.write("Processing resume (Word)...")
                resume_text = docx_to_text(resume_file)
            elif file_type == "text/plain":
                st.write("Processing resume (Text)...")
                resume_text = txt_to_text(resume_file)
            else:
                st.error("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
                return

            # Step 1: Parse Job Description
            st.write("Processing job description...")
            job_desc_json = parse_job_description(job_description)
            if job_desc_json:
                st.json(job_desc_json)

            # Step 2: Parse the resume
            st.write("Processing resume...")
            resume_json = parse_resume_text(resume_text)
            if resume_json:
                st.json(resume_json)

            # Step 3: Compare Job Description and Resume
            if job_desc_json and resume_json:
                st.write("Comparing job description with resume...")
                comparison_result = compare_job_and_resume(job_desc_json, resume_json)
                st.write(comparison_result)

if __name__ == "__main__":
    main()
