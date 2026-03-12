<purpose>
Orchestrate the full HEP analysis from Wave 0 through Wave 7 with mandatory pause points at strategy approval and unblinding stage transitions.
</purpose>

<core_principle>
Wave-based execution with context isolation. Each wave loads fresh context from its artifact manifest. Gates enforce quality between transitions. Blinding enforcement prevents unauthorized data access at every stage.
</core_principle>

<required_reading>
Read STATE.md for current_wave and blinding_status before any operation.
Read analysis.yaml/analysis.json for analysis configuration.
</required_reading>

<process>

<step name="load_config" priority="first">
Load analysis state and configuration:

```bash
# Read current wave position and blinding status
CURRENT_WAVE=$(node "$HOME/.claude/get-analysis-done/bin/gad-tools.cjs" state get current_wave 2>/dev/null || echo "0")
BLINDING_STATUS=$(node "$HOME/.claude/get-analysis-done/bin/gad-tools.cjs" state get blinding_status 2>/dev/null || echo "blinded")
```

Parse `--from-wave N` argument if provided. Validate N >= CURRENT_WAVE.

If `--from-wave` is specified, set START_WAVE to N. Otherwise START_WAVE = CURRENT_WAVE.

Report:
```
## Analysis Execution

**Current wave:** {CURRENT_WAVE}
**Blinding status:** {BLINDING_STATUS}
**Starting from:** Wave {START_WAVE}
```
</step>

<step name="wave_0_strategy">
**Wave 0: Strategy Generation** (mandatory pause after)

If START_WAVE == 0:

1. Execute Wave 0 via run-wave workflow:
   ```
   Task(
     subagent_type="gad-lead-analyst",
     prompt="Execute /gad:run-wave 0 — generate the analysis strategy document."
   )
   ```

2. Evaluate gate-0-to-1 using evaluateGate from gate.cjs against the strategy output.

3. **MANDATORY PAUSE** — Physicist must approve the analysis strategy:
   ```
   ## Strategy Approval Required

   Wave 0 complete. The analysis strategy has been generated.

   **Review:** strategy/ANALYSIS_STRATEGY.md
   **Gate result:** gate-0-to-1 {pass/fail}

   Please review the strategy and respond:
   - "approved" to proceed to Wave 1
   - Feedback to revise the strategy
   ```

4. Wait for physicist approval. If feedback provided, re-run Wave 0 with adjustments.

5. After approval, increment current_wave to 1:
   ```bash
   node "$HOME/.claude/get-analysis-done/bin/gad-tools.cjs" state set current_wave 1
   ```
</step>

<step name="wave_loop">
**Waves 1-7: Sequential execution with gate evaluation**

For each wave N from max(START_WAVE, 1) to 7:

1. **Check unblinding transition requirement:**

   Waves that require blinding status changes:
   - Wave 6 (Unblinding): requires transition to `unblinded` status
   - Sideband access (Wave 3+): may require transition to `sidebands`
   - Partial unblinding (Wave 5+): may require transition to `partial_10pct`

   If the next wave requires a blinding transition that has not occurred:
   ```
   ## Unblinding Authorization Required

   **Wave {N}** requires blinding status: {required_status}
   **Current status:** {BLINDING_STATUS}

   This is a mandatory pause point. The physicist must authorize the blinding transition.

   Respond "authorize" to proceed with the transition, or "stop" to halt.
   ```
   Wait for physicist authorization before proceeding.

2. **Load wave manifest:**
   Read `wave-manifests/wave-{N}.yaml` to determine:
   - Which upstream artifacts to load into fresh context
   - Which specialist agents to spawn

3. **Execute the wave:**
   ```
   Task(
     subagent_type="gad-lead-analyst",
     prompt="Execute /gad:run-wave {N} — {wave_description from manifest}"
   )
   ```

4. **Evaluate gate (if not the last wave):**
   Load `gate-templates/gate-{N}-to-{N+1}.yaml` and evaluate using evaluateGate.

   If gate fails:
   - Run evaluateGateWithRetry with up to 2 retry attempts
   - Each retry spawns the relevant specialist to address the failing metric
   - If retries exhausted: generate GATE_FAILURE.md via generateGateFailureMd and PAUSE

   If gate passes:
   - Commit wave artifacts atomically via commitWaveArtifacts
   - Increment current_wave:
     ```bash
     node "$HOME/.claude/get-analysis-done/bin/gad-tools.cjs" state set current_wave {N+1}
     ```

5. **Check for mandatory pause (unblinding transitions):**
   If the NEXT wave (N+1) requires a blinding status that differs from current:
   - Wave 5->6 transition: requires `partial_10pct` -> `unblinded`
   - PAUSE and request physicist authorization (return to step 1 of next iteration)

6. **Proceed to next wave.**
</step>

<step name="final_summary">
**After Wave 7 completes:**

Generate the final analysis summary:
```
## Analysis Complete

All 8 waves executed successfully.

**Strategy:** strategy/ANALYSIS_STRATEGY.md
**Final results:** wave-7 outputs
**Blinding status:** {final_status}

### Wave Summary
| Wave | Name | Status | Key Output |
|------|------|--------|------------|
| 0 | Strategy Generation | Complete | ANALYSIS_STRATEGY.md |
| 1 | Foundation | Complete | Sample inventory, object definitions |
| 2 | Event Selection | Complete | Cutflow, BDT model, regions |
| 3 | Background Validation | Complete | Background yields, closure tests |
| 4 | Systematics and Stat Model | Complete | NP ranking, expected limit |
| 5 | Pre-Unblinding Review | Complete | Analysis note draft, checklist |
| 6 | Unblinding | Complete | Observed results, post-fit |
| 7 | Documentation | Complete | Final analysis note |
```
</step>

</process>

<pause_points>
Mandatory pauses (cannot be skipped):
1. After Wave 0: strategy approval
2. Before any blinding status transition: physicist authorization required
3. Gate failure after retries exhausted: GATE_FAILURE.md generated, physicist must decide next steps

Autonomous execution between pauses:
- Waves 1-5 run without pauses if no blinding transitions are needed and all gates pass
</pause_points>

<failure_handling>
- Gate failure with retries exhausted: generate GATE_FAILURE.md, pause for physicist
- Agent failure: report which specialist failed, offer re-run or skip
- Blinding violation: hard stop, non-recoverable — investigate before continuing
</failure_handling>
