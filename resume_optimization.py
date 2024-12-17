import os
from openai import OpenAI
import subprocess

# Define file paths
main_resume = "/home/wynt3r/JobSearch/resumes/resume_main.txt"
keywords_file = "/home/wynt3r/JobSearch/job_titles/seo/seo_unified_keywords_counts.txt"
optimized_resume = "/home/wynt3r/JobSearch/resumes/seo_resume_main_optimized.txt"

supporting_files = {
    "adobe": "/home/wynt3r/JobSearch/resumes/supporting/adobe.txt",
    "creditsesame": "/home/wynt3r/JobSearch/resumes/supporting/creditsesame.txt",
    "growthstyr": "/home/wynt3r/JobSearch/resumes/supporting/growthstyr.txt",
    "skills_utilities": "/home/wynt3r/JobSearch/resumes/supporting/skills_utilities.txt"
}

# Set your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key not found. Please set it as an environment variable.")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def load_keywords(file_path):
    """Load keywords and their counts from the keyword file."""
    keywords = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                keyword, count = line.rsplit(":", 1)
                keywords[keyword.strip()] = int(count.strip())
        print(f"Loaded {len(keywords)} keywords.")
    except FileNotFoundError:
        print(f"Error: Keywords file '{file_path}' not found.")
        exit()
    return keywords

def load_supporting_details(supporting_files):
    """Load content from supporting documents."""
    details = {}
    for name, path in supporting_files.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                details[name] = f.read().strip()
            print(f"Loaded supporting details from '{path}'.")
        except FileNotFoundError:
            print(f"Error: Supporting file '{path}' not found.")
            details[name] = ""  # Default to empty string if file not found
    return details

def generate_optimization_prompt(main_resume_text, supporting_details, keywords, job_field):
    """Generate a prompt to optimize the resume using GPT-4."""
    keywords_list = ", ".join(f"{k} ({v})" for k, v in keywords.items())
    
    # Access supporting details using correct keys
    adobe_details = supporting_details["adobe"]
    creditsesame_details = supporting_details["creditsesame"]
    growthstyr_details = supporting_details["growthstyr"]
    skills_details = supporting_details["skills_utilities"]

    return (
        f"Optimize the following resume for the role of {job_field} by incorporating relevant keywords, accomplishments, and skills. Ensure the resume is 2 to 3 pages long and maintains a professional tone.\n\n"
        f"Use the main resumt ({main_resume_text}) as a general reference.\n\n"
        f"Using the top keywords by counts ({keywords_list}) to optimize resume.\n\n"
        f"Use the skills and utilities from \n{skills_details} as needed.\n\n"
        f"For employer Adobe use this reference {adobe_details}.\n"
        f"For employer CreditSesame use this reference {creditsesame_details}.\n"
        f"For employer GrowthStyr use this reference {growthstyr_details}.\n"
        f"Please ensure the resume does not contain any non-ASCII characters.\n\n"
        f"The order of sections should be: \n\n"
        f"1. Personal Details\n"
        f"2. Summary\n"
        f"3. Key Quantifiable Accomplishments\n"
        f"4. Professional Experience\n"
        f"5. Skills & Utilities\n"
        f"6. Education\n"
    )

def optimize_resume(prompt):
    """Send the prompt to GPT-4 to optimize the resume."""
    print("Sending optimization request to OpenAI GPT-4...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=8000,
            n=1
        )
        content = response.choices[0].message.content
        print("Received optimized resume from GPT-4.")
        return content
    except Exception as e:
        print(f"Error optimizing resume: {e}")
        return None

# Load main resume
print("Loading main resume...")
try:
    with open(main_resume, "r", encoding="utf-8") as f:
        main_resume_text = f.read()
except FileNotFoundError:
    print(f"Error: Main resume file '{main_resume}' not found.")
    exit()

# Load supporting details
print("Loading supporting details...")
supporting_details = load_supporting_details(supporting_files)

# Load keywords
print("Loading keywords...")
keywords = load_keywords(keywords_file)

# Generate optimization prompt
print("Generating optimization prompt...")
prompt = generate_optimization_prompt(main_resume_text, supporting_details, keywords, "SEO Manager")

# Optimize resume
optimized_text = optimize_resume(prompt)

# Save the optimized resume
if optimized_text:
    print(f"Writing optimized resume to {optimized_resume}")
    try:
        with open(optimized_resume, "w", encoding="utf-8") as f:
            f.write(optimized_text)
        print(f"Successfully wrote optimized resume to {optimized_resume}.")
    except Exception as e:
        print(f"Error writing to optimized resume file: {e}")
