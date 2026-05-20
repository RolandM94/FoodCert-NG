from typing import Any, Optional

from django.db import transaction

from apps.audit.models import AuditLog
from apps.common.security import get_client_ip, get_user_agent


def log_action(
    *,
    action: str,
    actor: Optional[Any] = None,
    target: Any = None,
    target_type: str = "",
    target_id: str = "",
    organization=None,
    state=None,
    ip_address: str = "",
    user_agent: str = "",
    request=None,
    old_value: Optional[dict] = None,
    new_value: Optional[dict] = None,
    metadata: Optional[dict] = None,
) -> AuditLog:
    """Create an audit log for regulatory, financial, medical, and certificate events."""
    if target is not None:
        target_type = target_type or target.__class__.__name__
        target_id = target_id or str(getattr(target, "pk", ""))

    if request is not None:
        ip_address = ip_address or get_client_ip(request)
        user_agent = user_agent or get_user_agent(request)

    with transaction.atomic():
        return AuditLog.objects.create(
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            action=action,
            target_type=target_type,
            target_id=target_id,
            organization=organization or getattr(actor, "organization", None),
            state=state or getattr(actor, "state", None),
            ip_address=ip_address or None,
            user_agent=user_agent or "",
            old_value=old_value,
            new_value=new_value,
            metadata=metadata or {},
        )
