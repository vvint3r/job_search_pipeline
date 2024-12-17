import os
from collections import Counter

# Define file paths
keywords_file = "/home/wynt3r/JobSearch/job_titles/seo/seo_unified_keywords_counts.txt"
optimized_resume_file = "/home/wynt3r/JobSearch/resumes/seo_resume_main_optimized.txt"
output_comparison_file = "/home/wynt3r/JobSearch/resumes/seo_resume_main_optimized_compare_kwds.txt"

# Function to load keywords and their counts from the keyword index file


def load_keywords(file_path):
    keywords = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                keyword, count = line.rsplit(":", 1)
                keywords[keyword.strip()] = int(count.strip())
        print(f"Loaded {len(keywords)} keywords from {file_path}.")
    except FileNotFoundError:
        print(f"Error: Keywords file '{file_path}' not found.")
        exit()
    return keywords

# Function to count keywords in the optimized resume


def count_keywords_in_resume(file_path, keywords):
    keyword_counts = Counter()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            resume_text = f.read().lower()
            for keyword in keywords:
                keyword_counts[keyword] = resume_text.count(keyword.lower())
        print(f"Counted keywords in the resume from {file_path}.")
    except FileNotFoundError:
        print(f"Error: Optimized resume file '{file_path}' not found.")
        exit()
    return keyword_counts


# Load the original keyword index and counts
print("Loading original keyword index...")
original_keywords = load_keywords(keywords_file)

# Count the occurrences of keywords in the optimized resume
print("Counting keywords in the optimized resume...")
resume_keyword_counts = count_keywords_in_resume(optimized_resume_file, original_keywords)

# Write the comparison results to the output file
print(f"Writing comparison results to {output_comparison_file}...")
try:
    with open(output_comparison_file, "w", encoding="utf-8") as f:
        f.write("Keyword, Original Count, Resume Count\n")
        for keyword, original_count in original_keywords.items():
            resume_count = resume_keyword_counts.get(keyword, 0)
            f.write(f"{keyword}, {original_count}, {resume_count}\n")
    print(f"Successfully wrote comparison results to {output_comparison_file}.")
except Exception as e:
    print(f"Error writing to comparison file: {e}")
