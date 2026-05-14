# HimAndRobot Codex Plugins

Personal Codex plugin marketplace for HimAndRobot.

## Plugins

### PlanForge

PlanForge is a lightweight Superpowers-inspired planning and execution workflow for Codex.

Marketplace entry: `planforge`

## Structure

```text
.agents/plugins/marketplace.json
plugins/planforge/.codex-plugin/plugin.json
plugins/planforge/skills/
```

The marketplace is the source of truth for the included plugins. PlanForge lives inside `plugins/planforge` so marketplace installs use the same copy that is maintained here.
