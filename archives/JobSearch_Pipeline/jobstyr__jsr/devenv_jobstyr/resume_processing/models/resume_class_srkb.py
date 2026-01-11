import spacy
from keybert import KeyBERT
import yake
from pathlib import Path
import pandas as pd

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize KeyBERT model
kw_model = KeyBERT("all-mpnet-base-v2")

# YAKE model settings
yake_language = "en"
yake_max_ngram_size = 3
yake_deduplication_threshold = 0.9
yake_num_keywords = 10
yake_kw_extractor = yake.KeywordExtractor(
    lan=yake_language,
    n=yake_max_ngram_size,
    dedupLim=yake_deduplication_threshold,
    top=yake_num_keywords,
)

def extract_keywords_spacy(text):
    """Extract keywords using spaCy named entities and noun chunks."""
    doc = nlp(text)
    keywords = list(set([ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "GPE", "PRODUCT"]]))
    keywords.extend([chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3])
    return list(set(keywords))

def extract_keywords_keybert(text):
    """Extract keywords using KeyBERT."""
    return [kw for kw, _ in kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english')]

def extract_keywords_yake(text):
    """Extract keywords using YAKE."""
    return [kw for kw, _ in yake_kw_extractor.extract_keywords(text)]

# Process input and output files
def process_file(input_file: Path, output_dir: Path):
    try:
        # Read input file
        with open(input_file, "r", encoding="utf-8") as infile:
            text = infile.read()

        # Extract keywords using spaCy
        spacy_keywords = extract_keywords_spacy(text)
        spacy_df = pd.DataFrame(spacy_keywords, columns=["Keywords"])
        spacy_output_file = output_dir / "spacy" / "resume_spacy_keywords.csv"
        spacy_output_file.parent.mkdir(parents=True, exist_ok=True)
        spacy_df.to_csv(spacy_output_file, index=False)
        print(f"Keywords extracted with spaCy written to: {spacy_output_file}")

        # Extract keywords using KeyBERT
        keybert_keywords = extract_keywords_keybert(text)
        keybert_df = pd.DataFrame(keybert_keywords, columns=["Keywords"])
        keybert_output_file = output_dir / "keybert" / "resume_keybert_keywords.csv"
        keybert_output_file.parent.mkdir(parents=True, exist_ok=True)
        keybert_df.to_csv(keybert_output_file, index=False)
        print(f"Keywords extracted with KeyBERT written to: {keybert_output_file}")

        # Extract keywords using YAKE
        yake_keywords = extract_keywords_yake(text)
        yake_df = pd.DataFrame(yake_keywords, columns=["Keywords"])
        yake_output_file = output_dir / "yake" / "resume_yake_keywords.csv"
        yake_output_file.parent.mkdir(parents=True, exist_ok=True)
        yake_df.to_csv(yake_output_file, index=False)
        print(f"Keywords extracted with YAKE written to: {yake_output_file}")

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
def main():
    base_dir = Path('C:/Users/vasil/OneDrive/Desktop/gProjects/gjobstyr/resume_processing')
    input_file = base_dir / "resume_outputs" / "cleaned" / "resume_cleaned.txt"
    output_dir = base_dir / "resume_outputs"
    
    process_file(input_file, output_dir)

if __name__ == "__main__":
    main()
