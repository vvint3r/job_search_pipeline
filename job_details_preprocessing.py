import os
import re
import csv

# Define file paths
input_file = "/home/wynt3r/JobSearch/job_results/seo/seo_job_details.csv"
stop_words_file = "/home/wynt3r/JobSearch/stop_words.txt"
output_raw_file = "/home/wynt3r/JobSearch/job_results/seo/seo_manager__job_details_raw.txt"
output_with_stop = "/home/wynt3r/JobSearch/job_results/seo/seo_manager__job_details_cleaned_w_stop.txt"
output_without_stop = "/home/wynt3r/JobSearch/job_results/seo/seo_manager__job_details_cleaned_wo_stop.txt"
chunk_dir = "/home/wynt3r/JobSearch/job_results/seo/chunks/"

# Function to extract job descriptions from CSV and store raw text


def extract_raw_job_descriptions(input_file, output_file):
    """Extract raw job descriptions and write them to a file."""
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile, \
            open(output_file, 'w', encoding='utf-8') as outfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            job_description = row.get('Job Description', '')
            outfile.write(job_description + '\n')
    print(f"Successfully wrote raw text to {output_file}.")

# Function to load stop words


def load_stop_words(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            stop_words = set(word.strip().lower() for word in f if word.strip())
        print(f"Loaded {len(stop_words)} stop words.")
        return stop_words
    except FileNotFoundError:
        print(f"Error: Stop words file '{file_path}' not found.")
        exit()

# Function to clean text (removes stop words if specified)


def clean_text(text, stop_words=None):
    """Clean text by removing punctuation, and optionally stop words."""
    # Convert text to lowercase
    text = text.lower()
    # Replace dashes with spaces
    text = text.replace("-", " ")
    # Remove punctuation and special characters
    text = re.sub(r"[^a-z0-9]+", " ", text)
    # Remove stop words if provided
    if stop_words:
        for stop_word in stop_words:
            text = text.replace(f" {stop_word} ", " ")
    return text.strip()

# Function to split text into chunks


def split_into_chunks(text, num_chunks, output_dir, prefix):
    """Split text into equal-sized chunks."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    words = text.split()
    chunk_size = max(1, len(words) // num_chunks)

    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < num_chunks - 1 else len(words)
        chunk_words = words[start:end]
        chunk_file = os.path.join(output_dir, f"{prefix}_chunk_{i + 1}.txt")
        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(" ".join(chunk_words))
        print(f"Successfully wrote chunk {i + 1} to {chunk_file}.")


# Step 1: Extract and save raw text
extract_raw_job_descriptions(input_file, output_raw_file)

# Step 2: Load stop words
stop_words = load_stop_words(stop_words_file)

# Step 3: Clean text with and without stop words
with open(output_raw_file, "r", encoding="utf-8") as f:
    raw_text = f.read()

# Save cleaned text with stop words
print(f"Writing cleaned text with stop words to {output_with_stop}")
with open(output_with_stop, "w", encoding="utf-8") as f:
    f.write(clean_text(raw_text))  # Keeps stop words

# Save cleaned text without stop words
print(f"Writing cleaned text without stop words to {output_without_stop}")
with open(output_without_stop, "w", encoding="utf-8") as f:
    f.write(clean_text(raw_text, stop_words))  # Removes stop words

# Step 4: Split cleaned texts into chunks
print("Splitting text into chunks...")
split_into_chunks(raw_text, 20, chunk_dir, "raw")  # Raw text chunks
split_into_chunks(clean_text(raw_text), 20, chunk_dir, "with_stop")
split_into_chunks(clean_text(raw_text, stop_words), 20, chunk_dir, "without_stop")
