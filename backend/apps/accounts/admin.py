"""Admin configuration for accounts."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, FarmerProfile, ConsumerProfile


class FarmerProfileInline(admin.StackedInline):
    model = FarmerProfile
    can_delete = False
    verbose_name_plural = "Farmer Profile"
    fk_name = "user"
    extra = 0


class ConsumerProfileInline(admin.StackedInline):
    model = ConsumerProfile
    can_delete = False
    verbose_name_plural = "Consumer Profile"
    fk_name = "user"
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "email_verified",
        "is_active",
        "date_joined",
    ]
    list_filter = ["role", "is_active", "email_verified", "date_joined"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            _("FarmDirect"),
            {
                "fields": (
                    "role",
                    "phone",
                    "avatar",
                    "date_of_birth",
                    "email_verified",
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            _("FarmDirect"),
            {
                "fields": ("email", "first_name", "last_name", "role"),
            },
        ),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.role == User.Role.FARMER:
            return [FarmerProfileInline]
        return [ConsumerProfileInline]


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = [
        "farm_name",
        "user",
        "city",
        "state",
        "is_verified",
        "years_farming",
        "created_at",
    ]
    list_filter = ["is_verified", "state", "created_at"]
    search_fields = ["farm_name", "user__email", "city"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ConsumerProfile)
class ConsumerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "city", "state", "receive_newsletter", "created_at"]
    list_filter = ["receive_newsletter", "state", "created_at"]
    search_fields = ["user__email", "user__first_name", "city"]
    readonly_fields = ["created_at", "updated_at"]
