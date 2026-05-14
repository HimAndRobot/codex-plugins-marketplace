---
name: generate-or-update-prompt
description: Use when the user wants to create a new prompt or update an existing prompt for a supported OpenAI model using bundled model guidance.
---

# Generate Or Update Prompt

Create or update prompts using supported OpenAI model guidance.

This skill does not validate prompt behavior through execution. Use `review-prompt` for real testing and approval.

## Required References

Read as needed:

- `skills/_shared/model-guidance.md`
- `skills/_shared/prompt-artifact-format.md`

## Supported Models

- `gpt-5.5`
- `gpt-5.4`
- `gpt-5.3-codex`
- `gpt-5.2`

If the user asks for another model, stop and ask them to choose one of the supported models.

## Flow

1. Determine whether this is a new prompt or an update to an existing prompt.
2. Ask for the target model before making prompt decisions if the model is not already clear.
3. Load the matching model guidance.
4. For updates, read the existing prompt and summarize current intent, structure, main instructions, conflicts, and requested behavior change.
5. Ask one question at a time only for information that matters to this prompt type, user goal, and selected model guidance.
6. Do not use a fixed assistant-style questionnaire. Derive questions from the prompt type.
7. Generate or update the prompt.
8. Save artifacts using `prompt-artifact-format.md`.
9. Mark generated prompts as `draft/unreviewed`.
10. Offer to start `review-prompt`.

## Question Strategy

Examples:

- Extraction prompt: ask about schema, required fields, invalid input, ambiguity, and fallback behavior.
- Agentic coding prompt: ask about autonomy, tools, verification, context limits, and completion criteria.
- Classifier prompt: ask about labels, boundaries, examples, ambiguous cases, and output format.
- Conversational assistant prompt: ask about collaboration style, stopping conditions, uncertainty, and tone only when those affect behavior.

Do not ask about an end user, tone, personality, or audience unless those are relevant to the requested prompt.

## Output Rules

The prompt file must include:

- YAML frontmatter from the artifact format.
- A clear prompt title.
- Target model.
- The prompt body.
- Notes on what changed when updating an existing prompt.
- Status `draft/unreviewed`.

## Handoff

After saving:

> Prompt saved as draft/unreviewed at `<path>`. This has not been validated through execution yet. Do you want to start `review-prompt` now?
