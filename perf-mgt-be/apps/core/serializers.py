from rest_framework import serializers

from apps.core.models import (
    UnitOfMeasure,
    Unit,
    Profile,
    UserUnit
)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = "__all__"


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = "__all__"


class UserUnitSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = UserUnit
        fields = "__all__"