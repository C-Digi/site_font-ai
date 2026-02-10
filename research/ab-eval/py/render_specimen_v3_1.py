import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import tempfile
import argparse

def draw_section(draw, text, font, x, y, max_width, fill=(0, 0, 0), section_spacing=30, line_spacing=10):
    """Draws text with robust wrapping and dynamic vertical spacing."""
    if not text:
        return y
        
    lines = []
    words = text.split(' ')
    current_line_parts = []
    
    for word in words:
        test_line = ' '.join(current_line_parts + [word]) if current_line_parts else word
        if draw.textlength(test_line, font=font) <= max_width:
            current_line_parts.append(word)
        else:
            if current_line_parts:
                lines.append(' '.join(current_line_parts))
                current_line_parts = [word]
                if draw.textlength(word, font=font) > max_width:
                    word_line = current_line_parts.pop()
                    temp = ""
                    for char in word_line:
                        if draw.textlength(temp + char, font=font) <= max_width:
                            temp += char
                        else:
                            lines.append(temp)
                            temp = char
                    if temp:
                        current_line_parts = [temp]
            else:
                temp = ""
                for char in word:
                    if draw.textlength(temp + char, font=font) <= max_width:
                        temp += char
                    else:
                        lines.append(temp)
                        temp = char
                if temp:
                    current_line_parts = [temp]
                    
    if current_line_parts:
        lines.append(' '.join(current_line_parts))

    curr_y = y
    for line in lines:
        bbox = draw.textbbox((x, curr_y), line, font=font, anchor="lt")
        draw.text((x, curr_y), line, font=font, fill=fill, anchor="lt")
        curr_y = bbox[3] + line_spacing
        
    return curr_y + section_spacing

def finalize_and_save(tall_img, current_y, output_path, target_size=(1024, 1024), margin=40):
    """Crops the tall image to content, scales to fit target_size, and saves."""
    # Crop to content (0, 0, 1024, current_y)
    content_img = tall_img.crop((0, 0, 1024, min(current_y, tall_img.height)))
    
    # Get bounding box of non-white areas to be even more precise
    gray = content_img.convert('L')
    from PIL import ImageOps
    inverted = ImageOps.invert(gray)
    bbox = inverted.getbbox()
    
    if not bbox:
        final_img = Image.new('RGB', target_size, color=(255, 255, 255))
        final_img.save(output_path)
        return

    # Add margin to bbox
    bbox = (
        max(0, bbox[0] - margin),
        max(0, bbox[1] - margin),
        min(1024, bbox[2] + margin),
        min(content_img.height, bbox[3] + margin)
    )
    
    cropped = content_img.crop(bbox)
    
    # Scale to fit target_size while maintaining aspect ratio
    w, h = cropped.size
    target_w, target_h = target_size
    
    scale = min(target_w / w, target_h / h)
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Center on final white canvas
    final_img = Image.new('RGB', target_size, color=(255, 255, 255))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    final_img.paste(resized, (paste_x, paste_y))
    
    final_img.save(output_path)

def render_specimen_v3_1(font_path, output_dir, font_name):
    """Renders split specimen v3.1 for a font with enhanced micro-distinction blocks."""
    WIDTH = 1024
    TALL_HEIGHT = 4096 
    
    try:
        # Load font at different sizes
        font_display = ImageFont.truetype(font_path, 200)
        font_large = ImageFont.truetype(font_path, 72)
        font_medium = ImageFont.truetype(font_path, 48)
        font_small = ImageFont.truetype(font_path, 24)
        font_micro = ImageFont.truetype(font_path, 12)
        font_nano = ImageFont.truetype(font_path, 8)
    except Exception as e:
        print(f"  Error loading font {font_path}: {e}")
        return False

    margin = 50
    max_w = WIDTH - (2 * margin)

    # --- IMAGE 1: MACRO & CHARACTER SET ---
    img1 = Image.new('RGB', (WIDTH, TALL_HEIGHT), color=(255, 255, 255))
    draw1 = ImageDraw.Draw(img1)
    
    y = 60
    y = draw_section(draw1, "Abg", font_display, margin, y, max_w)
    
    chars_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars_lower = "abcdefghijklmnopqrstuvwxyz"
    y = draw_section(draw1, chars_upper, font_large, margin, y, max_w)
    y = draw_section(draw1, chars_lower, font_large, margin, y, max_w)

    chars_num_sym = "0123456789 !@#$%^&*()_+"
    y = draw_section(draw1, chars_num_sym, font_large, margin, y, max_w)
    
    finalize_and_save(img1, y, os.path.join(output_dir, f"{font_name}_top.png"))

    # --- IMAGE 2: MICRO-TELLS & TEXTURE ---
    img2 = Image.new('RGB', (WIDTH, TALL_HEIGHT), color=(255, 255, 255))
    draw2 = ImageDraw.Draw(img2)
    
    y = 60
    
    # NEW V3.1: Dedicated Distinction Block (Macro-scale)
    distinction = "il1I0O"
    y = draw_section(draw2, "Critical Distinction (Macro):", font_small, margin, y, max_w, fill=(100, 100, 100), section_spacing=10)
    y = draw_section(draw2, distinction, font_display, margin, y, max_w)
    
    pairs = "rn/m  vv/w  e/o  S/s  C/c"
    y = draw_section(draw2, "Legibility Pairs (Zoomed):", font_small, margin, y, max_w, fill=(100, 100, 100), section_spacing=10)
    y = draw_section(draw2, pairs, font_large, margin, y, max_w)

    # Expanded Style Identifiers
    tells = "a g y Q & f t G S R k 1 2 3 M W"
    y = draw_section(draw2, "Style Identifiers:", font_small, margin, y, max_w, fill=(100, 100, 100), section_spacing=10)
    y = draw_section(draw2, tells, font_large, margin, y, max_w)

    pangram = "The quick brown fox jumps over the lazy dog."
    y = draw_section(draw2, f"Body 24pt: {pangram}", font_small, margin, y, max_w, section_spacing=15)
    y = draw_section(draw2, f"Body 12pt: {pangram}", font_micro, margin, y, max_w, section_spacing=10)
    y = draw_section(draw2, f"Body 8pt: {pangram}", font_nano, margin, y, max_w, section_spacing=30)

    strip_text = "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
    y = draw_section(draw2, "Contrast & Rhythm Strip:", font_small, margin, y, max_w, fill=(100, 100, 100), section_spacing=10)
    y = draw_section(draw2, strip_text, font_medium, margin, y, max_w)
    
    finalize_and_save(img2, y, os.path.join(output_dir, f"{font_name}_bottom.png"))
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="research/ab-eval/data/corpus.200.json")
    parser.add_argument("--out", default="research/ab-eval/out/specimens_v3_1")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    
    if not os.path.exists(args.corpus):
        print(f"Error: Corpus file not found: {args.corpus}")
        return

    with open(args.corpus, 'r') as f:
        corpus = json.load(f)
        
    for font in corpus:
        name = font['name']
        print(f"Processing {name}...")
        files = font.get('files', {})
        url = files.get('400') or (next(iter(files.values())) if files else None)
        
        if not url:
            print(f"  No URL for {name}")
            continue
            
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name
            
            safe_name = name.replace(" ", "_")
            render_specimen_v3_1(tmp_path, args.out, safe_name)
            os.remove(tmp_path)
        except Exception as e:
            print(f"  Failed {name}: {e}")

if __name__ == "__main__":
    main()
