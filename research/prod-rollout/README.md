# B2 (Qwen3-VL) Production Rollout

> [!IMPORTANT]
> **SSoT MIGRATED**: The Single Source of Truth has moved to the [LightSpec root](/.lightspec/).
> This folder now serves as a repository for implementation artifacts and rollout tracking.
> Refer to `.lightspec/font-search-rag.md` for current specs.

This folder serves as the historical documentation for the production migration to B2 retrieval (`Qwen/Qwen3-VL-Embedding-8B`).

## 🎯 Goals
- Replace text-only embeddings with multimodal (image + short text) embeddings.
- Improve retrieval quality for visual and style-driven font searches.
- Maintain system stability with a non-blocking background queue for JIT (Just-In-Time) seeding.

## 📂 Documentation Structure
- [`RUNBOOK.md`](RUNBOOK.md): Step-by-step operator guide for Week 1 and Week 2.
- [`PROGRESS.md`](PROGRESS.md) (Deprecated): Detailed checklist for tracking migration status.
- [`DECISIONS.md`](DECISIONS.md) (Deprecated): Log of architectural decisions and their justifications.
- [`WORK_BREAKDOWN.md`](WORK_BREAKDOWN.md): Task decomposition, milestones, and acceptance criteria.

## 🔗 Related Resources
- [Qwen3-VL Investigation](../../research/qwen3-vl-investigation.md)
- [A/B Evaluation Plan](../../_05_guides/2026-02-05_offline-ab-eval-plan_qwen3-vl.md)
- [Handoff (Feb 6)](../../2026-02-06T07-28-41_handoff.md)

## 🏗️ Core Decisions Recap
1. **Target:** B2 Variant (Glyph image + short structured text).
2. **JIT Seeding:** Queue-based background processing (does not block search requests).
3. **Hosting:** External font hosting remains (no self-hosting of binaries).
4. **Dimensions:** 4096 dimensions (consistent with Qwen3).
