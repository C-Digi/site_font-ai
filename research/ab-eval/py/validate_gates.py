"""
Governance Gate Validator
Aligns with research/ab-eval/EVALUATION_CONTRACT.md

Policies:
1. Label Remapping: Input reports MUST have remapped labels (2 -> 0) before metric computation.
2. Tie-break Order: Agreement -> Recall@10 -> Precision@10 -> MRR@10.
3. Strict Gates: No proxy metrics for G1 (Agreement).
"""
import json
import argparse
import sys
from pathlib import Path

def load_report(path: Path):
    if not path.exists():
        print(f"Error: Report not found at {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_gates(report, baseline=None):
    # Thresholds from EVALUATION_CONTRACT.md
    AGREEMENT_DELTA_MIN = 0.01
    PRECISION_DELTA_MIN = -0.02
    
    gates = {
        "G1 (Agreement Delta)": {"status": "FAIL", "value": 0.0, "threshold": f">= {AGREEMENT_DELTA_MIN}"},
        "G2 (Precision Delta)": {"status": "FAIL", "value": 0.0, "threshold": f">= {PRECISION_DELTA_MIN}"},
        "G3 (Helps/Hurts Net)": {"status": "FAIL", "value": 0, "threshold": "> 0"},
        "G4 (Visual QA)": {"status": "PENDING", "value": "Manual", "threshold": "Zero clipping/overlap"}
    }

    # Extract metrics for treatment (usually B2 or C)
    # We'll look for B2 or C (alpha=0.5) if they exist, otherwise the first non-A variant
    variants = report.get("variants", {})
    treatment_name = "B2" if "B2" in variants else (
        "C (alpha=0.5)" if "C (alpha=0.5)" in variants else None
    )
    if not treatment_name:
        # Fallback to first variant that isn't A
        for v in variants:
            if v != "A":
                treatment_name = v
                break
    
    if not treatment_name:
        print("Error: No treatment variant found in report.")
        return False, gates

    treatment = variants[treatment_name]
    baseline_metrics = variants.get("A", {})
    
    if baseline:
        baseline_metrics = baseline.get("variants", {}).get("A", baseline_metrics)

    # G1: Agreement Delta
    # Note: Contract strictly requires Agreement. No proxies (like Recall) allowed.
    treatment_agreement = treatment.get("agreement") or treatment.get("Agreement")
    baseline_agreement = baseline_metrics.get("agreement") or baseline_metrics.get("Agreement")
    
    if treatment_agreement is not None and baseline_agreement is not None:
        delta = treatment_agreement - baseline_agreement
        gates["G1 (Agreement Delta)"]["value"] = delta
        if delta >= AGREEMENT_DELTA_MIN:
            gates["G1 (Agreement Delta)"]["status"] = "PASS"
    else:
        gates["G1 (Agreement Delta)"]["status"] = "FAIL (Missing Agreement Metric)"

    # G2: Precision Delta
    treatment_prec = treatment.get("precision") or treatment.get("Precision@10")
    baseline_prec = baseline_metrics.get("precision") or baseline_metrics.get("Precision@10")
    
    if treatment_prec is not None and baseline_prec is not None:
        delta_p = treatment_prec - baseline_prec
        gates["G2 (Precision Delta)"]["value"] = delta_p
        if delta_p >= PRECISION_DELTA_MIN:
            gates["G2 (Precision Delta)"]["status"] = "PASS"
    else:
        gates["G2 (Precision Delta)"]["status"] = "SKIP (Missing Metric)"

    # G3: Helps/Hurts Net
    helps = report.get("helps_hurts", {}).get("helps_count", 0)
    hurts = report.get("helps_hurts", {}).get("hurts_count", 0)
    net = helps - hurts
    gates["G3 (Helps/Hurts Net)"]["value"] = net
    if net > 0:
        gates["G3 (Helps/Hurts Net)"]["status"] = "PASS"
    elif "helps_hurts" not in report:
        gates["G3 (Helps/Hurts Net)"]["status"] = "SKIP (Missing Data)"

    # G4: Visual QA (Manual input from report metadata/results)
    manual_g4 = report.get("visual_qa", {}).get("status")
    if manual_g4:
        gates["G4 (Visual QA)"]["status"] = manual_g4
        gates["G4 (Visual QA)"]["value"] = report.get("visual_qa", {}).get("evidence", "Manual")

    # Final decision
    # STRICT POLICY: PENDING status (like G4) MUST block a programmatic "GO".
    # All gates must be explicitly "PASS" for a "GO" decision.
    all_pass = all(g["status"] == "PASS" for g in gates.values())
    
    return all_pass, gates

def main():
    parser = argparse.ArgumentParser(description="Validate report against governance gates.")
    parser.add_argument("report", help="Path to report.json")
    parser.add_argument("--baseline", help="Path to baseline report.json (optional)")
    parser.add_argument("--out", help="Path to save gate results (json)")
    args = parser.parse_args()

    report = load_report(Path(args.report))
    baseline = load_report(Path(args.baseline)) if args.baseline else None

    if not report:
        sys.exit(1)

    success, gates = validate_gates(report, baseline)

    print("\n=== GOVERNANCE GATE CHECK ===")
    print(f"{'Gate':<30} | {'Status':<10} | {'Value':<10} | {'Threshold':<10}")
    print("-" * 70)
    for name, result in gates.items():
        val_str = f"{result['value']:.4f}" if isinstance(result['value'], float) else str(result['value'])
        print(f"{name:<30} | {result['status']:<10} | {val_str:<10} | {result['threshold']:<10}")
    
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump({"success": success, "gates": gates}, f, indent=2)
        print(f"\nResults saved to {args.out}")

    print("-" * 70)
    if success:
        print("OVERALL STATUS: PASS (GO)")
        sys.exit(0)
    else:
        print("OVERALL STATUS: FAIL (NO-GO)")
        sys.exit(1)

if __name__ == "__main__":
    main()
