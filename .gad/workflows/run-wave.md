<purpose>
Execute a single analysis wave N: load its artifact manifest for context, spawn specialist agents, collect outputs, generate WAVE_REPORT.md, and commit all artifacts atomically.
</purpose>

<core_principle>
Each wave starts with fresh context. The wave manifest defines exactly which upstream artifacts to load — nothing more. This prevents stale state from bleeding between waves and keeps each wave's context budget focused.
</core_principle>

<required_reading>
Read STATE.md for current_wave and blinding_status.
Read wave-manifests/wave-N.yaml for this wave's artifact manifest.
</required_reading>

<process>

<step name="validate" priority="first">
Validate wave number and state:

```bash
# Parse wave number from arguments
WAVE_N=$ARGUMENTS

# Validate wave number
if [[ -z "$WAVE_N" ]] || [[ "$WAVE_N" -lt 0 ]] || [[ "$WAVE_N" -gt 7 ]]; then
  echo "ERROR: Wave number must be an integer 0-7. Got: $WAVE_N"
  exit 1
fi

# Read current wave from state
CURRENT_WAVE=$(node "$HOME/.claude/get-analysis-done/bin/gad-tools.cjs" state get current_wave 2>/dev/null || echo "0")

# Validate wave N >= current_wave
if [[ "$WAVE_N" -lt "$CURRENT_WAVE" ]]; then
  echo "ERROR: Cannot execute wave $WAVE_N — current_wave is $CURRENT_WAVE. Waves cannot go backwards."
  exit 1
fi
```
</step>

<step name="load_manifest">
Load the wave manifest for context clearing and agent determination:

Read `wave-manifests/wave-${WAVE_N}.yaml` and parse:
- `wave`: integer wave number
- `description`: human-readable wave name
- `load_artifacts`: list of `{ path, reason }` entries — these are the ONLY upstream artifacts to load
- `clear_context`: always true — context is cleared before loading artifacts
- `agents`: list of specialist agents to spawn

Report:
```
## Wave {N}: {description}

**Artifacts to load:** {count} upstream artifacts
**Agents to spawn:** {agent list}
**Context cleared:** Yes (fresh context per wave)
```
</step>

<step name="load_artifacts">
Clear context and load only the artifacts specified in the manifest:

For each entry in `load_artifacts`:
1. Read the file at `path`
2. Verify it exists (warn if missing but continue — upstream wave may not have produced it yet)
3. Include in the agent spawning context

This is the context isolation mechanism. Agents see ONLY:
- The analysis config
- The artifacts listed in this wave's manifest
- No other upstream state
</step>

<step name="spawn_agents">
Spawn specialist agents based on the wave manifest's `agents` list.

**Wave-to-agent mapping:**

| Wave | Agents | Purpose |
|------|--------|---------|
| 0 | lead-analyst | Strategy generation |
| 1 | theory-scout, data-explorer, detector-specialist, lead-analyst | Foundation: literature, samples, objects, review |
| 2 | signal-lead, ml-specialist, background-estimator | Event selection: cutflow, BDT, regions |
| 3 | background-estimator, cross-checker | Background validation: yields, closure tests |
| 4 | systematic-source-evaluator, systematics-fitter, lead-analyst | Systematics and stat model |
| 5 | note-writer, cross-checker, lead-analyst | Pre-unblinding review and checklist |
| 6 | systematics-fitter, cross-checker | Unblinding: observed results |
| 7 | note-writer | Final documentation |

For each agent in the wave's agent list:
```
Task(
  subagent_type="gad-{agent-name}",
  prompt="
    <objective>
    Execute your role in Wave {N}: {description}.
    </objective>

    <context>
    {loaded artifacts from step load_artifacts}
    </context>

    <output>
    Produce your wave artifacts and report completion status.
    </output>
  "
)
```

Agents execute with fresh context. The orchestrator collects their outputs.
</step>

<step name="collect_outputs">
Collect all agent outputs:
- List of artifacts produced (files created/modified)
- Agent completion status (complete/failed)
- Key findings from each agent

If any agent fails:
- Report which agent failed and why
- Offer to re-run the failing agent or continue with partial results
</step>

<step name="generate_wave_report">
Generate WAVE_REPORT.md with the following structure:

```markdown
# Wave {N} Report: {wave_name}

**Date:** {ISO date}
**Status:** {complete/partial/failed}
**Blinding Status:** {current blinding status}

## Agents Executed

| Agent | Status | Duration | Key Output |
|-------|--------|----------|------------|
| {agent} | {complete/failed} | {time} | {primary artifact} |

## Artifacts Produced

| File | Description | Agent |
|------|-------------|-------|
| {path} | {what it contains} | {which agent produced it} |

## Key Findings

{Summary of important findings from agent outputs. For each agent, 2-3 key points.}

## Gate Status

**Gate:** gate-{N}-to-{N+1}.yaml
**Result:** {pass/fail/pending}
**Details:** {per-metric results if evaluated}
```

Write WAVE_REPORT.md to the wave output directory.
</step>

<step name="commit_artifacts">
Commit all wave artifacts atomically using commitWaveArtifacts from wave.cjs:

```bash
# Collect all artifact paths produced by agents
ARTIFACT_PATHS=({list of artifact file paths})

# Add WAVE_REPORT.md to the artifact list
ARTIFACT_PATHS+=("wave-{N}/WAVE_REPORT.md")

# Atomic commit
node -e "
  const { commitWaveArtifacts } = require('./get-analysis-done/bin/lib/wave.cjs');
  const result = commitWaveArtifacts(process.cwd(), ${WAVE_N}, ${JSON.stringify(ARTIFACT_PATHS)});
  console.log(JSON.stringify(result));
"
```

Report:
```
## Wave {N} Complete

**Artifacts committed:** {count} files
**Commit:** {hash}
**WAVE_REPORT:** wave-{N}/WAVE_REPORT.md
```
</step>

</process>

<context_clearing>
Context clearing is the fundamental mechanism for wave isolation:
1. Each wave starts with a fresh agent context (via Task tool spawning)
2. The wave manifest's load_artifacts list is the ONLY source of upstream context
3. This prevents context pollution — Wave 3 does not see Wave 1 intermediate files unless explicitly listed
4. The manifest acts as a contract: "this wave needs exactly these inputs"
</context_clearing>

<failure_handling>
- Agent spawn failure: retry once, then report
- Missing upstream artifact: warn and continue (may produce degraded results)
- All agents fail: report wave failure, do not commit, do not advance current_wave
- Partial failure: commit successful agent outputs, report failures in WAVE_REPORT.md
</failure_handling>
