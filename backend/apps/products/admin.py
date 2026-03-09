"""Admin configuration for products."""

from django.contrib import admin

from .models import Category, FarmProduct, ProductImage, SeasonalAvailability


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "sort_order"]


class SeasonalAvailabilityInline(admin.TabularInline):
    model = SeasonalAvailability
    extra = 0
    fields = ["season", "start_month", "end_month", "year", "is_pre_order"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "sort_order", "is_active"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(FarmProduct)
class FarmProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "farm",
        "category",
        "price",
        "unit",
        "stock_quantity",
        "is_organic",
        "is_active",
        "is_featured",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "is_featured",
        "is_organic",
        "is_non_gmo",
        "is_pesticide_free",
        "category",
        "unit",
    ]
    search_fields = ["name", "farm__name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ProductImageInline, SeasonalAvailabilityInline]
    fieldsets = (
        (None, {"fields": ("farm", "category", "name", "slug", "description", "short_description")}),
        ("Pricing", {"fields": ("price", "compare_at_price", "unit")}),
        ("Inventory", {"fields": ("stock_quantity", "low_stock_threshold")}),
        ("Image", {"fields": ("image",)}),
        (
            "Attributes",
            {"fields": ("is_organic", "is_non_gmo", "is_pesticide_free")},
        ),
        ("Status", {"fields": ("is_active", "is_featured", "created_at", "updated_at")}),
    )
