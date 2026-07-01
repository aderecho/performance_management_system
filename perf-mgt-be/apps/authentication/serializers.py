from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from django.db import transaction
from apps.core.models import Profile, UserUnit, Unit
from apps.core.serializers import ProfileSerializer, UserUnitSerializer
from .models import AuditLog
from .services import get_effective_permissions, get_role_permission_ids

User = get_user_model()


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class RefreshTokenCookieSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=False, allow_blank=False)


class AuditLogQuerySerializer(serializers.Serializer):
    module = serializers.ChoiceField(
        choices=[choice[0] for choice in AuditLog.MODULE_CHOICES],
        required=False,
    )
    action = serializers.CharField(required=False, allow_blank=True)
    target_type = serializers.CharField(required=False, allow_blank=True)
    user = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=1000)


class AuditLogSerializer(serializers.ModelSerializer):
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "user_email",
            "user_full_name",
            "module",
            "action",
            "target_type",
            "target_id",
            "target_label",
            "summary",
            "metadata",
            "ip_address",
            "user_agent",
            "created_at",
        ]
        read_only_fields = fields

    def get_user_full_name(self, obj):
        profile = getattr(obj.user, "profile", None) if obj.user else None
        if profile:
            name = " ".join(
                part for part in (profile.first_name, profile.last_name) if part
            ).strip()
            if name:
                return name
        return obj.user_email or "System"


class PermissionSerializer(serializers.ModelSerializer):
    app_label = serializers.CharField(source="content_type.app_label", read_only=True)
    model = serializers.CharField(source="content_type.model", read_only=True)
    permission = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "codename",
            "app_label",
            "model",
            "permission",
        ]

    def get_permission(self, obj):
        return f"{obj.content_type.app_label}.{obj.codename}"


class RoleSerializer(serializers.ModelSerializer):
    is_deleted = serializers.SerializerMethodField()
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.select_related("content_type").all(),
        many=True,
        required=False,
    )
    permission_details = PermissionSerializer(
        source="permissions",
        many=True,
        read_only=True,
    )
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "is_deleted",
            "permissions",
            "permission_details",
            "permission_count",
        ]

    def get_is_deleted(self, obj):
        return bool(getattr(obj, "is_deleted", False))

    def get_permission_count(self, obj):
        return obj.permissions.count()


class RoleStatusSerializer(serializers.Serializer):
    is_deleted = serializers.BooleanField()


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    user_units = UserUnitSerializer(many=True, read_only=True)
    primary_unit = serializers.SerializerMethodField()
    role_ids = serializers.SerializerMethodField()
    direct_permission_ids = serializers.SerializerMethodField()
    role_permission_ids = serializers.SerializerMethodField()
    denied_permission_ids = serializers.SerializerMethodField()
    effective_permissions = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()
    role_names = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'is_active', 
            'is_superuser', 
            'role_ids',
            'role_names',
            'direct_permission_ids',
            'role_permission_ids',
            'denied_permission_ids',
            'effective_permissions',
            'permission_count',
            'profile', 
            'user_units', 
            'primary_unit', 
            'created_at', 
            'updated_at'
        ]
    
    

    def get_primary_unit(self, obj):
        primary = obj.user_units.filter(is_primary=True, is_active=True).first()
        return primary.unit.short_code if primary else None

    def get_role_ids(self, obj):
        return list(obj.groups.order_by("name").values_list("id", flat=True))

    def get_direct_permission_ids(self, obj):
        return list(
            obj.user_permissions.order_by(
                "content_type__app_label",
                "content_type__model",
                "codename",
            ).values_list("id", flat=True)
        )

    def get_role_permission_ids(self, obj):
        return get_role_permission_ids(obj)

    def get_denied_permission_ids(self, obj):
        return list(
            obj.denied_permissions.order_by(
                "content_type__app_label",
                "content_type__model",
                "codename",
            ).values_list("id", flat=True)
        )

    def get_effective_permissions(self, obj):
        return get_effective_permissions(obj)

    def get_permission_count(self, obj):
        return len(get_effective_permissions(obj))
    
    def get_role_names(self, obj):
        return list(obj.groups.order_by("name").values_list("name", flat=True))


class UserProfileCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    middle_name = serializers.CharField(
        max_length=150,
        allow_blank=True,
        required=False,
    )
    last_name = serializers.CharField(max_length=150)
    suffix = serializers.CharField(
        max_length=50,
        allow_blank=True,
        required=False,
    )


class UserUnitCreateSerializer(serializers.Serializer):
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.all())
    is_primary = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)


def sync_user_units(user, user_units_data):
    submitted_unit_ids = []

    for user_unit in user_units_data:
        unit = user_unit["unit"]
        submitted_unit_ids.append(unit.id)

        UserUnit.objects.update_or_create(
            user=user,
            unit=unit,
            defaults={
                "is_primary": user_unit.get("is_primary", False),
                "is_active": user_unit.get("is_active", True),
            },
        )

    UserUnit.objects.filter(user=user).exclude(
        unit_id__in=submitted_unit_ids
    ).update(
        is_primary=False,
        is_active=False,
    )


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    user_permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    denied_permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    profile = UserProfileCreateSerializer(write_only=True)
    user_units = UserUnitCreateSerializer(
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "is_active",
            "is_superuser",
            "role_ids",
            "user_permission_ids",
            "denied_permission_ids",
            "profile",
            "user_units",
        ]

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        user_units_data = validated_data.pop("user_units", [])
        role_ids = validated_data.pop("role_ids", [])
        user_permission_ids = validated_data.pop("user_permission_ids", [])
        denied_permission_ids = validated_data.pop("denied_permission_ids", [])
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        Profile.objects.update_or_create(
            user=user,
            defaults={
                "first_name": profile_data.get("first_name", ""),
                "middle_name": profile_data.get("middle_name", ""),
                "last_name": profile_data.get("last_name", ""),
                "suffix": profile_data.get("suffix", ""),
            },
        )

        for user_unit in user_units_data:
            UserUnit.objects.create(
                user=user,
                unit=user_unit["unit"],
                is_primary=user_unit.get("is_primary", False),
                is_active=user_unit.get("is_active", True),
            )

        user.groups.set(role_ids)
        user.user_permissions.set(user_permission_ids)
        user.denied_permissions.set(denied_permission_ids)

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,
        allow_blank=True,
    )
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    user_permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    denied_permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    profile = UserProfileCreateSerializer(write_only=True, required=False)
    user_units = UserUnitCreateSerializer(
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "is_active",
            "is_superuser",
            "role_ids",
            "user_permission_ids",
            "denied_permission_ids",
            "profile",
            "user_units",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        user_units_data = validated_data.pop("user_units", None)
        role_ids = validated_data.pop("role_ids", None)
        user_permission_ids = validated_data.pop("user_permission_ids", None)
        denied_permission_ids = validated_data.pop("denied_permission_ids", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if profile_data is not None:
            Profile.objects.update_or_create(
                user=instance,
                defaults={
                    "first_name": profile_data.get("first_name", ""),
                    "middle_name": profile_data.get("middle_name", ""),
                    "last_name": profile_data.get("last_name", ""),
                    "suffix": profile_data.get("suffix", ""),
                },
            )

        if user_units_data is not None:
            sync_user_units(instance, user_units_data)

        if role_ids is not None:
            instance.groups.set(role_ids)

        if user_permission_ids is not None:
            instance.user_permissions.set(user_permission_ids)

        if denied_permission_ids is not None:
            instance.denied_permissions.set(denied_permission_ids)

        return instance
