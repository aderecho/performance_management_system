from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from apps.core.models import Profile, UserUnit, Unit
from apps.core.serializers import ProfileSerializer, UserUnitSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    user_units = UserUnitSerializer(many=True, read_only=True)
    primary_unit = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 
            'email', 
            'is_active', 
            'is_superuser', 
            'profile', 
            'user_units', 
            'primary_unit', 
            'created_at', 
            'updated_at'
        ]

    def get_primary_unit(self, obj):
        primary = obj.user_units.filter(is_primary=True, is_active=True).first()
        return primary.unit.short_code if primary else None
    
        # If to return the full unit details
        # if primary and primary.unit:
        #     return UnitSerializer(primary.unit).data
        # return None

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
            "profile",
            "user_units",
        ]

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        user_units_data = validated_data.pop("user_units", [])
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

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,
        allow_blank=True,
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
            "profile",
            "user_units",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        user_units_data = validated_data.pop("user_units", None)
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

        return instance
