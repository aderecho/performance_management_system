from django.contrib import admin
from .models import Unit, UnitOfMeasure, UserUnit
from .models import Profile


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    fields = ("name", "short_code", "description")
    ordering = ("name",)
    list_display = ("name", "short_code")
    search_fields = ("name", "short_code")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    fields = ("name", "short_code", "description", "parent")
    ordering = ("name",)
    list_display = ("name", "short_code", "parent_name")
    search_fields = ("name", "short_code")

    @admin.display(description="Parent")
    def parent_name(self, obj):
        return obj.parent.name if obj.parent else "—"


@admin.register(UserUnit)
class UserUnitAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "unit",
        "is_primary",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_primary",
        "is_active",
        "unit",
    )
    search_fields = (
        "user__username",
        "user__email",
        "unit__name",
        "unit__short_code",
    )
    ordering = ("user", "-is_primary", "unit")

    autocomplete_fields = ("user", "unit")

    def save_model(self, request, obj, form, change):
        """
        Enforce only ONE primary unit per user
        """
        if obj.is_primary:
            UserUnit.objects.filter(
                user=obj.user,
                is_primary=True
            ).exclude(pk=obj.pk).update(is_primary=False)

        super().save_model(request, obj, form, change)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = 'user'
    extra = 0

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'middle_name', 'suffix']
    search_fields = ['user__email', 'first_name', 'last_name']