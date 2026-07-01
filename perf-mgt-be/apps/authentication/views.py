
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework import viewsets

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.db import connection
from django.http import JsonResponse

from .authentication import CookieJWTAuthentication

from .serializers import (
    AuditLogQuerySerializer,
    AuditLogSerializer,
    LoginRequestSerializer,
    PermissionSerializer,
    RefreshTokenCookieSerializer,
    RoleSerializer,
    RoleStatusSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from .models import AuditLog
from .services import (
    AuditLogService,
    UserDashboardService,
    get_effective_permissions,
    user_has_effective_permission,
)

User = get_user_model()

JWT_COOKIE_SAMESITE = "Lax"
JWT_COOKIE_PATH = "/"


def jwt_cookie_max_age(setting_name):
    lifetime = settings.SIMPLE_JWT[setting_name]
    return int(lifetime.total_seconds())


def set_access_cookie(response, access_token):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=JWT_COOKIE_SAMESITE,
        max_age=jwt_cookie_max_age("ACCESS_TOKEN_LIFETIME"),
        path=JWT_COOKIE_PATH,
    )


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=JWT_COOKIE_SAMESITE,
        max_age=jwt_cookie_max_age("REFRESH_TOKEN_LIFETIME"),
        path=JWT_COOKIE_PATH,
    )


def clear_jwt_cookies(response):
    response.delete_cookie(
        "access_token",
        path=JWT_COOKIE_PATH,
        samesite=JWT_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        "refresh_token",
        path=JWT_COOKIE_PATH,
        samesite=JWT_COOKIE_SAMESITE,
    )


def rotate_refresh_token(refresh):
    if not api_settings.ROTATE_REFRESH_TOKENS:
        return None

    if api_settings.BLACKLIST_AFTER_ROTATION:
        try:
            refresh.blacklist()
        except AttributeError:
            pass

    refresh.set_jti()
    refresh.set_exp()
    refresh.set_iat()
    return str(refresh)


class IsSuperuserOrActionPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        permission_resolver = getattr(view, "get_action_permissions", None)
        if callable(permission_resolver):
            required_permissions = permission_resolver(request)
        else:
            required_permissions = None

        if required_permissions is None:
            required_permissions = getattr(view, "action_permissions", {}).get(
                getattr(view, "action", None)
            )
        required_permission = getattr(view, "required_permission", None)

        if required_permissions is None and required_permission:
            required_permissions = required_permission

        if isinstance(required_permissions, str):
            required_permissions = [required_permissions]

        if required_permissions:
            return all(
                user_has_effective_permission(user, permission)
                for permission in required_permissions
            )

        return user.is_staff


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)


def changed_payload_fields(payload, excluded=None):
    excluded = set(excluded or [])
    return sorted(
        key
        for key in payload.keys()
        if key not in excluded and "password" not in key.lower()
    )


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = JsonResponse({"message": "Login successful"})
        set_access_cookie(response, access_token)
        set_refresh_cookie(response, refresh_token)

        AuditLogService.record(
            request=request,
            user=user,
            module=AuditLog.MODULE_AUTH,
            action="login.success",
            target_type="user",
            target_id=user.id,
            target_label=user.email,
            summary=f"{user.email} signed in.",
        )

        return response
    

class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Blacklist refresh token
        Clear JWT cookies
        """

        auth_user = None
        try:
            auth_result = CookieJWTAuthentication().authenticate(request)
            if auth_result:
                auth_user = auth_result[0]
        except Exception:
            auth_user = None

        serializer = RefreshTokenCookieSerializer(data=request.COOKIES)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                # Token may already be invalid/expired
                pass

        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )

        clear_jwt_cookies(response)

        if auth_user:
            AuditLogService.record(
                request=request,
                user=auth_user,
                module=AuditLog.MODULE_AUTH,
                action="logout.success",
                target_type="user",
                target_id=auth_user.id,
                target_label=auth_user.email,
                summary=f"{auth_user.email} signed out.",
            )

        return response


class SessionCheckView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        user = request.user
        if user and user.is_authenticated:
            return Response({
                "active": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.profile.first_name,
                    "last_name": user.profile.last_name,
                    "is_superadmin": user.is_superuser,
                    "roles": list(user.groups.values_list("name", flat=True)),
                    "permissions": get_effective_permissions(user),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "active": False
            }, status=status.HTTP_401_UNAUTHORIZED)
        

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RefreshTokenCookieSerializer(data=request.COOKIES)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            rotated_refresh_token = rotate_refresh_token(refresh)
        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = JsonResponse({"message": "Token refreshed"})
        set_access_cookie(response, access_token)
        if rotated_refresh_token:
            set_refresh_cookie(response, rotated_refresh_token)
        return response
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().prefetch_related(
        "user_units__unit",
        "profile",
        "groups",
        "groups__permissions__content_type",
        "user_permissions__content_type",
        "denied_permissions__content_type",
    )

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperuserOrActionPermission]
    action_permissions = {
        "list": "authentication.view_user",
        "retrieve": "authentication.view_user",
        "create": "authentication.add_user",
        "update": "authentication.change_user",
        "partial_update": "authentication.change_user",
        "destroy": "authentication.delete_user",
    }

    def get_action_permissions(self, request):
        if self.action == "partial_update" and set(request.data.keys()) == {"is_active"}:
            return "authentication.delete_user"
        return None

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.distinct().order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        AuditLogService.record(
            request=request,
            module=AuditLog.MODULE_ADMIN,
            action="user.create",
            target_type="user",
            target_id=user.id,
            target_label=user.email,
            summary=f"Created user {user.email}.",
            metadata={
                "fields": changed_payload_fields(request.data, excluded={"password"}),
                "role_count": user.groups.count(),
                "direct_permission_count": user.user_permissions.count(),
                "denied_permission_count": user.denied_permissions.count(),
            },
        )

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        fields = changed_payload_fields(request.data, excluded={"password"})
        status_action = None
        if "is_active" in request.data:
            status_action = "user.activate" if user.is_active else "user.deactivate"

        AuditLogService.record(
            request=request,
            module=AuditLog.MODULE_ADMIN,
            action=status_action or "user.update",
            target_type="user",
            target_id=user.id,
            target_label=user.email,
            summary=f"Updated user {user.email}.",
            metadata={
                "fields": fields,
                "role_count": user.groups.count(),
                "direct_permission_count": user.user_permissions.count(),
                "denied_permission_count": user.denied_permissions.count(),
                "is_active": user.is_active,
            },
        )

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)



class UserDashboardStatsView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperuserOrActionPermission]
    required_permission = "authentication.view_user"

    def get(self, request):
        data = UserDashboardService.get_stats()
        return Response(data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperuser]

    def get_queryset(self):
        query_serializer = AuditLogQuerySerializer(data=self.request.query_params)
        query_serializer.is_valid(raise_exception=True)
        return AuditLogService.filtered_queryset(query_serializer.validated_data)


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperuserOrActionPermission]
    action_permissions = {
        "list": "auth.view_group",
        "retrieve": "auth.view_group",
        "create": "auth.add_group",
        "update": "auth.change_group",
        "partial_update": "auth.change_group",
        "destroy": "auth.delete_group",
    }

    def get_action_permissions(self, request):
        if self.action == "list":
            user = request.user
            if user_has_effective_permission(user, "auth.view_group"):
                return "auth.view_group"
            if user_has_effective_permission(user, "authentication.add_user"):
                return "authentication.add_user"
            if user_has_effective_permission(user, "authentication.change_user"):
                return "authentication.change_user"
        return None

    def get_queryset(self):
        return Group.objects.prefetch_related(
            "permissions__content_type"
        ).extra(
            select={"is_deleted": "auth_group.is_deleted"}
        ).order_by("name")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        role_name = response.data.get("name", "")
        AuditLogService.record(
            request=request,
            module=AuditLog.MODULE_ADMIN,
            action="role.create",
            target_type="role",
            target_id=response.data.get("id", ""),
            target_label=role_name,
            summary=f"Created role {role_name}.",
            metadata={
                "fields": changed_payload_fields(request.data),
                "permission_count": response.data.get("permission_count", 0),
            },
        )
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        role_name = response.data.get("name", "")
        AuditLogService.record(
            request=request,
            module=AuditLog.MODULE_ADMIN,
            action="role.update",
            target_type="role",
            target_id=response.data.get("id", ""),
            target_label=role_name,
            summary=f"Updated role {role_name}.",
            metadata={
                "fields": changed_payload_fields(request.data),
                "permission_count": response.data.get("permission_count", 0),
            },
        )
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        target_id = instance.id
        role_name = instance.name
        response = super().destroy(request, *args, **kwargs)
        AuditLogService.record(
            request=request,
            module=AuditLog.MODULE_ADMIN,
            action="role.delete",
            target_type="role",
            target_id=target_id,
            target_label=role_name,
            summary=f"Deleted role {role_name}.",
        )
        return response

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        is_deleted_serializer = RoleStatusSerializer(
            data=request.data,
            partial=True,
        )
        is_deleted_serializer.is_valid(raise_exception=True)

        if "is_deleted" in is_deleted_serializer.validated_data:
            value = is_deleted_serializer.validated_data["is_deleted"]
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE auth_group SET is_deleted = %s WHERE id = %s",
                    [value, instance.id],
                )

            instance = self.get_queryset().get(pk=instance.pk)
            action = "role.deactivate" if value else "role.activate"
            AuditLogService.record(
                request=request,
                module=AuditLog.MODULE_ADMIN,
                action=action,
                target_type="role",
                target_id=instance.id,
                target_label=instance.name,
                summary=f"{'Inactivated' if value else 'Activated'} role {instance.name}.",
                metadata={"is_deleted": value},
            )
            return Response(self.get_serializer(instance).data)

        return super().partial_update(request, *args, **kwargs)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PermissionSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperuserOrActionPermission]
    action_permissions = {
        "list": "auth.view_permission",
        "retrieve": "auth.view_permission",
    }

    def get_action_permissions(self, request):
        if self.action == "list":
            user = request.user
            if user_has_effective_permission(user, "auth.view_permission"):
                return "auth.view_permission"
            if user_has_effective_permission(user, "auth.add_group"):
                return "auth.add_group"
            if user_has_effective_permission(user, "auth.change_group"):
                return "auth.change_group"
        return None

    def get_queryset(self):
        return Permission.objects.select_related("content_type").order_by(
            "content_type__app_label",
            "content_type__model",
            "codename",
        )
