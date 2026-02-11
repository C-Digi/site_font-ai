import argparse
import json
from pathlib import Path
from typing import Dict, Any, Tuple


def remap_casey_label(label: Any) -> int:
    """
    Governance policy: non-binary label 2 is treated as 0 for primary metrics.
    """
    if label == 2:
        return 0
    return 1 if label == 1 else 0


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_case_map(results: Dict[str, Any]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    out: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for r in results.get("details", []):
        key = (r["query_id"], r["font_name"])
        out[key] = {
            "human": remap_casey_label(r.get("human_match", 0)),
            "ai": r.get("ai_match_gated", 0),
            "confidence": r.get("confidence", 0.0),
            "evidence": r.get("evidence", ""),
            "thought": r.get("thought", ""),
        }
    return out


def compute_metrics(cases: Dict[Tuple[str, str], Dict[str, Any]]) -> Dict[str, Any]:
    tp = fp = fn = tn = 0
    considered = 0
    for _, c in cases.items():
        h = remap_casey_label(c["human"])
        a = c["ai"]

        # Keep parity with production-trial scorer: only binary human labels
        # affect confusion counts, but denominator remains full set size.
        if h not in (0, 1):
            continue

        considered += 1
        if h == 1 and a == 1:
            tp += 1
        elif h == 0 and a == 1:
            fp += 1
        elif h == 1 and a == 0:
            fn += 1
        else:
            tn += 1

    total = len(cases)
    agreement = (tp + tn) / total if total else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    return {
        "agreement": round(agreement, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "counts": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "considered_binary": considered,
            "total": total,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", required=True, help="Path to control results (Prompt V3)")
    parser.add_argument("--treatment", required=True, help="Path to treatment results (Prompt V4)")
    parser.add_argument("--output", default="research/ab-eval/out/week1_prompt_ab_compare.json")
    args = parser.parse_args()

    control = load_json(Path(args.control))
    treatment = load_json(Path(args.treatment))

    c_map = extract_case_map(control)
    t_map = extract_case_map(treatment)

    common_keys = sorted(set(c_map.keys()) & set(t_map.keys()))
    c_common = {k: c_map[k] for k in common_keys}
    t_common = {k: t_map[k] for k in common_keys}

    helps = []
    hurts = []

    for k in common_keys:
        c = c_common[k]
        t = t_common[k]
        h = remap_casey_label(c["human"])
        c_ok = c["ai"] == h
        t_ok = t["ai"] == h

        if (not c_ok) and t_ok:
            helps.append({
                "query_id": k[0],
                "font_name": k[1],
                "human": h,
                "control_pred": c["ai"],
                "treatment_pred": t["ai"],
            })
        elif c_ok and (not t_ok):
            hurts.append({
                "query_id": k[0],
                "font_name": k[1],
                "human": h,
                "control_pred": c["ai"],
                "treatment_pred": t["ai"],
            })

    control_metrics = compute_metrics(c_common)
    treatment_metrics = compute_metrics(t_common)

    out = {
        "metadata": {
            "control_path": args.control,
            "treatment_path": args.treatment,
            "common_coverage": len(common_keys),
            "control_total": len(c_map),
            "treatment_total": len(t_map),
        },
        "variants": {
            "A": control_metrics,
            "B": treatment_metrics,
        },
        "helps_hurts": {
            "helps_count": len(helps),
            "hurts_count": len(hurts),
            "net": len(helps) - len(hurts),
        },
        "control_metrics_common": control_metrics,
        "treatment_metrics_common": treatment_metrics,
        "delta_treatment_minus_control": {
            "agreement": round(treatment_metrics["agreement"] - control_metrics["agreement"], 4),
            "precision": round(treatment_metrics["precision"] - control_metrics["precision"], 4),
            "recall": round(treatment_metrics["recall"] - control_metrics["recall"], 4),
            "f1": round(treatment_metrics["f1"] - control_metrics["f1"], 4),
        },
        "helps_count": len(helps),
        "hurts_count": len(hurts),
        "net_help": len(helps) - len(hurts),
        "helps": helps,
        "hurts": hurts,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"Saved comparison to {out_path}")
    print(f"Common coverage: {len(common_keys)}")
    print(f"Helps/Hurts/Net: {len(helps)}/{len(hurts)}/{len(helps)-len(hurts)}")


if __name__ == "__main__":
    main()
