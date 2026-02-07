import json
import os

def main():
    report_path = "research/ab-eval/out/report_all.json"
    corpus_path = "research/ab-eval/data/corpus.200.json"
    queries_path = "research/ab-eval/data/queries.complex.v1.json"
    output_path = "research/ab-eval/out/spot-check-complex-2026-02-07.html"

    with open(report_path, "r") as f:
        report = json.load(f)
    with open(corpus_path, "r") as f:
        corpus = json.load(f)
    with open(queries_path, "r") as f:
        queries = json.load(f)

    # Map font name to file URL
    font_map = {f["name"]: f["files"].get("400") for f in corpus if "files" in f}
    
    # Representative queries
    selected_query_ids = [
        "cq_001", "cq_002", # visual_shape
        "cq_011", "cq_012", # semantic_mood
        "cq_021", "cq_025", # historical_context
        "cq_031", "cq_033"  # functional_pair
    ]
    
    selected_queries = [q for q in queries if q["id"] in selected_query_ids]
    
    # Results for A, B2, D (RRF)
    variants = ["A", "B2", "D (RRF)"]
    results = {}
    for var in variants:
        if var in report["per_query_top10"]:
            results[var] = {qid: report["per_query_top10"][var][qid] for qid in selected_query_ids if qid in report["per_query_top10"][var]}

    # Prepare CORPUS subset for HTML (only needed fonts)
    needed_fonts = set()
    for var in variants:
        for qid in selected_query_ids:
            if qid in results.get(var, {}):
                for font_name, score in results[var][qid][:5]:
                    needed_fonts.add(font_name)
    
    corpus_json = []
    for name in needed_fonts:
        if name in font_map:
            corpus_json.append({"name": name, "files": {"400": font_map[name]}})

    html_template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complex Spot-Check | AI Font Explorer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        :root {{
            --bg: #030712;
            --card: #0f172a;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.15);
            --border: #1e293b;
        }}
        body {{
            background-color: var(--bg);
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: -0.01em;
        }}
        .mono {{ font-family: 'IBM Plex Mono', monospace; }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: 48px 1fr 1fr 1fr;
            gap: 1px;
            background: var(--border);
        }}
        .grid-header {{
            background: #111827;
            padding: 0.75rem;
            font-size: 0.65rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #94a3b8;
        }}
        .grid-cell {{
            background: var(--bg);
            padding: 0.75rem;
            position: relative;
        }}
        .rank-cell {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 800;
            color: #475569;
            background: #090e1a;
        }}
        .font-card {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .font-preview {{
            background: white;
            color: black;
            height: 60px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            overflow: hidden;
            transition: transform 0.2s cubic-bezier(0.2, 0, 0, 1);
        }}
        .font-preview:hover {{
            transform: scale(1.02);
            z-index: 10;
        }}
        .font-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.7rem;
        }}
        .score-badge {{
            background: var(--accent-glow);
            color: #818cf8;
            padding: 2px 6px;
            border-radius: 9999px;
            font-weight: 600;
        }}
        .query-header {{
            background: linear-gradient(to right, #1e1b4b, #030712);
            padding: 1rem 1.5rem;
            border-left: 4px solid var(--accent);
            margin-top: 3rem;
            margin-bottom: 0;
        }}
        #dynamic-fonts {{ display: none; }}
    </style>
    <style id="dynamic-fonts"></style>
</head>
<body class="p-8 pb-24">
    <header class="max-w-7xl mx-auto mb-12">
        <div class="inline-block px-3 py-1 mb-4 text-[10px] font-bold tracking-widest uppercase border border-indigo-500/30 text-indigo-400 bg-indigo-500/5 rounded">
            Complex Evaluation Report: 2026-02-07
        </div>
        <h1 class="text-5xl font-extrabold mb-4 tracking-tight">
            Complex <span class="text-indigo-500">Spot-Check</span>
        </h1>
        <p class="text-slate-400 max-w-2xl text-lg leading-relaxed">
            Side-by-side comparison of <span class="text-white font-semibold">Variant A (Text)</span>, 
            <span class="text-white font-semibold">Variant B2 (Vision)</span>, and 
            <span class="text-white font-semibold">Variant D (RRF Hybrid)</span>.
        </p>
    </header>

    <div id="main-content" class="max-w-7xl mx-auto space-y-12"></div>

    <footer class="mt-20 py-12 border-t border-slate-800 max-w-7xl mx-auto text-center">
        <p class="text-slate-500 text-sm mono italic uppercase tracking-tighter">Generated for site_font-ai complex benchmark validation</p>
    </footer>

    <script>
        const CORPUS = {corpus_json};
        const QUERIES = {queries_json};
        const RESULTS = {results_json};

        function init() {{
            const styleTag = document.getElementById('dynamic-fonts');
            CORPUS.forEach(font => {{
                if (font.files && font.files['400']) {{
                    const fontFace = `@font-face {{
                        font-family: '${{font.name}}';
                        src: url('${{font.files['400']}}') format('truetype');
                    }}`;
                    styleTag.appendChild(document.createTextNode(fontFace));
                }}
            }});

            const container = document.getElementById('main-content');
            
            QUERIES.forEach(query => {{
                const section = document.createElement('section');
                section.innerHTML = `
                    <div class="query-header">
                        <div class="flex justify-between items-center">
                            <div>
                                <span class="text-[10px] font-bold uppercase tracking-widest text-indigo-400 mb-1 block">${{query.class}}</span>
                                <h3 class="text-xl font-bold italic">"${{query.text}}"</h3>
                            </div>
                            <span class="mono text-xs text-slate-500">${{query.id}}</span>
                        </div>
                    </div>
                    <div class="comparison-grid">
                        <div class="grid-header">#</div>
                        <div class="grid-header">Variant A (Text)</div>
                        <div class="grid-header">Variant B2 (Vision)</div>
                        <div class="grid-header">Variant D (RRF Hybrid)</div>
                        ${{[1,2,3,4,5].map(rank => `
                            <div class="grid-cell rank-cell">${{rank}}</div>
                            ${{['A', 'B2', 'D (RRF)'].map(varName => {{
                                const res = RESULTS[varName] && RESULTS[varName][query.id] ? RESULTS[varName][query.id][rank-1] : null;
                                if (!res) return '<div class="grid-cell"></div>';
                                const [name, score] = res;
                                return `
                                    <div class="grid-cell">
                                        <div class="font-card">
                                            <div class="font-preview" style="font-family: '${{name}}', sans-serif">
                                                Abg
                                            </div>
                                            <div class="font-meta">
                                                <span class="font-bold truncate pr-2">${{name}}</span>
                                                <span class="score-badge mono">${{score.toFixed(3)}}</span>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            }}).join('')}}
                        `).join('')}}
                    </div>
                `;
                container.appendChild(section);
            }});
        }}
        init();
    </script>
</body>
</html>
"""
    
    with open(output_path, "w") as f:
        f.write(html_template.format(
            corpus_json=json.dumps(corpus_json),
            queries_json=json.dumps(selected_queries),
            results_json=json.dumps(results)
        ))
    
    print(f"Generated {output_path}")

if __name__ == "__main__":
    main()
