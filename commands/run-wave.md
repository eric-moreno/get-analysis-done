---
name: gad:run-wave
description: Execute a single analysis wave, produce WAVE_REPORT.md, and commit artifacts
argument-hint: "<wave-number>"
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
Execute a single analysis wave N (0-7). Load the wave manifest for context, spawn the appropriate specialist agents, collect their outputs, generate WAVE_REPORT.md, and commit all wave artifacts atomically.

After completion, the physicist can review the wave report at their own pace and resume with `/gad:run-wave N+1`.

**Arguments:**
- `wave-number` (required): Integer 0-7 specifying which wave to execute.
</objective>

<execution_context>
@~/.claude/get-analysis-done/workflows/run-wave.md
</execution_context>

<context>
Wave manifest: wave-manifests/wave-N.yaml (defines artifacts to load and agents to spawn).
State: .planning/STATE.md (current_wave, blinding_status).
Gate templates: gate-templates/gate-N-to-N+1.yaml (evaluated after wave completes).

Each wave starts with fresh context. Only artifacts listed in the wave manifest's load_artifacts section are loaded. No stale state bleeds between waves.
</context>

<process>
Execute the run-wave workflow from @~/.claude/get-analysis-done/workflows/run-wave.md end-to-end.
Validate wave number, load manifest, spawn agents, collect outputs, generate WAVE_REPORT.md, commit artifacts.
</process>
