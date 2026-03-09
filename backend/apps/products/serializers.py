"""Serializers for the product catalog."""

from rest_framework import serializers

from .models import Category, FarmProduct, ProductImage, SeasonalAvailability


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "parent",
            "children",
            "sort_order",
            "is_active",
            "product_count",
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "sort_order"]
        read_only_fields = ["id"]


class SeasonalAvailabilitySerializer(serializers.ModelSerializer):
    season_display = serializers.CharField(
        source="get_season_display", read_only=True
    )

    class Meta:
        model = SeasonalAvailability
        fields = [
            "id",
            "season",
            "season_display",
            "start_month",
            "end_month",
            "year",
            "notes",
            "is_pre_order",
            "expected_date",
        ]
        read_only_fields = ["id"]


class FarmProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""

    farm_name = serializers.CharField(source="farm.name", read_only=True)
    farm_slug = serializers.CharField(source="farm.slug", read_only=True)
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )
    is_in_stock = serializers.BooleanField(read_only=True)
    on_sale = serializers.BooleanField(read_only=True)
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)

    class Meta:
        model = FarmProduct
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "price",
            "compare_at_price",
            "unit",
            "unit_display",
            "image",
            "farm_name",
            "farm_slug",
            "category_name",
            "is_organic",
            "is_non_gmo",
            "is_pesticide_free",
            "is_in_stock",
            "is_featured",
            "on_sale",
            "stock_quantity",
            "created_at",
        ]


class FarmProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for product detail views."""

    farm_name = serializers.CharField(source="farm.name", read_only=True)
    farm_slug = serializers.CharField(source="farm.slug", read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    seasonal_availability = SeasonalAvailabilitySerializer(
        many=True, read_only=True
    )
    is_in_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    on_sale = serializers.BooleanField(read_only=True)
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)

    class Meta:
        model = FarmProduct
        fields = [
            "id",
            "farm",
            "farm_name",
            "farm_slug",
            "category",
            "name",
            "slug",
            "description",
            "short_description",
            "price",
            "compare_at_price",
            "unit",
            "unit_display",
            "stock_quantity",
            "low_stock_threshold",
            "image",
            "images",
            "is_organic",
            "is_non_gmo",
            "is_pesticide_free",
            "is_in_stock",
            "is_low_stock",
            "is_active",
            "is_featured",
            "on_sale",
            "seasonal_availability",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FarmProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating / updating products."""

    class Meta:
        model = FarmProduct
        fields = [
            "farm",
            "category",
            "name",
            "slug",
            "description",
            "short_description",
            "price",
            "compare_at_price",
            "unit",
            "stock_quantity",
            "low_stock_threshold",
            "image",
            "is_organic",
            "is_non_gmo",
            "is_pesticide_free",
            "is_active",
            "is_featured",
        ]

    def validate_farm(self, value):
        request = self.context["request"]
        if value.farmer.user != request.user:
            raise serializers.ValidationError(
                "You can only add products to your own farms."
            )
        return value
