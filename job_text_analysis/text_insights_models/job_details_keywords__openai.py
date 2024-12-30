import os
from openai import OpenAI

# Set your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key not found. Please set it as an environment variable.")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Define file paths
chunk_dir = "/home/wynt3r/JobSearch/job_results/seo/chunks/"
output_file = "/home/wynt3r/JobSearch/job_titles/seo/seo_manager__jd_keywords.txt"

# Define the job field
job_field = "SEO Manager"


def generate_prompt_for_chunk(chunk_text, job_field):
    return (
        f"The following are job description extracts for the role of \"{job_field}\":\n\n"
        f"{chunk_text}\n\n"
        f"Based on the text, identify phrases (from 1 to 3 words long) that are relevant to the job title: \"{job_field}\". \n\n"
        f"Only include phrases where the words appear in the exact order as they do in the text, and they must be contiguous.\n\n"
        f"Do not create phrases by combining non-contiguous words.\n\n"
        f"Provide the output as a unique list of keywords, separated by commas, sorted by relevance.\n"
        f"Only generate keywords.\n"
    )
    

def deduplicate_keywords(response_content):
    """Deduplicate and clean the list of keywords."""
    if not response_content:
        return ""
    keywords = [kw.strip() for kw in response_content.split(",") if kw.strip()]
    unique_keywords = sorted(set(keywords), key=keywords.index)  # Maintain original order
    return ", ".join(unique_keywords)

def extract_keywords(prompt):
    print(f"Status: Sending prompt to OpenAI for keyword extraction.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.5,
            max_tokens=8000,
            n=1
        )
        content = response.choices[0].message.content
        print(f"Status: Received response from OpenAI:\n{content[:100]}...\n")
        return content
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return None

# Process each chunk with OpenAI API
print(f"Processing chunks with OpenAI API and writing results to {output_file}")
try:
    with open(output_file, "w", encoding="utf-8") as f:
        chunk_files = sorted([os.path.join(chunk_dir, file) for file in os.listdir(chunk_dir) if file.endswith('.txt')])
        for i, chunk_file in enumerate(chunk_files, start=1):
            print(f"Processing chunk {i} of {len(chunk_files)}...")
            try:
                with open(chunk_file, "r", encoding="utf-8") as chunk_f:
                    chunk_text = chunk_f.read()
                    # Ensure text in chunk preserves key phrases separated by commas
                    formatted_chunk_text = ", ".join(chunk_text.split())
                    prompt = generate_prompt_for_chunk(formatted_chunk_text, job_field)
                    response_content = extract_keywords(prompt)
                    if response_content:
                        deduplicated_content = deduplicate_keywords(response_content)
                        f.write(f"Chunk {i} Keywords:\n")
                        f.write(deduplicated_content + "\n\n")
            except Exception as e:
                print(f"Error reading chunk {chunk_file}: {e}")
    print(f"Successfully wrote all keywords to {output_file}.")
except Exception as e:
    print(f"Error writing to output file: {e}")
