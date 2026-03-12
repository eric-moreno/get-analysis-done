/**
 * Gate — Quality gate evaluation engine
 *
 * Evaluates YAML-defined quality gate criteria against JSON source data.
 * Supports threshold comparison, file existence checks, and cross-check
 * agreement validation. Produces structured pass/fail reports with
 * per-metric diagnostics.
 *
 * Node.js 16 compatible: no structuredClone, no Array.at().
 */

const fs = require('fs');
const path = require('path');
const { safeReadFile } = require('./core.cjs');
const { extractFrontmatter, reconstructFrontmatter } = require('./frontmatter.cjs');

// ─── YAML Parser (constrained gate schema only) ─────────────────────────────

/**
 * Parse a gate YAML file content. Only handles the gate-specific schema:
 *   gate: "..."
 *   description: "..."
 *   criteria:
 *     - metric: ...
 *       operator: ...
 *       ...
 *   on_failure:
 *     max_retries: N
 *     ...
 *
 * NOT a general-purpose YAML parser. Max 3 levels of nesting.
 */
function parseGateYaml(content) {
  const lines = content.split('\n');
  const result = {
    gate: null,
    description: null,
    criteria: [],
    on_failure: {},
  };

  let currentSection = null; // 'criteria' | 'on_failure' | null
  let currentItem = null;    // current criteria item being built

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trimEnd();

    // Skip empty lines and comments
    if (trimmed === '' || trimmed.startsWith('#')) continue;

    // Top-level keys (no indentation)
    if (!line.startsWith(' ') && !line.startsWith('\t')) {
      // Flush any pending criteria item
      if (currentItem && currentSection === 'criteria') {
        result.criteria.push(currentItem);
        currentItem = null;
      }

      if (trimmed.startsWith('gate:')) {
        result.gate = parseYamlValue(trimmed.slice(5));
        currentSection = null;
      } else if (trimmed.startsWith('description:')) {
        result.description = parseYamlValue(trimmed.slice(12));
        currentSection = null;
      } else if (trimmed.startsWith('criteria:')) {
        currentSection = 'criteria';
      } else if (trimmed.startsWith('on_failure:')) {
        currentSection = 'on_failure';
      }
      continue;
    }

    // Indented content
    if (currentSection === 'criteria') {
      const stripped = trimmed.replace(/^\s+/, '');

      // New criteria item (starts with "- ")
      if (stripped.startsWith('- ')) {
        if (currentItem) {
          result.criteria.push(currentItem);
        }
        currentItem = {};
        const kvPart = stripped.slice(2);
        const kv = parseKeyValue(kvPart);
        if (kv) {
          currentItem[kv.key] = kv.value;
        }
      } else if (currentItem) {
        // Continuation of current item
        const kv = parseKeyValue(stripped);
        if (kv) {
          currentItem[kv.key] = kv.value;
        }
      }
    } else if (currentSection === 'on_failure') {
      const stripped = trimmed.replace(/^\s+/, '');
      const kv = parseKeyValue(stripped);
      if (kv) {
        result.on_failure[kv.key] = kv.value;
      }
    }
  }

  // Flush last criteria item
  if (currentItem && currentSection === 'criteria') {
    result.criteria.push(currentItem);
  }

  return result;
}

/**
 * Parse a simple "key: value" string.
 */
function parseKeyValue(str) {
  const colonIdx = str.indexOf(':');
  if (colonIdx < 0) return null;
  const key = str.slice(0, colonIdx).trim();
  const rawValue = str.slice(colonIdx + 1).trim();
  return { key, value: parseYamlValue(rawValue) };
}

/**
 * Parse a YAML scalar value: strip quotes, convert numbers/booleans.
 */
function parseYamlValue(raw) {
  const trimmed = (raw || '').trim();
  if (trimmed === '') return null;

  // Quoted string — strip quotes
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) ||
      (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1);
  }

  // Boolean
  if (trimmed === 'true') return true;
  if (trimmed === 'false') return false;

  // Number
  const num = Number(trimmed);
  if (!isNaN(num) && trimmed !== '') return num;

  return trimmed;
}

// ─── Data Access ─────────────────────────────────────────────────────────────

/**
 * Load and parse a JSON source file.
 */
function loadSourceData(cwd, sourcePath) {
  const fullPath = path.join(cwd, sourcePath);
  const content = safeReadFile(fullPath);
  if (content === null) {
    return { data: null, error: 'Source file not found: ' + sourcePath };
  }
  try {
    return { data: JSON.parse(content), error: null };
  } catch (e) {
    return { data: null, error: 'Failed to parse JSON: ' + sourcePath + ' — ' + e.message };
  }
}

/**
 * Traverse a dot-separated field path in a nested object.
 * e.g., getNestedField({a: {b: 3}}, "a.b") -> 3
 */
function getNestedField(obj, fieldPath) {
  if (!obj || !fieldPath) return undefined;
  const parts = fieldPath.split('.');
  let current = obj;
  for (let i = 0; i < parts.length; i++) {
    if (current === null || current === undefined) return undefined;
    current = current[parts[i]];
  }
  return current;
}

// ─── Operators ───────────────────────────────────────────────────────────────

const OPERATORS = {
  '>=': function(a, b) { return a >= b; },
  '<=': function(a, b) { return a <= b; },
  '>':  function(a, b) { return a > b; },
  '<':  function(a, b) { return a < b; },
  '==': function(a, b) { return String(a) === String(b); },
  '!=': function(a, b) { return String(a) !== String(b); },
};

// ─── Gate Evaluation ─────────────────────────────────────────────────────────

/**
 * Evaluate a gate YAML file against source data.
 *
 * @param {string} cwd - Working directory
 * @param {string} gateYamlPath - Relative path to gate YAML file
 * @returns {{ passed: boolean, gate: string, results: Array, failed: Array, error?: string }}
 */
function evaluateGate(cwd, gateYamlPath) {
  const fullPath = path.join(cwd, gateYamlPath);
  const yamlContent = safeReadFile(fullPath);

  if (yamlContent === null) {
    return {
      passed: false,
      gate: null,
      results: [],
      failed: [],
      error: 'Gate file not found: ' + gateYamlPath,
    };
  }

  const gateDef = parseGateYaml(yamlContent);
  const results = [];
  const failed = [];

  for (let i = 0; i < gateDef.criteria.length; i++) {
    const criterion = gateDef.criteria[i];
    const metricResult = evaluateCriterion(cwd, criterion);
    results.push(metricResult);
    if (!metricResult.passed) {
      failed.push(metricResult);
    }
  }

  return {
    passed: failed.length === 0,
    gate: gateDef.gate,
    results: results,
    failed: failed,
  };
}

/**
 * Evaluate a single criterion.
 */
function evaluateCriterion(cwd, criterion) {
  const type = criterion.type || 'threshold';

  if (type === 'file_exists') {
    return evaluateFileExists(cwd, criterion);
  }

  if (type === 'cross_check') {
    return evaluateCrossCheck(cwd, criterion);
  }

  // Default: threshold comparison
  return evaluateThreshold(cwd, criterion);
}

function evaluateThreshold(cwd, criterion) {
  const { metric, operator, threshold, source, field } = criterion;
  const { data, error: loadError } = loadSourceData(cwd, source);

  if (data === null) {
    return {
      metric: metric,
      passed: false,
      actual: null,
      threshold: threshold,
      operator: operator,
      error: loadError,
    };
  }

  const actual = getNestedField(data, field);

  if (actual === undefined) {
    return {
      metric: metric,
      passed: false,
      actual: undefined,
      threshold: threshold,
      operator: operator,
      error: 'Field not found: ' + field,
    };
  }

  const compareFn = OPERATORS[operator];
  if (!compareFn) {
    return {
      metric: metric,
      passed: false,
      actual: actual,
      threshold: threshold,
      operator: operator,
      error: 'Unknown operator: ' + operator,
    };
  }

  const passed = compareFn(actual, threshold);
  return {
    metric: metric,
    passed: passed,
    actual: actual,
    threshold: threshold,
    operator: operator,
  };
}

function evaluateFileExists(cwd, criterion) {
  const { metric } = criterion;
  const filePath = criterion.path;
  const fullPath = path.join(cwd, filePath);
  const exists = fs.existsSync(fullPath);

  return {
    metric: metric,
    passed: exists,
    actual: exists ? 'exists' : 'missing',
    threshold: 'file must exist',
    type: 'file_exists',
  };
}

function evaluateCrossCheck(cwd, criterion) {
  const { metric, source_a, field_a, source_b, field_b, tolerance } = criterion;

  const resA = loadSourceData(cwd, source_a);
  const resB = loadSourceData(cwd, source_b);

  if (resA.data === null) {
    return { metric: metric, passed: false, error: resA.error, type: 'cross_check' };
  }
  if (resB.data === null) {
    return { metric: metric, passed: false, error: resB.error, type: 'cross_check' };
  }

  const valueA = getNestedField(resA.data, field_a);
  const valueB = getNestedField(resB.data, field_b);

  if (valueA === undefined || valueB === undefined) {
    return {
      metric: metric,
      passed: false,
      actual: { a: valueA, b: valueB },
      error: 'One or both fields not found',
      type: 'cross_check',
    };
  }

  const diff = Math.abs(valueA - valueB);
  const tol = tolerance || 0.01;
  const passed = diff <= tol;

  return {
    metric: metric,
    passed: passed,
    actual: { a: valueA, b: valueB, diff: diff },
    threshold: 'agreement within ' + tol,
    type: 'cross_check',
  };
}

// ─── State Integration Helpers ───────────────────────────────────────────────

/**
 * Read gate_retries_remaining from STATE.md frontmatter.
 * Returns null if STATE.md doesn't exist or field is missing.
 */
function readGateRetriesFromState(cwd) {
  var statePath = path.join(cwd, '.planning', 'STATE.md');
  var content = safeReadFile(statePath);
  if (content === null) return null;
  var fm = extractFrontmatter(content);
  var val = fm.gate_retries_remaining;
  if (val === undefined || val === null) return null;
  var parsed = parseInt(val, 10);
  return isNaN(parsed) ? null : parsed;
}

/**
 * Write gate_retries_remaining into STATE.md frontmatter.
 * If the field doesn't exist yet, it is added.
 * No-op if STATE.md doesn't exist (graceful fallback).
 */
function writeGateRetriesToState(cwd, value) {
  var statePath = path.join(cwd, '.planning', 'STATE.md');
  var content = safeReadFile(statePath);
  if (content === null) return;

  var fm = extractFrontmatter(content);
  fm.gate_retries_remaining = value;

  // Reconstruct frontmatter and splice back
  var yamlStr = reconstructFrontmatter(fm);
  var body = content.replace(/^---\n[\s\S]*?\n---\n*/, '');
  var newContent = '---\n' + yamlStr + '\n---\n\n' + body;
  fs.writeFileSync(statePath, newContent, 'utf-8');
}

// ─── Retry Logic ─────────────────────────────────────────────────────────────

/**
 * Evaluate a gate with retry logic and state-based retry tracking.
 *
 * When STATE.md exists, gate_retries_remaining is used to track retry budget
 * across process restarts (resumable retries). The field is decremented BEFORE
 * each retry callback so interrupted retries persist their consumed budget.
 *
 * When STATE.md is absent, falls back to stateless YAML-based max_retries.
 *
 * @param {string} cwd
 * @param {string} gateYamlPath
 * @param {Function} retryCallback - Called with (failedResult, attemptNumber)
 * @returns {Promise<Object>} Final gate result
 */
async function evaluateGateWithRetry(cwd, gateYamlPath, retryCallback) {
  // Read gate YAML to get max_retries
  var fullPath = path.join(cwd, gateYamlPath);
  var yamlContent = safeReadFile(fullPath);
  if (yamlContent === null) {
    return {
      passed: false,
      gate: null,
      results: [],
      failed: [],
      error: 'Gate file not found: ' + gateYamlPath,
    };
  }

  var gateDef = parseGateYaml(yamlContent);
  var maxRetries = (gateDef.on_failure && gateDef.on_failure.max_retries) || 2;

  // Determine if state-based tracking is available
  var statePath = path.join(cwd, '.planning', 'STATE.md');
  var hasState = safeReadFile(statePath) !== null;

  // Initialize or read gate_retries_remaining from STATE.md
  var retryBudget = maxRetries;
  if (hasState) {
    var stateRetries = readGateRetriesFromState(cwd);
    if (stateRetries === null || stateRetries > maxRetries) {
      // Missing or stale — initialize to max_retries
      writeGateRetriesToState(cwd, maxRetries);
      retryBudget = maxRetries;
    } else {
      retryBudget = stateRetries;
    }
  }

  // First evaluation
  var result = evaluateGate(cwd, gateYamlPath);
  if (result.passed) {
    // Success: reset gate_retries_remaining to max_retries
    if (hasState) {
      writeGateRetriesToState(cwd, maxRetries);
    }
    return result;
  }

  // Retry loop using state-tracked budget
  for (var attempt = 1; attempt <= retryBudget; attempt++) {
    // Decrement BEFORE callback (persist consumed budget for resumability)
    if (hasState) {
      writeGateRetriesToState(cwd, retryBudget - attempt);
    }
    await retryCallback(result, attempt);
    result = evaluateGate(cwd, gateYamlPath);
    if (result.passed) {
      // Success: reset gate_retries_remaining to max_retries
      if (hasState) {
        writeGateRetriesToState(cwd, maxRetries);
      }
      return result;
    }
  }

  // All retries exhausted
  result.retries_exhausted = true;
  return result;
}

// ─── Diagnosis ───────────────────────────────────────────────────────────────

/**
 * Generate a structured diagnosis for a failed metric result.
 */
function diagnoseFailure(failedResult) {
  const { metric, operator, threshold, actual } = failedResult;

  // Determine likely cause based on metric name patterns
  let likely_cause = 'Metric did not meet the required threshold';
  let suggested_fix = 'Review the analysis step that produces this metric';

  if (metric && metric.includes('efficiency')) {
    likely_cause = 'Selection cuts may be too tight, reducing signal acceptance';
    suggested_fix = 'Loosen selection criteria or review cut optimization. Check if signal MC matches data kinematics.';
  } else if (metric && metric.includes('rejection')) {
    likely_cause = 'Background rejection insufficient — discriminant not powerful enough';
    suggested_fix = 'Add discriminating variables to BDT/MVA, retrain with more features, or tighten working point.';
  } else if (metric && metric.includes('chi') || (metric && metric.includes('closure'))) {
    likely_cause = 'Closure test or chi-squared indicates mismodeling';
    suggested_fix = 'Check MC normalization, review shape systematic uncertainties, validate control regions.';
  } else if (metric && metric.includes('pull')) {
    likely_cause = 'Nuisance parameter pull exceeds expected range — possible over-constraint or mismodeling';
    suggested_fix = 'Review systematic uncertainty definitions, check for correlations, validate constraint terms.';
  } else if (metric && metric.includes('crosscheck') || (metric && metric.includes('agreement'))) {
    likely_cause = 'Cross-check result disagrees with main analysis beyond tolerance';
    suggested_fix = 'Compare analysis configurations, check for bugs in cross-check implementation, review shared inputs.';
  }

  return {
    metric: metric,
    expected: operator ? (operator + ' ' + threshold) : String(threshold),
    actual: actual,
    likely_cause: likely_cause,
    suggested_fix: suggested_fix,
  };
}

// ─── Report Formatting ──────────────────────────────────────────────────────

/**
 * Format a gate evaluation result as a markdown report.
 */
function formatGateReport(gateResult) {
  const lines = [];
  lines.push('# Gate Report: ' + (gateResult.gate || 'Unknown'));
  lines.push('');
  lines.push('**Status:** ' + (gateResult.passed ? 'PASSED' : 'FAILED'));
  lines.push('');
  lines.push('## Metrics');
  lines.push('');
  lines.push('| Metric | Status | Actual | Threshold |');
  lines.push('|--------|--------|--------|-----------|');

  for (let i = 0; i < gateResult.results.length; i++) {
    var r = gateResult.results[i];
    var status = r.passed ? 'PASS' : 'FAIL';
    var actual = r.actual !== undefined ? String(r.actual) : 'N/A';
    var threshold = r.threshold !== undefined ? String(r.threshold) : 'N/A';
    if (r.operator) {
      threshold = r.operator + ' ' + threshold;
    }
    lines.push('| ' + r.metric + ' | ' + status + ' | ' + actual + ' | ' + threshold + ' |');
  }

  if (gateResult.failed && gateResult.failed.length > 0) {
    lines.push('');
    lines.push('## Failed Metrics');
    lines.push('');
    for (let j = 0; j < gateResult.failed.length; j++) {
      var f = gateResult.failed[j];
      var diag = diagnoseFailure(f);
      lines.push('### ' + f.metric);
      lines.push('- **Expected:** ' + diag.expected);
      lines.push('- **Actual:** ' + diag.actual);
      lines.push('- **Likely cause:** ' + diag.likely_cause);
      lines.push('- **Suggested fix:** ' + diag.suggested_fix);
      lines.push('');
    }
  }

  return lines.join('\n');
}

/**
 * Generate a GATE_FAILURE.md report from a failed gate result and retry history.
 */
function generateGateFailureMd(gateResult, retryHistory) {
  const lines = [];
  lines.push('# Gate Failure Report');
  lines.push('');
  lines.push('**Gate:** ' + (gateResult.gate || 'Unknown'));
  lines.push('**Date:** ' + new Date().toISOString().split('T')[0]);
  lines.push('**Status:** ESCALATED (max retries exhausted)');
  lines.push('');
  lines.push('## Failing Metrics');
  lines.push('');

  var failedMetrics = gateResult.failed || [];
  for (let i = 0; i < failedMetrics.length; i++) {
    var f = failedMetrics[i];
    lines.push('- **Metric:** ' + f.metric);
    lines.push('  - **Expected:** ' + (f.operator ? f.operator + ' ' : '') + f.threshold);
    lines.push('  - **Actual:** ' + f.actual);
    lines.push('');
  }

  lines.push('## Retry History');
  lines.push('');

  if (retryHistory && retryHistory.length > 0) {
    for (let j = 0; j < retryHistory.length; j++) {
      var entry = retryHistory[j];
      lines.push('### Attempt ' + (j + 1));
      lines.push('- **Diagnosis:** ' + (entry.diagnosis || 'N/A'));
      lines.push('- **Fix attempted:** ' + (entry.fix_attempted || 'N/A'));
      lines.push('- **Result:** ' + (entry.result || 'Still failing'));
      lines.push('');
    }
  } else {
    lines.push('No retry history available.');
    lines.push('');
  }

  lines.push('## Suggested Next Steps');
  lines.push('');

  for (let k = 0; k < failedMetrics.length; k++) {
    var diag = diagnoseFailure(failedMetrics[k]);
    lines.push('- **' + diag.metric + ':** ' + diag.suggested_fix);
  }

  return lines.join('\n');
}

// ─── Exports ─────────────────────────────────────────────────────────────────

module.exports = {
  parseGateYaml,
  evaluateGate,
  evaluateGateWithRetry,
  diagnoseFailure,
  formatGateReport,
  generateGateFailureMd,
  getNestedField,
  loadSourceData,
  OPERATORS,
};
