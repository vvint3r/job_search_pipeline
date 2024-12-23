import re
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
import spacy
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Define file paths
input_file = "/home/wynt3r/JobSearch/job_results/seo/seo_manager__job_details_cleaned_w_stop.txt"
output_file = "/home/wynt3r/JobSearch/job_results/seo/seo_manager_keyphrases.txt"

# Initialize KeyBERT model
model = KeyBERT()

# Function to preprocess text using SpaCy (without removing stop words)


def preprocess_text(text):
    """Preprocess text using SpaCy for lemmatization, keep stop words."""
    doc = nlp(text)
    clean_text = " ".join([token.text for token in doc if not token.is_punct])  # Keep stop words
    return clean_text

# Function to extract key phrases using KeyBERT


def extract_key_phrases(text):
    """Extract 2 to 3-word key phrases using KeyBERT."""
    # Preprocess the text
    cleaned_text = preprocess_text(text)

    # Use KeyphraseCountVectorizer to enforce 2-3 word n-grams
    vectorizer = KeyphraseCountVectorizer(spacy_pipeline=nlp, stop_words=None)

    # Extract key phrases directly with ngram control
    key_phrases = model.extract_keywords(
        cleaned_text,
        vectorizer=vectorizer,
        top_n=50                       # Top 50 key phrases by relevance
    )
    return key_phrases


# Read the input file
print(f"Reading input file: {input_file}")
try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print(f"Error: Input file '{input_file}' not found.")
    exit()

# Extract key phrases
print("Extracting key phrases using KeyBERT with 2-3 words...")
key_phrases = extract_key_phrases(text)

# Write the results to the output file
print(f"Writing key phrases and scores to {output_file}")
try:
    with open(output_file, "w", encoding="utf-8") as f:
        for phrase, score in key_phrases:
            f.write(f"{phrase}: {score:.4f}\n")
    print(f"Successfully wrote key phrases to {output_file}.")
except Exception as e:
    print(f"Error writing to output file: {e}")




import re
from keybert import KeyBERT
from keyphrase_vectorizers import KeyphraseCountVectorizer
import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Define file paths
input_file = "/home/wynt3r/JobSearch/job_results/seo/seo_manager__job_details_cleaned_w_stop.txt"
output_file = "/home/wynt3r/JobSearch/job_results/seo/seo_manager_keyphrases.txt"

# Initialize KeyBERT model
model = KeyBERT()

# Function to preprocess text using SpaCy (without removing stop words)
def preprocess_text(text):
    """Preprocess text using SpaCy for lemmatization, keep stop words."""
    doc = nlp(text)
    clean_text = " ".join([token.text for token in doc if not token.is_punct])  # Keep stop words
    return clean_text

# Function to extract key phrases using KeyBERT
def extract_key_phrases(text):
    """Extract 2 to 3-word key phrases using KeyBERT."""
    # Preprocess the text
    cleaned_text = preprocess_text(text)

    # Use KeyphraseCountVectorizer to enforce 2-3 word n-grams
    vectorizer = KeyphraseCountVectorizer(spacy_pipeline=nlp, stop_words=None)

    # Extract key phrases directly with ngram control
    key_phrases = model.extract_keywords(
        cleaned_text,
        vectorizer=vectorizer,
        top_n=50                       # Top 50 key phrases by relevance
    )
    return key_phrases

# Read the input file
print(f"Reading input file: {input_file}")
try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print(f"Error: Input file '{input_file}' not found.")
    exit()

# Extract key phrases
print("Extracting key phrases using KeyBERT with 2-3 words...")
key_phrases = extract_key_phrases(text)

# Write the results to the output file
print(f"Writing key phrases and scores to {output_file}")
try:
    with open(output_file, "w", encoding="utf-8") as f:
        for phrase, score in key_phrases:
            f.write(f"{phrase}: {score:.4f}\n")
    print(f"Successfully wrote key phrases to {output_file}.")
except Exception as e:
    print(f"Error writing to output file: {e}")