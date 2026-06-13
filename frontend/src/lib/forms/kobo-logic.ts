export type KoboLogicCondition = {
  question_key: string;
  operator: string;
  value?: unknown;
};

export type KoboLogicRule = {
  target_type: "question" | "section";
  target_key: string;
  action: "show" | "hide" | "require" | "warning" | "critical_warning";
  match?: "all" | "any";
  conditions: KoboLogicCondition[];
  message?: string;
};

export type KoboLogic = {
  rules?: KoboLogicRule[];
};

export type KoboLogicState = {
  hiddenQuestions: Set<string>;
  hiddenSections: Set<string>;
  requiredQuestions: Set<string>;
  warnings: Array<{ target_key: string; message: string; severity: string }>;
};

function blank(value: unknown) {
  if (value === null || value === undefined) return true;
  if (typeof value === "string") return value.trim() === "";
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value as Record<string, unknown>).length === 0;
  return false;
}

function numberValue(value: unknown) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function evaluateCondition(condition: KoboLogicCondition, values: Record<string, unknown>) {
  const actual = values[condition.question_key];
  const expected = condition.value;
  switch (condition.operator) {
    case "equals": return actual === expected;
    case "not_equals": return actual !== expected;
    case "contains": return Array.isArray(actual) || typeof actual === "string" ? actual.includes(expected as never) : false;
    case "not_contains": return Array.isArray(actual) || typeof actual === "string" ? !actual.includes(expected as never) : true;
    case "is_empty": return blank(actual);
    case "is_not_empty": return !blank(actual);
    case "is_selected": return Array.isArray(actual) && actual.includes(expected);
    case "is_not_selected": return !(Array.isArray(actual) && actual.includes(expected));
  }
  const actualNumber = numberValue(actual);
  const expectedNumber = numberValue(expected);
  if (actualNumber === null || expectedNumber === null) return false;
  if (condition.operator === "greater_than") return actualNumber > expectedNumber;
  if (condition.operator === "less_than") return actualNumber < expectedNumber;
  if (condition.operator === "greater_than_or_equal") return actualNumber >= expectedNumber;
  if (condition.operator === "less_than_or_equal") return actualNumber <= expectedNumber;
  if (condition.operator === "between" || condition.operator === "not_between") {
    const bounds = Array.isArray(expected) ? expected : [];
    const low = numberValue(bounds[0]);
    const high = numberValue(bounds[1]);
    if (low === null || high === null) return false;
    const inside = low <= actualNumber && actualNumber <= high;
    return condition.operator === "between" ? inside : !inside;
  }
  return false;
}

export function evaluateKoboLogic(logic: KoboLogic | undefined, values: Record<string, unknown>): KoboLogicState {
  const state: KoboLogicState = { hiddenQuestions: new Set(), hiddenSections: new Set(), requiredQuestions: new Set(), warnings: [] };
  for (const rule of logic?.rules || []) {
    const results = (rule.conditions || []).map((condition) => evaluateCondition(condition, values));
    const matched = rule.match === "any" ? results.some(Boolean) : results.length > 0 && results.every(Boolean);
    if (!matched) continue;
    if (rule.action === "hide") {
      if (rule.target_type === "section") state.hiddenSections.add(rule.target_key);
      else state.hiddenQuestions.add(rule.target_key);
    } else if (rule.action === "show") {
      if (rule.target_type === "section") state.hiddenSections.delete(rule.target_key);
      else state.hiddenQuestions.delete(rule.target_key);
    } else if (rule.action === "require") {
      state.requiredQuestions.add(rule.target_key);
    } else if (rule.action === "warning" || rule.action === "critical_warning") {
      state.warnings.push({ target_key: rule.target_key, message: rule.message || "Review this response.", severity: rule.action });
    }
  }
  return state;
}
