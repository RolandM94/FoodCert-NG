from rest_framework.permissions import BasePermission

FEDERAL_STANDARDS_ROLES = {"super_admin", "federal_admin"}

STANDARDS_CREATE_ROLES = {"super_admin", "federal_admin"}

STANDARDS_APPROVE_ROLES = {"super_admin", "federal_admin"}

STATE_VIEW_ROLES = {"state_admin"}

FACILITY_VIEW_ROLES = {"facility_admin"}

AUDITOR_ROLES = {"super_admin", "federal_admin"}


class CanViewStandards(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (
            FEDERAL_STANDARDS_ROLES
            | STATE_VIEW_ROLES
            | FACILITY_VIEW_ROLES
        )


class CanManageStandards(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role in FEDERAL_STANDARDS_ROLES


class CanApprovePolicyVersion(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in STANDARDS_APPROVE_ROLES


class CanViewStandardsAudit(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in AUDITOR_ROLES


class CanAcknowledgePolicy(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (STATE_VIEW_ROLES | FEDERAL_STANDARDS_ROLES)
