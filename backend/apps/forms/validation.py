import re
from urllib.parse import urlparse

from apps.forms.logic import evaluate_form_logic, is_question_visible, is_section_visible


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9][0-9\s().-]{6,}$")


def _blank(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, dict)):
        return len(value) == 0
    return False


def _number(value):
    if value == "" or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _valid_url(value):
    parsed = urlparse(str(value))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _file_extension(name):
    if not name or "." not in str(name):
        return ""
    return str(name).rsplit(".", 1)[-1].lower()


def _media_metadata(item):
    if isinstance(item, dict):
        return {
            "file_name": item.get("file_name") or item.get("name") or "",
            "mime_type": item.get("mime_type") or item.get("type") or "",
            "file_size": item.get("file_size") or item.get("size"),
        }
    return {"file_name": str(item), "mime_type": "", "file_size": None}


def _csv_rule(value):
    if isinstance(value, str):
        return [item.strip().lower().lstrip(".") for item in value.split(",") if item.strip()]
    if isinstance(value, (list, tuple)):
        return [str(item).strip().lower().lstrip(".") for item in value if str(item).strip()]
    return []


def _question_error(question, message):
    return {
        "key": question.get("key", ""),
        "label": question.get("label", question.get("key", "Question")),
        "message": question.get("validation_message") or message,
    }


def validate_form_response(schema, response_data, logic=None):
    errors = []
    data = response_data or {}
    sections = schema.get("sections") if isinstance(schema, dict) else []
    logic_state = evaluate_form_logic(logic or {}, data)

    for section in sections or []:
        if not is_section_visible(section, logic_state):
            continue
        for question in section.get("questions", []) or []:
            if not is_question_visible(question, logic_state):
                continue
            active_question = {**question, "required": question.get("required") or question.get("key") in logic_state["required_questions"]}
            errors.extend(validate_question(active_question, data.get(question.get("key")), data))

    return errors


def validate_question(question, value, response_data):
    errors = []
    question_type = question.get("type") or question.get("question_type")
    key = question.get("key", "")
    rules = question.get("validation") or question.get("validation_rules") or {}

    if question_type in {"instruction", "section_header", "hidden", "calculated_field", "calculated_number"}:
        return errors

    if question.get("required") and _blank(value):
        errors.append(_question_error(question, "This field is required."))
        return errors

    if _blank(value):
        return errors

    if question_type == "repeat_group":
        items = value if isinstance(value, list) else []
        min_repeats = rules.get("min_repeats")
        max_repeats = rules.get("max_repeats")
        if question.get("required") and not items:
            errors.append(_question_error(question, "At least one item is required."))
        if min_repeats is not None and len(items) < int(min_repeats):
            errors.append(_question_error(question, f"At least {min_repeats} item(s) are required."))
        if max_repeats is not None and len(items) > int(max_repeats):
            errors.append(_question_error(question, f"No more than {max_repeats} item(s) are allowed."))
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(_question_error(question, f"Repeat item {index + 1} is invalid."))
                continue
            for nested in question.get("questions", []) or []:
                for nested_error in validate_question(nested, item.get(nested.get("key")), response_data):
                    nested_error["key"] = f"{key}.{index}.{nested_error['key']}"
                    nested_error["label"] = f"{question.get('label', key)} item {index + 1}: {nested_error['label']}"
                    errors.append(nested_error)
        return errors

    if question_type == "email" and not EMAIL_RE.match(str(value)):
        errors.append(_question_error(question, "Enter a valid email address."))
    if question_type == "phone" and not PHONE_RE.match(str(value)):
        errors.append(_question_error(question, "Enter a valid phone number."))
    if question_type == "url" and not _valid_url(value):
        errors.append(_question_error(question, "Enter a valid URL."))

    if question_type in {"number", "decimal", "currency", "percentage", "compliance_score"}:
        numeric_value = _number(value)
        if numeric_value is None:
            errors.append(_question_error(question, "Enter a valid number."))
        else:
            if rules.get("min_value") is not None and numeric_value < float(rules["min_value"]):
                errors.append(_question_error(question, f"Value must be at least {rules['min_value']}."))
            if rules.get("max_value") is not None and numeric_value > float(rules["max_value"]):
                errors.append(_question_error(question, f"Value must be no more than {rules['max_value']}."))

    if isinstance(value, str):
        if rules.get("min_length") is not None and len(value) < int(rules["min_length"]):
            errors.append(_question_error(question, f"Enter at least {rules['min_length']} characters."))
        if rules.get("max_length") is not None and len(value) > int(rules["max_length"]):
            errors.append(_question_error(question, f"Enter no more than {rules['max_length']} characters."))
        if rules.get("regex") and not re.search(str(rules["regex"]), value):
            errors.append(_question_error(question, "Value does not match the required format."))

    if question_type in {"single_choice", "dropdown", "likert", "rating", "risk_rating"}:
        options = question.get("options") or (["Low", "Medium", "High", "Critical"] if question_type == "risk_rating" else [])
        if options and value not in options:
            errors.append(_question_error(question, "Select one of the allowed options."))
    if question_type == "multiple_choice":
        selected = value if isinstance(value, list) else []
        options = question.get("options") or []
        if not isinstance(value, list):
            errors.append(_question_error(question, "Select one or more options."))
        if options and any(item not in options for item in selected):
            errors.append(_question_error(question, "One or more selected options are not allowed."))
        if rules.get("min_selected") is not None and len(selected) < int(rules["min_selected"]):
            errors.append(_question_error(question, f"Select at least {rules['min_selected']} option(s)."))
        if rules.get("max_selected") is not None and len(selected) > int(rules["max_selected"]):
            errors.append(_question_error(question, f"Select no more than {rules['max_selected']} option(s)."))

    if question_type == "gps":
        if not isinstance(value, dict) or _blank(value.get("latitude")) or _blank(value.get("longitude")):
            errors.append(_question_error(question, "Capture latitude and longitude."))
    if question_type == "signature" and _blank(value):
        errors.append(_question_error(question, "Signature is required."))
    if question_type in {"image_upload", "file_upload", "video_upload", "audio_upload"}:
        files = value if isinstance(value, list) else []
        if question.get("required") and not files:
            errors.append(_question_error(question, "Upload at least one file."))
        if rules.get("min_files") is not None and len(files) < int(rules["min_files"]):
            errors.append(_question_error(question, f"Upload at least {rules['min_files']} file(s)."))
        if rules.get("max_files") is not None and len(files) > int(rules["max_files"]):
            errors.append(_question_error(question, f"Upload no more than {rules['max_files']} file(s)."))
        allowed_extensions = _csv_rule(rules.get("allowed_file_types") or rules.get("allowed_extensions"))
        allowed_mime_types = _csv_rule(rules.get("allowed_mime_types"))
        max_file_size = rules.get("max_file_size")
        if rules.get("max_file_size_mb") is not None:
            max_file_size = int(float(rules["max_file_size_mb"]) * 1024 * 1024)
        for item in files:
            media = _media_metadata(item)
            extension = _file_extension(media["file_name"])
            mime_type = str(media["mime_type"] or "").lower()
            if allowed_extensions and extension and extension not in allowed_extensions:
                errors.append(_question_error(question, f"{media['file_name']} is not an allowed file type."))
            if allowed_mime_types and mime_type and mime_type not in allowed_mime_types:
                errors.append(_question_error(question, f"{media['file_name']} is not an allowed media type."))
            if max_file_size is not None and media["file_size"] is not None and int(media["file_size"]) > int(max_file_size):
                errors.append(_question_error(question, f"{media['file_name']} exceeds the maximum file size."))

    return errors
