import json
from pathlib import Path
import base64
from datetime import datetime

def image_to_base64(path):
    if not path.exists():
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def main():
    out_dir = Path("research/ab-eval/out")
    specimen_dir = out_dir / "specimens_v2_medium_nobias"
    
    # Load results
    try:
        with open(out_dir / "full_set_no_bias_qwen235b.json", "r") as f:
            qwen235b = json.load(f)
    except:
        qwen235b = {"details": []}
        
    try:
        with open(out_dir / "full_set_no_bias_vl_plus.json", "r") as f:
            vl_plus = json.load(f)
    except:
        vl_plus = {"details": []}

    # Group by query/font
    data = {}
    
    def add_to_data(results, model_key):
        for r in results.get("details", []):
            key = (r["query_id"], r["font_name"])
            if key not in data:
                data[key] = {
                    "query_id": r["query_id"],
                    "query_text": r["query_text"],
                    "font_name": r["font_name"],
                    "human_match": r["human_match"],
                    "judgments": {}
                }
            data[key]["judgments"][model_key] = {
                "match": r["ai_match"],
                "thought": r["thought"]
            }

    add_to_data(qwen235b, "qwen235b")
    add_to_data(vl_plus, "vl_plus")

    # Filter for conflicts with Casey
    conflicts = []
    for key, val in data.items():
        j = val["judgments"]
        h = val["human_match"]
        
        m1 = j.get("qwen235b", {}).get("match")
        m2 = j.get("vl_plus", {}).get("match")
        
        # Conflict criteria: at least one model differs from Casey’s label
        if (m1 is not None and m1 != h) or (m2 is not None and m2 != h):
            conflicts.append(val)

    # Sort by query_id
    conflicts.sort(key=lambda x: (x["query_id"], x["font_name"]))

    # Build HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Model Alignment Conflict Review (Full Set - No Bias)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.2; color: #f8fafc; max-width: 1600px; margin: 0 auto; padding: 10px; background: #020617; }}
        h1 {{ border-bottom: 2px solid #1e293b; padding-bottom: 5px; margin: 0 0 10px 0; font-size: 1.2em; }}
        .query-group {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; margin-bottom: 10px; overflow: hidden; }}
        .query-header {{ background: #1e293b; padding: 4px 12px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
        .query-text {{ font-weight: bold; font-size: 0.95em; color: #fff; }}
        .query-id {{ color: #94a3b8; font-size: 0.75em; }}
        .conflict-row {{ display: flex; border-bottom: 1px solid #1e293b; padding: 8px 12px; gap: 12px; }}
        .conflict-row:last-child {{ border-bottom: none; }}
        .specimen {{ flex: 0 0 180px; }}
        .specimen img {{ width: 100%; border: 1px solid #334155; border-radius: 4px; filter: invert(0.9) hue-rotate(180deg); }}
        .judgments {{ flex: 1; display: flex; gap: 8px; min-width: 0; }}
        .judgment-box {{ flex: 1; min-width: 0; background: #1e293b; border: 1px solid #334155; border-radius: 4px; padding: 6px; font-size: 0.75em; display: flex; flex-direction: column; position: relative; }}
        .judgment-box.match-1 {{ border-left: 3px solid #22c55e; }}
        .judgment-box.match-0 {{ border-left: 3px solid #ef4444; }}
        .judgment-header {{ font-weight: bold; margin-bottom: 4px; display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 2px; }}
        
        .human-label {{ background: #020617; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; display: inline-block; font-weight: 800; border: 2px solid transparent; margin-bottom: 4px; }}
        .human-label.match-1 {{ border-color: #22c55e; }}
        .human-label.match-0 {{ border-color: #ef4444; }}
        .human-label.match-2 {{ border-color: #eab308; }}
        
        .alignment-status {{ font-weight: 900; text-transform: uppercase; font-size: 0.7em; padding: 1px 4px; border-radius: 3px; }}
        .alignment-status.correct {{ background: #22c55e; color: #fff; }}
        .alignment-status.incorrect {{ background: #ef4444; color: #fff; }}
        .alignment-status.edge {{ background: #eab308; color: #000; }}
        
        .thought {{ color: #cbd5e1; font-style: italic; margin-bottom: 4px; flex-grow: 1; overflow-y: auto; max-height: 120px; line-height: 1.3; font-size: 0.9em; }}
        .controls {{ background: #0f172a; border-top: 1px solid #1e293b; padding: 4px 12px; display: flex; align-items: center; gap: 20px; justify-content: space-between; font-size: 0.8em; }}
        .btn {{ padding: 4px 8px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }}
        .btn-success {{ background: #22c55e; color: white; position: fixed; bottom: 20px; right: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); padding: 8px 16px; font-size: 0.9em; z-index: 1000; }}
        
        .button-group {{ display: flex; gap: 3px; flex-wrap: wrap; }}
        .vote-btn {{ padding: 2px 6px; font-size: 0.8em; border: 1px solid #334155; background: #0f172a; color: #94a3b8; cursor: pointer; border-radius: 3px; transition: all 0.1s; }}
        .vote-btn:hover {{ background: #1e293b; color: #fff; }}
        .vote-btn.active {{ background: #3b82f6; color: white; border-color: #2563eb; }}
        
        .override-section {{ margin-top: auto; padding-top: 4px; border-top: 1px dashed #334155; }}
        .overall-group {{ display: flex; gap: 6px; align-items: center; }}
        .original-label {{ font-size: 0.8em; color: #64748b; margin-left: auto; }}
    </style>
</head>
<body>
    <header style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h1>Model Alignment Conflict Review (Full Set - No Bias)</h1>
        <div style="font-size: 0.8em; color: #94a3b8;">Total conflicts: {len(conflicts)}</div>
    </header>
    
    <div id="review-container">
    """

    for item in conflicts:
        safe_name = item["font_name"].replace(" ", "_").replace("/", "_")
        img_path = specimen_dir / f"{safe_name}.png"
        img_data = image_to_base64(img_path)
        img_src = f"data:image/png;base64,{img_data}" if img_data else ""

        html += f"""
        <div class="query-group" 
             data-qid="{item['query_id']}" 
             data-font="{item['font_name']}"
             data-casey-label="{item['human_match']}">
            <div class="query-header">
                <div class="query-text">{item['query_id']} | {item['font_name']} | {item['query_text']}</div>
                <div class="original-label">Original: {'MATCH' if item['human_match'] == 1 else ('NO MATCH' if item['human_match'] == 0 else 'EITHER')}</div>
            </div>
            <div class="conflict-row">
                <div class="specimen">
                    <img src="{img_src}" alt="{item['font_name']}">
                </div>
                <div class="judgments">
                    <div class="judgment-box human-ref" data-current-label="{item['human_match']}">
                        <div class="judgment-header">CASEY (Human)</div>
                        <div style="text-align: center; padding: 4px 0;">
                            <div class="human-label match-{item['human_match']}">{'MATCH' if item['human_match'] == 1 else ('NO MATCH' if item['human_match'] == 0 else 'EITHER')}</div>
                        </div>
                        <div class="override-section">
                            <div style="font-size: 0.7em; color: #94a3b8; margin-bottom: 2px;">Override:</div>
                            <div class="button-group" data-field="human-override">
                                <button class="vote-btn {'active' if item['human_match'] == 1 else ''}" onclick="setHumanVote(this, 1)">Match</button>
                                <button class="vote-btn {'active' if item['human_match'] == 0 else ''}" onclick="setHumanVote(this, 0)">No Match</button>
                                <button class="vote-btn {'active' if item['human_match'] == 2 else ''}" onclick="setHumanVote(this, 2)">Either</button>
                            </div>
                        </div>
                    </div>
        """
        
        for m_key, m_name in [("qwen235b", "Qwen 235B"), ("vl_plus", "Qwen VL Plus")]:
            j = item["judgments"].get(m_key)
            if j:
                match_class = f"match-{j['match']}"
                html += f"""
                <div class="judgment-box {match_class}" data-model-match="{j['match']}" data-model-key="{m_key}">
                    <div class="judgment-header">
                        <span>{m_name}</span>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span>{'MATCH' if j['match'] else 'NO MATCH'}</span>
                            <span class="alignment-status"></span>
                        </div>
                    </div>
                    <div class="thought">{j['thought']}</div>
                </div>
                """
            else:
                html += f"""<div class="judgment-box" style="opacity: 0.4;"><div class="judgment-header">{m_name}</div><div class="thought">N/A</div></div>"""

        html += f"""
                </div>
            </div>
            <div class="controls">
                <div class="overall-group">
                    <span style="font-weight: bold; color: #94a3b8;">Preferred:</span>
                    <div class="button-group" data-field="overall-vote">
                        <button class="vote-btn" onclick="setVote(this, 'qwen235b')">Qwen 235B</button>
                        <button class="vote-btn" onclick="setVote(this, 'vl_plus')">Qwen VL Plus</button>
                        <button class="vote-btn" onclick="setVote(this, 'tie')">Tie</button>
                        <button class="vote-btn" onclick="setVote(this, 'none')">None</button>
                    </div>
                </div>
                <div style="font-size: 0.85em; color: #64748b; font-style: italic;">
                    Conflict Case: {item['query_id']} vs Models
                </div>
            </div>
        </div>
        """

    html += """
    </div>

    <button class="btn btn-success" onclick="exportResults()">Export Review JSON</button>

    <script>
        const STORAGE_KEY = 'alignment-review-data-v1';
        let reviewData = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');

        function save() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(reviewData));
        }

        function setVote(btn, value) {
            const group = btn.parentElement;
            group.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            group.dataset.value = value;

            const qGroup = btn.closest('.query-group');
            const key = qGroup.dataset.qid + '|' + qGroup.dataset.font;
            if (!reviewData[key]) reviewData[key] = { };
            
            if (group.dataset.field === 'overall-vote') {
                reviewData[key].overall = value;
            }
            save();
        }

        function setHumanVote(btn, value) {
            const group = btn.parentElement;
            group.querySelectorAll('.vote-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            group.dataset.value = value;
            
            // Update the display label
            const box = btn.closest('.judgment-box');
            const labelDiv = box.querySelector('.human-label');
            labelDiv.textContent = value === 1 ? 'MATCH' : (value === 0 ? 'NO MATCH' : 'EITHER');
            labelDiv.className = 'human-label match-' + value;
            
            // Update the query group dataset for export
            const queryGroup = btn.closest('.query-group');
            queryGroup.dataset.caseyLabel = value;

            const key = queryGroup.dataset.qid + '|' + queryGroup.dataset.font;
            if (!reviewData[key]) reviewData[key] = { };
            reviewData[key].human_override = value;
            
            updateAlignmentIndicators(queryGroup, value);
            save();
        }

        function updateAlignmentIndicators(queryGroup, humanLabel) {
            queryGroup.querySelectorAll('.judgment-box[data-model-match]').forEach(box => {
                const modelMatch = parseInt(box.dataset.modelMatch);
                const statusSpan = box.querySelector('.alignment-status');
                const hl = parseInt(humanLabel);
                
                if (hl === 2) {
                    statusSpan.textContent = 'EDGE';
                    statusSpan.className = 'alignment-status edge';
                } else if (modelMatch === hl) {
                    statusSpan.textContent = 'CORRECT';
                    statusSpan.className = 'alignment-status correct';
                } else {
                    statusSpan.textContent = 'INCORRECT';
                    statusSpan.className = 'alignment-status incorrect';
                }
            });
        }

        function init() {
            document.querySelectorAll('.query-group').forEach(group => {
                const key = group.dataset.qid + '|' + group.dataset.font;
                const data = reviewData[key];
                
                // Always update indicators initially based on initial human label
                const currentHumanLabel = data && data.human_override !== undefined ? data.human_override : group.dataset.caseyLabel;
                updateAlignmentIndicators(group, currentHumanLabel);

                if (!data) return;
                
                // Restore overall vote
                if (data.overall) {
                    const btn = group.querySelector(`.button-group[data-field="overall-vote"] .vote-btn[onclick*="'${data.overall}'"]`);
                    if (btn) {
                        btn.classList.add('active');
                        btn.parentElement.dataset.value = data.overall;
                    }
                }
                
                // Restore human override
                if (data.human_override !== undefined) {
                    const btn = group.querySelector(`.button-group[data-field="human-override"] .vote-btn[onclick*=", ${data.human_override})"]`);
                    if (btn) setHumanVote(btn, data.human_override);
                }
            });
        }
        window.onload = init;

        function exportResults() {
            const results = {
                timestamp: new Date().toISOString(),
                decisions: []
            };
            
            document.querySelectorAll('.query-group').forEach(group => {
                const qid = group.dataset.qid;
                const font = group.dataset.font;
                const caseyLabel = group.dataset.caseyLabel;
                
                const overallGroup = group.querySelector('.button-group[data-field="overall-vote"]');
                const overallVote = overallGroup.dataset.value || "";
                
                const models = {};
                group.querySelectorAll('.judgment-box[data-model-match]').forEach(box => {
                    const modelKey = box.dataset.modelKey;
                    const modelMatch = parseInt(box.dataset.modelMatch);
                    models[modelKey] = {
                        match: modelMatch,
                        is_correct: modelMatch === parseInt(caseyLabel)
                    };
                });
                
                results.decisions.push({
                    query_id: qid,
                    font_name: font,
                    casey_label: parseInt(caseyLabel),
                    overall_vote: overallVote,
                    models: models
                });
            });
            
            const blob = new Blob([JSON.stringify(results, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `full_set_review_export_${new Date().getTime()}.json`;
            a.click();
        }
    </script>
</body>
</html>
    """

    out_file = out_dir / "alignment_full_set_review.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated HTML artifact: {out_file}")

if __name__ == "__main__":
    main()
