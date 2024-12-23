import re
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora
from gensim.models import LdaModel
from nltk.util import ngrams
from rake_nltk import Rake
import spacy

# Ensure required NLTK data files are available
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Spacy NLP Model
nlp = spacy.load("en_core_web_sm")

# Define file paths
input_file = "job_results/seo/seo_manager__jd_ready.txt"
output_keywords_file = "job_titles/seo/seo_manager__tfidf_keywords.txt"
output_topics_file = "job_titles/seo/seo_manager__lda_topics.txt"
output_rake_file = "job_titles/seo/seo_manager__rake_keywords.txt"
output_spacy_file = "job_titles/seo/seo_manager__spacy_keywords.txt"

# Function to preprocess text with optional n-grams
def preprocess_text_with_ngrams(text, include_ngrams=True):
    text = text.lower()
    text = re.sub(r'[\W\d]', ' ', text)  # Remove punctuation and numbers
    words = nltk.word_tokenize(text)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    words = [word for word in words if word not in stop_words and len(word) > 1]
    if not words:
        words = ["placeholder"]  # Fallback token

    # Optionally generate bigrams and trigrams
    if include_ngrams:
        bigrams = generate_ngrams(words, 2)
        trigrams = generate_ngrams(words, 3)
        return words + bigrams + trigrams
    return words

# Function to load and preprocess text data
def load_and_preprocess_text(file_path):
    print(f"Reading input file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        exit()
    if not text.strip():
        print("Error: Input file is empty.")
        exit()
    return preprocess_text_with_ngrams(text)

# Function to generate n-grams
def generate_ngrams(tokens, n=2):
    return [' '.join(gram) for gram in ngrams(tokens, n)]

# TF-IDF to extract keywords
def extract_keywords_with_tfidf(corpus, top_n=100):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([' '.join(doc) for doc in corpus])
    terms = vectorizer.get_feature_names_out()
    tfidf_scores = np.sum(X.toarray(), axis=0)
    term_scores = dict(zip(terms, tfidf_scores))
    sorted_terms = sorted(term_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_terms[:top_n]

# LDA for topic modeling
def extract_topics_with_lda(corpus, num_topics=10, passes=15):
    dictionary = corpora.Dictionary(corpus)
    dictionary.filter_extremes(no_below=1, no_above=1.0)  # Adjust thresholds
    bow_corpus = [dictionary.doc2bow(doc) for doc in corpus]
    if not bow_corpus or all(len(doc) == 0 for doc in bow_corpus):
        raise ValueError("Cannot compute LDA: All documents are empty after preprocessing.")
    lda_model = LdaModel(bow_corpus, num_topics=num_topics, id2word=dictionary, passes=passes)
    return lda_model.print_topics(-1)

def extract_key_phrases_with_rake(text, n=3):
    """
    Extract unique key phrases using RAKE with up to n-word phrases.
    """
    rake = Rake()  # Use default or custom stopwords as needed
    rake.extract_keywords_from_text(text)

    ranked_phrases = rake.get_ranked_phrases_with_scores()
    print(f"RAKE extracted {len(ranked_phrases)} phrases.")  # Debug

    # Filter for phrases with up to n words and remove duplicates
    seen = set()
    filtered_phrases = []
    for score, phrase in ranked_phrases:
        if len(phrase.split()) <= n and phrase not in seen:
            filtered_phrases.append((score, phrase))
            seen.add(phrase)

    print(f"Filtered to {len(filtered_phrases)} unique phrases with up to {n} words.")  # Debug
    return filtered_phrases

# Function for Spacy-based key phrase extraction
def extract_noun_phrases_with_spacy(text, n=3):
    """
    Extract noun phrases with Spacy, limiting results to 1 to n words.
    """
    doc = nlp(text)
    noun_phrases = set()  # Use a set to ensure uniqueness

    for chunk in doc.noun_chunks:
        # Limit the phrases to those with 1 to n words
        if 1 <= len(chunk.text.split()) <= n:
            noun_phrases.add(chunk.text.strip())

    print(f"Spacy extracted {len(noun_phrases)} noun phrases.")  # Debug
    return list(noun_phrases)

# Main workflow
def main():
    # Load and preprocess the text
    corpus = [load_and_preprocess_text(input_file)]

    # Extract top keywords using TF-IDF
    print("Extracting keywords using TF-IDF...")
    top_keywords = extract_keywords_with_tfidf(corpus)
    print(f"Writing TF-IDF keywords to {output_keywords_file}")
    with open(output_keywords_file, "w", encoding="utf-8") as f:
        for term, score in top_keywords:
            f.write(f"{term}: {score}\n")

    # Extract topics using LDA
    print("Extracting topics using LDA...")
    lda_topics = extract_topics_with_lda(corpus)
    print(f"Writing LDA topics to {output_topics_file}")
    with open(output_topics_file, "w", encoding="utf-8") as f:
        for idx, topic in lda_topics:
            f.write(f"Topic {idx}: {topic}\n")

    # Extract key phrases using RAKE
    print("Extracting key phrases using RAKE...")
    with open(output_rake_file, "w", encoding="utf-8") as f:
        rake_phrases = extract_key_phrases_with_rake(' '.join(corpus[0]))
        for score, phrase in rake_phrases:
            f.write(f"{phrase}: {score}\n")

    # Extract noun phrases using Spacy
    print("Extracting noun phrases using Spacy...")
    with open(output_spacy_file, "w", encoding="utf-8") as f:
        noun_phrases = extract_noun_phrases_with_spacy(' '.join(corpus[0]))
        for phrase in noun_phrases:
            f.write(f"{phrase}\n")

    print("Processing complete.")

# Run the workflow
if __name__ == "__main__":
    main()
