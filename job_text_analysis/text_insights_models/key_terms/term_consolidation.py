import pandas as pd
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import defaultdict
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
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        return True
    except Exception as e:
        logging.error(f"Error downloading NLTK data: {e}")
        return False

def consolidate_terms(input_file, use_lemmatizer=True):
    """
    Consolidate similar terms from unique terms CSV file.
    Args:
        input_file: Path to the unique terms CSV file
        use_lemmatizer: If True, use lemmatization; if False, use stemming
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Initialize stemmer/lemmatizer
        if use_lemmatizer:
            word_processor = WordNetLemmatizer()
            process_word = lambda x: word_processor.lemmatize(x, pos='v')  # Try verb form first
        else:
            word_processor = PorterStemmer()
            process_word = word_processor.stem
            
        # Create dictionary to store grouped terms
        term_groups = defaultdict(list)
        
        # Group terms by their root form
        for _, row in df.iterrows():
            term = row['term']
            root = process_word(term)
            term_groups[root].append(row.to_dict())
            
        # Consolidate metrics for each group
        consolidated_terms = []
        
        for root, terms in term_groups.items():
            if len(terms) > 1:  # Only process groups with multiple terms
                # Find the most frequent term to use as representative
                representative_term = max(terms, key=lambda x: x['total_occurrences'])['term']
                
                # Calculate consolidated metrics
                total_occurrences = sum(term['total_occurrences'] for term in terms)
                num_jobs = sum(term['num_jobs_with_term'] for term in terms)
                avg_percentage = sum(term['percentage_jobs'] for term in terms) / len(terms)
                avg_occurrences = sum(term['avg_occurrences'] for term in terms) / len(terms)
                
                # Get all related terms except the representative
                related_terms = [term['term'] for term in terms if term['term'] != representative_term]
                
                consolidated_terms.append({
                    'representative_term': representative_term,
                    'related_terms': ', '.join(related_terms),
                    'total_occurrences': total_occurrences,
                    'num_jobs_with_term': num_jobs,
                    'percentage_jobs': avg_percentage,
                    'avg_occurrences': avg_occurrences,
                    'group_size': len(terms)
                })
            else:
                # Keep single terms as is, but maintain the same structure
                term = terms[0]
                consolidated_terms.append({
                    'representative_term': term['term'],
                    'related_terms': '',
                    'total_occurrences': term['total_occurrences'],
                    'num_jobs_with_term': term['num_jobs_with_term'],
                    'percentage_jobs': term['percentage_jobs'],
                    'avg_occurrences': term['avg_occurrences'],
                    'group_size': 1
                })
        
        # Convert to DataFrame and sort by total occurrences
        consolidated_df = pd.DataFrame(consolidated_terms)
        consolidated_df = consolidated_df.sort_values('total_occurrences', ascending=False)
        
        # Generate output filename
        input_dir = os.path.dirname(input_file)
        base_name = os.path.basename(input_file)
        filename, ext = os.path.splitext(base_name)
        output_file = os.path.join(input_dir, f"{filename}_consolidated{ext}")
        
        # Save to CSV
        consolidated_df.to_csv(output_file, index=False)
        logging.info(f"Consolidated terms saved to {output_file}")
        
        return output_file
        
    except Exception as e:
        logging.error(f"Error consolidating terms: {e}")
        raise

def main(input_file):
    """Main function to consolidate terms."""
    try:
        # Setup NLTK
        if not setup_nltk():
            raise Exception("Failed to setup NLTK")
            
        # Process the file
        consolidate_terms(input_file)
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Consolidate similar terms from unique terms CSV')
    parser.add_argument('input_file', help='Path to the unique terms CSV file')
    args = parser.parse_args()
    
    main(args.input_file) 