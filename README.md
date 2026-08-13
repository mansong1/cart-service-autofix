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

The `CI_Auto_Fix` pipeline in project `Agent_DLC`:

1. **Build & Test** — installs deps, runs ruff and pytest. Fails on `main`.
2. **Auto Fix** — the `ci_autofix_agent` worker agent reads the failing output,
   diagnoses each root cause, patches `src/cart.py`, and re-runs the suite until green.
3. **Verify** — an independent clean run of lint + tests over the agent's patch.
4. **Open PR** — the fix is pushed to a branch and raised as a pull request for human review.

The agent is scoped to `src/**` only. It may never edit `tests/**` — the fix has to
be a real fix, not a rewritten assertion.
