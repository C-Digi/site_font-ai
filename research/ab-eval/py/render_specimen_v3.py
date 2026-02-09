import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import tempfile
import argparse

def render_specimen_v3(font_path, output_dir, font_name):
    """Renders split specimen v3 for a font."""
    WIDTH, HEIGHT = 1024, 1024
    
    try:
        # Load font at different sizes
        font_display = ImageFont.truetype(font_path, 200) # Larger
        font_large = ImageFont.truetype(font_path, 72)
        font_medium = ImageFont.truetype(font_path, 48)
        font_small = ImageFont.truetype(font_path, 24)
        font_micro = ImageFont.truetype(font_path, 12)
        font_nano = ImageFont.truetype(font_path, 8)
    except Exception as e:
        print(f"  Error loading font {font_path}: {e}")
        return False

    # --- IMAGE 1: MACRO & CHARACTER SET ---
    img1 = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw1 = ImageDraw.Draw(img1)
    
    y_offset = 60
    margin = 50

    # 1. Display Section
    draw1.text((margin, y_offset), "Abg", font=font_display, fill=(0, 0, 0))
    y_offset += 240

    # 2. Character Set Section (Upper/Lower)
    chars_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars_lower = "abcdefghijklmnopqrstuvwxyz"
    
    draw1.text((margin, y_offset), chars_upper, font=font_large, fill=(0, 0, 0))
    y_offset += 100
    draw1.text((margin, y_offset), chars_lower, font=font_large, fill=(0, 0, 0))
    y_offset += 120

    # 3. Numbers and core Symbols
    chars_num_sym = "0123456789 !@#$%^&*()_+"
    draw1.text((margin, y_offset), chars_num_sym, font=font_large, fill=(0, 0, 0))
    
    img1.save(os.path.join(output_dir, f"{font_name}_top.png"))

    # --- IMAGE 2: MICRO-TELLS & TEXTURE ---
    img2 = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw2 = ImageDraw.Draw(img2)
    
    y_offset = 60

    # 1. Micro-tell Strips (Large)
    pairs = "il1I  O0  rn/m  vv/w  e/o"
    draw2.text((margin, y_offset), "Legibility Pairs (Zoomed):", font=font_small, fill=(100, 100, 100))
    y_offset += 40
    draw2.text((margin, y_offset), pairs, font=font_large, fill=(0, 0, 0))
    y_offset += 120

    # 2. Strategic "Tells" (The characters that define style)
    tells = "a g y Q & f t G S R k 1 2 3"
    draw2.text((margin, y_offset), "Style Identifiers:", font=font_small, fill=(100, 100, 100))
    y_offset += 40
    draw2.text((margin, y_offset), tells, font=font_large, fill=(0, 0, 0))
    y_offset += 120

    # 3. Paragraphs at different sizes
    pangram = "The quick brown fox jumps over the lazy dog."
    draw2.text((margin, y_offset), f"Body 24pt: {pangram}", font=font_small, fill=(0, 0, 0))
    y_offset += 60
    draw2.text((margin, y_offset), f"Body 12pt: {pangram}", font=font_micro, fill=(0, 0, 0))
    y_offset += 40
    draw2.text((margin, y_offset), f"Body 8pt: {pangram}", font=font_nano, fill=(0, 0, 0))
    y_offset += 80

    # 4. Contrast / Detail Strip
    strip_text = "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
    draw2.text((margin, y_offset), "Contrast & Rhythm Strip:", font=font_small, fill=(100, 100, 100))
    y_offset += 40
    draw2.text((margin, y_offset), strip_text, font=font_medium, fill=(0, 0, 0))
    
    img2.save(os.path.join(output_dir, f"{font_name}_bottom.png"))
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.toy.json")
    parser.add_argument("--out", default="research/ab-eval/out/specimens_v3")
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
            continue
            
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name
            
            safe_name = name.replace(" ", "_")
            render_specimen_v3(tmp_path, args.out, safe_name)
            os.remove(tmp_path)
        except Exception as e:
            print(f"  Failed {name}: {e}")

if __name__ == "__main__":
    main()
