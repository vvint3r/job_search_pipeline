import openai
from openai import OpenAI
import pandas as pd
from pathlib import Path
import sys
import json
import os
from typing import Dict, List, Optional

class ResumeAnalyzer:
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key."""
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = """

        You are an expert job description and resume analyzer specializing in job requirements and qualification comparison. 
                    
        Extract a comprehensive list of keywords (2 to 3 words long) from the job_descriptions_file and compare it (for matches) against the resume_file.
        
        Specifically, you need to analyze the job description and resume to identify the following categories and sections:

        Section Type: Requirements
        - Section could also be referenced as: Job Description/Requirements/Responsibilities/What You'll Do/You Will
        - Some sample starting text identifiers for this section would be: Develop/Oversee/Monitor/Conduct/Collaborate/Lead/Manage/Create/Provide/Analyze/Evaluate/Participate/Deliver/Work/Use/ Stay/Apply/Design/Oversee/Monitor/Support/Present/Establish/Prioritize/Define
        - Notes: Generally, we are looking for the job functions, expectations, leadership, management, etc. (mostly soft skills)

        Section Type: Job Qualifications/What You’ll Bring/Skills/Expertise/You Have/Experience
        - Sample Starting Identifiers:
        --Strong/Familiar/Experience/Hands-on/Related/Expertise/Excellent/Comfortable/Demonstrated/Proven/Knowledge/Mastery/Deep/In-Depth/Ability/Proficiency/Previous/Familiarity/Have/Possess/Are/Passion/Advanced
        - Notes: Generally, we are looking for the skills and abilities required here such as technical, tools, technologies, methods, approaches, industry knowledge, etc. (hard skills)

        For each category, provide a thorough analysis capturing ALL relevant terms from the job description.

        Format as JSON with arrays of {key_text, section_type, category_label, resume_exact_match, resume_partial_match, resume_broad_match}, where each key is described below:
        - key_text: the extracted text of value
        - section_type: either responsibility or qualification
        - category_label: can be one or more of the following; analytics, marketing, engineering, management, business, statistics
        - resume_exact_match: provide the matched keyword that was found in the resume
        - resume_partial_match: provide a partial match that was found in the resume
        - resume_broad_match: provide a broad match that was found in the resume
                    
        Be thorough and comprehensive in the analysis."""

    def read_file(self, file_path: str) -> str:
        """Read content from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

    def analyze_resume(self, job_description: str, resume_text: str) -> Optional[Dict]:
        """Analyze resume using GPT-4o with expanded context."""
        try:
            combined_text = f"Job Description:\n{job_description}\n\nResume:\n{resume_text}"
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using larger context model
                messages=[{"role": "system", "content": self.system_prompt}, {"role": "user", "content": combined_text}],
                temperature=0.3,  # Slightly higher for more comprehensive results
                max_tokens=4000,  # Increased token limit
                n=1
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Enhanced JSON extraction
                content = content.replace('\n', ' ').replace('\r', '')
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    cleaned_json = content[json_start:json_end]
                    try:
                        return json.loads(cleaned_json)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        print(f"Cleaned JSON content: {cleaned_json}")
                else:
                    print("No valid JSON object found in the response.")
                raise
                
        except Exception as e:
            print(f"Error in API call: {e}")
            return None

    def process_and_display(self, analysis_result: Dict, output_base_path: Path, output_dir: Path) -> None:
        """Process results and display/save with enhanced formatting."""
        if not analysis_result:
            print("No analysis results to process")
            return

        print("\nRESUME ANALYSIS RESULTS")
        print("=" * 80)

        output_dir.mkdir(parents=True, exist_ok=True)

        for category, items in analysis_result.items():
            if not items:
                continue

            # Create DataFrame for this category
            df = pd.DataFrame(items)
            
            # Rename 'importance_score' to 'score' if it exists
            if 'importance_score' in df.columns:
                df.rename(columns={'importance_score': 'score'}, inplace=True)
                
            # Handle missing 'score' column gracefully
            if 'score' not in df.columns:
                df['score'] = 0.0  # Set default score to 0.0 if not provided

            # Round score and sort by it if available
            if 'score' in df.columns:
                df['score'] = df['score'].round(3)
                df = df.sort_values('score', ascending=False)

            # Create filename with category and gpt35 label
            category_clean = category.lower().replace(' & ', '_').replace(' ', '_')
            filename = f"{output_base_path.stem}_{category_clean}_gpt35.csv"
            output_path = output_dir / filename
            
            # Save to CSV
            df.to_csv(output_path, index=False)

            # Enhanced display format
            print(f"\n{category.upper()}")
            print("=" * 80)
            print(f"Total items: {len(df)}")
            print("-" * 80)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            print(df.to_string(index=False))
            print(f"\nSaved to: {output_path}")
            print("-" * 80)

def calculate_cost(text_length: int) -> float:
    """Calculate approximate cost of analysis."""
    # GPT-4o pricing (per 1K tokens)
    input_cost_per_k = 0.0015
    output_cost_per_k = 0.002
    
    # Rough token estimate (1 token ≈ 4 characters)
    input_tokens = (len(str(text_length)) + 200) / 4
    output_tokens = 4000  # Updated to match max_tokens
    
    cost = (input_tokens / 1000 * input_cost_per_k) + (output_tokens / 1000 * output_cost_per_k)
    return cost

def ensure_output_directory(base_dir: Path) -> Path:
    """Create and return the resume_outputs/gpt35 directory."""
    output_dir = base_dir / "resume_outputs" / "gpt35"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_api_key() -> str:
    """Get OpenAI API key from environment variable or command line."""
    # First check environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    
    # If not found in environment, check command line args
    if not api_key and len(sys.argv) > 2:
        api_key = sys.argv[2]
        print("Warning: Using API key from command line. Consider setting OPENAI_API_KEY environment variable instead.")
    
    if not api_key:
        print("Error: OpenAI API key not found. Please either:")
        print("1. Set the OPENAI_API_KEY environment variable:")
        print("   export OPENAI_API_KEY='your-api-key'")
        print("2. Or provide it as a command line argument:")
        print("   python script.py resume.txt 'your-api-key'")
        sys.exit(1)
        
    return api_key

def main():
    base_dir = Path('C:/Users/vasil/OneDrive/Desktop/gProjects/gjobstyr/resume_processing')
    job_descriptions_file = base_dir / "jobs" / "job_descriptions.txt"
    resume_file = base_dir / "resumes" / "marketing_analytics.txt"
    api_key = get_api_key()
    
    try:
        # Create output directory
        output_dir = ensure_output_directory(base_dir)
        print(f"Output directory: {output_dir}")
        
        analyzer = ResumeAnalyzer(api_key)
        
        # Read job description and resume
        print(f"Reading job description from: {job_descriptions_file}")
        job_description = analyzer.read_file(job_descriptions_file)
        
        print(f"Reading resume from: {resume_file}")
        resume_text = analyzer.read_file(resume_file)
        
        # Calculate and display estimated cost
        estimated_cost = calculate_cost(len(job_description) + len(resume_text))
        print(f"Estimated cost of analysis: ${estimated_cost:.4f}")
        
        # Analyze resume
        print("Analyzing resume with GPT-4o...")
        analysis_result = analyzer.analyze_resume(job_description, resume_text)
        
        if analysis_result:
            # Process and display results
            analyzer.process_and_display(analysis_result, resume_file, output_dir)
        else:
            print("Analysis failed to produce results")
            
    except Exception as e:
        print(f"Error processing resume: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
