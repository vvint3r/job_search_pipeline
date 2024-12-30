import pandas as pd
import nltk
from nltk.corpus import stopwords
import string
import re
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_nltk():
    """Download required NLTK data."""
    try:
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        return True
    except Exception as e:
        logging.error(f"Error downloading NLTK data: {e}")
        return False

def clean_text(text):
    """Clean text by removing stop words, handling punctuation, and normalizing spaces."""
    try:
        if pd.isna(text) or not isinstance(text, str):
            return ""
            
        # Get stop words
        stop_words = set(stopwords.words('english'))
        
        # Replace punctuation with spaces, except for important symbols
        translator = str.maketrans({p: ' ' for p in string.punctuation})
        text = text.translate(translator)
        
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        words = text.split()
        
        # Remove stop words
        words = [word for word in words if word not in stop_words]
        
        # Join words and normalize spaces
        text = ' '.join(words)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    except Exception as e:
        logging.error(f"Error cleaning text: {e}")
        return text

def process_job_details_file(input_file):
    """Process a job details CSV file to create a version without stop words."""
    try:
        # Verify input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        # Create output filename in the same directory as input
        input_dir = os.path.dirname(input_file)
        input_basename = os.path.basename(input_file)
        filename, ext = os.path.splitext(input_basename)
        
        # Set output path (in same directory)
        output_file = os.path.join(input_dir, f"{filename}_nostop{ext}")
        
        # Read input CSV
        df = pd.read_csv(input_file)
        logging.info(f"Read {len(df)} rows from {input_file}")
        
        # Clean description column
        if 'description' in df.columns:
            logging.info("Processing description column...")
            df['description'] = df['description'].apply(clean_text)
            
            # Save processed file
            df.to_csv(output_file, index=False)
            logging.info(f"Saved processed file to {output_file}")
            return output_file
        else:
            raise KeyError("No 'description' column found in the input file")
            
    except Exception as e:
        logging.error(f"Error processing file {input_file}: {e}")
        raise

def main(job_title, input_file=None):
    """Main function to process job details files for a specific job title."""
    try:
        # Setup NLTK
        if not setup_nltk():
            raise Exception("Failed to setup NLTK")
        
        if input_file:
            # Process specific file
            process_job_details_file(input_file)
        else:
            # Process all files in job title directory (original behavior)
            job_title_clean = job_title.lower().replace(' ', '_')
            details_folder = f"./job_search/job_post_details/{job_title_clean}"
            
            if not os.path.exists(details_folder):
                raise FileNotFoundError(f"Job details folder not found: {details_folder}")
            
            csv_files = [f for f in os.listdir(details_folder) if f.endswith('.csv')]
            
            if not csv_files:
                raise FileNotFoundError(f"No CSV files found in {details_folder}")
            
            for csv_file in csv_files:
                input_path = os.path.join(details_folder, csv_file)
                process_job_details_file(input_path)
            
        logging.info(f"Completed processing files for {job_title}")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process job details files to remove stop words')
    parser.add_argument('job_title', help='Job title to process')
    parser.add_argument('--input-file', help='Specific input file to process')
    args = parser.parse_args()
    
    main(args.job_title, args.input_file) 