import json
import os
import random
from pathlib import Path

def gen_human_review_html():
    corpus_path = Path("research/ab-eval/data/corpus.200.json")
    descriptions_path = Path("research/ab-eval/out/descriptions_bakeoff_qwen32_235_full200.jsonl")
    output_path = Path("research/ab-eval/human_review_v1.html")
    
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
    fonts_data = {}
    for row in descriptions:
        name = row["font_name"]
        model = row["model"]
        if name not in fonts_data:
            fonts_data[name] = {"name": name, "models": {}}
        
        parsed = row.get("metadata", {}).get("parsed_json", {})
        fonts_data[name]["models"][model] = {
            "description": row["description"],
            "parsed": parsed,
            "latency": row["metadata"].get("elapsed_sec")
        }

    # Stratified Sampling (aim for ~40-50 fonts total)
    # Categories: serif, sans-serif, display, handwriting, monospace
    by_cat = {}
    for f in corpus:
        cat = f.get("category", "unknown")
        if cat not in by_cat: by_cat[cat] = []
        by_cat[cat].append(f)
    
    sample_corpus = []
    # Take 10 from each main category if available
    for cat in by_cat:
        random.seed(42) # Deterministic sample
        pop = [f for f in by_cat[cat] if f["name"] in fonts_data]
        sample_corpus.extend(random.sample(pop, min(len(pop), 10)))

    # Sort sample by category then name
    sample_corpus.sort(key=lambda x: (x.get("category", ""), x["name"]))

    corpus_map = {f["name"]: f for f in sample_corpus}
    
    final_data = []
    for f in sample_corpus:
        name = f["name"]
        data = fonts_data[name]
        data["files"] = f.get("files", {})
        data["category"] = f.get("category", "unknown")
        final_data.append(data)

    html_template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Human Review Tool | AI Font Explorer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        :root {
            --bg: #020617;
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
            border-radius: 1.25rem;
            overflow: hidden;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }
        .font-preview {
            background: white;
            color: black;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            border-radius: 0.75rem;
            box-shadow: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
        }
        .glyph-img {
            max-height: 140px;
            object-fit: contain;
            border-radius: 0.75rem;
            border: 1px solid #334155;
            background: #fff;
        }
        .tab-btn {
            padding: 0.5rem 1rem;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid transparent;
            color: #64748b;
            transition: all 0.2s;
        }
        .tab-btn.active {
            color: var(--accent);
            border-bottom-color: var(--accent);
            background: rgba(99, 102, 241, 0.05);
        }
        .score-btn {
            padding: 0.5rem 1.25rem;
            border-radius: 0.75rem;
            font-weight: 800;
            font-size: 0.875rem;
            border: 2px solid transparent;
            transition: all 0.2s;
            background: #1e293b;
            color: #94a3b8;
        }
        .score-btn:hover { background: #334155; color: #f8fafc; }
        .score-btn.active[data-score="0"] { border-color: #ef4444; background: #ef4444; color: white; }
        .score-btn.active[data-score="1"] { border-color: #f59e0b; background: #f59e0b; color: white; }
        .score-btn.active[data-score="2"] { border-color: #10b981; background: #10b981; color: white; }
        
        .attribute-label {
            font-size: 0.65rem;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #475569;
            margin-bottom: 0.25rem;
        }
        .attribute-value {
            font-size: 0.9375rem;
            line-height: 1.4;
            color: #cbd5e1;
        }
        .summary-box {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            padding: 1.25rem;
        }
    </style>
    <style id="dynamic-fonts"></style>
</head>
<body class="p-8 pb-32">
    <header class="max-w-6xl mx-auto mb-12 flex justify-between items-center">
        <div>
            <div class="flex items-center gap-3 mb-4">
                <div class="px-2 py-1 bg-indigo-500 text-white text-[10px] font-black uppercase rounded">Bakeoff v1</div>
                <div class="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Stratified Sample (46 fonts)</div>
            </div>
            <h1 class="text-5xl font-extrabold tracking-tight">Human <span class="text-indigo-500">Spot-Check</span></h1>
        </div>
        <button onclick="exportResults()" class="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-2xl font-black transition-all shadow-xl flex items-center gap-3 uppercase text-xs tracking-widest">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
            Export Results
        </button>
    </header>

    <div id="review-list" class="max-w-6xl mx-auto"></div>

    <script>
        const FONT_DATA = REPLACE_FONT_DATA;
        const reviews = JSON.parse(localStorage.getItem('font-reviews-v2') || '{}');
        const activeTabs = {}; // font_name -> model_id

        function render() {
            const container = document.getElementById('review-list');
            container.innerHTML = '';

            FONT_DATA.forEach((font, idx) => {
                const models = Object.keys(font.models);
                if (!activeTabs[font.name]) activeTabs[font.name] = models[0];
                const activeModel = activeTabs[font.name];
                const modelData = font.models[activeModel] || { parsed: {} };
                const p = modelData.parsed || {};
                
                const fontReview = reviews[font.name] || {};
                const modelReview = fontReview[activeModel] || { score: null, notes: '' };

                const card = document.createElement('div');
                card.className = 'review-card';
                card.innerHTML = `
                    <!-- Header -->
                    <div class="px-8 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
                        <div class="flex items-center gap-4">
                            <span class="text-xs font-black text-slate-600 mono">#${String(idx + 1).padStart(2, '0')}</span>
                            <h2 class="text-2xl font-black text-white">${font.name}</h2>
                            <span class="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-bold text-slate-400 uppercase tracking-widest">${font.category}</span>
                        </div>
                        <div class="flex bg-slate-950 rounded-lg p-1 border border-slate-800">
                            ${models.map(m => `
                                <button onclick="setTab('${font.name}', '${m}')" class="tab-btn px-4 py-1.5 rounded-md text-[10px] ${activeModel === m ? 'active bg-slate-900 text-indigo-400 shadow-sm' : ''}">
                                    ${m.includes('235b') ? '235B (Winner)' : '32B (Challenger)'}
                                </button>
                            `).join('')}
                        </div>
                    </div>

                    <div class="p-8 grid grid-cols-12 gap-10">
                        <!-- Left: Visuals & Rating -->
                        <div class="col-span-4 space-y-6">
                            <div class="space-y-2">
                                <label class="attribute-label block">Live Render</label>
                                <div class="font-preview" style="font-family: '${font.name}'">Sphynx 123</div>
                            </div>
                            
                            <div class="space-y-2">
                                <label class="attribute-label block">Ground Truth (Glyphs)</label>
                                <img src="out/glyphs/${font.name.replace(/ /g, '_')}.png" class="glyph-img w-full" alt="Glyphs">
                            </div>

                            <div class="bg-indigo-500/5 rounded-2xl p-6 border border-indigo-500/10 space-y-6">
                                <div class="space-y-3">
                                    <label class="attribute-label block text-indigo-400">Score for this model</label>
                                    <div class="flex gap-2">
                                        <button class="score-btn flex-1 ${modelReview.score === 0 ? 'active' : ''}" data-score="0" onclick="setScore('${font.name}', '${activeModel}', 0)">0</button>
                                        <button class="score-btn flex-1 ${modelReview.score === 1 ? 'active' : ''}" data-score="1" onclick="setScore('${font.name}', '${activeModel}', 1)">1</button>
                                        <button class="score-btn flex-1 ${modelReview.score === 2 ? 'active' : ''}" data-score="2" onclick="setScore('${font.name}', '${activeModel}', 2)">2</button>
                                    </div>
                                </div>
                                <div class="space-y-3">
                                    <label class="attribute-label block text-indigo-400">Notes</label>
                                    <textarea 
                                        class="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm focus:outline-none focus:border-indigo-500 transition-all" 
                                        rows="3"
                                        placeholder="Specific feedback for ${activeModel.includes('235b') ? '235B' : '32B'}..."
                                        oninput="setNotes('${font.name}', '${activeModel}', this.value)"
                                    >${modelReview.notes}</textarea>
                                </div>
                            </div>
                        </div>

                        <!-- Right: Descriptions -->
                        <div class="col-span-8 space-y-8">
                            <div class="grid grid-cols-2 gap-x-8 gap-y-6">
                                <div><label class="attribute-label">Geometry & Shape</label><p class="attribute-value">${p.shape || '-'}</p></div>
                                <div><label class="attribute-label">Stroke Contrast</label><p class="attribute-value">${p.contrast || '-'}</p></div>
                                <div><label class="attribute-label">Terminal Style</label><p class="attribute-value">${p.terminals || '-'}</p></div>
                                <div><label class="attribute-label">X-Height Impression</label><p class="attribute-value">${p.x_height || '-'}</p></div>
                                <div><label class="attribute-label">Relative Width</label><p class="attribute-value">${p.width || '-'}</p></div>
                                <div>
                                    <label class="attribute-label">Suggested Moods</label>
                                    <div class="flex flex-wrap gap-2 mt-1">
                                        ${(p.mood || []).map(m => `<span class="bg-indigo-500/10 text-indigo-300 px-2 py-1 rounded text-[10px] font-bold border border-indigo-500/20">${m}</span>`).join('')}
                                    </div>
                                </div>
                                <div class="col-span-2">
                                    <label class="attribute-label">Recommended Use Cases</label>
                                    <div class="flex flex-wrap gap-2 mt-1">
                                        ${(p.use_cases || []).map(u => `<span class="bg-emerald-500/10 text-emerald-300 px-2 py-1 rounded text-[10px] font-bold border border-emerald-500/20">${u}</span>`).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <div class="summary-box">
                                <label class="attribute-label block mb-2">Integrated Summary</label>
                                <p class="text-xl text-white font-medium leading-relaxed italic pr-4 border-l-4 border-indigo-500/30 pl-4">"${p.summary || '-'}"</p>
                            </div>

                            <div class="flex justify-between items-center text-[10px] font-bold text-slate-500 mono bg-slate-900/30 px-4 py-2 rounded-lg border border-slate-800/50">
                                <span>INFERENCE LATENCY: ${modelData.latency || 'N/A'} SEC</span>
                                <span class="uppercase">Bakeoff Artifact: qwen32_235_full200.jsonl</span>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        function setTab(name, model) {
            activeTabs[name] = model;
            render();
        }

        function setScore(name, model, score) {
            if (!reviews[name]) reviews[name] = {};
            if (!reviews[name][model]) reviews[name][model] = { score: null, notes: '' };
            reviews[name][model].score = score;
            localStorage.setItem('font-reviews-v2', JSON.stringify(reviews));
            render();
        }

        function setNotes(name, model, notes) {
            if (!reviews[name]) reviews[name] = {};
            if (!reviews[name][model]) reviews[name][model] = { score: null, notes: '' };
            reviews[name][model].notes = notes;
            localStorage.setItem('font-reviews-v2', JSON.stringify(reviews));
        }

        function exportResults() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reviews, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "bakeoff_human_review_results.json");
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
    
    print(f"Generated {output_path} with {len(final_data)} fonts.")

if __name__ == "__main__":
    gen_human_review_html()
