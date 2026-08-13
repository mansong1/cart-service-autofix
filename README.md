# cart-service

A deliberately small pricing service used to demo the **Harness CI Auto-Fix worker agent**.

The pricing rules live in `src/cart.py`; the agreed business rules are encoded as
unit tests in `tests/test_cart.py`. The tests are the contract.

## Running locally

```bash
pip install -r requirements.txt
python -m pytest tests/ -q      # unit tests
python -m ruff check .          # lint
```

## The demo

`main` intentionally ships a broken `src/cart.py`. Four real bugs are seeded:

| # | Bug | Symptom |
|---|-----|---------|
| 1 | `VAT_RATE` set to `0.175` instead of `0.20` | every VAT and total assertion is low |
| 2 | `apply_discount` treats `percent_off` as a fraction, not a percent | a 20% coupon takes 20x off |
| 3 | `apply_discount` lost its upper clamp at 100 | coupons above 100% invert the total |
| 4 | `shipping_cost` uses `>` instead of `>=` | shipping charged *at* the free threshold |

Plus an unused `import os` that fails lint.

## Two pipelines

The demo deliberately uses **two separate pipelines** in project `Agent_DLC`, because
that is how this works in real life: your build pipeline has no idea an agent exists.

### 1. `cart_service_ci` — the build that breaks

An ordinary CI pipeline. Installs deps, runs ruff, runs pytest. It fails on `main`
with 8 failed / 8 passed and 2 lint errors. There is **no auto-fix wiring in it at
all** — no failure-log staging, no exit-code massaging, nothing added for the agent's
benefit. You could point the auto-fix pipeline at any failing build.

### 2. `CI_Auto_Fix` — the repair

Takes the failed execution as input (or finds the most recent failure itself):

1. **Snapshot Baseline** — checksums `tests/` and the build config so tampering can
   be proven either way. Deliberately does *not* run the suite.
2. **Auto Fix Agent** — `ci_autofix_agent` calls `harness_diagnose` and
   `harness_get resource_type=execution_log` over the Harness MCP server to pull the
   *upstream* run's real console output, diagnoses each root cause, and patches
   `src/cart.py`.
3. **Verify Fix** — independent clean run of lint + tests over the agent's patch,
   plus a checksum tamper check against the baseline.
4. **Raise Fix PR** — pushes the patch to `ci-autofix/build-<n>` and opens a PR on
   GitHub, using the agent's own fix report as the PR body.
5. **Fix Gate** — fails the run unless the patch verified *and* a PR exists.

## Guardrails

- The agent may edit `src/**` only. It may never edit `tests/**`, `pyproject.toml`,
  `requirements.txt`, or any pipeline YAML — the fix has to be a real fix, not a
  rewritten assertion. Verification re-checks this with checksums.
- The agent's MCP access is read-only by instruction: it reads build state, and does
  not re-run pipelines, edit entities, commit, or open PRs.
- Commit and PR mechanics are a plain script, not an agent — so the write-scoped
  GitHub token never enters an LLM's context, and only paths under `src/` are staged.
- Nothing is ever auto-merged. Human review is always required.
