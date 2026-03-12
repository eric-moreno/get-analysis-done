---
name: gad:run-analysis
description: Execute full HEP analysis from Wave 0 through Wave 7 with mandatory pause points
argument-hint: "[--from-wave N]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
---
<objective>
Execute the full analysis workflow from Wave 0 (strategy generation) through Wave 7 (documentation).

Mandatory pause points:
- After Wave 0: physicist must approve the analysis strategy before proceeding
- At each unblinding stage transition (sidebands, partial_10pct, unblinded): physicist must authorize

Waves 1-5 run autonomously between pause points. Each wave clears context and loads only upstream artifacts defined in its wave manifest.

**Flags:**
- `--from-wave N` — Resume analysis from wave N (skips completed waves). Validates N >= current_wave from STATE.md.
</objective>

<execution_context>
@~/.claude/get-analysis-done/workflows/run-analysis.md
</execution_context>

<context>
Analysis config: analysis.yaml or analysis.json in project root.
State: .planning/STATE.md (current_wave, blinding_status).
Gate templates: gate-templates/gate-N-to-N+1.yaml.
Wave manifests: wave-manifests/wave-N.yaml.

The run-analysis workflow orchestrates the full wave sequence. Each wave is executed via the run-wave workflow with fresh context. Gates are evaluated between waves using the gate evaluation engine (gate.cjs).
</context>

<process>
Execute the run-analysis workflow from @~/.claude/get-analysis-done/workflows/run-analysis.md end-to-end.
Respect all mandatory pause points. Do not skip gate evaluations.
</process>
