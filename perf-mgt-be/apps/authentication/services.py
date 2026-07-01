from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Q

from .models import AuditLog

User = get_user_model()


SENSITIVE_METADATA_KEYS = {
    "password",
    "token",
    "access",
    "refresh",
    "access_token",
    "refresh_token",
    "cookie",
    "cookies",
    "authorization",
}


def permission_to_code(permission):
    return f"{permission.content_type.app_label}.{permission.codename}"


def permission_queryset_to_codes(queryset):
    return {
        permission_to_code(permission)
        for permission in queryset.select_related("content_type")
    }


def get_effective_permissions(user):
    if not user or not getattr(user, "is_authenticated", False):
        return []

    if user.is_superuser:
        return sorted(permission_queryset_to_codes(Permission.objects.all()))

    direct_permissions = permission_queryset_to_codes(user.user_permissions.all())
    role_permissions = permission_queryset_to_codes(
        Permission.objects.filter(group__user=user).distinct()
    )
    granted_permissions = direct_permissions | role_permissions
    denied_permissions = permission_queryset_to_codes(user.denied_permissions.all())
    return sorted(granted_permissions - denied_permissions)


def user_has_effective_permission(user, permission):
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    return permission in get_effective_permissions(user)


def get_role_permission_ids(user):
    permission_ids = user.groups.values_list("permissions__id", flat=True).distinct()
    return sorted(permission_id for permission_id in permission_ids if permission_id is not None)


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR") if request else None
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") if request else None


def get_user_agent(request):
    return (request.META.get("HTTP_USER_AGENT", "") if request else "")[:500]


def sanitize_metadata(metadata):
    safe = {}
    for key, value in (metadata or {}).items():
        normalized_key = str(key).lower()
        if any(sensitive in normalized_key for sensitive in SENSITIVE_METADATA_KEYS):
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
        elif isinstance(value, (list, tuple, set)):
            safe[key] = [
                item if isinstance(item, (str, int, float, bool)) or item is None else str(item)
                for item in value
            ]
        else:
            safe[key] = str(value)
    return safe


class AuditLogService:
    @staticmethod
    def record(
        *,
        request=None,
        user=None,
        module,
        action,
        target_type="",
        target_id="",
        target_label="",
        summary="",
        metadata=None,
    ):
        resolved_user = user
        if resolved_user is None and request is not None:
            request_user = getattr(request, "user", None)
            if getattr(request_user, "is_authenticated", False):
                resolved_user = request_user

        return AuditLog.objects.create(
            user=resolved_user if getattr(resolved_user, "is_authenticated", False) else None,
            user_email=getattr(resolved_user, "email", "") or "",
            module=module,
            action=action,
            target_type=target_type or "",
            target_id=str(target_id or ""),
            target_label=str(target_label or "")[:255],
            summary=str(summary or "")[:500],
            metadata=sanitize_metadata(metadata),
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )

    @staticmethod
    def filtered_queryset(params):
        queryset = AuditLog.objects.select_related("user__profile").order_by("-created_at")

        module = params.get("module")
        action = params.get("action")
        target_type = params.get("target_type")
        user = params.get("user")
        date_from = params.get("date_from")
        date_to = params.get("date_to")
        search = params.get("search")

        if module:
            queryset = queryset.filter(module=module)
        if action:
            queryset = queryset.filter(action=action)
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        if user:
            queryset = queryset.filter(user_email__icontains=user)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        if search:
            queryset = queryset.filter(
                Q(user_email__icontains=search)
                | Q(action__icontains=search)
                | Q(target_type__icontains=search)
                | Q(target_label__icontains=search)
                | Q(summary__icontains=search)
            )

        try:
            limit = int(params.get("limit", 200))
        except (TypeError, ValueError):
            limit = 200

        limit = max(1, min(limit, 1000))
        return queryset[:limit]


class UserDashboardService:

    @staticmethod
    def get_stats():
        today = now()

        # Start of current month (e.g., Jan 1, 00:00:00)
        start_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Compute previous month range
        last_month_end = start_current_month - timedelta(seconds=1)
        start_last_month = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Total users
        total_current = User.objects.count()

        # Total users before current month
        total_last = User.objects.filter(created_at__lt=start_current_month).count()

        # Total active users
        active_current = User.objects.filter(is_active=True).count()

        # Total active users before current month
        active_last = User.objects.filter(
            is_active=True,
            updated_at__lt=start_current_month
        ).count()

        # Total active staff users
        active_staff_current = User.objects.filter(
            is_active=True,
            is_superuser=False
        ).count()

        # Total active staff users before current month
        active_staff_last = User.objects.filter(
            is_active=True,
            is_superuser=False,
            updated_at__lt=start_current_month
        ).count()

        # Total active admin users
        active_admin_current = User.objects.filter(
            is_active=True,
            is_superuser=True
        ).count()

        # Total active admin users before current month
        active_admin_last = User.objects.filter(
            is_active=True,
            is_superuser=True,
            updated_at__lt=start_current_month
        ).count()

        # Total new users
        new_current = User.objects.filter(
            created_at__gte=start_current_month
        ).count()

        # Total new users before current month
        new_last = User.objects.filter(
            created_at__gte=start_last_month,
            created_at__lt=start_current_month
        ).count()

        return {
            "total_users": UserDashboardService.build_metric(total_current, total_last),
            "active_users": UserDashboardService.build_metric(active_current, active_last),
            "active_staff": UserDashboardService.build_metric(active_staff_current, active_staff_last),
            "active_admin": UserDashboardService.build_metric(active_admin_current, active_admin_last),
            "new_users": UserDashboardService.build_metric(new_current, new_last),
        }


    def build_metric(current, previous):
        if previous == 0:
            trend = 100 if current > 0 else 0
        else:
            trend = ((current - previous) / previous) * 100

        return {
            "value": current,
            "previous": previous,
            "trend": round(trend, 2)
        }
