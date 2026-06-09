from secrets import token_urlsafe

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import InviteStatus, UserInvite, UserRole
from apps.audit.models import AuditAction
from apps.audit.services import log_action
from apps.notifications.models import Notification, NotificationCategory
from apps.organizations.models import Role
from apps.organizations.services_membership import create_membership

User = get_user_model()


INVITE_ROLE_MAP = {
    UserRole.STATE_ADMIN: {UserRole.STATE_ADMIN, UserRole.INSPECTOR},
    UserRole.FACILITY_ADMIN: {UserRole.DOCTOR, UserRole.LAB_STAFF, UserRole.FACILITY_ADMIN},
    UserRole.EMPLOYER: {UserRole.EMPLOYER, UserRole.FOOD_HANDLER},
    UserRole.SUPER_ADMIN: set(UserRole.values),
    UserRole.FEDERAL_ADMIN: set(UserRole.values),
}


class InviteService:
    @classmethod
    def can_manage_organization(cls, *, actor, organization):
        if actor.role in {UserRole.SUPER_ADMIN, UserRole.FEDERAL_ADMIN}:
            return True
        if actor.role == UserRole.STATE_ADMIN and organization.state_id == actor.state_id:
            return True
        if actor.role in {UserRole.FACILITY_ADMIN, UserRole.EMPLOYER} and organization.id == actor.organization_id:
            return True
        return False

    @classmethod
    def validate_invite_scope(cls, *, actor, organization, role, unit=None):
        if not cls.can_manage_organization(actor=actor, organization=organization):
            raise PermissionDenied("You cannot manage invites for this organization.")
        allowed_roles = INVITE_ROLE_MAP.get(actor.role, set())
        if role not in allowed_roles:
            raise ValidationError("You cannot invite users with this role.")
        if unit and unit.organization_id != organization.id:
            raise ValidationError("Invite unit must belong to the target organization.")
        if actor.role == UserRole.EMPLOYER and actor.unit_restricted and actor.unit_id and unit and unit.id != actor.unit_id:
            raise PermissionDenied("Branch managers can only invite users to their own branch.")
        if actor.role == UserRole.EMPLOYER and actor.unit_restricted and actor.unit_id and not unit:
            raise PermissionDenied("Branch managers must invite users into their own branch.")

    @classmethod
    @transaction.atomic
    def create_invite(cls, *, actor, organization, email, role, unit=None, unit_restricted=False, phone="", message="", expires_at=None, ministry_staff_role=""):
        cls.validate_invite_scope(actor=actor, organization=organization, role=role, unit=unit)
        invite = UserInvite.objects.create(
            organization=organization,
            unit=unit,
            unit_restricted=unit_restricted,
            invited_by=actor,
            email=email.lower(),
            phone=phone,
            role=role,
            ministry_staff_role=ministry_staff_role,
            message=message,
            token=token_urlsafe(32),
            expires_at=expires_at or timezone.now() + timezone.timedelta(days=7),
        )
        log_action(action=AuditAction.CREATE, actor=actor, target=invite, metadata={"event": "invite_created"})
        Notification.objects.create(
            recipient_email=invite.email,
            category=NotificationCategory.ACCOUNT,
            title="FoodCert NG invitation",
            message=f"You have been invited to join {organization.name} on FoodCert NG.",
            related_object_type=invite.__class__.__name__,
            related_object_id=invite.id,
        )
        return invite

    @classmethod
    @transaction.atomic
    def revoke(cls, *, invite, actor):
        if not cls.can_manage_organization(actor=actor, organization=invite.organization):
            raise PermissionDenied("You cannot revoke this invite.")
        if invite.status != InviteStatus.PENDING:
            raise ValidationError("Only pending invites can be revoked.")
        invite.status = InviteStatus.REVOKED
        invite.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=invite, metadata={"event": "invite_revoked"})
        return invite

    @classmethod
    @transaction.atomic
    def resend(cls, *, invite, actor):
        if not cls.can_manage_organization(actor=actor, organization=invite.organization):
            raise PermissionDenied("You cannot resend this invite.")
        if invite.status != InviteStatus.PENDING:
            raise ValidationError("Only pending invites can be resent.")
        invite.token = token_urlsafe(32)
        invite.expires_at = timezone.now() + timezone.timedelta(days=7)
        invite.save(update_fields=["token", "expires_at", "updated_at"])
        Notification.objects.create(
            recipient_email=invite.email,
            category=NotificationCategory.ACCOUNT,
            title="FoodCert NG invitation resent",
            message=f"Your invitation to join {invite.organization.name} has been resent.",
            related_object_type=invite.__class__.__name__,
            related_object_id=invite.id,
        )
        log_action(action=AuditAction.UPDATE, actor=actor, target=invite, metadata={"event": "invite_resent"})
        return invite

    @classmethod
    @transaction.atomic
    def decline(cls, *, invite, actor=None):
        if invite.status != InviteStatus.PENDING:
            raise ValidationError("Only pending invites can be declined.")
        invite.status = InviteStatus.DECLINED
        invite.save(update_fields=["status", "updated_at"])
        log_action(action=AuditAction.UPDATE, actor=actor, target=invite, metadata={"event": "invite_declined"})
        return invite

    @classmethod
    @transaction.atomic
    def expire_stale_invites(cls):
        updated = UserInvite.objects.filter(status=InviteStatus.PENDING, expires_at__lte=timezone.now()).update(status=InviteStatus.EXPIRED, updated_at=timezone.now())
        return updated

    @classmethod
    def accept(cls, *, invite, payload, actor=None):
        if invite.status != InviteStatus.PENDING:
            raise ValidationError("This invite is no longer pending.")
        if invite.expires_at <= timezone.now():
            invite.status = InviteStatus.EXPIRED
            invite.save(update_fields=["status", "updated_at"])
            raise ValidationError("This invite has expired.")
        user = actor if actor and actor.is_authenticated else None
        if not user:
            existing = User.objects.filter(email=invite.email).first()
            if existing:
                user = existing
            else:
                username = payload.get("username") or invite.email.split("@")[0]
                password = payload.get("password")
                if not password:
                    raise ValidationError("Password is required to accept this invite.")
                user = User(
                    username=username.lower(),
                    email=invite.email,
                    first_name=payload.get("first_name", ""),
                    last_name=payload.get("last_name", ""),
                    phone=payload.get("phone", invite.phone),
                )
                user.set_password(password)
                user.save()

        if invite.employer_staff_role:
            user.employer_staff_role = invite.employer_staff_role
        user.state = invite.unit.state if invite.unit and invite.unit.state else invite.organization.state
        if invite.phone and not user.phone:
            user.phone = invite.phone
        user.save(update_fields=["employer_staff_role", "state", "phone", "updated_at"])

        role = Role.objects.filter(code=invite.role).first()
        if not role:
            raise ValidationError("Invite role has not been configured.")
        create_membership(
            actor=invite.invited_by,
            organization=invite.organization,
            user=user,
            role=role,
            unit=invite.unit,
            unit_restricted=invite.unit_restricted or bool(invite.unit),
            invited_by=invite.invited_by,
        )

        invite.status = InviteStatus.ACCEPTED
        invite.accepted_by = user
        invite.accepted_at = timezone.now()
        invite.save(update_fields=["status", "accepted_by", "accepted_at", "updated_at"])

        if invite.ministry_staff_role and invite.role in {UserRole.STATE_ADMIN, UserRole.FEDERAL_ADMIN, UserRole.INSPECTOR}:
            from apps.ministries.models import MinistryStaffProfile, MinistryType

            ministry_type = MinistryType.FEDERAL if invite.role == UserRole.FEDERAL_ADMIN else MinistryType.STATE
            MinistryStaffProfile.objects.update_or_create(
                user=user,
                defaults={
                    "ministry_type": ministry_type,
                    "sub_role": invite.ministry_staff_role,
                    "state": user.state,
                    "lga": invite.unit.lga if invite.unit else None,
                    "unit": invite.unit,
                    "created_by": invite.invited_by,
                    "is_active": True,
                },
            )

        if invite.facility_staff_type:
            from apps.facilities.models import FacilityStaffProfile, MedicalFacility

            try:
                facility = invite.organization.medical_facility
            except MedicalFacility.DoesNotExist:
                facility = None

            if facility:
                profile, created = FacilityStaffProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "facility": facility,
                        "department": invite.unit,
                        "staff_type": invite.facility_staff_type,
                        "is_active": True,
                    },
                )
                log_action(
                    action=AuditAction.CREATE if created else AuditAction.UPDATE,
                    actor=user,
                    target=profile,
                    metadata={"event": "facility_staff_profile_created_from_invite"},
                )

        Notification.objects.create(
            recipient=invite.invited_by,
            category=NotificationCategory.SYSTEM,
            title="Invite accepted",
            message=f"{user.email} accepted your FoodCert NG organization invite.",
        )
        log_action(action=AuditAction.UPDATE, actor=user, target=invite, metadata={"event": "invite_accepted"})
        return user, invite
