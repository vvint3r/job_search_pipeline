import os
import logging
import pandas as pd
from abc import ABC, abstractmethod

class KeywordExtractor(ABC):
    @abstractmethod
    def extract_keywords(self, text, top_n=20):
        pass

class KeyBERTExtractor(KeywordExtractor):
    def __init__(self):
        from keybert import KeyBERT
        self.model = KeyBERT()
        self.custom_stop_words = {
            'experience', 'job', 'work', 'team', 'company', 'position', 'role',
            'candidate', 'ability', 'skills', 'qualified', 'requirements',
            'responsibilities', 'duties', 'year', 'years', 'required'
        }

    def extract_keywords(self, text, top_n=20):
        try:
            keywords = self.model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 1),
                stop_words=list(self.custom_stop_words),
                top_n=top_n
            )
            return [keyword for keyword, _ in keywords]
        except Exception as e:
            logging.error(f"KeyBERT extraction error: {e}")
            return []

class YAKEExtractor(KeywordExtractor):
    def __init__(self):
        import yake
        self.kw_extractor = yake.KeywordExtractor(
            lan="en", 
            n=1,
            dedupLim=0.3,
            top=20,
            features=None
        )

    def extract_keywords(self, text, top_n=20):
        try:
            keywords = self.kw_extractor.extract_keywords(text)
            return [keyword for keyword, _ in keywords[:top_n]]
        except Exception as e:
            logging.error(f"YAKE extraction error: {e}")
            return []

class SpacyExtractor(KeywordExtractor):
    def __init__(self):
        import spacy
        self.nlp = spacy.load("en_core_web_sm")

    def extract_keywords(self, text, top_n=20):
        try:
            doc = self.nlp(text)
            keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
            return list(set(keywords))[:top_n]
        except Exception as e:
            logging.error(f"SpaCy extraction error: {e}")
            return []

def get_extractor(model_type):
    extractors = {
        'keybert': KeyBERTExtractor,
        'yake': YAKEExtractor,
        'spacy': SpacyExtractor
    }
    return extractors.get(model_type, KeyBERTExtractor)()

def process_file(input_file, model_types):
    """Process a job details file to extract keywords using multiple models."""
    try:
        df = pd.read_csv(input_file)
        
        # Output filename in same directory as input
        input_dir = os.path.dirname(input_file)
        base_name = os.path.basename(input_file)
        filename, ext = os.path.splitext(base_name)
        output_file = os.path.join(input_dir, f"{filename}_keywords{ext}")
        
        # Extract keywords for each model
        for model_type in model_types:
            extractor = get_extractor(model_type)
            column_name = f"{model_type}_keys"
            df[column_name] = df['description'].apply(
                lambda x: ', '.join(extractor.extract_keywords(x))
            )
        
        # Save results
        df.to_csv(output_file, index=False)
        logging.info(f"Saved keywords to {output_file}")
        
    except Exception as e:
        logging.error(f"Error processing file {input_file}: {e}")
        raise

def main(input_file, model_types):
    """Main function to extract keywords from a specific job details file."""
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File not found: {input_file}")
        
        process_file(input_file, model_types)
        
    except Exception as e:
        logging.error(f"Error in keyword extraction: {e}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Path to the job details CSV file')
    parser.add_argument('--models', nargs='+', help='Keyword extraction models', default=['keybert', 'yake', 'spacy'])
    args = parser.parse_args()
    
    main(args.input_file, args.models) 