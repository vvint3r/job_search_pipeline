import os
from collections import Counter

# Define file paths
input_file = "/home/wynt3r/JobSearch/job_titles/seo/seo_manager__jd_keywords.txt"
output_file = "/home/wynt3r/JobSearch/job_titles/seo/seo_manager_unified_keywords_counts.txt"

# Function to unify all chunks into a single keyword list and count occurrences
# Includes nested phrase counting


def unify_and_count_keywords_with_nested(input_file):
    keyword_counter = Counter()

    print(f"Processing file: {input_file}")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            all_keywords = []
            for line in f:
                if line.strip() and not line.lower().startswith("chunk"):
                    keywords = [kw.strip().lower() for kw in line.split(',') if kw.strip()]
                    all_keywords.extend(keywords)

            # Count occurrences, including nested phrases
            for keyword in all_keywords:
                keyword_counter[keyword] += sum(1 for phrase in all_keywords if keyword in phrase)
    except Exception as e:
        print(f"Error reading input file {input_file}: {e}")

    return keyword_counter


# Combine all keywords and count occurrences
print("Combining all keywords and counting nested occurrences...")
keywords_count = unify_and_count_keywords_with_nested(input_file)

# Sort keywords by count in descending order
sorted_keywords_count = sorted(keywords_count.items(), key=lambda x: x[1], reverse=True)

# Write the results to the output file
print(f"Writing unified keywords and counts to {output_file}")
try:
    with open(output_file, "w", encoding="utf-8") as f:
        for keyword, count in sorted_keywords_count:
            f.write(f"{keyword}: {count}\n")
    print(f"Successfully wrote unified keywords and counts to {output_file}.")
except Exception as e:
    print(f"Error writing to output file: {e}")
