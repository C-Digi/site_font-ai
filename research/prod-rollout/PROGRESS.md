# Migration Progress Tracking

## Week 1: Foundation (Feb 6 – Feb 12)

| Task | Status | Owner | Milestone |
| :--- | :---: | :--- | :--- |
| Initialize SSoT Documentation | 🟢 Done | Assistant | M1: Prep |
| Update `tasks-user.md` with Roadmap | 🟢 Done | Assistant | M1: Prep |
| Implement B2 Embedding Utility | ⚪ Todo | Assistant | M2: Code |
| Design/Setup Background Queue for JIT | ⚪ Todo | Assistant | M2: Code |
| Update Search API for B2 Queries | ⚪ Todo | Assistant | M2: Code |
| Local E2E Validation (Toy Set) | ⚪ Todo | Assistant | M3: Valid |

## Week 2: Migration & Launch (Feb 13 – Feb 20)

| Task | Status | Owner | Milestone |
| :--- | :---: | :--- | :--- |
| Production Database Backup | ⚪ Todo | Operator | M4: Prod |
| Batch Re-embedding (Full Corpus) | ⚪ Todo | Assistant | M4: Prod |
| Deployment to Production | ⚪ Todo | Operator | M5: Launch |
| Human Visual-Intent Validation | ⚪ Todo | Operator | M6: Audit |

---

## ✅ Acceptance Criteria

### Milestone 1: Prep
- [x] Documentation folder `research/prod-rollout/` created.
- [x] Runbook and Progress tracking initialized.
- [x] Roadmap clearly communicated in `tasks-user.md`.

### Milestone 2: Code
- [ ] `generateB2Embedding` function exists and handles both image + text.
- [ ] Search API uses B2 embeddings by default.
- [ ] JIT seeding is non-blocking (request finishes before embedding is saved).

### Milestone 3: Valid
- [ ] Recall@10 on benchmark set meets or exceeds prior research (>= 0.36).
- [ ] No regressions in font card rendering.

---

## 📝 Commit Cadence Expectations
- **Atomic Commits:** One feature/fix per commit.
- **Documentation:** Update `PROGRESS.md` and `DECISIONS.md` alongside code changes.
- **Messages:** Use conventional commits (e.g., `feat:`, `fix:`, `docs:`).
