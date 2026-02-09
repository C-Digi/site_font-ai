import json
import os
from collections import defaultdict
import numpy as np

SSOT_PATH = "research/ab-eval/out/full_set_review_export_1770612809775.json"
PREDICTIONS_PATH = "research/ab-eval/out/full_set_no_bias_gemini3flashpreview.json"
QUERIES_PATH = "research/ab-eval/data/queries.medium.human.v1.json"

def analyze(results_path, label):
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found.")
        return None
        
    with open(SSOT_PATH, 'r') as f:
        ssot = json.load(f)
    
    with open(results_path, 'r') as f:
        predictions_raw = json.load(f)
    
    with open(QUERIES_PATH, 'r') as f:
        queries = json.load(f)

    query_map = {q['id']: q for q in queries}
    
    # Map (query_id, font_name) -> ground_truth (treat 2 as 1)
    gt_map = {}
    for item in ssot['decisions']:
        val = item['casey_label']
        if val == 2: val = 1
        gt_map[(item['query_id'], item['font_name'])] = val

    # Map (query_id, font_name) -> prediction
    pred_map = {}
    for item in predictions_raw['details']:
        pred_map[(item['query_id'], item['font_name'])] = item['ai_match']

    mismatches = []
    
    tp = fp = fn = tn = 0
    total = 0
    
    for (qid, fname), gt in gt_map.items():
        pred = pred_map.get((qid, fname))
        if pred is None:
            continue
            
        total += 1
        if pred == gt:
            if pred == 1: tp += 1
            else: tn += 1
        else:
            if pred == 1: fp += 1
            else: fn += 1
            mismatches.append({
                'query_id': qid,
                'font_name': fname,
                'gt': gt,
                'pred': pred,
                'query_text': query_map.get(qid, {}).get('text', 'unknown'),
                'category': query_map.get(qid, {}).get('class', 'unknown'),
                'thought': next((p.get('thought', '') for p in predictions_raw['details'] if p['query_id'] == qid and p['font_name'] == fname), "")
            })

    agreement = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n=== {label} ===")
    print(f"Total pairs evaluated: {total}")
    print(f"Agreement: {agreement:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1:        {f1:.4f}")
    print(f"TP: {tp}, FP: {fp}, FN: {fn}, TN: {tn}")

    # Bootstrap CI for agreement
    n_bootstrap = 1000
    bs_agreements = []
    keys = list(gt_map.keys())
    for _ in range(n_bootstrap):
        indices = np.random.choice(len(keys), len(keys), replace=True)
        bs_tp = bs_tn = bs_total = 0
        for idx in indices:
            k = keys[idx]
            gt = gt_map.get(k)
            pred = pred_map.get(k)
            if pred is None: continue
            bs_total += 1
            if pred == gt:
                if pred == 1: bs_tp += 1
                else: bs_tn += 1
        if bs_total > 0:
            bs_agreements.append((bs_tp + bs_tn) / bs_total)
    
    if bs_agreements:
        ci_low = np.percentile(bs_agreements, 2.5)
        ci_high = np.percentile(bs_agreements, 97.5)
        print(f"Agreement 95% CI: [{ci_low:.4f}, {ci_high:.4f}]")

    return {
        "label": label,
        "agreement": agreement,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "total": total,
        "mismatches": mismatches
    }

if __name__ == "__main__":
    baseline_g3 = analyze(PREDICTIONS_PATH, "Gemini 3 Flash Preview (Baseline)")
    baseline_g2 = analyze("research/ab-eval/out/intervention_baseline_v2_results.json", "Gemini 2.0 Flash (Baseline)")
    prompt_v3 = analyze("research/ab-eval/out/intervention_prompt_v3_results.json", "Intervention Prompt V3 (V2 Render)")
    full_v3 = analyze("research/ab-eval/out/intervention_full_v3_results.json", "Intervention Full V3 (Prompt+Render+Micro)")
    
    # Compare per query
    if full_v3 and baseline_g2:
        improved = []
        worsened = []
        
        with open("research/ab-eval/out/intervention_baseline_v2_results.json", 'r') as f:
            b_data = json.load(f)
        with open("research/ab-eval/out/intervention_full_v3_results.json", 'r') as f:
            v_data = json.load(f)
            
        b_map = {(d['query_id'], d['font_name']): d['ai_match'] for d in b_data['details']}
        v_map = {(d['query_id'], d['font_name']): d['ai_match'] for d in v_data['details']}
        
        with open(SSOT_PATH, 'r') as f:
            ssot = json.load(f)
        gt_map = {(d['query_id'], d['font_name']): (1 if d['casey_label'] >= 1 else 0) for d in ssot['decisions']}
        
        for k, gt in gt_map.items():
            b_pred = b_map.get(k)
            v_pred = v_map.get(k)
            
            if b_pred is not None and v_pred is not None:
                b_correct = (b_pred == gt)
                v_correct = (v_pred == gt)
                
                if not b_correct and v_correct:
                    improved.append(k)
                elif b_correct and not v_correct:
                    worsened.append(k)
        
        print(f"\nNet improvement (G2 V3 vs G2 Baseline): {len(improved) - len(worsened)} (Improved: {len(improved)}, worsened: {len(worsened)})")

    # Policy Intervention: Confidence Gating
    if full_v3:
        print("\n--- Policy Intervention: Confidence Gating ---")
        with open("research/ab-eval/out/intervention_full_v3_results.json", 'r') as f:
            v_data = json.load(f)
            
        with open(SSOT_PATH, 'r') as f:
            ssot = json.load(f)
        gt_map = {(d['query_id'], d['font_name']): (1 if d['casey_label'] >= 1 else 0) for d in ssot['decisions']}

        for threshold in [0.6, 0.7, 0.8, 0.9]:
            gated_matches = []
            gt_list = []
            for d in v_data['details']:
                k = (d['query_id'], d['font_name'])
                if k not in gt_map: continue
                
                m = d['ai_match']
                c = d.get('confidence', 0.5)
                if m == 1 and c < threshold:
                    gated_matches.append(0)
                else:
                    gated_matches.append(m)
                gt_list.append(gt_map[k])
            
            tp = fp = fn = tn = 0
            for g, p in zip(gt_list, gated_matches):
                if g == p:
                    if p == 1: tp += 1
                    else: tn += 1
                else:
                    if p == 1: fp += 1
                    else: fn += 1
            
            if len(gt_list) > 0:
                ag = (tp + tn) / len(gt_list)
                print(f"Threshold {threshold}: Agreement {ag:.4f}, TP {tp}, FP {fp}, FN {fn}, TN {tn}")
