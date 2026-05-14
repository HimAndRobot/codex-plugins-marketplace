# Review HTML Report

The review report is a static local HTML artifact for navigation and comparison. The user gives feedback in chat after inspecting it.

## Required Sections

- Review metadata: prompt name, timestamp, model, reasoning effort, number of variants, number of cases.
- Recommendation summary: best variant and why.
- Variant browser: prompt text for each variant.
- Case browser: test intent, generated case text, and expected behavior notes.
- Results matrix: each variant against each case.
- Output viewer: raw model output for selected run.
- Diff view: differences between baseline prompt and each variant.
- Diagnostics: observed strengths, failures, regressions, and concerns.

## Interaction

The report may use inline JavaScript for tabs, filters, and expand/collapse. It must not require a server.

## Safety

Do not include credentials or auth file contents.
