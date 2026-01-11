import spacy
import pandas as pd
from pathlib import Path
import sys
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from spacy.tokens import Doc

def read_resume_file(file_path):
    """Read resume content from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def clean_text(text):
    """Clean text based on observed patterns."""
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'\d{3}[-.]?\d{3}[-.]?\d{4}', '', text)
    
    # Remove special characters but keep hyphens in compound words
    text = re.sub(r'[^\w\s-]', ' ', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def should_exclude_term(term):
    """Determine if a term should be excluded."""
    # Common words to exclude
    exclude_words = {
        # Articles and prepositions
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        
        # Gerund verbs and common action words
        'focusing', 'utilizing', 'including', 'allowing', 'being', 'using', 'working',
        'providing', 'supporting', 'enabling', 'ensuring', 'maintaining', 'performing',
        'conducting', 'developing', 'implementing', 'managing', 'leading', 'driving',
        
        # Helper verbs
        'is', 'was', 'were', 'been', 'have', 'has', 'had', 'will', 'would', 'could', 'should',
        
        # Common resume words that don't carry specific meaning alone
        'various', 'multiple', 'different', 'other', 'new', 'key', 'main', 'primary',
        'secondary', 'etc', 'related', 'based', 'well', 'within', 'across', 'among',
        
        # Numbers and single letters
        'i', 'ii', 'iii', 'iv', 'v', 'x', 'xi'
    }
    
    return (
        term.lower() in exclude_words or
        len(term) <= 2 or  # Very short terms
        term.isdigit() or  # Pure numbers
        bool(re.match(r'^[0-9.,%]+$', term))  # Numbers with common separators
    )

def extract_terms(doc, nlp):
    """Extract single terms from document."""
    terms = []
    
    for token in doc:
        if (
            not should_exclude_term(token.text) and
            token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB'] and
            len(token.text) > 2
        ):
            terms.append(token.text.lower())
    
    # Count frequencies
    term_counts = Counter(terms)
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {'Term': term, 'Frequency': count}
        for term, count in term_counts.items()
        if not should_exclude_term(term)
    ])
    
    # Sort by frequency
    if not df.empty:
        df = df.sort_values('Frequency', ascending=False)
    
    return df

class PhraseDetector:
    def __init__(self, nlp):
        self.nlp = nlp
        self.common_patterns = set()
        self.collocation_scores = {}
        
    def analyze_document_structure(self, doc: Doc):
        """Analyze document structure to identify common noun phrase patterns."""
        noun_phrase_patterns = []
        
        for chunk in doc.noun_chunks:
            # Get the POS pattern of the chunk
            pattern = ' '.join([token.pos_ for token in chunk])
            if len(pattern.split()) == 2:  # Only consider 2-word patterns
                noun_phrase_patterns.append(pattern)
        
        # Get most common patterns
        pattern_counts = Counter(noun_phrase_patterns)
        self.common_patterns = {pattern for pattern, count in pattern_counts.items() 
                              if count > 1}  # Patterns that appear multiple times
    
    def calculate_mutual_information(self, doc: Doc):
        """Calculate mutual information scores for word pairs."""
        word_freq = Counter()
        pair_freq = Counter()
        total_pairs = 0
        
        # Count frequencies
        for token in doc:
            if self._is_valid_token(token):
                word_freq[token.text.lower()] += 1
        
        # Count pair frequencies
        for i in range(len(doc) - 1):
            word1, word2 = doc[i:i+2]
            if self._is_valid_token(word1) and self._is_valid_token(word2):
                pair = (word1.text.lower(), word2.text.lower())
                pair_freq[pair] += 1
                total_pairs += 1
        
        # Calculate mutual information scores
        total_words = sum(word_freq.values())
        for pair, pair_count in pair_freq.items():
            word1, word2 = pair
            if word1 in word_freq and word2 in word_freq:
                expected = (word_freq[word1] * word_freq[word2]) / total_words
                actual = pair_count
                if expected > 0:
                    mi_score = np.log2(actual / expected)
                    self.collocation_scores[pair] = mi_score
    
    def _is_valid_token(self, token):
        """Check if token is valid for analysis."""
        return (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and 
                token.pos_ in ['NOUN', 'PROPN', 'ADJ'])
    
    def is_valid_pair(self, word1, word2):
        """Determine if two words form a valid phrase based on analysis."""
        doc = self.nlp(f"{word1} {word2}")
        if len(doc) != 2:
            return False
            
        # Check if follows common POS patterns
        pattern = f"{doc[0].pos_} {doc[1].pos_}"
        if pattern in self.common_patterns:
            return True
            
        # Check collocation score
        pair = (word1.lower(), word2.lower())
        if pair in self.collocation_scores and self.collocation_scores[pair] > 0:
            return True
            
        # Additional linguistic checks
        return (
            # Check if it's a proper noun phrase
            (doc[0].pos_ in ['ADJ', 'NOUN', 'PROPN'] and doc[1].pos_ in ['NOUN', 'PROPN']) or
            
            # Check for technical terms (uppercase followed by noun)
            (doc[0].text[0].isupper() and doc[1].pos_ == 'NOUN') or
            
            # Check for measurement or quantity phrases
            (doc[0].like_num and doc[1].pos_ == 'NOUN') or
            
            # Check for common technical prefixes
            (doc[0].text.lower() in {'data', 'machine', 'deep', 'artificial'} and 
             doc[1].pos_ in ['NOUN', 'PROPN'])
        )

def extract_pairs(doc, phrase_detector):
    """Extract word pairs using dynamic detection."""
    pairs = []
    
    # First, analyze document structure
    phrase_detector.analyze_document_structure(doc)
    phrase_detector.calculate_mutual_information(doc)
    
    # Extract pairs
    for i in range(len(doc) - 1):
        word1, word2 = doc[i:i+2]
        
        # Skip if either word is invalid
        if (word1.is_stop or word1.is_punct or word1.is_space or
            word2.is_stop or word2.is_punct or word2.is_space):
            continue
        
        # Check if pair is valid using dynamic detection
        if phrase_detector.is_valid_pair(word1.text, word2.text):
            pairs.append(f"{word1.text} {word2.text}")
    
    # Count frequencies
    pair_counts = Counter(pairs)
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {'Term': pair, 'Frequency': count}
        for pair, count in pair_counts.items()
    ])
    
    # Sort by frequency
    if not df.empty:
        df = df.sort_values('Frequency', ascending=False)
    
    return df

def process_resume(input_path):
    """Process resume with dynamic pair detection."""
    input_path = Path(input_path)
    
    # Define output paths
    output_base_path = Path('C:/Users/vasil/OneDrive/Desktop/gProjects/gjobstyr/resume_processing/resume_outputs/gen_agg')
    output_base_path.mkdir(parents=True, exist_ok=True)
    terms_output = output_base_path / f"{input_path.stem}_terms.csv"
    pairs_output = output_base_path / f"{input_path.stem}_pairs.csv"
    
    print(f"Reading resume from: {input_path}")
    resume_text = read_resume_file(input_path)
    cleaned_text = clean_text(resume_text)
    
    # Load spaCy model
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(cleaned_text)
    
    # Initialize phrase detector
    phrase_detector = PhraseDetector(nlp)
    
    # Extract terms and pairs
    terms_df = extract_terms(doc, nlp)
    pairs_df = extract_pairs(doc, phrase_detector)
    
    # Save to CSV files
    terms_df.to_csv(terms_output, index=False)
    pairs_df.to_csv(pairs_output, index=False)
    
    print(f"\nFiles saved:")
    print(f"- Single terms: {terms_output}")
    print(f"- Word pairs: {pairs_output}")
    
    return terms_df, pairs_df

def main():
    base_dir = Path('C:/Users/vasil/OneDrive/Desktop/gProjects/gjobstyr/resume_processing')
    input_file = base_dir / "resume_outputs/cleaned" / "resume_cleaned.txt"
    try:
        terms_df, pairs_df = process_resume(input_file)
        
        print("\nTop single terms:")
        print(terms_df.head(10))
        print("\nTop word pairs:")
        print(pairs_df.head(10))
        
    except Exception as e:
        print(f"Error processing resume: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
