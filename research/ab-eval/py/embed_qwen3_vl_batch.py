import os
import json
import argparse
import numpy as np
import subprocess
import sys
from embed_qwen3_vl import Qwen3VLEmbedder

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.toy.json")
    parser.add_argument("--queries", default="research/ab-eval/data/queries.toy.json")
    parser.add_argument("--model", default="Qwen/Qwen3-VL-Embedding-8B")
    parser.add_argument("--out_dir", default="research/ab-eval/out")
    parser.add_argument("--glyph_dir", default="research/ab-eval/out/glyphs")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    # 1. Ensure glyph sheets exist
    print("Ensuring glyph sheets exist...")
    render_script = os.path.join("research", "ab-eval", "py", "render_glyph_sheet.py")
    subprocess.run([sys.executable, render_script, "--corpus", args.corpus, "--out", args.glyph_dir], check=True)

    # 2. Load data
    with open(args.corpus, 'r') as f:
        corpus = json.load(f)
    with open(args.queries, 'r') as f:
        queries = json.load(f)

    # 3. Initialize embedder
    embedder = Qwen3VLEmbedder(model_name=args.model)

    # 4. Generate B1 Doc Embeddings (Image only)
    print("\nGenerating B1 Doc Embeddings (Image only)...")
    b1_items = []
    for font in corpus:
        safe_name = font['name'].replace(' ', '_').replace('/', '_')
        glyph_path = os.path.join(args.glyph_dir, f"{safe_name}.png")
        if os.path.exists(glyph_path):
            b1_items.append({"image": glyph_path})
        else:
            print(f"Warning: Glyph not found for {font['name']}, using empty dict")
            b1_items.append({}) # Should probably handle this better
    
    b1_embs = embedder.embed_items(b1_items)
    np.save(os.path.join(args.out_dir, "embeddings_vl_docs_b1.npy"), b1_embs)
    
    # Save metadata for mapping
    with open(os.path.join(args.out_dir, "metadata_docs.json"), 'w') as f:
        json.dump([{"name": f["name"]} for f in corpus], f)

    # 5. Generate B2 Doc Embeddings (Image + short text)
    print("\nGenerating B2 Doc Embeddings (Image + short text)...")
    b2_items = []
    for font in corpus:
        safe_name = font['name'].replace(' ', '_').replace('/', '_')
        glyph_path = os.path.join(args.glyph_dir, f"{safe_name}.png")
        # Short structured text: Name, Category, Tags
        text_desc = f"Font: {font['name']}. Category: {font['category']}. Tags: {', '.join(font.get('tags', []))}."
        item = {"text": text_desc}
        if os.path.exists(glyph_path):
            item["image"] = glyph_path
        b2_items.append(item)
    
    b2_embs = embedder.embed_items(b2_items)
    np.save(os.path.join(args.out_dir, "embeddings_vl_docs_b2.npy"), b2_embs)

    # 6. Generate Query Embeddings (Text only)
    print("\nGenerating VL Query Embeddings (Text only)...")
    query_items = [{"text": q["text"]} for q in queries]
    query_embs = embedder.embed_items(query_items)
    np.save(os.path.join(args.out_dir, "embeddings_vl_queries.npy"), query_embs)
    
    # Save query metadata
    with open(os.path.join(args.out_dir, "metadata_queries.json"), 'w') as f:
        json.dump([{"id": q["id"], "text": q["text"]} for q in queries], f)

    print("\nBatch embedding complete.")

if __name__ == "__main__":
    main()
