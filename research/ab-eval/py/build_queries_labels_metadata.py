import json
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.200.json")
    parser.add_argument("--queries-out", default="research/ab-eval/data/queries.200.json")
    parser.add_argument("--labels-out", default="research/ab-eval/data/labels.200.json")
    args = parser.parse_args()

    if not os.path.exists(args.corpus):
        print(f"Error: Corpus file {args.corpus} not found.")
        return

    with open(args.corpus, 'r') as f:
        corpus = json.load(f)

    # Define query templates
    # (query_text, category_match, subset_match)
    templates = [
        ("serif fonts", "serif", None),
        ("sans-serif fonts", "sans-serif", None),
        ("display fonts", "display", None),
        ("handwriting fonts", "handwriting", None),
        ("monospace fonts", "monospace", None),
        ("elegant serif", "serif", None),
        ("modern sans-serif", "sans-serif", None),
        ("decorative display", "display", None),
        ("cursive style", "handwriting", None),
        ("fixed-width coding font", "monospace", None),
        ("fonts with cyrillic support", None, "cyrillic"),
        ("fonts with greek support", None, "greek"),
        ("vietnamese language support", None, "vietnamese"),
        ("korean fonts", None, "korean"),
        ("japanese fonts", None, "japanese"),
    ]

    queries = []
    labels = {}

    for i, (q_text, cat, sub) in enumerate(templates):
        qid = f"q_{i+1:03d}"
        
        # Find relevant fonts
        relevant_fonts = []
        for font in corpus:
            name = font['name']
            is_match = False
            
            if cat and font.get('category') == cat:
                is_match = True
            
            if sub and sub in font.get('tags', []):
                is_match = True
                
            if is_match:
                relevant_fonts.append(name)
        
        # Only add query if there are relevant fonts in this corpus
        if relevant_fonts:
            queries.append({
                "id": qid,
                "text": q_text,
                "class": "category_proxy" if cat else "subset_proxy"
            })
            labels[qid] = relevant_fonts

    print(f"Generated {len(queries)} queries with labels based on metadata.")
    
    with open(args.queries_out, 'w') as f:
        json.dump(queries, f, indent=2)
    
    with open(args.labels_out, 'w') as f:
        json.dump(labels, f, indent=2)

    print(f"Saved queries to {args.queries_out}")
    print(f"Saved labels to {args.labels_out}")
    print("\nIMPORTANT: These labels are PROXY labels derived from objective metadata (category/subsets).")
    print("They measure retrieval consistency with known metadata, not necessarily nuanced visual style.")

if __name__ == "__main__":
    main()
