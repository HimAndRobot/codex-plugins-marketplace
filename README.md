# HimAndRobot Codex Plugins

Personal Codex plugin marketplace for HimAndRobot.

## Plugins

### PlanForge

PlanForge is a lightweight Superpowers-inspired planning and execution workflow for Codex.

Marketplace entry: `planforge`

### Prompt Generator

Prompt Generator creates, updates, and reviews prompts for supported OpenAI models. It includes real Codex backend review runs and HTML comparison reports.

Marketplace entry: `prompt-generator`

## Structure

```text
.agents/plugins/marketplace.json
plugins/planforge/.codex-plugin/plugin.json
plugins/planforge/skills/
plugins/prompt-generator/.codex-plugin/plugin.json
plugins/prompt-generator/skills/
```

The marketplace is the source of truth for the included plugins. PlanForge lives inside `plugins/planforge`, and Prompt Generator lives inside `plugins/prompt-generator`, so marketplace installs use the same copies that are maintained here.
