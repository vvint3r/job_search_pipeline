import re
import csv

def extract_job_descriptions(csv_file):
  with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile, \
       open('job_results\seo\seo_manager__job_details.txt', 'w', encoding='utf-8') as outfile:

    reader = csv.DictReader(csvfile)
    for row in reader:
      job_description = row.get('Job Description', '')
      outfile.write(job_description + '\n')
      
extract_job_descriptions('job_results\seo\seo_job_details.csv')

# Define file paths
input_file = "job_results/seo/seo_manager__job_details.txt"
stop_words_file = "stop_words.txt"
cleaned_file = "job_results/seo/seo_manager__jd_ready.txt"

# Function to load stop words from a file
def load_stop_words(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            stop_words = set(word.strip().lower() for word in f if word.strip())
        print(f"Loaded {len(stop_words)} stop words.")
        return stop_words
    except FileNotFoundError:
        print(f"Error: Stop words file '{file_path}' not found.")
        exit()

# Function to clean text
def clean_text(text, stop_words):
    # Convert text to lowercase
    text = text.lower()
    # Replace dashes with spaces
    text = text.replace("-", " ")
    # Remove punctuation and special characters and replace with space
    text = re.sub(r"[^a-z0-9]+", " ", text)
    # Remove leading and trailing spaces
    text = text.strip()
    # Split text into words and remove stop words
    words = text.split()
    cleaned_words = [word for word in words if word not in stop_words]
    # Join the words back into a single string
    cleaned_text = " ".join(cleaned_words)
    return cleaned_text

# Load stop words
stop_words = load_stop_words(stop_words_file)

# Read input file
print(f"Reading input file: {input_file}")
try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print(f"Error: File {input_file} not found.")
    exit()

# Clean the text
print("Cleaning the text...")
cleaned_text = clean_text(text, stop_words)

# Write cleaned text to output file
print(f"Writing cleaned text to {cleaned_file}")
try:
    with open(cleaned_file, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
    print(f"Successfully wrote cleaned text to {cleaned_file}.")
except Exception as e:
    print(f"Error writing to cleaned file: {e}")