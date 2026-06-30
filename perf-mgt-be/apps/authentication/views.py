
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.db import connection
from django.http import JsonResponse

from .authentication import CookieJWTAuthentication

from .serializers import (
    LoginRequestSerializer,
    PermissionSerializer,
    RefreshTokenCookieSerializer,
    RoleSerializer,
    RoleStatusSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from .services import UserDashboardService

User = get_user_model()


class IsSuperuserOrActionPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        required_permissions = getattr(view, "action_permissions", {}).get(
            getattr(view, "action", None)
        )
        required_permission = getattr(view, "required_permission", None)

        if required_permissions is None and required_permission:
            required_permissions = required_permission

        if isinstance(required_permissions, str):
            required_permissions = [required_permissions]

        if required_permissions:
            return all(user.has_perm(permission) for permission in required_permissions)

        return user.is_staff


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

        # Set secure cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite="Lax", #Lax
            max_age=60 * 30,  # 30 minutes
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production (HTTPS)
            samesite="Lax", #Lax
            max_age=60 * 60 * 24 * 7,  # 7 days
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

        # Clear cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

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
                    "permissions": list(user.get_all_permissions()),
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
        from rest_framework_simplejwt.tokens import RefreshToken
        serializer = RefreshTokenCookieSerializer(data=request.COOKIES)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data.get("refresh_token")

        if not refresh_token:
            return Response({"error": "No refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except Exception:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        response = JsonResponse({"message": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False, # True in production
            samesite="Lax",
            max_age=60 * 30,  # 30 minutes
        )
        return response
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().prefetch_related(
        "user_units__unit",
        "profile",
        "groups",
        "groups__permissions__content_type",
        "user_permissions__content_type",
    )

    permission_classes = [IsSuperuserOrActionPermission]
    action_permissions = {
        "list": "authentication.view_user",
        "retrieve": "authentication.view_user",
        "create": "authentication.add_user",
        "update": "authentication.change_user",
        "partial_update": "authentication.change_user",
        "destroy": "authentication.delete_user",
    }

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

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)



class UserDashboardStatsView(APIView):
    permission_classes = [IsSuperuserOrActionPermission]
    required_permission = "authentication.view_user"

    def get(self, request):
        data = UserDashboardService.get_stats()
        return Response(data)


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [IsSuperuserOrActionPermission]
    action_permissions = {
        "list": "auth.view_group",
        "retrieve": "auth.view_group",
        "create": "auth.add_group",
        "update": "auth.change_group",
        "partial_update": "auth.change_group",
        "destroy": "auth.delete_group",
    }

    def get_queryset(self):
        return Group.objects.prefetch_related(
            "permissions__content_type"
        ).extra(
            select={"is_deleted": "auth_group.is_deleted"}
        ).order_by("name")

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
            return Response(self.get_serializer(instance).data)

        return super().partial_update(request, *args, **kwargs)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PermissionSerializer
    permission_classes = [IsSuperuserOrActionPermission]
    action_permissions = {
        "list": "auth.view_permission",
        "retrieve": "auth.view_permission",
    }

    def get_queryset(self):
        return Permission.objects.select_related("content_type").order_by(
            "content_type__app_label",
            "content_type__model",
            "codename",
        )
