"""Serializers for farms, certifications, and harvest calendar."""

from rest_framework import serializers

from .models import Farm, FarmPhoto, FarmCertification, HarvestCalendar
from apps.accounts.serializers import FarmerProfileSerializer


class FarmPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmPhoto
        fields = ["id", "image", "caption", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]


class FarmCertificationSerializer(serializers.ModelSerializer):
    certification_type_display = serializers.CharField(
        source="get_certification_type_display", read_only=True
    )
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = FarmCertification
        fields = [
            "id",
            "certification_type",
            "certification_type_display",
            "name",
            "certifying_body",
            "certificate_number",
            "issued_date",
            "expiry_date",
            "document",
            "is_verified",
            "is_expired",
            "created_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at"]


class HarvestCalendarSerializer(serializers.ModelSerializer):
    season_display = serializers.CharField(
        source="get_season_display", read_only=True
    )

    class Meta:
        model = HarvestCalendar
        fields = [
            "id",
            "product_name",
            "season",
            "season_display",
            "start_month",
            "end_month",
            "expected_harvest_date",
            "notes",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        start = attrs.get("start_month", 1)
        end = attrs.get("end_month", 12)
        if not (1 <= start <= 12) or not (1 <= end <= 12):
            raise serializers.ValidationError(
                "Months must be between 1 and 12."
            )
        return attrs


class FarmListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    farmer_name = serializers.CharField(
        source="farmer.user.get_full_name", read_only=True
    )
    certification_count = serializers.IntegerField(read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "cover_image",
            "logo",
            "city",
            "state",
            "farmer_name",
            "is_featured",
            "accepts_pickup",
            "accepts_delivery",
            "minimum_order_amount",
            "certification_count",
            "product_count",
            "created_at",
        ]


class FarmDetailSerializer(serializers.ModelSerializer):
    """Full serializer for farm detail views."""

    farmer = FarmerProfileSerializer(read_only=True)
    certifications = FarmCertificationSerializer(many=True, read_only=True)
    harvest_entries = HarvestCalendarSerializer(many=True, read_only=True)
    photos = FarmPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "farmer",
            "name",
            "slug",
            "description",
            "short_description",
            "cover_image",
            "logo",
            "address",
            "city",
            "state",
            "zip_code",
            "latitude",
            "longitude",
            "phone",
            "email",
            "website",
            "delivery_radius_miles",
            "accepts_pickup",
            "accepts_delivery",
            "minimum_order_amount",
            "is_active",
            "is_featured",
            "certifications",
            "harvest_entries",
            "photos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_featured", "created_at", "updated_at"]


class FarmCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating or updating a farm."""

    class Meta:
        model = Farm
        fields = [
            "name",
            "slug",
            "description",
            "short_description",
            "cover_image",
            "logo",
            "address",
            "city",
            "state",
            "zip_code",
            "latitude",
            "longitude",
            "phone",
            "email",
            "website",
            "delivery_radius_miles",
            "accepts_pickup",
            "accepts_delivery",
            "minimum_order_amount",
            "is_active",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        farmer_profile = request.user.farmer_profile
        validated_data["farmer"] = farmer_profile
        return super().create(validated_data)
