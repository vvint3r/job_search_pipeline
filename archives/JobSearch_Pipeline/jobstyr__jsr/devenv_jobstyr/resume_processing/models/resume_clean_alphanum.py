import re
import os

def clean_resume_text(text):
    """
    Clean resume text while preserving dots and replacing hyphens with spaces.
    Maintains proper spacing around dots in abbreviations and sentences.
    
    Args:
        text (str): Input resume text
        
    Returns:
        str: Cleaned text with preserved formatting
    """
    # Replace multiple spaces, tabs, and newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Replace hyphens with spaces
    text = re.sub(r'-', ' ', text)
    
    # Replace other special characters (excluding dots) with spaces if they might be word separators
    text = re.sub(r'[/\\|_]', ' ', text)
    
    # Remove remaining special characters (excluding dots and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s.]', '', text)
    
    # Clean up multiple consecutive dots
    text = re.sub(r'\.+', '.', text)
    
    # Remove spaces before dots
    text = re.sub(r'\s+\.', '.', text)
    
    # Fix spacing after dots based on context
    # Keep space after dots followed by capital letters or lowercase words like 'avg.'
    text = re.sub(r'\.\s*([A-Z])', r'. \1', text)  # Ensure space before capitals
    text = re.sub(r'\.\s*([a-z])', r'. \1', text)  # Ensure space before lowercase
    
    # Clean up any resulting multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def process_resume():
    """
    Read resume from input file, clean it, and write to output file.
    """
    input_path = r"C:\Users\vasil\OneDrive\Desktop\gProjects\gjobstyr\resume_processing\resume_inputs\resume.txt"
    output_dir = r"C:\Users\vasil\OneDrive\Desktop\gProjects\gjobstyr\resume_processing\resume_outputs\cleaned"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "resume_alphanum.txt")
    
    try:
        # Read input file
        with open(input_path, 'r', encoding='utf-8') as file:
            resume_text = file.read()
        
        # Clean the text
        cleaned_text = clean_resume_text(resume_text)
        
        # Write results to output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(cleaned_text)
        
        print("Resume cleaning completed successfully.")
        print(f"Cleaned resume written to: {output_file}")
        
        # Display sample of cleaned text
        preview_length = 200
        print(f"\nFirst {preview_length} characters of cleaned text:")
        print(cleaned_text[:preview_length] + "...")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file at {input_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    process_resume()