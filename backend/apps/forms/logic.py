def _blank(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, dict)):
        return len(value) == 0
    return False


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_condition(condition, response_data):
    key = condition.get("question_key") or condition.get("field")
    operator = condition.get("operator", "equals")
    expected = condition.get("value")
    actual = response_data.get(key)

    if operator == "equals":
        return actual == expected
    if operator == "not_equals":
        return actual != expected
    if operator == "contains":
        return expected in actual if isinstance(actual, (list, str)) else False
    if operator == "not_contains":
        return expected not in actual if isinstance(actual, (list, str)) else True
    if operator == "is_empty":
        return _blank(actual)
    if operator == "is_not_empty":
        return not _blank(actual)
    if operator == "is_selected":
        return isinstance(actual, list) and expected in actual
    if operator == "is_not_selected":
        return not (isinstance(actual, list) and expected in actual)

    actual_number = _number(actual)
    expected_number = _number(expected)
    if actual_number is None or expected_number is None:
        return False
    if operator == "greater_than":
        return actual_number > expected_number
    if operator == "less_than":
        return actual_number < expected_number
    if operator == "greater_than_or_equal":
        return actual_number >= expected_number
    if operator == "less_than_or_equal":
        return actual_number <= expected_number
    if operator == "between":
        bounds = expected if isinstance(expected, list) else []
        if len(bounds) != 2:
            return False
        low = _number(bounds[0])
        high = _number(bounds[1])
        return low is not None and high is not None and low <= actual_number <= high
    if operator == "not_between":
        bounds = expected if isinstance(expected, list) else []
        if len(bounds) != 2:
            return False
        low = _number(bounds[0])
        high = _number(bounds[1])
        return low is not None and high is not None and not (low <= actual_number <= high)
    return False


def evaluate_rule(rule, response_data):
    conditions = rule.get("conditions") or []
    if not conditions:
        return False
    results = [evaluate_condition(condition, response_data) for condition in conditions]
    return any(results) if rule.get("match") == "any" else all(results)


def evaluate_form_logic(logic, response_data):
    state = {"hidden_questions": set(), "hidden_sections": set(), "required_questions": set(), "warnings": []}
    rules = logic.get("rules") if isinstance(logic, dict) else []
    for rule in rules or []:
        if not evaluate_rule(rule, response_data or {}):
            continue
        target_key = rule.get("target_key") or rule.get("question_key") or rule.get("section_key")
        target_type = rule.get("target_type", "question")
        action = rule.get("action", "show")
        if not target_key:
            continue
        if action == "hide":
            if target_type == "section":
                state["hidden_sections"].add(target_key)
            else:
                state["hidden_questions"].add(target_key)
        elif action == "show":
            if target_type == "section":
                state["hidden_sections"].discard(target_key)
            else:
                state["hidden_questions"].discard(target_key)
        elif action == "require":
            state["required_questions"].add(target_key)
        elif action in {"warning", "critical_warning"}:
            state["warnings"].append({"target_key": target_key, "message": rule.get("message", "Review this response."), "severity": action})
    return state


def is_section_visible(section, logic_state):
    return section.get("key") not in logic_state["hidden_sections"]


def is_question_visible(question, logic_state):
    return question.get("key") not in logic_state["hidden_questions"]
