from rake_nltk import Rake
from collections import Counter
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt')  # Ensure NLTK resources are available

def generate_dynamic_stopwords(text, threshold=5):
    """
    Generate stopwords dynamically based on word frequency in the text.
    Args:
        text (str): Input text to analyze.
        threshold (int): Minimum frequency for a word to be treated as a stopword.

    Returns:
        set: A set of dynamically generated stopwords.
    """
    words = word_tokenize(text.lower())
    freq = Counter(words)
    # Remove single-character words and tokens below the threshold
    return {word for word, count in freq.items() if count > threshold or len(word) == 1}

def extract_key_phrases_with_rake(text, n=3, dynamic_stopwords=None):
    """
    Extract unique key phrases using RAKE with up to n-word phrases.

    Args:
        text (str): The input text to analyze.
        n (int): The maximum number of words in a phrase to include.
        dynamic_stopwords (set): Dynamically generated stopwords to add to RAKE.

    Returns:
        list of tuples: A list of (score, phrase) tuples for the extracted phrases.
    """
    # Initialize RAKE with combined default and dynamic stopwords
    rake = Rake(stopwords=dynamic_stopwords)

    # Extract phrases using RAKE
    rake.extract_keywords_from_text(text)

    # Retrieve ranked phrases and their scores
    ranked_phrases = rake.get_ranked_phrases_with_scores()
    print(f"RAKE extracted {len(ranked_phrases)} phrases.")  # Debug

    # Filter phrases to include only those with up to n words and ensure uniqueness
    seen = set()
    filtered_phrases = []
    for score, phrase in ranked_phrases:
        if len(phrase.split()) <= n and phrase not in seen:
            filtered_phrases.append((score, phrase))
            seen.add(phrase)

    print(f"Filtered to {len(filtered_phrases)} unique phrases with up to {n} words.")  # Debug
    return filtered_phrases

if __name__ == "__main__":
    input_file = "job_results/seo/seo_manager__jd_ready.txt"
    output_file = "job_titles/seo/seo_manager__rake_keywords.txt"

    # Read input text from file
    print(f"Reading input file: {input_file}")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        exit()

    # Generate dynamic stopwords
    print("Generating dynamic stopwords...")
    dynamic_stopwords = generate_dynamic_stopwords(text)

    # Extract phrases with a limit of 3 words per phrase
    phrases = extract_key_phrases_with_rake(text, n=3, dynamic_stopwords=dynamic_stopwords)

    # Write results to output file
    print(f"Writing {len(phrases)} phrases to {output_file}")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for score, phrase in phrases:
                f.write(f"{phrase}: {score}\n")
        print(f"Successfully wrote RAKE phrases to {output_file}.")
    except Exception as e:
        print(f"Error writing to output file: {e}")
