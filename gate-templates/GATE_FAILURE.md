# Gate Failure Report

**Gate:** {gate_name}
**Date:** {date}
**Status:** ESCALATED (max retries exhausted)

## Failing Metrics

- **Metric:** {metric}
  - **Expected:** {operator} {threshold}
  - **Actual:** {actual_value}

## Retry History

### Attempt 1
- **Diagnosis:** {diagnosis_1}
- **Fix attempted:** {fix_1}
- **Result:** {result_1}

### Attempt 2
- **Diagnosis:** {diagnosis_2}
- **Fix attempted:** {fix_2}
- **Result:** {result_2}

## Suggested Next Steps

- Review the failing metric and its upstream dependencies
- Check if the issue is in data, configuration, or analysis logic
- Consider relaxing thresholds if physics justification supports it
- Escalate to analysis team for manual review if automated fixes exhausted
