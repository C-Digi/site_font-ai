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
    specimen_dir = out_dir / "specimens_v2_medium"
    
    # Load results
    try:
        with open(out_dir / "spot_check_alignment_qwen3vl_235b.json", "r") as f:
            qwen235b = json.load(f)
    except:
        qwen235b = {"details": []}
        
    try:
        with open(out_dir / "spot_check_alignment_vl_plus.json", "r") as f:
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
        # We also check if the model actually responded (not None)
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
    <title>Model Alignment Conflict Review (Spot Check)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #333; max-width: 1400px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        h1 {{ border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
        .query-group {{ background: white; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 30px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .query-header {{ background: #eee; padding: 15px; border-bottom: 1px solid #ddd; }}
        .query-text {{ font-weight: bold; font-size: 1.2em; color: #111; }}
        .query-id {{ color: #666; font-size: 0.9em; }}
        .conflict-row {{ display: flex; border-bottom: 1px solid #eee; padding: 20px; }}
        .conflict-row:last-child {{ border-bottom: none; }}
        .specimen {{ flex: 0 0 300px; margin-right: 20px; }}
        .specimen img {{ width: 100%; border: 1px solid #ccc; border-radius: 4px; }}
        .judgments {{ flex: 1; display: flex; gap: 15px; overflow-x: auto; }}
        .judgment-box {{ flex: 1; min-width: 300px; background: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px; padding: 10px; font-size: 0.85em; display: flex; flex-direction: column; }}
        .judgment-box.match-1 {{ border-left: 5px solid #28a745; }}
        .judgment-box.match-0 {{ border-left: 5px solid #dc3545; }}
        .judgment-header {{ font-weight: bold; margin-bottom: 5px; display: flex; justify-content: space-between; }}
        .human-label {{ background: #007bff; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; margin-bottom: 10px; display: inline-block; font-weight: bold; }}
        .thought {{ color: #555; font-style: italic; margin-bottom: 10px; flex-grow: 1; overflow-y: auto; max-height: 150px; }}
        .controls {{ background: #fff; border-top: 1px solid #ddd; padding: 15px; display: flex; align-items: center; gap: 20px; justify-content: space-between; }}
        .btn {{ padding: 8px 16px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; position: fixed; bottom: 20px; right: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); padding: 12px 24px; font-size: 1.1em; z-index: 1000; }}
        select {{ padding: 6px; border-radius: 4px; border: 1px solid #ccc; }}
        .font-name {{ font-weight: bold; margin-bottom: 10px; font-size: 1.1em; }}
        .user-vote-box {{ margin-top: 10px; padding-top: 10px; border-top: 1px dashed #ccc; }}
    </style>
</head>
<body>
    <h1>Model Alignment Conflict Review (Spot Check)</h1>
    <p>Showing decisions where at least one model disagrees with Casey (Human). Total conflicts: {len(conflicts)}</p>
    
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
                <div class="query-id">{item['query_id']} | {item['font_name']}</div>
                <div class="query-text">{item['query_text']}</div>
            </div>
            <div class="conflict-row">
                <div class="specimen">
                    <img src="{img_src}" alt="{item['font_name']}">
                </div>
                <div class="judgments">
                    <div class="judgment-box human-ref">
                        <div class="judgment-header">CASEY (Human)</div>
                        <div class="human-label">{'MATCH' if item['human_match'] else 'NO MATCH'}</div>
                        <div style="font-size: 0.9em; color: #666;">Gold standard label.</div>
                    </div>
        """
        
        for m_key, m_name in [("qwen235b", "Qwen 235B"), ("vl_plus", "Qwen VL Plus")]:
            j = item["judgments"].get(m_key)
            if j:
                match_class = f"match-{j['match']}"
                html += f"""
                <div class="judgment-box {match_class}" data-model-match="{j['match']}">
                    <div class="judgment-header">
                        <span>{m_name}</span>
                        <span>{'MATCH' if j['match'] else 'NO MATCH'}</span>
                    </div>
                    <div class="thought">{j['thought']}</div>
                    <div class="user-vote-box">
                        <label>Reviewer Decision:</label>
                        <select class="decision-vote" data-model="{m_key}">
                            <option value="">-- Rate --</option>
                            <option value="correct">Model is Correct</option>
                            <option value="incorrect">Model is Incorrect</option>
                            <option value="ambiguous">Ambiguous</option>
                        </select>
                    </div>
                </div>
                """
            else:
                html += f"""<div class="judgment-box" style="opacity: 0.5;"><div class="judgment-header">{m_name}</div>N/A</div>"""

        html += f"""
                </div>
            </div>
            <div class="controls">
                <div>
                    <label>Overall Preferred Model:</label>
                    <select class="overall-vote">
                        <option value="">-- Choose --</option>
                        <option value="qwen235b">Qwen 235B</option>
                        <option value="vl_plus">Qwen VL Plus</option>
                        <option value="tie">Tie</option>
                        <option value="none">None</option>
                    </select>
                </div>
                <div style="font-size: 0.8em; color: #666;">
                    Conflict: Casey={item['human_match']} vs Models
                </div>
            </div>
        </div>
        """

    html += """
    </div>

    <button class="btn btn-success" onclick="exportResults()">Export Review JSON</button>

    <script>
        function exportResults() {
            const results = {
                timestamp: new Date().toISOString(),
                decisions: []
            };
            
            document.querySelectorAll('.query-group').forEach(group => {
                const qid = group.dataset.qid;
                const font = group.dataset.font;
                const caseyLabel = group.dataset.caseyLabel;
                const overallVote = group.querySelector('.overall-vote').value;
                
                const models = {};
                group.querySelectorAll('.judgment-box[data-model-match]').forEach(box => {
                    const voteSel = box.querySelector('.decision-vote');
                    const modelKey = voteSel.dataset.model;
                    models[modelKey] = {
                        match: box.dataset.modelMatch,
                        user_evaluation: voteSel.value
                    };
                });
                
                results.decisions.push({
                    query_id: qid,
                    font_name: font,
                    casey_label: caseyLabel,
                    overall_vote: overallVote,
                    models: models
                });
            });
            
            const blob = new Blob([JSON.stringify(results, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `alignment_review_export_${new Date().getTime()}.json`;
            a.click();
        }
    </script>
</body>
</html>
    """

    out_file = out_dir / "alignment_conflict_review.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated HTML artifact: {out_file}")

if __name__ == "__main__":
    main()
