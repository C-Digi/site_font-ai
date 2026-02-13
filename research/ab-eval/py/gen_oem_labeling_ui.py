import json
import os
from pathlib import Path

def gen_oem_labeling_ui():
    manifest_path = Path("research/ab-eval/out/week4_p2_labeling_manifest.json")
    output_path = Path("research/ab-eval/out/week4_p2_adjudication.html")
    
    if not manifest_path.exists():
        print(f"Manifest missing at {manifest_path}")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    pairs = manifest.get("pairs", [])

    html_template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OEM Adjudication (Week 4 P2) | AI Font Explorer</title>
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
        }
        .mono { font-family: 'IBM Plex Mono', monospace; }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid var(--border); padding: 1rem; text-align: left; vertical-align: top; }
        th { background: #1e293b; position: sticky; top: 0; z-index: 10; }
        tr:nth-child(even) { background: rgba(255, 255, 255, 0.02); }
        .match-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        .match-1 { background: #065f46; color: #a7f3d0; }
        .match-0 { background: #7f1d1d; color: #fecaca; }
        .diff { background: rgba(234, 179, 8, 0.1); border-left: 4px solid #eab308; }
        .id-cell { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #94a3b8; }
    </style>
</head>
<body class="p-8">
    <header class="mb-8">
        <h1 class="text-3xl font-extrabold mb-2">OEM Adjudication Package</h1>
        <p class="text-slate-400">Week 4 Phase 2: Systematic alignment review for 100 OEM pairs.</p>
        <div class="mt-4 flex gap-4 text-sm">
            <span class="flex items-center gap-2"><div class="w-3 h-3 bg-yellow-500 rounded-sm"></div> AI Disagreement</span>
        </div>
    </header>

    <div class="table-container bg-slate-900/50 rounded-xl border border-slate-800">
        <table>
            <thead>
                <tr>
                    <th class="w-16">ID</th>
                    <th class="w-1/4">Query / Font</th>
                    <th class="w-1/3">Variant V3 (Baseline)</th>
                    <th class="w-1/3">Variant V5.1 (Treatment)</th>
                </tr>
            </thead>
            <tbody id="pairs-body">
                {rows}
            </tbody>
        </table>
    </div>

    <footer class="mt-12 text-slate-500 text-sm border-t border-slate-800 pt-8 pb-12">
        <p>Generated for deterministic gating path. Adjudicate labels in <code class="bg-slate-800 px-1 rounded">labels.medium.human.v1.json</code>.</p>
    </footer>
</body>
</html>
"""

    rows = []
    for i, pair in enumerate(pairs):
        is_diff = pair["v3_match"] != pair["v5_1_match"]
        diff_class = "diff" if is_diff else ""
        
        v3_match_badge = f'<span class="match-badge match-{pair["v3_match"]}">{ "MATCH" if pair["v3_match"] == 1 else "NO MATCH" }</span>'
        v5_1_match_badge = f'<span class="match-badge match-{pair["v5_1_match"]}">{ "MATCH" if pair["v5_1_match"] == 1 else "NO MATCH" }</span>'

        row = f"""
                <tr class="{diff_class}">
                    <td class="id-cell">{i+1}</td>
                    <td>
                        <div class="text-xs text-slate-500 mono mb-1">{pair["query_id"]}</div>
                        <div class="font-bold text-lg mb-2">{pair["query_text"]}</div>
                        <div class="text-accent font-semibold">{pair["font_name"]}</div>
                    </td>
                    <td>
                        <div class="mb-2">{v3_match_badge}</div>
                        <div class="text-sm text-slate-300 leading-relaxed italic border-l-2 border-slate-700 pl-3">
                            "{pair["v3_evidence"]}"
                        </div>
                    </td>
                    <td>
                        <div class="mb-2">{v5_1_match_badge}</div>
                        <div class="text-sm text-slate-300 leading-relaxed italic border-l-2 border-slate-700 pl-3">
                            "{pair["v5_1_evidence"]}"
                        </div>
                    </td>
                </tr>"""
        rows.append(row)

    final_html = html_template.replace("{rows}", "\n".join(rows))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"Generated adjudication UI at {output_path}")

if __name__ == "__main__":
    gen_oem_labeling_ui()
