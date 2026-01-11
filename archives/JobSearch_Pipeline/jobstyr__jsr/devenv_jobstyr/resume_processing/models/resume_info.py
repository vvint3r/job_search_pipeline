import re
import os

def extract_job_titles(text):
    """
    Extract job titles from resume text while filtering out educational qualifications 
    and descriptive statements.
    """
    # Find text within square brackets or underline markdown
    bracketed_titles = re.findall(r'\[(.*?)\]|{\.underline}', text)
    
    # Find lines that look like job titles
    lines = text.split('\n')
    job_titles = []
    
    # Keywords that indicate actual job titles
    job_indicators = [
        'Consultant', 'Manager', 'Director', 'Analyst', 'Lead', 
        'Engineer', 'Analytics'
    ]
    
    # Keywords that indicate non-job-title lines
    exclude_indicators = [
        'MS', 'BS', 'PhD', 'Bachelor', 'Master', 'School', 
        'University', 'Years', 'expertise', 'experience'
    ]
    
    for line in lines:
        # Clean the line
        line = line.strip()
        
        # Skip empty lines, headers, or lines with exclusion indicators
        if not line or line.startswith('**') or line.startswith('#'):
            continue
            
        if any(excl in line for excl in exclude_indicators):
            continue
            
        # Look for lines that match job title patterns
        if re.match(r'^[A-Z][A-Za-z\s,&-]+', line) and any(indicator in line for indicator in job_indicators):
            # Remove parenthetical content
            line = re.sub(r'\s*\(.*?\)', '', line)
            job_titles.append(line)
    
    # Clean up bracketed titles
    cleaned_titles = []
    for title in bracketed_titles:
        # Remove markdown and clean whitespace
        title = re.sub(r'{\.underline}', '', title).strip()
        if title and any(indicator in title for indicator in job_indicators) and \
           not any(excl in title for excl in exclude_indicators):
            cleaned_titles.append(title)
    
    # Combine and remove duplicates while preserving order
    all_titles = []
    seen = set()
    for title in cleaned_titles + job_titles:
        if title not in seen and len(title.split()) <= 5:  # Reasonable title length
            all_titles.append(title)
            seen.add(title)
    
    return all_titles

def process_resume():
    """
    Read resume from input file, extract job titles, and write to output file.
    """
    input_path = r"C:\Users\vasil\OneDrive\Desktop\gProjects\gjobstyr\resume_processing\resume_inputs\resume.txt"
    output_dir = r"C:\Users\vasil\OneDrive\Desktop\gProjects\gjobstyr\resume_processing\resume_outputs\basics"
    output_file = os.path.join(output_dir, "job_titles.txt")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read input file
        with open(input_path, 'r', encoding='utf-8') as file:
            resume_text = file.read()
        
        # Extract job titles
        job_titles = extract_job_titles(resume_text)
        
        # Write results to output file
        with open(output_file, 'w', encoding='utf-8') as file:
            for title in job_titles:
                file.write(f"{title}\n")
        
        print(f"Successfully extracted {len(job_titles)} job titles:")
        for title in job_titles:
            print(f"- {title}")
        print(f"\nResults written to: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    process_resume()