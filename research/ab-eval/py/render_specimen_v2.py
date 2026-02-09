import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import tempfile
import argparse

def render_specimen_v2(font_path, output_path):
    """Renders a deterministic 1024x1024 specimen v2 for a font."""
    WIDTH, HEIGHT = 1024, 1024
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        # Load font at different sizes
        font_display = ImageFont.truetype(font_path, 160)
        font_medium = ImageFont.truetype(font_path, 48)
        font_small = ImageFont.truetype(font_path, 24)
        font_micro = ImageFont.truetype(font_path, 12)
        font_nano = ImageFont.truetype(font_path, 8)
    except Exception as e:
        print(f"  Error loading font {font_path}: {e}")
        return False

    y_offset = 40
    margin = 40

    # 1. Display Section (Large Glyph)
    draw.text((margin, y_offset), "Abg", font=font_display, fill=(0, 0, 0))
    y_offset += 200

    # 2. Character Set Section
    chars_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars_lower = "abcdefghijklmnopqrstuvwxyz"
    chars_num_sym = "0123456789 !@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    draw.text((margin, y_offset), chars_upper, font=font_medium, fill=(0, 0, 0))
    y_offset += 70
    draw.text((margin, y_offset), chars_lower, font=font_medium, fill=(0, 0, 0))
    y_offset += 70
    draw.text((margin, y_offset), chars_num_sym, font=font_medium, fill=(0, 0, 0))
    y_offset += 100

    # 3. Micro-tell Strips
    # Comparison pairs
    pairs = "il1I|  O0  rn/m  vv/w  e/o"
    draw.text((margin, y_offset), "Legibility Pairs:", font=font_small, fill=(100, 100, 100))
    y_offset += 30
    draw.text((margin, y_offset), pairs, font=font_medium, fill=(0, 0, 0))
    y_offset += 80

    # Paragraphs at different sizes
    pangram = "The quick brown fox jumps over the lazy dog."
    draw.text((margin, y_offset), f"24pt: {pangram}", font=font_small, fill=(0, 0, 0))
    y_offset += 50
    draw.text((margin, y_offset), f"12pt: {pangram}", font=font_micro, fill=(0, 0, 0))
    y_offset += 30
    draw.text((margin, y_offset), f"8pt: {pangram}", font=font_nano, fill=(0, 0, 0))
    y_offset += 40

    # Contrast / Detail Strip (Repeating vertical bars)
    strip_text = "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
    draw.text((margin, y_offset), "Contrast Strip:", font=font_small, fill=(100, 100, 100))
    y_offset += 30
    draw.text((margin, y_offset), strip_text, font=font_medium, fill=(0, 0, 0))
    y_offset += 60

    # 4. Vertical "Micro-tell" side strip (optional but good for detail)
    # We'll just add a footer for reproducibility
    draw.text((margin, HEIGHT - 40), f"Specimen v2 - Deterministic 1024 - No Label", font=font_nano, fill=(150, 150, 150))

    img.save(output_path)
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.toy.json")
    parser.add_argument("--out", default="research/ab-eval/out/specimens_v2")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    
    with open(args.corpus, 'r') as f:
        corpus = json.load(f)
        
    for font in corpus:
        name = font['name']
        print(f"Processing {name}...")
        files = font.get('files', {})
        url = files.get('400') or (next(iter(files.values())) if files else None)
        
        if not url:
            print(f"  No file URL for {name}")
            continue
            
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name
                
            safe_name = name.replace(' ', '_').replace('/', '_')
            output_path = os.path.join(args.out, f"{safe_name}.png")
            
            if render_specimen_v2(tmp_path, output_path):
                print(f"  Saved to {output_path}")
            
            os.remove(tmp_path)
        except Exception as e:
            print(f"  Failed to process {name}: {e}")

if __name__ == "__main__":
    main()
