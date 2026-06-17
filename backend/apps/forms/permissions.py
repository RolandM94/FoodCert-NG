from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole

ADMIN_ROLES = {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN}
CREATOR_ROLES = ADMIN_ROLES
ASSIGNER_ROLES = ADMIN_ROLES
REVIEWER_ROLES = ADMIN_ROLES
EXPORT_ROLES = ADMIN_ROLES | {UserRole.INSPECTOR}

FORM_PERMISSIONS = {
    "forms.template.view": ADMIN_ROLES | {UserRole.INSPECTOR},
    "forms.template.view_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.template.view_federal_shared": {UserRole.STATE_ADMIN},
    "forms.template.create": CREATOR_ROLES,
    "forms.template.create_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.template.create_state": {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN},
    "forms.template.update": CREATOR_ROLES,
    "forms.template.publish": CREATOR_ROLES,
    "forms.template.publish_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.template.share_to_states": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.template.mark_as_standard": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.template.adopt_federal": {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN},
    "forms.template.clone_federal": {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN},
    "forms.template.archive": CREATOR_ROLES,
    "forms.template.version": CREATOR_ROLES,
    "forms.assignment.view": ADMIN_ROLES | {UserRole.INSPECTOR},
    "forms.assignment.view_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.assignment.view_federal_assigned": {UserRole.STATE_ADMIN},
    "forms.assignment.create": ASSIGNER_ROLES,
    "forms.assignment.create_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.assignment.create_state": {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN},
    "forms.assignment.assign_to_states": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.assignment.assign_national_operational": {UserRole.SUPER_ADMIN},
    "forms.assignment.update": ASSIGNER_ROLES,
    "forms.assignment.cancel": ASSIGNER_ROLES,
    "forms.assignment.send_reminder": ASSIGNER_ROLES,
    "forms.response.view": ADMIN_ROLES | {UserRole.INSPECTOR, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.FOOD_HANDLER},
    "forms.response.view_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.response.view_state": {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN},
    "forms.response.view_cross_state_aggregate": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.response.view_sensitive_detail": {UserRole.SUPER_ADMIN},
    "forms.response.submit": {UserRole.INSPECTOR, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.FOOD_HANDLER, UserRole.DOCTOR, UserRole.LAB_STAFF} | ADMIN_ROLES,
    "forms.response.submit_federal_assigned": {UserRole.SUPER_ADMIN, UserRole.STATE_ADMIN},
    "forms.response.review": REVIEWER_ROLES,
    "forms.response.review_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.response.return": REVIEWER_ROLES,
    "forms.response.export": EXPORT_ROLES,
    "forms.report.view_federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.report.view_cross_state": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.offline.download": ADMIN_ROLES | {UserRole.INSPECTOR},
    "forms.offline.sync": ADMIN_ROLES | {UserRole.INSPECTOR},
    "forms.export.create": EXPORT_ROLES,
    "forms.export.federal": {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN},
    "forms.export.sensitive_detail": {UserRole.SUPER_ADMIN},
    "forms.export.download": EXPORT_ROLES,
}

SENSITIVITY_LEVELS = ("public", "internal", "confidential", "medical", "pii", "financial")

SENSITIVITY_VISIBLE_ROLES = {
    "public": set(UserRole),
    "internal": ADMIN_ROLES | {UserRole.INSPECTOR, UserRole.EMPLOYER, UserRole.FACILITY_ADMIN, UserRole.DOCTOR},
    "confidential": ADMIN_ROLES | {UserRole.INSPECTOR},
    "medical": ADMIN_ROLES | {UserRole.DOCTOR, UserRole.FACILITY_ADMIN},
    "pii": ADMIN_ROLES,
    "financial": ADMIN_ROLES,
}


def user_has_form_permission(user, permission_code: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, "role", None)
    allowed_roles = FORM_PERMISSIONS.get(permission_code)
    if allowed_roles is None:
        return False
    return role in allowed_roles


def user_can_view_sensitivity(user, sensitivity: str) -> bool:
    if not sensitivity or sensitivity == "public":
        return True
    role = getattr(user, "role", None)
    visible_roles = SENSITIVITY_VISIBLE_ROLES.get(sensitivity, set())
    return role in visible_roles


def filter_sensitive_fields(schema: dict, user) -> dict:
    if not schema or not schema.get("sections"):
        return schema
    filtered = {"sections": []}
    for section in schema.get("sections", []):
        filtered_section = {**section, "questions": []}
        for question in section.get("questions", []):
            sensitivity = question.get("sensitivity", "public")
            if user_can_view_sensitivity(user, sensitivity):
                if question.get("type") == "repeat_group":
                    visible_nested = []
                    for nested in question.get("questions", []) or []:
                        nested_sensitivity = nested.get("sensitivity", "public")
                        if user_can_view_sensitivity(user, nested_sensitivity):
                            visible_nested.append(nested)
                        else:
                            visible_nested.append({
                                "key": nested["key"],
                                "label": nested.get("label", ""),
                                "type": "hidden",
                                "sensitivity": nested_sensitivity,
                                "masked": True,
                            })
                    filtered_section["questions"].append({**question, "questions": visible_nested})
                else:
                    filtered_section["questions"].append(question)
            else:
                filtered_section["questions"].append({
                    "key": question["key"],
                    "label": question.get("label", ""),
                    "type": "hidden",
                    "sensitivity": sensitivity,
                    "masked": True,
                })
        filtered["sections"].append(filtered_section)
    return filtered


def filter_response_json_by_sensitivity(schema: dict, response_json: dict, user) -> dict:
    if not schema or not response_json:
        return response_json
    visible_keys = set()
    repeat_visible = {}
    for section in schema.get("sections", []):
        for question in section.get("questions", []):
            sensitivity = question.get("sensitivity", "public")
            if question.get("type") == "repeat_group" and user_can_view_sensitivity(user, sensitivity):
                visible_keys.add(question.get("key"))
                repeat_visible[question.get("key")] = {
                    nested.get("key")
                    for nested in question.get("questions", []) or []
                    if user_can_view_sensitivity(user, nested.get("sensitivity", "public"))
                }
            elif user_can_view_sensitivity(user, sensitivity):
                visible_keys.add(question.get("key"))
    filtered = {}
    for key, value in response_json.items():
        if key not in visible_keys:
            continue
        if key in repeat_visible and isinstance(value, list):
            allowed_nested = repeat_visible[key]
            filtered[key] = [
                {nested_key: nested_value for nested_key, nested_value in item.items() if nested_key in allowed_nested}
                for item in value
                if isinstance(item, dict)
            ]
        else:
            filtered[key] = value
    return filtered


def get_user_form_permissions(user) -> list:
    if not user or not user.is_authenticated:
        return []
    return [code for code, roles in FORM_PERMISSIONS.items() if user.role in roles]


class CanCreateTemplate(BasePermission):
    message = "You do not have permission to create form templates."

    def has_permission(self, request, view):
        return user_has_form_permission(request.user, "forms.template.create")


class CanPublishTemplate(BasePermission):
    message = "You do not have permission to publish form templates."

    def has_permission(self, request, view):
        return user_has_form_permission(request.user, "forms.template.publish")


class CanCreateAssignment(BasePermission):
    message = "You do not have permission to create form assignments."

    def has_permission(self, request, view):
        return user_has_form_permission(request.user, "forms.assignment.create")


class CanReviewResponse(BasePermission):
    message = "You do not have permission to review form responses."

    def has_permission(self, request, view):
        return user_has_form_permission(request.user, "forms.response.review")


class CanExportResponses(BasePermission):
    message = "You do not have permission to export form responses."

    def has_permission(self, request, view):
        return user_has_form_permission(request.user, "forms.export.create")
