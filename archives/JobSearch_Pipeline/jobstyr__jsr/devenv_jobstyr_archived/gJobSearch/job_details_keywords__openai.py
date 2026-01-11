import os
from openai import OpenAI

# Set your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OpenAI API key not found. Please set it as an environment variable.")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Define file paths
input_file = "job_results/seo/seo_manager__jd_ready.txt"
output_file = "job_titles/seo/seo_manager__jd_keywords.txt"

# Define the job field
job_field = "SEO Manager"

# Function to read and chunk text
def split_text_into_chunks(text, max_tokens=4000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        current_length += len(word) + 1  # Account for space
        if current_length > max_tokens:
            # Join the chunk words with spaces and add to chunks
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = len(word) + 1
        current_chunk.append(word)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# Function to format chunk as individual words
def format_chunk_as_individual_words(chunk):
    words = chunk.split()
    return "\n".join(words)  # Each word on a new line

# Function to generate a prompt for a chunk of text
def generate_prompt_for_chunk(chunk, job_field):
    return (
        f"The following are individual words extracted from a job description for the role of \"{job_field}\":\n\n"
        f"{chunk}\n\n"
        f"Based on the words above, identify at least 100 or more terms (1 to 3 words each) that are "
        f"relevant to the job title: \"{job_field}\". Provide the output as a list of keywords, separated "
        f"by commas, sorted by relevance.\n"
    )

# Function to interact with OpenAI API
def extract_keywords(prompt):
    print(f"Status: Sending prompt to OpenAI for keyword extraction.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
            max_tokens=8000,
            n=1
        )
        content = response.choices[0].message.content
        print(f"Status: Received response from OpenAI:\n{content[:100]}...\n")
        return content
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return None

# Read and process the input file
print(f"Reading input file: {input_file}")
try:
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()
except FileNotFoundError:
    print(f"Error: File {input_file} not found.")
    exit()

# Split the text into chunks
chunks = split_text_into_chunks(text, max_tokens=4000)
print(f"Split input text into {len(chunks)} chunks.")

# Process each chunk and write results to output file
print(f"Writing results to {output_file}")
try:
    with open(output_file, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, start=1):
            print(f"Processing chunk {i} of {len(chunks)}...")
            prompt = generate_prompt_for_chunk(chunk, job_field)
            response_content = extract_keywords(prompt)
            if response_content:
                # Write the keywords for the chunk to the file
                f.write(f"Chunk {i} Keywords:\n")
                f.write(response_content + "\n\n")
        print(f"Successfully wrote all keywords to {output_file}.")
except Exception as e:
    print(f"Error writing to output file: {e}")
