from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsActiveUser
from apps.organizations.models import OrganizationMembership, OrganizationType, Role
from apps.organizations.stakeholder_labels import STAKEHOLDER_LABELS


class StakeholderContextView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        user = request.user
        membership = user.current_membership

        if not membership or not membership.organization:
            return Response({"error": "No active organization membership."}, status=400)

        organization = membership.organization
        org_type = organization.organization_type

        labels = STAKEHOLDER_LABELS.get(org_type, STAKEHOLDER_LABELS[OrganizationType.EMPLOYER])

        can_view_users = request.user.role in {
            UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN,
            UserRole.FACILITY_ADMIN, UserRole.EMPLOYER,
        }
        can_view_roles = request.user.role in {
            UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN,
            UserRole.FACILITY_ADMIN, UserRole.EMPLOYER,
        }
        can_view_units = request.user.role in {
            UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN,
            UserRole.FACILITY_ADMIN, UserRole.EMPLOYER,
        }
        can_view_invites = request.user.role in {
            UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN,
            UserRole.FACILITY_ADMIN, UserRole.EMPLOYER,
        }
        can_view_audit = request.user.role in {
            UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.STATE_ADMIN,
        }

        return Response({
            "organization": {
                "id": str(organization.id),
                "name": organization.name,
                "organization_type": org_type,
                "status": organization.status,
                "state": organization.state_id,
                "state_name": organization.state.name if organization.state else None,
                "lga_name": organization.lga.name if organization.lga else None,
            },
            "membership": {
                "id": str(membership.id),
                "role": membership.role.code if membership.role else None,
                "role_name": membership.role.name if membership.role else None,
                "unit": str(membership.unit_id) if membership.unit else None,
                "unit_name": membership.unit.name if membership.unit else None,
                "unit_restricted": membership.unit_restricted,
                "status": membership.status,
            },
            "labels": {
                "module_title": "Stakeholder Management",
                "stakeholders": labels["stakeholders"],
                "units": labels["units"],
                "unit": labels["unit"],
                "invite_button": labels["invite_button"],
            },
            "permissions": {
                "can_view_users": can_view_users,
                "can_invite_users": can_view_users,
                "can_view_roles": can_view_roles,
                "can_view_units": can_view_units,
                "can_view_invites": can_view_invites,
                "can_view_audit_logs": can_view_audit,
            },
        })


class StakeholderSummaryView(views.APIView):
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        user = request.user
        membership = user.current_membership

        if not membership or not membership.organization:
            return Response({"error": "No active organization membership."}, status=400)

        organization = membership.organization
        memberships = OrganizationMembership.objects.filter(organization=organization)

        total_users = memberships.count()
        active_users = memberships.filter(status="active").count()
        pending_invites = memberships.filter(status="invited").count()
        suspended_users = memberships.filter(status="suspended").count()
        total_units = organization.units.count()
        active_units = organization.units.filter(status="active").count()
        roles_in_use = Role.objects.filter(
            organization_type=organization.organization_type, status="active"
        ).count() if organization.organization_type else 0
        users_without_unit = memberships.filter(unit__isnull=True, status="active").count()
        users_with_unit_restriction = memberships.filter(unit_restricted=True, status="active").count()

        recent = []
        for m in memberships.select_related("user", "role", "unit").order_by("-updated_at")[:5]:
            recent.append({
                "id": str(m.id),
                "user_name": m.user.get_full_name() or m.user.email,
                "role_name": m.role.name if m.role else None,
                "unit_name": m.unit.name if m.unit else None,
                "status": m.status,
                "updated_at": m.updated_at.isoformat(),
            })

        return Response({
            "summary": {
                "total_users": total_users,
                "active_users": active_users,
                "pending_invites": pending_invites,
                "suspended_users": suspended_users,
                "total_units": total_units,
                "active_units": active_units,
                "roles_in_use": roles_in_use,
                "users_without_unit": users_without_unit,
                "users_with_unit_restriction": users_with_unit_restriction,
            },
            "recent_activity": recent,
        })
