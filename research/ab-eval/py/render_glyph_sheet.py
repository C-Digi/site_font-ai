import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import tempfile
import argparse

def render_font(font_path, output_path, text="ABCDEFGHIJKLM\nnopqrstuvwxyz\n1234567890", size=40):
    """Renders a deterministic glyph sheet for a font."""
    img = Image.new('RGB', (512, 256), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"  Error loading font {font_path}: {e}")
        return False
    
    # Use a fixed offset for determinism instead of centering which might vary with font metrics
    draw.multiline_text((20, 20), text, font=font, fill=(0, 0, 0), spacing=10)
    img.save(output_path)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.toy.json")
    parser.add_argument("--out", default="research/ab-eval/out/glyphs")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    
    with open(args.corpus, 'r') as f:
        corpus = json.load(f)
        
    for font in corpus:
        name = font['name']
        print(f"Processing {name}...")
        files = font.get('files', {})
        # Try 400 weight first, then any available
        url = files.get('400') or (next(iter(files.values())) if files else None)
        
        if not url:
            print(f"  No file URL for {name}")
            continue
            
        try:
            # Download font
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name
                
            safe_name = name.replace(' ', '_').replace('/', '_')
            output_path = os.path.join(args.out, f"{safe_name}.png")
            
            if render_font(tmp_path, output_path):
                print(f"  Saved to {output_path}")
            
            os.remove(tmp_path)
        except Exception as e:
            print(f"  Failed to process {name}: {e}")

if __name__ == "__main__":
    main()
