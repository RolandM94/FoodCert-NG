from apps.accounts.models import UserRole
from apps.assessments.models import AssessmentFormScope


def can_manage_assessment_form_template(user, template) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == UserRole.SUPER_ADMIN:
        return True
    if template.scope == AssessmentFormScope.NATIONAL:
        return user.role == UserRole.FEDERAL_ADMIN
    if template.scope == AssessmentFormScope.STATE:
        return user.role == UserRole.STATE_ADMIN and user.state_id == template.state_id
    if template.scope == AssessmentFormScope.FACILITY:
        return user.role == UserRole.FACILITY_ADMIN and user.organization_id == template.facility.organization_id
    return False


def can_approve_assessment_form_template(user, template) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == UserRole.SUPER_ADMIN:
        return True
    if template.scope == AssessmentFormScope.NATIONAL:
        return user.role == UserRole.FEDERAL_ADMIN
    if template.scope in {AssessmentFormScope.STATE, AssessmentFormScope.FACILITY}:
        return user.role == UserRole.STATE_ADMIN and user.state_id == (template.state_id or template.facility.state_id)
    return False


def can_manage_assessment_requirement_set(user, requirement_set) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.role == UserRole.SUPER_ADMIN:
        return True
    if requirement_set.scope == AssessmentFormScope.NATIONAL:
        return user.role == UserRole.FEDERAL_ADMIN
    if requirement_set.scope == AssessmentFormScope.STATE:
        return user.role == UserRole.STATE_ADMIN and user.state_id == requirement_set.state_id
    if requirement_set.scope == AssessmentFormScope.FACILITY:
        return user.role == UserRole.FACILITY_ADMIN and user.organization_id == requirement_set.facility.organization_id
    return False
