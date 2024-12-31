import pandas as pd
from collections import Counter
import os
import logging

def generate_unique_terms_report(input_file):
    """Generate a report of unique terms from job descriptions."""
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        if 'description' not in df.columns:
            raise KeyError("No 'description' column found in the input file")
        
        # Concatenate all descriptions into a single string
        all_descriptions = ' '.join(df['description'].dropna())
        
        # Split into words and count occurrences
        words = all_descriptions.split()
        word_counts = Counter(words)
        
        # Calculate metrics
        total_jobs = len(df)
        unique_terms = []
        
        for word, total_occurrences in word_counts.items():
            num_jobs_with_term = sum(df['description'].str.contains(rf'\b{word}\b', na=False))
            percentage_jobs = (num_jobs_with_term / total_jobs) * 100 if total_jobs > 0 else 0
            avg_occurrences = total_occurrences / num_jobs_with_term if num_jobs_with_term > 0 else 0
            
            unique_terms.append({
                'term': word,
                'total_occurrences': total_occurrences,
                'num_jobs_with_term': num_jobs_with_term,
                'percentage_jobs': percentage_jobs,
                'avg_occurrences': avg_occurrences
            })
        
        # Convert to DataFrame
        unique_terms_df = pd.DataFrame(unique_terms)
        
        # Generate output filename
        input_dir = os.path.dirname(input_file)
        base_name = os.path.basename(input_file)
        filename, ext = os.path.splitext(base_name)
        output_file = os.path.join(input_dir, f"{filename}_unq_terms{ext}")
        
        # Save to CSV
        unique_terms_df.to_csv(output_file, index=False)
        logging.info(f"Unique terms report saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Error generating unique terms report: {e}")
        raise