import re
from spacy.lang.en.stop_words import STOP_WORDS
from pathlib import Path

# Add additional custom stopwords (connecting words, helper verbs, etc.)
custom_stopwords = set(STOP_WORDS).union({
    "and", "or", "but", "so", "because", "with", "in", "on", "at",
    "is", "are", "was", "were", "be", "been", "being",
    "of", "for", "to", "from", "by", "about", "like", "as", "the", "an", "a",
    "this", "that", "these", "those", "it", "its", "they", "them", "their"
})

def clean_text(text):
    # Remove special characters and extra spaces
    text = re.sub(r"[^\w\s]", " ", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces

    # Remove parenthetical words/symbols
    text = re.sub(r"\(.*?\)|\[.*?\]|\{.*?\}|\".*?\"", "", text)

    # Remove gerund verbs (-ing words)
    text = re.sub(r"\b\w+ing\b", "", text)

    # Remove email/phone formatting characters
    text = re.sub(r"[+\-()\d@.]", "", text)
    
    # Remove single-letter words (except 'a' and 'I')
    text = re.sub(r"\b[b-zB-Z]\b", "", text)

    # Remove stopwords
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in custom_stopwords]

    return " ".join(filtered_words)

# Process input and output files
def process_file(input_file: Path, output_file: Path):
    try:
        # Read input file
        with open(input_file, "r", encoding="utf-8") as infile:
            text = infile.read()

        # Clean the text
        cleaned_text = clean_text(text)

        # Write the cleaned text to output file
        output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(cleaned_text)

        print(f"Cleaned text written to: {output_file}")

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
def main():
    base_dir = Path('C:/Users/vasil/OneDrive/Desktop/gProjects/gjobstyr/resume_processing')
    input_file = base_dir / "resume_inputs" / "resume.txt"
    output_file = base_dir / "resume_outputs" / "cleaned" / "resume_cleaned.txt"
    
    process_file(input_file, output_file)

if __name__ == "__main__":
    main()
