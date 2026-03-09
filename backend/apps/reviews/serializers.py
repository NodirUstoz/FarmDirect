"""Serializers for reviews and replies."""

from rest_framework import serializers
from django.db.models import Avg

from .models import Review, ReviewReply
from apps.accounts.serializers import UserSerializer


class ReviewReplySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = ReviewReply
        fields = ["id", "author", "body", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class ReviewSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = ReviewReplySerializer(many=True, read_only=True)
    target_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "author",
            "farm",
            "product",
            "rating",
            "title",
            "body",
            "image",
            "is_verified_purchase",
            "is_approved",
            "helpful_count",
            "replies",
            "target_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "is_verified_purchase",
            "is_approved",
            "helpful_count",
            "created_at",
            "updated_at",
        ]

    def get_target_name(self, obj):
        if obj.farm:
            return obj.farm.name
        if obj.product:
            return obj.product.name
        return None

    def validate(self, attrs):
        farm = attrs.get("farm")
        product = attrs.get("product")

        if farm and product:
            raise serializers.ValidationError(
                "A review must target either a farm or a product, not both."
            )
        if not farm and not product:
            raise serializers.ValidationError(
                "A review must target either a farm or a product."
            )
        return attrs


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["farm", "product", "rating", "title", "body", "image"]

    def validate(self, attrs):
        farm = attrs.get("farm")
        product = attrs.get("product")

        if farm and product:
            raise serializers.ValidationError(
                "A review must target either a farm or a product, not both."
            )
        if not farm and not product:
            raise serializers.ValidationError(
                "A review must target either a farm or a product."
            )

        # Check for duplicate reviews
        user = self.context["request"].user
        existing = Review.objects.filter(author=user)
        if farm:
            existing = existing.filter(farm=farm)
        if product:
            existing = existing.filter(product=product)
        if existing.exists():
            raise serializers.ValidationError(
                "You have already reviewed this item."
            )

        return attrs

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user

        # Mark as verified if the customer has ordered this product
        from apps.orders.models import OrderItem

        user = validated_data["author"]
        product = validated_data.get("product")
        if product:
            has_purchased = OrderItem.objects.filter(
                order__customer=user,
                product=product,
                order__status__in=["delivered", "picked_up"],
            ).exists()
            validated_data["is_verified_purchase"] = has_purchased

        return super().create(validated_data)


class ReviewStatsSerializer(serializers.Serializer):
    """Aggregated review statistics."""

    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField(
        child=serializers.IntegerField()
    )
