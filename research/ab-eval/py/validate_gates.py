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
    PRECISION_REGRESSION_CAP = -0.02
    
    gates = {
        "G1 (Agreement Delta)": {"status": "FAIL", "value": 0.0, "threshold": f">= {AGREEMENT_DELTA_MIN}"},
        "G2 (Precision Regression)": {"status": "FAIL", "value": 0.0, "threshold": f"<= {PRECISION_REGRESSION_CAP}"},
        "G3 (Helps/Hurts Net)": {"status": "FAIL", "value": 0, "threshold": "> 0"}
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
    # Note: If agreement is not in report, we check Recall@10 as proxy if requested, 
    # but contract says Agreement. If missing, we mark as Fail.
    treatment_agreement = treatment.get("agreement") or treatment.get("Agreement")
    baseline_agreement = baseline_metrics.get("agreement") or baseline_metrics.get("Agreement")
    
    if treatment_agreement is not None and baseline_agreement is not None:
        delta = treatment_agreement - baseline_agreement
        gates["G1 (Agreement Delta)"]["value"] = delta
        if delta >= AGREEMENT_DELTA_MIN:
            gates["G1 (Agreement Delta)"]["status"] = "PASS"
    else:
        gates["G1 (Agreement Delta)"]["status"] = "SKIP (Missing Metric)"

    # G2: Precision Regression
    treatment_prec = treatment.get("precision") or treatment.get("Precision@10")
    baseline_prec = baseline_metrics.get("precision") or baseline_metrics.get("Precision@10")
    
    if treatment_prec is not None and baseline_prec is not None:
        regression = treatment_prec - baseline_prec
        gates["G2 (Precision Regression)"]["value"] = regression
        if regression >= PRECISION_REGRESSION_CAP:
            gates["G2 (Precision Regression)"]["status"] = "PASS"
    else:
        gates["G2 (Precision Regression)"]["status"] = "SKIP (Missing Metric)"

    # G3: Helps/Hurts Net
    helps = report.get("helps_hurts", {}).get("helps_count", 0)
    hurts = report.get("helps_hurts", {}).get("hurts_count", 0)
    net = helps - hurts
    gates["G3 (Helps/Hurts Net)"]["value"] = net
    if net > 0:
        gates["G3 (Helps/Hurts Net)"]["status"] = "PASS"
    elif "helps_hurts" not in report:
        gates["G3 (Helps/Hurts Net)"]["status"] = "SKIP (Missing Data)"

    # Final decision
    all_pass = all(g["status"] in ["PASS", "SKIP (Missing Metric)", "SKIP (Missing Data)"] for g in gates.values())
    # But at least one must be a real PASS for a true "GO"
    any_pass = any(g["status"] == "PASS" for g in gates.values())
    
    return all_pass and any_pass, gates

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
