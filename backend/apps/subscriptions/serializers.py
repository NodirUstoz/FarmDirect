"""Serializers for subscriptions."""

from rest_framework import serializers

from .models import (
    SubscriptionPlan,
    SubscriptionBox,
    SubscriptionOrder,
    SubscriptionOrderItem,
)
from apps.products.serializers import FarmProductListSerializer


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(
        source="get_frequency_display", read_only=True
    )
    size_display = serializers.CharField(
        source="get_size_display", read_only=True
    )

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "frequency",
            "frequency_display",
            "size",
            "size_display",
            "price",
            "compare_at_price",
            "item_count",
            "image",
            "is_active",
            "created_at",
        ]


class SubscriptionOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionOrderItem
        fields = ["id", "product", "product_name", "quantity", "price"]
        read_only_fields = ["id"]


class SubscriptionOrderSerializer(serializers.ModelSerializer):
    items = SubscriptionOrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = SubscriptionOrder
        fields = [
            "id",
            "status",
            "status_display",
            "delivery_date",
            "items",
            "total",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total", "created_at", "updated_at"]


class SubscriptionBoxSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    recent_orders = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionBox
        fields = [
            "id",
            "plan",
            "status",
            "status_display",
            "preferred_categories",
            "preferred_farms",
            "exclude_items",
            "delivery_address",
            "delivery_city",
            "delivery_state",
            "delivery_zip",
            "delivery_notes",
            "next_delivery_date",
            "recent_orders",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_recent_orders(self, obj):
        orders = obj.orders.all()[:5]
        return SubscriptionOrderSerializer(orders, many=True).data


class SubscriptionBoxCreateSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField()

    class Meta:
        model = SubscriptionBox
        fields = [
            "plan_id",
            "preferred_categories",
            "preferred_farms",
            "exclude_items",
            "delivery_address",
            "delivery_city",
            "delivery_state",
            "delivery_zip",
            "delivery_notes",
        ]

    def validate_plan_id(self, value):
        try:
            SubscriptionPlan.objects.get(pk=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Subscription plan not found or inactive.")
        return value

    def create(self, validated_data):
        plan_id = validated_data.pop("plan_id")
        categories = validated_data.pop("preferred_categories", [])
        farms = validated_data.pop("preferred_farms", [])
        plan = SubscriptionPlan.objects.get(pk=plan_id)
        user = self.context["request"].user

        box = SubscriptionBox.objects.create(
            customer=user,
            plan=plan,
            **validated_data,
        )
        if categories:
            box.preferred_categories.set(categories)
        if farms:
            box.preferred_farms.set(farms)

        return box


class SubscriptionBoxUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionBox
        fields = [
            "status",
            "preferred_categories",
            "preferred_farms",
            "exclude_items",
            "delivery_address",
            "delivery_city",
            "delivery_state",
            "delivery_zip",
            "delivery_notes",
        ]
