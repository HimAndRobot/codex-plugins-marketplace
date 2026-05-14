# Prompt Artifact Format

Prompt Generator writes prompt artifacts in the active project, not inside the plugin, unless the user explicitly chooses another root.

## Directories

```text
docs/prompts/current/
docs/prompts/drafts/<prompt-name>/
docs/prompts/reviews/<prompt-name>/<timestamp>/
```

## Current Prompt File

Use:

```text
docs/prompts/current/<prompt-name>.md
```

Every current prompt file starts with YAML frontmatter:

```yaml
---
name: prompt-name
model: gpt-5.5
status: draft/unreviewed
updated_at: 2026-05-13T22:30:00-03:00
source_skill: generate-or-update-prompt
---
```

Allowed `status` values:

- `draft/unreviewed`
- `reviewed`

## Draft Backup

Before replacing an existing current prompt, copy the old version to:

```text
docs/prompts/drafts/<prompt-name>/<timestamp>.md
```

## Review Round

Each review round writes:

```text
docs/prompts/reviews/<prompt-name>/<timestamp>/cases.json
docs/prompts/reviews/<prompt-name>/<timestamp>/metadata.json
docs/prompts/reviews/<prompt-name>/<timestamp>/recommendation.json
docs/prompts/reviews/<prompt-name>/<timestamp>/runs.json
docs/prompts/reviews/<prompt-name>/<timestamp>/variants.json
docs/prompts/reviews/<prompt-name>/<timestamp>/review.html
docs/prompts/reviews/<prompt-name>/<timestamp>/variants/variant-1.md
docs/prompts/reviews/<prompt-name>/<timestamp>/variants/variant-2.md
```

`metadata.json` records the prompt name, model, timestamp, reasoning effort when used, variant count, case count, optional baseline prompt, and diagnostics. `variants.json` contains the variant ids, prompt text, change summaries, and hypotheses. `recommendation.json` contains the recommended variant id, reason, and optional diagnostics. `cases.json` contains generated cases, and `runs.json` contains the execution results from `scripts/codex_prompt_review.py`.

Do not leave prompt artifacts loose outside this structure.
