"""Federal field-ownership locking for health declaration form templates.

Federal-owned fields published on the national declaration template are locked:
States and facilities that derive the template may ADD fields but cannot delete,
hide, rename, weaken (make optional), or relabel a federal-locked field.

A question is federal-locked when its definition carries either
``field_owner == "federal"`` or ``locked is True``.
"""

from rest_framework.exceptions import ValidationError


def _iter_questions(schema):
    for section in (schema or {}).get("sections", []) or []:
        for question in section.get("questions", []) or []:
            yield question


def federal_locked_questions(schema):
    """Return {key: question} for every federal-locked question in a schema."""
    locked = {}
    for question in _iter_questions(schema):
        if question.get("field_owner") == "federal" or question.get("locked") is True:
            key = question.get("key") or question.get("id")
            if key:
                locked[key] = question
    return locked


def assert_federal_locks_preserved(source_schema, derived_schema):
    """Raise ValidationError if a derived schema weakens any federal-locked field.

    Checks that every federal-locked field from the source is still present, still
    required (if it was required), not hidden, and keeps the same label and type.
    """
    source_locked = federal_locked_questions(source_schema)
    if not source_locked:
        return
    derived = {}
    for question in _iter_questions(derived_schema):
        key = question.get("key") or question.get("id")
        if key:
            derived[key] = question

    violations = []
    for key, original in source_locked.items():
        current = derived.get(key)
        if current is None:
            violations.append(f"Federal field '{key}' cannot be removed.")
            continue
        if original.get("label") and current.get("label") != original.get("label"):
            violations.append(f"Federal field '{key}' cannot be renamed.")
        if original.get("type") and current.get("type") != original.get("type"):
            violations.append(f"Federal field '{key}' type cannot be changed.")
        if original.get("required") and not current.get("required"):
            violations.append(f"Federal field '{key}' cannot be made optional.")
        if current.get("hidden") is True:
            violations.append(f"Federal field '{key}' cannot be hidden.")
    if violations:
        raise ValidationError({"federal_fields": violations})
