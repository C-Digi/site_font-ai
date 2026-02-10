# Week 3 Report: Dynamic Threshold Calibration

## Objective
Maximize Agreement with SSoT using dynamic confidence gating.

## Calibration Methods
- Baseline: Fixed 0.9 gate
- Global Sweep: Optimal single T
- Group-Aware: T optimized for Technical vs Subjective queries

## Leaderboard

| Policy | Agreement | Precision | Recall | F1 | TP | FP | FN | TN | Cov | Delta |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Baseline (0.9) | 0.6761 | 0.8158 | 0.6889 | 0.7470 | 31 | 7 | 14 | 136 | 0.1538 | +0.0000 |
| Global (0.00) | 0.6761 | 0.8158 | 0.6889 | 0.7470 | 31 | 7 | 14 | 136 | 0.1538 | +0.0000 |
| **Dynamic** | **0.6761** | 0.8158 | 0.6889 | 0.7470 | 31 | 7 | 14 | 136 | 0.1538 | +0.0000 |

## Recommended Policy

| Group | Threshold |
| :--- | :--- |
| Subjective | 0.00 |
| Technical | 0.00 |

## Observed Accuracy vs Confidence

| Conf | Accuracy | Count |
| :--- | :--- | :--- |
| 0.9 | 0.6667 | 6 |
| 0.95 | 0.7500 | 4 |
| 1.0 | 0.8571 | 28 |
