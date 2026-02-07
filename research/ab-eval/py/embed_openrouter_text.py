import os
import sys
import json
import requests
import numpy as np
from dotenv import load_dotenv
import argparse

# Load .env.local from the project root
load_dotenv(".env.local")

def get_embedding(text, api_key):
    """Calls OpenRouter to get the embedding for a given text."""
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")
    
    url = "https://openrouter.ai/api/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3-embedding-8b",
        "input": text
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()['data'][0]['embedding']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.toy.json")
    parser.add_argument("--queries", default="research/ab-eval/data/queries.toy.json")
    parser.add_argument("--out_docs", default="research/ab-eval/out/embeddings_text_docs.jsonl")
    parser.add_argument("--out_queries", default="research/ab-eval/out/embeddings_text_queries.jsonl")
    args = parser.parse_args()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment (.env.local or process env).")
        sys.exit(2)

    # Process Corpus
    print(f"Embedding corpus from {args.corpus}...")
    with open(args.corpus, 'r') as f:
        corpus = json.load(f)
    
    with open(args.out_docs, 'w') as f:
        for font in corpus:
            # Match contextString from scripts/seed-fonts.ts:193
            context = f"Name: {font['name']}. Category: {font['category']}. Tags: {', '.join(font['tags'])}. Description: {font['description']}"
            print(f"  Embedding font: {font['name']}...")
            try:
                embedding = get_embedding(context, api_key)
                f.write(json.dumps({"name": font['name'], "embedding": embedding}) + "\n")
            except Exception as e:
                print(f"    Failed: {e}")

    # Process Queries
    print(f"Embedding queries from {args.queries}...")
    with open(args.queries, 'r') as f:
        queries = json.load(f)
    
    with open(args.out_queries, 'w') as f:
        for q in queries:
            print(f"  Embedding query: {q['text']}...")
            try:
                # Match POST() from src/app/api/search/route.ts:50 (raw message)
                embedding = get_embedding(q['text'], api_key)
                f.write(json.dumps({"id": q['id'], "text": q['text'], "embedding": embedding}) + "\n")
            except Exception as e:
                print(f"    Failed: {e}")

    print("Embedding complete.")

if __name__ == "__main__":
    main()
