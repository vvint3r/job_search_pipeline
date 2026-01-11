import pandas as pd
import re
from rapidfuzz import fuzz, process

# Load job titles and secondary matching keywords
title_mapping = {
    "Marketing Analytics": ["Marketing Analytics"],
    "Growth Marketing": ["Growth Marketing"],
    "Data Analyst: Marketing": ["Data Analyst", "Marketing"],
    "Data Analyst: Product": ["Data Analyst", "Product"],
    "Demand Generation": ["Demand Generation", "User Acquisition"],
    "Search Marketing": [
        "Search Engine Optimization", "Search Marketing", "SEO", 
        "Search Engine Marketing", "SEM"
    ],
    "Marketing": ["Marketing"],
    "Data Analyst": ["Data Analyst"]
}

seniority_mapping = {
    "Manager": ["Manager"],
    "Sr. Manager": ["Sr\. Manager", "Senior Manager"],
    "Director": ["Director"],
    "Sr. Director": ["Sr\. Director", "Senior Director"],
    "Associate Director": ["Associate Director"],
    "Dept Head": ["Head"],
    "Staff (Principle)": ["Staff", "Principal"],
    "Executive (VP)": ["VP", "Vice President"],
}

specialized_mapping = [
    "Technical", "Enterprise", "Senior", "Jr", "Lead", "Product"
]

def classify_title(title):
    # Define default values
    unified_title_lev1 = "-"
    unified_title_lev2 = "-"
    seniority_level = "Individual Contributor"

    # Match against level 1 job titles using fuzzy matching
    best_match = None
    best_score = 0
    for key, values in title_mapping.items():
        for value in values:
            score = fuzz.partial_ratio(value.lower(), title.lower())
            if score > best_score and score > 80:  # Set threshold for approximate match
                best_score = score
                best_match = key
    
    if best_match:
        if best_match == "Data Analyst" and ("Marketing" not in title and "Product" not in title):
            unified_title_lev1 = best_match
        elif best_match != "Data Analyst":
            unified_title_lev1 = best_match

    # Match specialized role determinant (lev2)
    for keyword in specialized_mapping:
        if re.search(keyword, title, re.IGNORECASE):
            unified_title_lev2 = keyword
            break

    # Match seniority level
    for level, keywords in seniority_mapping.items():
        for keyword in keywords:
            if re.search(keyword, title, re.IGNORECASE):
                seniority_level = level
                break

    return unified_title_lev1, unified_title_lev2, seniority_level

# Load CSV
df = pd.read_csv('job_titles.csv')

# Apply classification
df[['unified_title_lev1', 'unified_title_lev2', 'seniority_level']] = df['Job Title'].apply(
    lambda x: pd.Series(classify_title(x))
)

# Save the output
df.to_csv('classified_job_titles.csv', index=False)

print("Classification complete and saved to 'classified_job_titles.csv'")
