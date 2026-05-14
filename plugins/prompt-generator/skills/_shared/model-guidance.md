# Model Guidance

Use this reference before generating, updating, or reviewing prompts. The supported model set is closed for the first release.

Official source: https://developers.openai.com/api/docs/guides/prompt-guidance

## Supported Models

- `gpt-5.5`
- `gpt-5.4`
- `gpt-5.3-codex`
- `gpt-5.2`

## Shared Rules

- Ask for the target model before making prompt decisions when the model is not already explicit.
- If the requested model is unsupported, stop and ask the user to choose one supported model: `gpt-5.5`, `gpt-5.4`, `gpt-5.3-codex`, or `gpt-5.2`.
- Convert model guidance into prompt decisions: role, goal, success criteria, constraints, output shape, reasoning effort, tool rules, validation rules, context handling, and stopping conditions.
- Do not use a fixed questionnaire. Ask only questions required by the prompt type, user goal, risk level, and selected model guidance.
- Preserve the user's intended behavior over generic prompt-engineering templates.
- Keep prompts as short as the task allows, then add explicit blocks only when they control measured behavior.
- Define what "done" means for the model: required outputs, evidence boundaries, validation steps, blockers, fallback behavior, and when to stop.
- Treat `ALWAYS`, `NEVER`, `must`, and `only` as invariants. For judgment calls, write decision rules instead of absolute commands.
- For prompt updates, change one behavior surface at a time when possible: model, reasoning effort, prompt structure, output format, tool policy, or personality.
- For prompt reviews, check whether the prompt is operational: it should guide generation, execution, validation, and failure handling rather than merely describe intent.

## GPT-5.5

### Use When

Use `gpt-5.5` guidance when the user targets GPT-5.5 or wants the newest general OpenAI behavior for a production assistant, agent, support workflow, research workflow, coding workflow, or customer-facing experience.

### Operational Guidance

- Prefer outcome-first prompts. Define the desired result, success criteria, constraints, available evidence, final answer shape, and stop rules before adding process detail.
- Reduce inherited process-heavy prompt stacks. Keep legacy instructions only when they protect a real invariant, fix a known regression, or define an integration contract.
- Use shorter personality and collaboration blocks. Personality should steer tone; collaboration style should steer when to ask, assume, proceed, validate, or surface risk.
- For conversational products, include only tone and collaboration traits that change behavior: warmth, directness, formality, initiative, assumption policy, uncertainty handling, and correction behavior.
- Add a short preamble rule for long-running or tool-heavy workflows so the user sees a concise first update before tools or extended work.
- For Responses workflows that replay assistant output items, preserve assistant `phase` values. Use `commentary` for progress updates and `final_answer` for the completed answer.
- Set `text.verbosity` or equivalent prompt-level length guidance explicitly when output size matters. Use concise defaults unless the task needs traceable reasoning, comparison, or a stable artifact.
- Specify formatting by product need: paragraphs for normal conversation, bullets or tables for comparison, JSON or strict schema for machine-read output, and hard length limits for customer-facing artifacts.
- For grounded answers, define what claims require evidence, what counts as enough evidence, how citations should appear, and what to do when evidence is missing.
- Add retrieval budgets for search-heavy prompts: when to make the first lookup, when to make another lookup, when to stop, and when absence of evidence is not enough to answer "no."
- For creative drafting, separate source-backed facts from creative wording. Forbid invented names, metrics, dates, roadmap claims, capabilities, or customer outcomes.
- For coding, artifact, visual, and planning prompts, include validation rules: targeted tests, type/lint/build checks, render inspection, smoke tests, or an explicit explanation when validation cannot run.
- Re-evaluate `low` and `medium` reasoning effort before escalating. Prefer stronger prompt contracts, evidence rules, and validation loops before increasing reasoning effort.
- Use the suggested structure for complex prompts: role, personality, goal, success criteria, constraints, output, and stop rules. Keep each section short.

### Prompt Review Checks

- Does the prompt define the outcome instead of over-prescribing every step?
- Are success criteria, output shape, evidence rules, validation, blockers, and stop rules explicit?
- Are personality and collaboration instructions short, behavior-changing, and subordinate to the task?
- Does the prompt avoid unnecessary absolute rules while preserving true invariants?
- Is reasoning effort justified by task complexity rather than used as the first fix?
- For tool-heavy workflows, are preambles, phase preservation, assistant-item replay, retrieval budgets, and validation rules covered when relevant?
- For creative or customer-facing output, does the prompt distinguish source-backed facts from permissible style or narrative work?

## GPT-5.4

### Use When

Use `gpt-5.4` guidance when the user targets GPT-5.4 for mainline production assistants, long-running agents, multi-tool workflows, evidence-heavy synthesis, long-context analysis, spreadsheet or finance workflows, or structured customer-facing writing.

### Operational Guidance

- Use GPT-5.4 for workflows that benefit from reliable multi-step execution, stronger style control, explicit output contracts, and long-context coherence.
- Start with the smallest prompt that passes evals. Add explicit blocks only to address a known failure mode such as tool routing, dependency ordering, citation drift, incomplete batches, or unsafe action.
- Create a compact output contract. State exact sections, order, length limits, required format, and what content belongs in progress updates versus final output.
- Add verbosity controls that prefer concise, information-dense writing without removing required evidence, reasoning, or completion checks.
- Define follow-through behavior: proceed when intent is clear and action is reversible, ask permission for irreversible or external-side-effect actions, and ask only when a missing choice materially changes the outcome.
- Make instruction priority explicit. User instructions override default style and initiative, newer user instructions override conflicting older ones, and safety, honesty, privacy, and permission constraints remain fixed.
- For tool routing, describe each tool boundary clearly and require prerequisite checks before action. If the task depends on a lookup, file read, memory retrieval, or prior result, resolve it first.
- Prompt for parallel tool calls only when retrieval or lookup steps are independent. Require synthesis after parallel retrieval before taking additional action.
- Add a completeness contract for long-horizon work: track required deliverables internally, cover all requested items, mark blocked items with missing data, and confirm coverage before finalizing.
- Add empty-result recovery for search and retrieval. If results are empty, partial, or suspiciously narrow, try alternate wording, broader filters, prerequisite lookup, or alternate sources before concluding.
- Add a verification loop before final answers and high-impact actions. Check requirement coverage, grounding, requested schema or style, safety, and reversibility.
- For active agents, include a pre-flight/action/post-flight frame: state intended action briefly, execute through the tool, then report outcome and validation.
- For vision or computer-use prompts, specify image detail when precision matters. Use high or original detail for OCR, localization, dense screens, or click accuracy; use low only when speed and cost dominate.
- For research prompts, lock claims to retrieved evidence, define citation format, require contradiction resolution, and prevent unsupported references.
- Use compaction for long-running Responses sessions after major milestones. Treat compacted items as opaque and keep prompts functionally identical after compaction.
- Separate persistent personality from per-response writing controls. Define persona, channel, emotional register, formatting, and length without letting personality override required JSON, schemas, or task output.
- Treat reasoning effort as a last-mile knob. Start with `none` for execution-heavy transforms, triage, and extraction; start with `low` or `medium` when ambiguity, nuanced interpretation, or recovery behavior matters; reserve `high` or `xhigh` for eval-proven long reasoning gains.
- Before increasing reasoning effort, add or improve completeness, verification, and tool-persistence rules.

### Prompt Review Checks

- Does the prompt include a clear output contract and concise verbosity controls?
- Does it define when to proceed, ask, stop, retry, or mark work blocked?
- Are dependencies, tool boundaries, parallelism rules, and prerequisite checks explicit?
- Is completion defined for lists, batches, paginated results, long-running workflows, and partial retrieval?
- Does it include evidence, citation, and contradiction-handling rules where factual claims matter?
- Are verification steps present before final answers or high-impact actions?
- Is reasoning effort selected from task shape and eval results rather than defaulting high?
- If the workflow is long-running, does it account for compaction and phase preservation where relevant?

## GPT-5.3 Codex

### Use When

Use `gpt-5.3-codex` guidance for Codex or agentic coding prompts: code generation, code review, debugging, test repair, repository edits, migration work, tool-driven implementation, or long-running software tasks.

### Operational Guidance

- Design prompts for efficient agentic coding. Give the task, ownership boundaries, constraints, allowed tools, verification expectations, and completion criteria.
- Avoid requiring upfront plans or lengthy preambles for simple coding tasks. Ask for visible updates only when they orient the user during tool-heavy or long-running work.
- For preambles, require short human-readable progress and intent updates, not logs of every tool call. Avoid repetitive canned phrasing and prefer concrete status.
- Preserve `phase` metadata in Responses integrations. `commentary` marks preamble or progress messages; `final_answer` marks closeout. Dropping phase data can degrade long-running behavior.
- Keep the model moving on reversible coding work when the request is clear. Ask only when missing information materially affects architecture, behavior, safety, destructive actions, or external side effects.
- Specify codebase discovery rules: inspect relevant files, prefer existing patterns and APIs, avoid unrelated refactors, and respect user or teammate changes.
- Use strong ownership boundaries. Tell the model exactly which files or areas it may edit and which areas are off-limits.
- Prefer exact patch tools for file edits when available. For shell work, define safe command behavior, non-destructive defaults, and approval points for destructive or privileged actions.
- Define tool response truncation expectations for large outputs: preserve useful beginning and ending context, mark middle truncation clearly, and avoid treating truncated output as complete evidence.
- Manage context for multi-hour or long-thread tasks. Summarize durable facts, compact after major milestones when supported, and keep prompt behavior stable after compaction.
- For delegated or parallel work, define independent task boundaries, merge expectations, review checkpoints, and how conflicts are handled.
- Require verification proportional to risk: targeted tests for changed behavior, lint/type/build checks where available, smoke tests for integrations, and explicit reporting when validation cannot run.
- For code review prompts, prioritize bugs, regressions, security risks, missing tests, and concrete file/line evidence before summaries or style notes.
- For debugging prompts, require reproduction, evidence gathering, hypothesis testing, minimal fix, regression test or targeted validation, and a clear final account.
- Define completion criteria: requested files changed, tests or checks run, residual risks reported, no unrelated files modified, and no future tasks executed.

### Prompt Review Checks

- Does the prompt control autonomy without slowing obvious reversible coding work?
- Are file ownership, off-limits areas, destructive actions, approvals, and teammate changes handled?
- Are tool use, patching, shell commands, context truncation, compaction, and phase metadata covered when relevant?
- Does the prompt require evidence-based debugging or code review rather than generic advice?
- Are validation commands or fallback checks explicit and proportional to risk?
- Does the final response contract require changed files, verification results, blockers, and residual concerns?
- Does the prompt avoid long upfront planning and repetitive progress narration unless the task needs it?

## GPT-5.2

### Use When

Use `gpt-5.2` guidance when the user targets GPT-5.2 for reliable production agents, structured output, document analysis, extraction, coding, finance workflows, long-context work, or migration from earlier GPT-4 or GPT-5 models.

### Operational Guidance

- Use GPT-5.2 when the prompt needs stronger instruction following, clean formatting, disciplined execution, and explicit steerability over tone, verbosity, and output shape.
- Add clear length and shape constraints. For normal answers, define sentence or bullet limits; for complex work, define short sections such as What changed, Where, Risks, Next steps, and Open questions.
- Prevent scope drift explicitly. For frontend, UX, design, and coding prompts, require the model to implement exactly the requested behavior, follow existing design systems, avoid extra features, and choose the simplest valid interpretation when ambiguous.
- For long-context prompts, require a lightweight internal outline, restatement of user constraints, and claim anchoring to specific sections, documents, pages, clauses, or records.
- For ambiguity, ask up to a small number of precise clarifying questions or present a few labeled interpretations with assumptions. Do not fabricate exact figures, external references, line numbers, or unsupported claims.
- Add high-risk self-checks for legal, financial, compliance, safety, or production-impact contexts. Require the model to review assumptions, unsupported specifics, and overly strong language before finalizing.
- Use compaction for long-running, tool-heavy workflows when context pressure grows. Compact after major milestones, not every turn; treat compacted items as opaque; keep prompts functionally identical when resuming.
- For agentic workflows, keep user updates short and event-driven. Send updates at phase changes or when discoveries change the plan, not for routine tool calls.
- For tool use, describe each tool in one or two sentences, prefer tools over memory for fresh or user-specific data, parallelize independent reads, and summarize changes plus validation after writes.
- For extraction, PDF, Office, and table workflows, provide a schema or JSON shape, distinguish required and optional fields, specify null behavior for missing data, and require an extraction completeness pass.
- For multi-document extraction, serialize per-document results separately and include stable identifiers such as filename, contract title, page range, or record ID.
- For research prompts, define the research bar: when to search, whether to follow second-order leads, how to resolve contradictions, citation expectations, and when further research is unlikely to change the answer.
- For migration to GPT-5.2, switch the model first and keep the prompt functionally identical before editing. Pin `reasoning_effort`, run evals, then make targeted prompt changes only for measured regressions.
- Preserve prior latency and reasoning profile during migration. Use `none` for GPT-4o or GPT-4.1 style fast migrations; preserve existing GPT-5.1 effort unless evals show a need to adjust.

### Prompt Review Checks

- Does the prompt state exact verbosity, sections, schema, or output format where consistency matters?
- Does it prevent extra features, uncontrolled styling, or broader scope than the user requested?
- For long-context work, does it force re-grounding in the source and anchor claims to concrete locations?
- Does it handle ambiguity without hallucinating specifics or over-claiming uncertain facts?
- Are high-risk contexts protected by a final assumption and grounding self-check?
- Are tool rules concise, parallelism rules safe, and write/update validation explicit?
- For extraction workflows, are schema, missing-field behavior, per-document serialization, and completeness checks defined?
- For migrations, did the review separate model change, reasoning-effort pinning, eval baseline, and prompt edits into separate steps?
