import os
import json
import requests
import random
import time
import argparse

def fetch_fonts_list():
    """Fetches the list of all fonts from Fontsource."""
    print("Fetching fonts list from Fontsource...")
    resp = requests.get("https://api.fontsource.org/v1/fonts", timeout=10)
    resp.raise_for_status()
    return resp.json()

def fetch_font_details(font_id):
    """Fetches details for a specific font."""
    resp = requests.get(f"https://api.fontsource.org/v1/fonts/{font_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_best_file_url(details):
    """Extracts a stable TTF or WOFF2 URL for the 400 normal variant."""
    variants = details.get('variants', {})
    # Try 400 weight, then 500, then whatever is available
    weights = ['400', '500', 'regular']
    for w in weights:
        if w in variants:
            styles = variants[w]
            # Try normal, then italic
            for s in ['normal', 'italic']:
                if s in styles:
                    subsets = styles[s]
                    # Try latin, then anything
                    for sub in ['latin', 'latin-ext', next(iter(subsets.keys()))]:
                        if sub in subsets:
                            url_dict = subsets[sub].get('url', {})
                            # Prefer TTF for better compatibility with some renderers, then WOFF2
                            return url_dict.get('ttf') or url_dict.get('woff2')
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--out", default="research/ab-eval/data/corpus.200.json")
    parser.add_argument("--fonts-dir", default="research/ab-eval/out/fonts")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    os.makedirs(args.fonts_dir, exist_ok=True)

    all_fonts = fetch_fonts_list()
    # Filter for Google fonts to keep it clean
    google_fonts = [f for f in all_fonts if f.get('type') == 'google']
    
    # Group by category
    by_cat = {}
    for f in google_fonts:
        cat = f.get('category', 'other')
        if cat not in by_cat: by_cat[cat] = []
        by_cat[cat].append(f)
    
    print(f"Categories found: {list(by_cat.keys())}")
    
    # Stratified sampling
    target_count = args.limit
    cats = ['sans-serif', 'serif', 'display', 'handwriting', 'monospace']
    per_cat = target_count // len(cats)
    
    selected_fonts = []
    for cat in cats:
        fonts_in_cat = by_cat.get(cat, [])
        # Shuffle for variety
        random.seed(42) # Reproducibility
        random.shuffle(fonts_in_cat)
        selected_fonts.extend(fonts_in_cat[:per_cat])
    
    # Fill remaining if any
    if len(selected_fonts) < target_count:
        remaining_count = target_count - len(selected_fonts)
        already_selected = {f['id'] for f in selected_fonts}
        others = [f for f in google_fonts if f['id'] not in already_selected]
        random.shuffle(others)
        selected_fonts.extend(others[:remaining_count])

    print(f"Selected {len(selected_fonts)} fonts. Fetching details and validating URLs...")
    
    corpus = []
    for i, f in enumerate(selected_fonts):
        fid = f['id']
        print(f"[{i+1}/{len(selected_fonts)}] Processing {fid}...")
        try:
            details = fetch_font_details(fid)
            url = get_best_file_url(details)
            
            if not url:
                print(f"  Warning: No suitable file URL for {fid}")
                continue
                
            # Basic validation (HEAD request)
            try:
                head = requests.head(url, timeout=5, allow_redirects=True)
                if head.status_code >= 400:
                    print(f"  Warning: URL validation failed for {fid} ({head.status_code})")
                    continue
            except Exception as e:
                print(f"  Warning: URL validation error for {fid}: {e}")
                continue

            # Create corpus entry
            entry = {
                "name": f['family'],
                "category": f.get('category', 'unknown'),
                "source": "Google Fonts (via Fontsource)",
                "tags": f.get('subsets', []), # Use subsets as proxy tags if nothing else
                "description": f"A {f.get('category')} font from Google Fonts.",
                "files": {
                    "400": url
                },
                "fontsource_id": fid
            }
            corpus.append(entry)
            
            # Optional: Download to cache
            # ext = "ttf" if ".ttf" in url else "woff2"
            # local_path = os.path.join(args.fonts_dir, f"{fid}.{ext}")
            # if not os.path.exists(local_path):
            #     r = requests.get(url, timeout=10)
            #     with open(local_path, 'wb') as f_out:
            #         f_out.write(r.content)
            
            # Be nice to the API
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  Error processing {fid}: {e}")

    print(f"Successfully built corpus with {len(corpus)} fonts.")
    with open(args.out, 'w') as f:
        json.dump(corpus, f, indent=2)
    print(f"Saved to {args.out}")

if __name__ == "__main__":
    main()
