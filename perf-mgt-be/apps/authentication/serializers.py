from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.core.serializers import ProfileSerializer, UserUnitSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    user_units = UserUnitSerializer(many=True, read_only=True)
    primary_unit = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'is_active', 'is_superuser', 'profile', 'user_units', 'primary_unit', 'created_at', 'updated_at', 'updated_at']

    def get_primary_unit(self, obj):
        primary = obj.user_units.filter(is_primary=True, is_active=True).first()
        return primary.unit.short_code if primary else None
    
        # If to return the full unit details
        # if primary and primary.unit:
        #     return UnitSerializer(primary.unit).data
        # return None