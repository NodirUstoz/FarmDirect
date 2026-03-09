"""Admin configuration for farms."""

from django.contrib import admin

from .models import Farm, FarmPhoto, FarmCertification, HarvestCalendar


class FarmPhotoInline(admin.TabularInline):
    model = FarmPhoto
    extra = 1
    fields = ["image", "caption", "sort_order"]


class FarmCertificationInline(admin.TabularInline):
    model = FarmCertification
    extra = 0
    fields = [
        "certification_type",
        "name",
        "certifying_body",
        "issued_date",
        "expiry_date",
        "is_verified",
    ]


class HarvestCalendarInline(admin.TabularInline):
    model = HarvestCalendar
    extra = 0
    fields = [
        "product_name",
        "season",
        "start_month",
        "end_month",
        "is_available",
    ]


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "farmer",
        "city",
        "state",
        "is_active",
        "is_featured",
        "created_at",
    ]
    list_filter = ["is_active", "is_featured", "state", "accepts_delivery"]
    search_fields = ["name", "farmer__user__email", "city"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [FarmPhotoInline, FarmCertificationInline, HarvestCalendarInline]
    fieldsets = (
        (None, {"fields": ("farmer", "name", "slug", "description", "short_description")}),
        ("Images", {"fields": ("cover_image", "logo")}),
        (
            "Location",
            {"fields": ("address", "city", "state", "zip_code", "latitude", "longitude")},
        ),
        ("Contact", {"fields": ("phone", "email", "website")}),
        (
            "Delivery",
            {
                "fields": (
                    "delivery_radius_miles",
                    "accepts_pickup",
                    "accepts_delivery",
                    "minimum_order_amount",
                )
            },
        ),
        ("Status", {"fields": ("is_active", "is_featured", "created_at", "updated_at")}),
    )


@admin.register(FarmCertification)
class FarmCertificationAdmin(admin.ModelAdmin):
    list_display = [
        "farm",
        "certification_type",
        "name",
        "issued_date",
        "expiry_date",
        "is_verified",
    ]
    list_filter = ["certification_type", "is_verified"]
    search_fields = ["farm__name", "name", "certifying_body"]


@admin.register(HarvestCalendar)
class HarvestCalendarAdmin(admin.ModelAdmin):
    list_display = [
        "farm",
        "product_name",
        "season",
        "start_month",
        "end_month",
        "is_available",
    ]
    list_filter = ["season", "is_available"]
    search_fields = ["farm__name", "product_name"]
