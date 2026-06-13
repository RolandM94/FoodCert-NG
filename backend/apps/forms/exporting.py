def flatten_response_for_export(schema, response_data):
    """Flatten a response into stable export columns, including repeat-group items."""
    flattened = {}
    data = response_data or {}
    sections = schema.get("sections") if isinstance(schema, dict) else []

    for section in sections or []:
        for question in section.get("questions", []) or []:
            _flatten_question(flattened, question, data.get(question.get("key")), question.get("key", ""))

    return flattened


def response_export_row(form_response):
    schema = form_response.template_version.schema_json if form_response.template_version_id else {}
    flattened = flatten_response_for_export(schema, form_response.response_json)
    base = {
        "response_id": str(form_response.id),
        "assignment_id": str(form_response.assignment_id),
        "assignment_title": form_response.assignment.title if form_response.assignment_id else "",
        "template_id": str(form_response.template_id),
        "template_title": form_response.template.title if form_response.template_id else "",
        "respondent_id": str(form_response.respondent_user_id),
        "respondent_name": form_response.respondent_user.get_full_name() if form_response.respondent_user_id else "",
        "respondent_email": form_response.respondent_user.email if form_response.respondent_user_id else "",
        "status": form_response.status,
        "sync_status": form_response.sync_status,
        "risk_rating": form_response.risk_rating,
        "score": form_response.score,
        "context_type": form_response.context_type,
        "context_id": form_response.context_id,
        "started_at": form_response.started_at.isoformat() if form_response.started_at else "",
        "last_saved_at": form_response.last_saved_at.isoformat() if form_response.last_saved_at else "",
        "submitted_at": form_response.submitted_at.isoformat() if form_response.submitted_at else "",
        "reviewed_at": form_response.reviewed_at.isoformat() if form_response.reviewed_at else "",
    }
    return {**base, **flattened}


def attachment_export_row(attachment):
    return {
        "attachment_id": str(attachment.id),
        "response_id": str(attachment.response_id),
        "question_key": attachment.question_key,
        "repeat_group_key": attachment.repeat_group_key,
        "repeat_item_id": attachment.repeat_item_id,
        "file_name": attachment.file_name,
        "file_type": attachment.file_type,
        "file_size": attachment.file_size,
        "mime_type": attachment.mime_type,
        "file_url": attachment.file_url,
        "sync_status": attachment.sync_status,
        "captured_at": attachment.captured_at.isoformat() if attachment.captured_at else "",
        "gps_latitude": str(attachment.gps_latitude) if attachment.gps_latitude is not None else "",
        "gps_longitude": str(attachment.gps_longitude) if attachment.gps_longitude is not None else "",
        "created_at": attachment.created_at.isoformat() if attachment.created_at else "",
    }


def _flatten_question(flattened, question, value, prefix):
    question_type = question.get("type") or question.get("question_type")
    key = prefix or question.get("key", "")
    if not key:
        return

    if question_type == "repeat_group":
        items = value if isinstance(value, list) else []
        flattened[f"{key}.__count"] = len(items)
        nested_questions = question.get("questions", []) or []
        for index, item in enumerate(items, start=1):
            item_data = item if isinstance(item, dict) else {}
            for nested in nested_questions:
                nested_key = nested.get("key", "")
                if nested_key:
                    _flatten_question(flattened, nested, item_data.get(nested_key), f"{key}[{index}].{nested_key}")
        return

    flattened[key] = value
