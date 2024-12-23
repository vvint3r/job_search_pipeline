from top2vec import Top2Vec
import os

# Define file paths
input_file = "/home/wynt3r/JobSearch/job_results/seo/seo_manager__job_details_cleaned_w_stop.txt"
output_model_file = "/home/wynt3r/JobSearch/job_results/seo/top2vec_model"
output_keywords_file = "/home/wynt3r/JobSearch/job_results/seo/seo_manager_top2vec_keywords.txt"

# Function to split text into sentences or chunks


def load_documents_as_sentences(file_path):
    """Load text and split it into sentences."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        sentences = text.split(". ")  # Split on periods for sentence chunks
        print(f"Loaded {len(sentences)} sentences as individual documents.")
        return sentences
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit()

# Train Top2Vec model and extract topics


def extract_topics_with_top2vec(sentences, output_model_file, output_keywords_file, num_words=10):
    """Train Top2Vec and extract topics."""
    print("Training Top2Vec model...")
    try:
        model = Top2Vec(sentences, speed="learn", workers=4)
        print("Top2Vec model training complete.")
        model.save(output_model_file)

        # Extract topics
        topic_words, _, _ = model.get_topics()
        print(f"Extracted {len(topic_words)} topics.")

        # Write keywords to file
        with open(output_keywords_file, "w", encoding="utf-8") as f:
            for i, words in enumerate(topic_words):
                f.write(f"Topic {i + 1}: {', '.join(words[:num_words])}\n")
        print(f"Successfully wrote topics to {output_keywords_file}.")
    except Exception as e:
        print(f"Error training Top2Vec or extracting topics: {e}")


# Load documents
sentences = load_documents_as_sentences(input_file)

# Train and extract topics
extract_topics_with_top2vec(sentences, output_model_file, output_keywords_file)
