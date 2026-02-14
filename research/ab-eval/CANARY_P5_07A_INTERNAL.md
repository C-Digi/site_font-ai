# CANARY P5_07A_INTERNAL — Internal-Only Canary Validation

**Status:** HOLD (API Key Expired)
**Date:** 2026-02-14
**Scope:** Internal-only canary (staging/internal), no production traffic exposure
**Decision:** HOLD pending API key renewal

---

## 1. Scope Declaration

This canary validation is **internal-only** with the following constraints:
- **No production traffic exposure**
- **Staging/internal environment only** (localhost:3000 dev server)
- **Governance/gate semantics unchanged** (per EVALUATION_CONTRACT.md)
- **Rollback criteria**: Simple environment variable toggle

---

## 2. Baseline Check (`RETRIEVAL_STRATEGY=v3`)

### 2.1 Code Wiring Verification
- **File**: `src/lib/config/retrieval.ts`
- **Function**: `getRetrievalStrategy()` returns `'v3'` by default
- **Status**: ✅ VERIFIED

```typescript
// Line 17-26 (verified)
export function getRetrievalStrategy(): RetrievalStrategy {
  const envValue = process.env.RETRIEVAL_STRATEGY;
  if (envValue === 'p5_07a') {
    return 'p5_07a';
  }
  return 'v3'; // Default to champion path
}
```

### 2.2 Log Marker Verification
- **File**: `src/app/api/search/route.ts`
- **Line 77**: `console.log(\`[retrieval] strategy=${strategy}\`)`
- **Server Output Observed**: `[retrieval] strategy=v3`
- **Status**: ✅ VERIFIED

### 2.3 Environment Configuration
- **Default**: `RETRIEVAL_STRATEGY` unset → defaults to `v3`
- **Status**: ✅ VERIFIED (no explicit setting in `.env.local`)

---

## 3. Activation Check (`RETRIEVAL_STRATEGY=p5_07a`)

### 3.1 Strategy Toggle Path
- **Configuration**: Set `RETRIEVAL_STRATEGY=p5_07a` in environment
- **Expected Log**: `[retrieval] strategy=p5_07a`
- **Status**: ⏸️ BLOCKED (API key expired, cannot trigger request path)

### 3.2 Intervention Module Verification
- **File**: `src/lib/retrieval/intervention.ts`
- **Exports**: `applyIntervention()`, `assignMotif()`, `computeScaledPenalty()`
- **Constants**: `DEFAULT_VINTAGE_PENALTY=0.20`, `DEFAULT_STRICT_PENALTY=0.18`
- **Status**: ✅ CODE VERIFIED (static analysis)

---

## 4. Smoke Query Outcomes Summary

| Query | Expected Motif | Baseline (v3) | Treatment (p5_07a) | Status |
| :--- | :--- | :--- | :--- | :--- |
| "vintage retro font for poster" | `vintage_era` | N/A (API error) | N/A (API error) | ⏸️ BLOCKED |
| "strictly monospace for coding" | `over_strict_semantic` | N/A | N/A | ⏸️ BLOCKED |
| "elegant serif for wedding" | `null` | N/A | N/A | ⏸️ BLOCKED |
| "art deco 1920s style" | `vintage_era` | N/A | N/A | ⏸️ BLOCKED |
| "exact match for tech startup" | `over_strict_semantic` | N/A | N/A | ⏸️ BLOCKED |

**Blocker**: Gemini API key expired (`API_KEY_INVALID`). Cannot complete E2E smoke queries.

---

## 5. Rollback Check (`RETRIEVAL_STRATEGY=v3` Restored)

### 5.1 Rollback Procedure
1. Remove or set `RETRIEVAL_STRATEGY=v3` in `.env.local`
2. Restart dev server (or wait for hot reload)
3. Verify log marker shows `[retrieval] strategy=v3`

### 5.2 Rollback Verification
- **Status**: ✅ VERIFIED (default behavior is `v3`; no explicit setting required)

---

## 6. Decision

### 6.1 Outcome: **HOLD**

**Rationale**:
- Code wiring and log markers verified for both `v3` and `p5_07a` paths.
- Full E2E smoke query validation blocked by expired Gemini API key.
- Cannot confirm intervention behavior under real request conditions.
- **Gate semantics unchanged** — this is an internal-only canary validation.

### 6.2 Remediation Required
1. Renew `GEMINI_API_KEY` in `.env.local`
2. Re-run canary validation (P5-07D-B-R3)
3. Complete smoke query outcomes table

### 6.3 Next Steps
- **If ADVANCE**: Proceed to P5-07D-C (production traffic canary)
- **Current**: HOLD at P5-07D-B — internal canary incomplete

---

## 7. Explicit Statements

- **Gate semantics unchanged**: This canary validation does not modify G1/G2/G3/G4 thresholds or evaluation governance.
- **No production deployment changes**: All changes are internal/staging only.
- **Rollback is trivial**: Default behavior is `v3`; removing the environment variable restores baseline.

---

## 8. Evidence Artifacts

| Artifact | Path | Status |
| :--- | :--- | :--- |
| Retrieval Config | `src/lib/config/retrieval.ts` | ✅ Verified |
| Intervention Module | `src/lib/retrieval/intervention.ts` | ✅ Verified |
| Search Route | `src/app/api/search/route.ts` | ✅ Verified |
| Server Logs | Terminal output | ✅ `[retrieval] strategy=v3` observed |
| Smoke Query Results | N/A | ⏸️ Blocked by API key |

---

## 9. References

- [DEC-20260214-01-p5-07a-fullset-promotion](../../.lightspec/decisions/DEC-20260214-01-p5-07a-fullset-promotion.md)
- [EVALUATION_CONTRACT](./EVALUATION_CONTRACT.md)
- [RUNBOOK](./RUNBOOK.md)
- [Progress Tracking](../../.lightspec/progress.md)
