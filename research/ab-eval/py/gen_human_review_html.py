import json
import os
from pathlib import Path

def gen_human_review_html():
    corpus_path = Path("research/ab-eval/data/corpus.200.json")
    descriptions_path = Path("research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl")
    output_path = Path("research/ab-eval/human_review_v1.html")
    glyph_dir = "out/glyphs" # Relative to research/ab-eval/

    if not corpus_path.exists() or not descriptions_path.exists():
        print("Required files missing.")
        return

    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    descriptions = []
    with open(descriptions_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                descriptions.append(json.loads(line))

    # Group descriptions by font name
    # We only care about the models we want to review.
    # The winner is 235B, challenger is 32B.
    fonts_data = {}
    for row in descriptions:
        name = row["font_name"]
        model = row["model"]
        if name not in fonts_data:
            fonts_data[name] = {"name": name, "models": {}}
        
        # Extract the structured data if it exists
        parsed = row.get("metadata", {}).get("parsed_json", {})
        fonts_data[name]["models"][model] = {
            "description": row["description"],
            "parsed": parsed,
            "latency": row["metadata"].get("elapsed_sec")
        }

    # Merge with corpus for file URLs
    corpus_map = {f["name"]: f for f in corpus}
    
    final_data = []
    for name, data in fonts_data.items():
        c_info = corpus_map.get(name, {})
        data["files"] = c_info.get("files", {})
        final_data.append(data)

    html_template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Human Review: Font Descriptions | AI Font Explorer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        :root {
            --bg: #030712;
            --card: #0f172a;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.15);
            --border: #1e293b;
        }
        body {
            background-color: var(--bg);
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: -0.01em;
        }
        .mono { font-family: 'IBM Plex Mono', monospace; }
        .review-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 1rem;
            overflow: hidden;
            margin-bottom: 2rem;
            transition: all 0.2s ease;
        }
        .review-card:focus-within {
            border-color: var(--accent);
            box-shadow: 0 0 20px var(--accent-glow);
        }
        .font-preview {
            background: white;
            color: black;
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            border-radius: 0.5rem;
        }
        .glyph-img {
            max-height: 200px;
            border-radius: 0.5rem;
            border: 1px solid #334155;
        }
        .score-btn {
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-weight: bold;
            border: 2px solid transparent;
            transition: all 0.2s;
            background: #1e293b;
        }
        .score-btn:hover { background: #334155; }
        .score-btn.active[data-score="0"] { border-color: #ef4444; background: #991b1b; color: white; }
        .score-btn.active[data-score="1"] { border-color: #f59e0b; background: #92400e; color: white; }
        .score-btn.active[data-score="2"] { border-color: #10b981; background: #065f46; color: white; }
    </style>
    <style id="dynamic-fonts"></style>
</head>
<body class="p-8 pb-24">
    <header class="max-w-7xl mx-auto mb-12 flex justify-between items-end">
        <div>
            <div class="inline-block px-3 py-1 mb-4 text-[10px] font-bold tracking-widest uppercase border border-indigo-500/30 text-indigo-400 bg-indigo-500/5 rounded">
                Production Candidate Review: 2026-02-08
            </div>
            <h1 class="text-5xl font-extrabold mb-4 tracking-tight">
                Human <span class="text-indigo-500">Review</span> Packet
            </h1>
            <p class="text-slate-400 max-w-2xl text-lg leading-relaxed">
                Reviewing descriptions from <span class="text-white font-semibold">Qwen3-VL-235B</span> and <span class="text-white font-semibold">Qwen3-VL-32B</span>.
            </p>
        </div>
        <div class="flex gap-4">
            <button onclick="exportResults()" class="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                Export Review Data
            </button>
        </div>
    </header>

    <div id="review-list" class="max-w-7xl mx-auto space-y-8"></div>

    <script>
        const FONT_DATA = REPLACE_FONT_DATA;
        const reviews = JSON.parse(localStorage.getItem('font-reviews') || '{}');

        function render() {
            const container = document.getElementById('review-list');
            container.innerHTML = '';

            FONT_DATA.forEach((font, idx) => {
                const card = document.createElement('div');
                card.className = 'review-card p-6';
                
                const model235 = font.models['qwen/qwen3-vl-235b-a22b-instruct'] || {};
                const p = model235.parsed || {};
                
                const review = reviews[font.name] || { score: null, notes: '' };

                card.innerHTML = `
                    <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
                        <!-- Left Col: Identity & Image -->
                        <div class="md:col-span-4 space-y-4">
                            <div class="flex justify-between items-center">
                                <h2 class="text-2xl font-bold truncate">${font.name}</h2>
                                <span class="text-slate-500 text-xs mono">#${idx + 1}</span>
                            </div>
                            
                            <div class="font-preview" style="font-family: '${font.name}'">
                                Sphynx
                            </div>
                            
                            <img src="out/glyphs/${font.name.replace(/ /g, '_')}.png" class="glyph-img w-full" alt="Glyph sheet">
                            
                            <div class="bg-slate-900 rounded-lg p-4 space-y-4">
                                <h3 class="text-xs font-bold uppercase tracking-widest text-slate-500">Your Review</h3>
                                <div class="flex gap-2">
                                    <button class="score-btn flex-1 ${review.score === 0 ? 'active' : ''}" data-score="0" onclick="setScore('${font.name}', 0)">0</button>
                                    <button class="score-btn flex-1 ${review.score === 1 ? 'active' : ''}" data-score="1" onclick="setScore('${font.name}', 1)">1</button>
                                    <button class="score-btn flex-1 ${review.score === 2 ? 'active' : ''}" data-score="2" onclick="setScore('${font.name}', 2)">2</button>
                                </div>
                                <textarea 
                                    class="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:outline-none focus:border-indigo-500" 
                                    placeholder="Add notes..."
                                    oninput="setNotes('${font.name}', this.value)"
                                >${review.notes}</textarea>
                            </div>
                        </div>

                        <!-- Right Col: AI Content -->
                        <div class="md:col-span-8 space-y-6">
                            <div class="grid grid-cols-2 gap-4">
                                <div><label class="block text-[10px] uppercase font-bold text-slate-500 mb-1">Shape</label><p class="text-sm">${p.shape || 'N/A'}</p></div>
                                <div><label class="block text-[10px] uppercase font-bold text-slate-500 mb-1">Contrast</label><p class="text-sm">${p.contrast || 'N/A'}</p></div>
                                <div><label class="block text-[10px] uppercase font-bold text-slate-500 mb-1">Terminals</label><p class="text-sm">${p.terminals || 'N/A'}</p></div>
                                <div><label class="block text-[10px] uppercase font-bold text-slate-500 mb-1">X-Height</label><p class="text-sm">${p.x_height || 'N/A'}</p></div>
                                <div><label class="block text-[10px] uppercase font-bold text-slate-500 mb-1">Width</label><p class="text-sm">${p.width || 'N/A'}</p></div>
                                <div><label class="block text-[10px] uppercase font-bold text-slate-500 mb-1">Moods</label><div class="flex flex-wrap gap-1">${(p.mood || []).map(m => `<span class="bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded text-[10px] font-bold">${m}</span>`).join('')}</div></div>
                            </div>
                            
                            <div class="border-t border-slate-800 pt-4">
                                <label class="block text-[10px] uppercase font-bold text-slate-500 mb-2 tracking-widest">Integrated Summary</label>
                                <p class="text-lg text-slate-200 italic leading-relaxed font-serif">"${p.summary || 'N/A'}"</p>
                            </div>

                            <div class="bg-indigo-500/5 rounded-lg p-4 flex justify-between items-center border border-indigo-500/10">
                                <span class="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Model: Qwen3-VL-235B</span>
                                <span class="text-[10px] mono text-slate-500">Latency: ${model235.latency || 'N/A'}s</span>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        function setScore(name, score) {
            if (!reviews[name]) reviews[name] = { score: null, notes: '' };
            reviews[name].score = score;
            localStorage.setItem('font-reviews', JSON.stringify(reviews));
            render();
        }

        function setNotes(name, notes) {
            if (!reviews[name]) reviews[name] = { score: null, notes: '' };
            reviews[name].notes = notes;
            localStorage.setItem('font-reviews', JSON.stringify(reviews));
        }

        function exportResults() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reviews, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "font_description_reviews.json");
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        }

        function init() {
            const styleTag = document.getElementById('dynamic-fonts');
            FONT_DATA.forEach(font => {
                if (font.files && font.files['400']) {
                    const fontFace = `@font-face {
                        font-family: '${font.name}';
                        src: url('${font.files['400']}') format('truetype');
                    }`;
                    styleTag.appendChild(document.createTextNode(fontFace));
                }
            });
            render();
        }
        init();
    </script>
</body>
</html>"""
    
    html_content = html_template.replace("REPLACE_FONT_DATA", json.dumps(final_data))
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Generated {output_path}")

if __name__ == "__main__":
    gen_human_review_html()
