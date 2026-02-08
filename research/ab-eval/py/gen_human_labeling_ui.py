import json
import os
from pathlib import Path

def gen_human_labeling_ui():
    corpus_path = Path("research/ab-eval/data/corpus.200.json")
    queries_path = Path("research/ab-eval/data/queries.medium.human.v1.json")
    pool_path = Path("research/ab-eval/data/candidate_pool.medium.v1.json")
    output_path = Path("research/ab-eval/human_labeling_medium_v1.html")
    
    if not all(p.exists() for p in [corpus_path, queries_path, pool_path]):
        print("Required files missing.")
        return

    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    corpus_map = {f["name"]: f for f in corpus}

    with open(queries_path, "r", encoding="utf-8") as f:
        queries = json.load(f)

    with open(pool_path, "r", encoding="utf-8") as f:
        pool = json.load(f)

    # Prepare data for the UI
    ui_data = {
        "queries": queries,
        "pool": pool,
        "fonts": {}
    }

    # Only include fonts that are in the pool
    all_pool_fonts = set()
    for q_pool in pool.values():
        all_pool_fonts.update(q_pool)
    
    for name in all_pool_fonts:
        if name in corpus_map:
            f = corpus_map[name]
            ui_data["fonts"][name] = {
                "name": name,
                "category": f.get("category", "unknown"),
                "files": f.get("files", {})
            }

    html_template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Human Labeling Tool (Medium v1) | AI Font Explorer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        :root {
            --bg: #020617;
            --card: #0f172a;
            --accent: #6366f1;
            --border: #1e293b;
        }
        body {
            background-color: var(--bg);
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: -0.01em;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .mono { font-family: 'IBM Plex Mono', monospace; }
        
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            padding: 1.5rem;
        }
        
        .font-card {
            background: var(--card);
            border: 2px solid var(--border);
            border-radius: 1rem;
            padding: 1rem;
            transition: all 0.2s;
            cursor: pointer;
            position: relative;
        }
        .font-card:hover { border-color: #334155; }
        .font-card.active { border-color: var(--accent); ring: 2px solid var(--accent); }
        
        .font-card.labeled-0 { border-color: #ef4444; opacity: 0.6; }
        .font-card.labeled-1 { border-color: #10b981; background: rgba(16, 185, 129, 0.05); }

        .glyph-preview {
            background: white;
            color: black;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            border-radius: 0.5rem;
            margin-bottom: 0.75rem;
            overflow: hidden;
        }

        .status-pill {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.65rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .sidebar {
            width: 320px;
            border-right: 1px solid var(--border);
            background: #020617;
            display: flex;
            flex-direction: column;
        }

        main {
            flex: 1;
            overflow-y: auto;
            background: #070b1d;
        }

        .key-hint {
            background: #1e293b;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            border-bottom: 2px solid #0f172a;
        }
    </style>
    <style id="dynamic-fonts"></style>
</head>
<body class="antialiased">
    <div class="flex flex-1 overflow-hidden">
        <!-- Sidebar -->
        <aside class="sidebar p-6 space-y-8">
            <div>
                <div class="flex items-center gap-2 mb-2">
                    <span class="px-2 py-0.5 bg-indigo-500 text-white text-[10px] font-black uppercase rounded">Medium v1</span>
                    <span class="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Binary Mode</span>
                </div>
                <h1 class="text-2xl font-black">Labeler</h1>
            </div>

            <div class="space-y-4">
                <label class="text-[10px] font-black uppercase text-slate-500 tracking-wider">Reviewer ID</label>
                <input id="reviewer-id" type="text" placeholder="Your Name" class="w-full bg-slate-900 border border-slate-800 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500">
            </div>

            <div class="space-y-4 flex-1">
                <label class="text-[10px] font-black uppercase text-slate-500 tracking-wider">Queries</label>
                <div id="query-list" class="space-y-2 overflow-y-auto max-h-[40vh] pr-2">
                    <!-- Queries injected here -->
                </div>
            </div>

            <div class="pt-6 border-t border-slate-800 space-y-4">
                <div class="flex justify-between items-center text-[10px] font-bold text-slate-500">
                    <span>PROGRESS</span>
                    <span id="global-progress">0/0</span>
                </div>
                <div class="w-full bg-slate-900 h-1 rounded-full overflow-hidden">
                    <div id="global-progress-bar" class="bg-indigo-500 h-full transition-all" style="width: 0%"></div>
                </div>
                
                <button onclick="exportJudgments()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-3 rounded-xl font-black transition-all shadow-lg flex items-center justify-center gap-2 uppercase text-xs tracking-widest">
                    Export JSON
                </button>
            </div>
            
            <div class="text-[10px] text-slate-500 space-y-2 mono uppercase">
                <p><span class="key-hint">D</span> / <span class="key-hint">F</span> Mark 0 / 1</p>
                <p><span class="key-hint">J</span> / <span class="key-hint">K</span> Next/Prev Font</p>
                <p><span class="key-hint">L</span> / <span class="key-hint">H</span> Next/Prev Query</p>
            </div>
        </aside>

        <!-- Main Content -->
        <main>
            <div id="query-header" class="sticky top-0 z-10 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 p-8">
                <div id="query-class" class="text-indigo-400 text-[10px] font-black uppercase tracking-[0.2em] mb-2">-</div>
                <h2 id="query-text" class="text-3xl font-extrabold tracking-tight mb-4">Select a query</h2>
                <div class="flex justify-between items-end">
                    <div class="text-slate-400 text-sm max-w-xl" id="query-hint">
                        Choose 1 if the font matches the description, 0 otherwise.
                    </div>
                    <div class="text-right">
                        <div class="text-[10px] font-bold text-slate-500 uppercase mb-1">Query Progress</div>
                        <div class="text-xl font-black text-white" id="query-progress">0 / 0</div>
                    </div>
                </div>
            </div>

            <div id="font-grid" class="card-grid">
                <!-- Fonts injected here -->
            </div>
        </main>
    </div>

    <script>
        const DATA = REPLACE_DATA;
        let currentQueryIdx = 0;
        let currentFontIdx = 0;
        
        // Load state from localStorage
        const STORAGE_KEY = 'human-judgments-v1';
        let judgments = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
        
        const reviewerInput = document.getElementById('reviewer-id');
        reviewerInput.value = localStorage.getItem('reviewer-id') || '';
        reviewerInput.onchange = (e) => localStorage.setItem('reviewer-id', e.target.value);

        function save() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(judgments));
            updateSidebar();
        }

        function updateSidebar() {
            const list = document.getElementById('query-list');
            list.innerHTML = '';
            
            let totalLabeled = 0;
            let totalPossible = 0;

            DATA.queries.forEach((q, idx) => {
                const qPool = DATA.pool[q.id] || [];
                const qJudgments = judgments[q.id] || {};
                const labeledCount = Object.keys(qJudgments).length;
                totalLabeled += labeledCount;
                totalPossible += qPool.length;

                const btn = document.createElement('button');
                btn.className = `w-full text-left p-3 rounded-lg text-xs transition-all flex justify-between items-center ${idx === currentQueryIdx ? 'bg-indigo-500/20 border border-indigo-500/50 text-indigo-100' : 'hover:bg-slate-900 text-slate-400'}`;
                btn.onclick = () => selectQuery(idx);
                
                const isComplete = labeledCount === qPool.length;
                btn.innerHTML = `
                    <span class="truncate pr-2">${q.text}</span>
                    <span class="mono text-[10px] ${isComplete ? 'text-emerald-500' : 'text-slate-600'}">${labeledCount}/${qPool.length}</span>
                `;
                list.appendChild(btn);
            });

            document.getElementById('global-progress').innerText = `${totalLabeled}/${totalPossible}`;
            document.getElementById('global-progress-bar').style.width = `${(totalLabeled / totalPossible) * 100}%`;
        }

        function selectQuery(idx) {
            currentQueryIdx = idx;
            currentFontIdx = 0;
            renderQuery();
            updateSidebar();
        }

        function renderQuery() {
            const query = DATA.queries[currentQueryIdx];
            if (!query) return;

            document.getElementById('query-text').innerText = query.text;
            document.getElementById('query-class').innerText = query.class.replace('_', ' ');
            
            const pool = DATA.pool[query.id] || [];
            const qJudgments = judgments[query.id] || {};
            
            document.getElementById('query-progress').innerText = `${Object.keys(qJudgments).length} / ${pool.length}`;

            const grid = document.getElementById('font-grid');
            grid.innerHTML = '';

            pool.forEach((fontName, idx) => {
                const font = DATA.fonts[fontName];
                const score = qJudgments[fontName];
                
                const card = document.createElement('div');
                card.id = `font-card-${idx}`;
                card.className = `font-card ${idx === currentFontIdx ? 'active' : ''} ${score !== undefined ? 'labeled-' + score : ''}`;
                card.onclick = () => { currentFontIdx = idx; renderQuery(); };
                
                card.innerHTML = `
                    ${score !== undefined ? `<div class="status-pill ${score === 1 ? 'bg-emerald-500' : 'bg-red-500'}">${score === 1 ? 'REL' : 'NOT'}</div>` : ''}
                    <div class="glyph-preview" style="font-family: '${fontName}'">
                        Sphinx 123
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-black uppercase text-slate-500 truncate mr-2">${fontName}</span>
                        <span class="text-[8px] font-bold text-slate-700 mono">${font.category}</span>
                    </div>
                `;
                grid.appendChild(card);
            });

            // Scroll into view
            const activeCard = document.getElementById(`font-card-${currentFontIdx}`);
            if (activeCard) activeCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        function markRelevance(score) {
            const query = DATA.queries[currentQueryIdx];
            const pool = DATA.pool[query.id] || [];
            const fontName = pool[currentFontIdx];
            
            if (!judgments[query.id]) judgments[query.id] = {};
            judgments[query.id][fontName] = score;
            
            save();
            
            // Auto-advance to next font
            if (currentFontIdx < pool.length - 1) {
                currentFontIdx++;
            }
            renderQuery();
        }

        function exportJudgments() {
            const reviewer = document.getElementById('reviewer-id').value || 'anonymous';
            const exportData = {
                reviewer_id: reviewer,
                timestamp: new Date().toISOString(),
                judgments: judgments
            };
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
            const downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", `judgments_medium_v1_${reviewer}.json`);
            document.body.appendChild(downloadAnchorNode);
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        }

        window.onkeydown = (e) => {
            if (document.activeElement.tagName === 'INPUT') return;

            const key = e.key.toLowerCase();

            if (key === '0' || key === 'd') markRelevance(0);
            if (key === '1' || key === 'f') markRelevance(1);
            
            if (key === 'j') {
                const query = DATA.queries[currentQueryIdx];
                const pool = DATA.pool[query.id] || [];
                if (currentFontIdx < pool.length - 1) {
                    currentFontIdx++;
                    renderQuery();
                }
            }
            if (key === 'k') {
                if (currentFontIdx > 0) {
                    currentFontIdx--;
                    renderQuery();
                }
            }
            if (key === 'n' || key === 'l') {
                if (currentQueryIdx < DATA.queries.length - 1) {
                    selectQuery(currentQueryIdx + 1);
                }
            }
            if (key === 'p' || key === 'h') {
                if (currentQueryIdx > 0) {
                    selectQuery(currentQueryIdx - 1);
                }
            }
        };

        function init() {
            const styleTag = document.getElementById('dynamic-fonts');
            Object.values(DATA.fonts).forEach(font => {
                if (font.files && font.files['400']) {
                    const fontFace = `@font-face {
                        font-family: '${font.name}';
                        src: url('${font.files['400']}') format('truetype');
                        font-display: swap;
                    }`;
                    styleTag.appendChild(document.createTextNode(fontFace));
                }
            });
            selectQuery(0);
        }
        init();
    </script>
</body>
</html>"""
    
    html_content = html_template.replace("REPLACE_DATA", json.dumps(ui_data))
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Generated {output_path} with {len(queries)} queries and {len(all_pool_fonts)} font candidates.")

if __name__ == "__main__":
    gen_human_labeling_ui()
