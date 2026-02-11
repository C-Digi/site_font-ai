import json
import re
from datetime import datetime, timezone
from pathlib import Path


def parse_manual_qa_status(qa_path: Path) -> str:
    """Parse manual QA status from QA markdown. Defaults to PENDING if unavailable."""
    if not qa_path.exists():
        return "PENDING"

    text = qa_path.read_text(encoding="utf-8")
    match = re.search(r"STATUS:\s*(PASS|FAIL|PENDING)", text, re.IGNORECASE)
    if not match:
        return "PENDING"
    return match.group(1).upper()

def derive_report():
    out_dir = Path("research/ab-eval/out")
    qa_path = Path("research/ab-eval/QA_SPECIMEN_V3_1.md")
    
    # Traceable Source: week2_specimen_v3_1_comparison.json
    # This file compares Specimen V2 (Control) vs Specimen V3.1 (Treatment)
    # Control is used as the Baseline (A) for this governance check.
    comparison_path = out_dir / "week2_specimen_v3_1_comparison.json"
    
    if not comparison_path.exists():
        print(f"Missing required artifact: {comparison_path}")
        return

    with open(comparison_path, "r", encoding="utf-8") as f:
        comp = json.load(f)

    now_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    qa_status = parse_manual_qa_status(qa_path)

    # Provenance Mapping:
    # Baseline Metrics -> control_metrics_common
    # Treatment Metrics -> treatment_metrics_common
    # Helps/Hurts -> helps_count, hurts_count
    
    derived = {
        "metadata": {
            "run_id": "governance_derivation_v3",
            "timestamp": now_utc,
            "source_artifact": comparison_path.as_posix(),
            "variants": ["A (Control/V2)", "B2_V3_1 (Treatment/V3.1)"]
        },
        "variants": {
            "A": {
                "Agreement": comp["control_metrics_common"]["agreement"],
                "Precision@10": comp["control_metrics_common"]["precision"],
                "Recall@10": comp["control_metrics_common"]["recall"]
            },
            "B2_V3_1": {
                "Agreement": comp["treatment_metrics_common"]["agreement"],
                "Precision@10": comp["treatment_metrics_common"]["precision"],
                "Recall@10": comp["treatment_metrics_common"]["recall"]
            }
        },
        "helps_hurts": {
            "helps_count": comp["helps_count"],
            "hurts_count": comp["hurts_count"],
            "net": comp["helps_count"] - comp["hurts_count"]
        },
        "visual_qa": {
            "status": qa_status,
            "evidence": qa_path.as_posix()
        },
        "provenance": {
            "G1": "Delta from treatment_metrics_common.agreement - control_metrics_common.agreement (cross-check: delta_treatment_minus_control.agreement)",
            "G2": "Delta from treatment_metrics_common.precision - control_metrics_common.precision (cross-check: delta_treatment_minus_control.precision)",
            "G3": "Net from helps_count - hurts_count (cross-check: net_help)",
            "G4": "Status from QA_SPECIMEN_V3_1.md Conclusion"
        }
    }
    
    out_path = out_dir / "governance_gate_ready_v3.json"
    with Path(out_path).open("w", encoding="utf-8") as f:
        json.dump(derived, f, indent=2)
    print(f"Created {out_path}")

if __name__ == "__main__":
    derive_report()
