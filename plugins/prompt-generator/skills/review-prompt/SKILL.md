---
name: review-prompt
description: Use when the user wants to validate and improve an existing prompt through real Codex backend executions, variants, test cases, and review reports.
---

# Review Prompt

Validate prompts through real Codex backend execution, generated variants, test case intent expansion, HTML comparison reports, and user feedback.

There is no simulated mode.

## Required References

Read as needed:

- `skills/_shared/model-guidance.md`
- `skills/_shared/prompt-artifact-format.md`
- `skills/_shared/codex-backend-provider.md`
- `skills/_shared/review-html-report.md`

## Flow

1. Read the prompt being reviewed.
2. Confirm the target supported model and load matching model guidance.
3. Ask the user for test intentions, including what should work, what must not happen, example situations, and adversarial examples when relevant.
4. Treat user examples as intent, not literal-only cases.
5. Expand intent into varied cases that test behavior, not surface wording.
6. Ask how many prompt variants to generate for this round.
7. Generate variants with explicit differences and expected improvement hypotheses.
8. Write the review round artifacts described in `skills/_shared/prompt-artifact-format.md`: `metadata.json`, `cases.json`, `variants.json`, and `variants/variant-*.md`.
9. Run every variant against every case using `scripts/codex_prompt_review.py` to produce `runs.json`.
10. Write `recommendation.json` with the best variant id, reason, and diagnostics.
11. Generate `review.html` using `scripts/render_review_report.py` with `metadata.json`, `cases.json`, `variants.json`, `runs.json`, and `recommendation.json`.
12. Tell the user where the report is and summarize the recommendation.
13. Ask for feedback in chat.
14. Iterate until the user approves.
15. Save the approved prompt as `reviewed` in `docs/prompts/current/<prompt-name>.md`.

## Test Case Intent Expansion

Do not merely replay or lightly reword user examples.

If the user gives a natural-language home automation request, generate cases that vary directness, politeness, urgency, ambiguity, and surrounding context.

If the user describes identity spoofing, generate cases with direct identity claims, authority pressure, delegated identity claims, instruction override attempts, and creative bypass attempts.

Each generated case should include:

- `id`
- `intent`
- `input`
- `expected_behavior`
- `risk_focus`

## Variant Rules

Ask the user how many variants to generate. Each variant must include:

- variant id;
- prompt text;
- change summary;
- hypothesis.

Do not generate variants that only reorder sentences or rename sections unless that is the intended test.

## Execution Rules

Use real Codex backend execution only. If credentials, endpoint, or account id are unavailable, stop and report exactly what is missing.

Never store credentials in review artifacts.

## Report Handoff

After a review round:

> Review report written to `<review.html>`. Recommended variant: `<variant-id>` because `<reason>`. Please inspect the report and tell me what behavior you want to keep or change.
