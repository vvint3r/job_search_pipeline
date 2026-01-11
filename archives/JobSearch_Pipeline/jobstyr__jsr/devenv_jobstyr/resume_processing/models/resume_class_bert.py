import pandas as pd
from pathlib import Path
import sys
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np
from typing import List, Dict, Tuple
import spacy
from collections import Counter
import re

class DynamicResumeAnalyzer:
    def __init__(self, n_categories=5):
        """Initialize the BERT model and other components."""
        print("Loading BERT model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModel.from_pretrained('bert-base-uncased')
        
        print("Loading spaCy model...")
        self.nlp = spacy.load('en_core_web_sm')
        
        self.n_categories = n_categories
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

    def read_resume(self, file_path: str) -> str:
        """Read resume content from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()

    def get_bert_embedding(self, text: str) -> np.ndarray:
        """Get BERT embedding for a piece of text."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
        
        return embeddings[0]

    def extract_sections(self, text: str) -> List[str]:
        """Extract resume sections based on common headers."""
        common_headers = [
            'education', 'experience', 'skills', 'projects', 'achievements',
            'certifications', 'summary', 'objective', 'work', 'employment',
            'technical', 'professional', 'leadership', 'volunteer'
        ]
        
        # Split text into lines
        lines = text.split('\n')
        sections = []
        current_section = []
        
        for line in lines:
            # Check if line might be a header
            if any(header in line.lower() for header in common_headers):
                if current_section:
                    sections.append(' '.join(current_section))
                current_section = []
            current_section.append(line)
            
        if current_section:
            sections.append(' '.join(current_section))
            
        return sections

    def extract_candidate_terms(self, text: str) -> List[str]:
        """Extract candidate terms using spaCy with enhanced patterns."""
        doc = self.nlp(text)
        terms = []
        
        # Custom patterns for technical terms
        technical_patterns = [
            # Version numbers
            r'\b\w+[-_]?\b(?:\.\d+)*\b',
            # Abbreviations
            r'\b[A-Z]{2,}\b',
            # Technology stacks
            r'\b[A-Za-z]+(?:\s*[+&]\s*[A-Za-z]+)+\b'
        ]
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:
                terms.append(chunk.text.lower())
        
        # Extract named entities
        for ent in doc.ents:
            if len(ent.text.split()) <= 3:
                terms.append(ent.text.lower())
        
        # Extract terms matching technical patterns
        for pattern in technical_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                terms.append(match.group().lower())
        
        # Extract individual tokens with specific POS tags
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                len(token.text) > 2):
                terms.append(token.text.lower())
        
        # Clean and deduplicate terms
        terms = list(set(terms))
        terms = [term.strip() for term in terms if len(term.strip()) > 2]
        return terms

    def discover_categories(self, terms: List[str]) -> Dict[str, List[str]]:
        """Discover categories dynamically using topic modeling."""
        # Create document-term matrix
        term_matrix = self.vectorizer.fit_transform([' '.join(terms)])
        
        # Apply NMF for topic modeling
        nmf_model = NMF(n_components=self.n_categories, random_state=42)
        nmf_output = nmf_model.fit_transform(term_matrix)
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Extract top terms for each topic
        categories = {}
        for topic_idx, topic in enumerate(nmf_model.components_):
            top_terms_idx = topic.argsort()[:-10:-1]  # Get top 10 terms
            top_terms = [feature_names[i] for i in top_terms_idx]
            category_name = f"category_{topic_idx+1}"
            categories[category_name] = top_terms
        
        return categories

    def analyze_resume(self, text: str) -> Dict[str, List[Dict[str, any]]]:
        """Analyze resume with dynamic categorization."""
        print("Extracting terms...")
        terms = self.extract_candidate_terms(text)
        
        print("Discovering categories...")
        categories = self.discover_categories(terms)
        
        # Get embeddings for all terms
        print("Computing term embeddings...")
        term_embeddings = {term: self.get_bert_embedding(term) for term in terms}
        
        # Initialize results
        results = {cat_name: [] for cat_name in categories.keys()}
        
        # Categorize terms
        print("Categorizing terms...")
        for term in terms:
            term_embedding = term_embeddings[term]
            
            # Find best matching category
            best_category = None
            best_score = -1
            
            for cat_name, cat_terms in categories.items():
                # Get average embedding for category terms
                cat_embeddings = [self.get_bert_embedding(ct) for ct in cat_terms[:3]]
                cat_embedding = np.mean(cat_embeddings, axis=0)
                
                # Calculate similarity
                score = float(cosine_similarity(
                    term_embedding.reshape(1, -1),
                    cat_embedding.reshape(1, -1)
                )[0][0])
                
                if score > best_score:
                    best_score = score
                    best_category = cat_name
            
            if best_score > 0.3:  # Threshold for inclusion
                results[best_category].append({
                    'term': term,
                    'score': best_score
                })
        
        # Sort results by score
        for category in results:
            results[category] = sorted(
                results[category],
                key=lambda x: x['score'],
                reverse=True
            )
        
        return results

    def save_results(self, results: Dict, output_dir: Path) -> None:
        """Save results to CSV files with _bert suffix in bert subdirectory."""
        output_dir.mkdir(parents=True, exist_ok=True)

        for category, items in results.items():
            if not items:
                continue

            df = pd.DataFrame(items)
            df['score'] = df['score'].round(3)
            df = df.sort_values('score', ascending=False)

            # Update filename format to include _bert suffix
            filename = f"resume_{category}_bert.csv"
            output_path = output_dir / filename
            
            df.to_csv(output_path, index=False)
            
            print(f"\n{category.upper()}")
            print("=" * 80)
            print(f"Total items: {len(df)}")
            print("-" * 80)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            print(df.to_string(index=False))
            print(f"\nSaved to: {output_path}")
            print("-" * 80)


def ensure_output_directory(base_dir: Path) -> Path:
    """Create and return the bert directory in resume_outputs."""
    output_dir = base_dir / "resume_outputs" / "bert"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def main():
    base_dir = Path(__file__).resolve().parent.parent  # Navigate to resume_processing folder
    resume_path = base_dir / "resume_inputs" / "resume.txt"
    output_dir = ensure_output_directory(base_dir)

    try:
        analyzer = DynamicResumeAnalyzer()
        print(f"Reading resume from: {resume_path}")
        resume_text = analyzer.read_resume(resume_path)
        
        print("Analyzing resume with BERT...")
        results = analyzer.analyze_resume(resume_text)
        
        analyzer.save_results(results, output_dir)
            
    except Exception as e:
        print(f"Error processing resume: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
