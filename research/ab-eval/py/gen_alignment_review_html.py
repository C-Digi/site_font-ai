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
        with open(out_dir / "spot_check_alignment.json", "r") as f:
            gpt52 = json.load(f)
    except:
        gpt52 = {"details": []}
        
    try:
        # Prioritize comprehensive results if they exist
        comp_file = out_dir / "comprehensive_235b_results.json"
        if comp_file.exists():
            with open(comp_file, "r") as f:
                qwen235b = json.load(f)
        else:
            with open(out_dir / "spot_check_alignment_qwen3vl_235b.json", "r") as f:
                qwen235b = json.load(f)
    except:
        qwen235b = {"details": []}
        
    try:
        with open(out_dir / "spot_check_alignment_qwen3vl_8b_local.json", "r") as f:
            qwen8b = json.load(f)
    except:
        qwen8b = {"details": []}

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

    add_to_data(gpt52, "gpt52")
    add_to_data(qwen235b, "qwen235b")
    add_to_data(qwen8b, "qwen8b")

    # Filter for conflicts
    conflicts = []
    for key, val in data.items():
        j = val["judgments"]
        h = val["human_match"]
        
        m1 = j.get("qwen235b", {}).get("match")
        m2 = j.get("qwen8b", {}).get("match")
        m3 = j.get("gpt52", {}).get("match")
        
        # Conflict criteria: any disagreement between any two or with human
        all_actors = [h]
        if m1 is not None: all_actors.append(m1)
        if m2 is not None: all_actors.append(m2)
        if m3 is not None: all_actors.append(m3)
        
        if len(set(all_actors)) > 1:
            conflicts.append(val)

    # Sort by query_id
    conflicts.sort(key=lambda x: (x["query_id"], x["font_name"]))

    # Build HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Model Alignment Conflict Review</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
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
        .judgment-box {{ flex: 1; min-width: 250px; background: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px; padding: 10px; font-size: 0.85em; }}
        .judgment-box.match-1 {{ border-left: 5px solid #28a745; }}
        .judgment-box.match-0 {{ border-left: 5px solid #dc3545; }}
        .judgment-header {{ font-weight: bold; margin-bottom: 5px; display: flex; justify-content: space-between; }}
        .human-label {{ background: #007bff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; margin-bottom: 10px; display: inline-block; }}
        .thought {{ color: #555; font-style: italic; display: -webkit-box; -webkit-line-clamp: 8; -webkit-box-orient: vertical; overflow: hidden; }}
        .thought:hover {{ -webkit-line-clamp: unset; }}
        .controls {{ background: #fff; border-top: 1px solid #ddd; padding: 15px; display: flex; align-items: center; gap: 20px; justify-content: flex-end; }}
        .btn {{ padding: 8px 16px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; position: fixed; bottom: 20px; right: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); padding: 12px 24px; font-size: 1.1em; }}
        select {{ padding: 6px; border-radius: 4px; border: 1px solid #ccc; }}
        .font-name {{ font-weight: bold; margin-bottom: 10px; font-size: 1.1em; }}
    </style>
</head>
<body>
    <h1>Model Alignment Conflict Review</h1>
    <p>Focusing on disagreements between models and human labels (Casey). Total conflicts: {len(conflicts)}</p>
    
    <div id="review-container">
    """

    current_query = None
    for item in conflicts:
        if item["query_id"] != current_query:
            if current_query is not None:
                html += """
                    </div>
                    <div class="controls">
                        <label>Favorite Model for this Query:</label>
                        <select class="query-vote" data-qid="{current_query}">
                            <option value="">-- Choose --</option>
                            <option value="qwen235b">Qwen 235B (OpenRouter)</option>
                            <option value="qwen8b">Qwen 8B (Local)</option>
                            <option value="tie">Tie / Both Good</option>
                            <option value="none">None / Both Bad</option>
                        </select>
                    </div>
                </div>
                """.replace("{current_query}", current_query)
            
            current_query = item["query_id"]
            html += f"""
            <div class="query-group">
                <div class="query-header">
                    <div class="query-id">{item['query_id']}</div>
                    <div class="query-text">{item['query_text']}</div>
                </div>
                <div class="conflict-list">
            """

        safe_name = item["font_name"].replace(" ", "_").replace("/", "_")
        img_path = specimen_dir / f"{safe_name}.png"
        img_data = image_to_base64(img_path)
        img_src = f"data:image/png;base64,{img_data}" if img_data else ""

        html += f"""
        <div class="conflict-row">
            <div class="specimen">
                <div class="font-name">{item['font_name']}</div>
                <img src="{img_src}" alt="{item['font_name']}">
            </div>
            <div class="judgments">
                <div class="judgment-box human-ref">
                    <div class="human-label">CASEY REFERENCE: {'MATCH' if item['human_match'] else 'NO MATCH'}</div>
                    <div style="font-size: 0.9em; color: #666;">This is the gold standard label.</div>
                </div>
        """
        
        for m_key, m_name in [("qwen235b", "Qwen 235B"), ("qwen8b", "Qwen 8B"), ("gpt52", "GPT-5.2")]:
            j = item["judgments"].get(m_key)
            if j:
                match_class = f"match-{j['match']}"
                html += f"""
                <div class="judgment-box {match_class}">
                    <div class="judgment-header">
                        <span>{m_name}</span>
                        <span>{'MATCH' if j['match'] else 'NO MATCH'}</span>
                    </div>
                    <div class="thought" title="{j['thought'].replace('"', '"')}">{j['thought']}</div>
                </div>
                """
            else:
                html += f"""<div class="judgment-box" style="opacity: 0.5;"><div class="judgment-header">{m_name}</div>N/A</div>"""

        html += """
            </div>
        </div>
        """

    # Close last query group
    if current_query is not None:
        html += """
                </div>
                <div class="controls">
                    <label>Favorite Model for this Query:</label>
                    <select class="query-vote" data-qid="{current_query}">
                        <option value="">-- Choose --</option>
                        <option value="qwen235b">Qwen 235B (OpenRouter)</option>
                        <option value="qwen8b">Qwen 8B (Local)</option>
                        <option value="tie">Tie / Both Good</option>
                        <option value="none">None / Both Bad</option>
                    </select>
                </div>
            </div>
            """.replace("{current_query}", current_query)

    html += """
    </div>

    <!-- Export Review JSON button removed per user request -->

    <script>
        // Export logic disabled
        function exportResults() {
            console.log("Export disabled");
        }

        function jsonPrettyPrint(obj) {
            return JSON.stringify(obj, null, 2);
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
