"""Serializers for user accounts and profiles."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import FarmerProfile, ConsumerProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handles new user sign-up."""

    password = serializers.CharField(
        write_only=True, min_length=8, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            "password",
            "password_confirm",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create the appropriate profile
        if user.role == User.Role.FARMER:
            FarmerProfile.objects.create(user=user, farm_name=f"{user.first_name}'s Farm")
        else:
            ConsumerProfile.objects.create(user=user)

        return user


class UserSerializer(serializers.ModelSerializer):
    """Public user representation."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "avatar",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "date_joined"]

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Allows users to update their own profile fields."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "date_of_birth",
        ]


class FarmerProfileSerializer(serializers.ModelSerializer):
    """Serializer for farmer profile data."""

    user = UserSerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = FarmerProfile
        fields = [
            "id",
            "user",
            "bio",
            "farm_name",
            "farm_address",
            "city",
            "state",
            "zip_code",
            "latitude",
            "longitude",
            "farm_size_acres",
            "years_farming",
            "website",
            "is_verified",
            "verified_at",
            "created_at",
            "updated_at",
            "rating",
        ]
        read_only_fields = ["id", "is_verified", "verified_at", "created_at", "updated_at"]

    def get_rating(self, obj):
        """Calculate average rating from farm reviews."""
        from apps.reviews.models import Review

        reviews = Review.objects.filter(farm__farmer=obj)
        if not reviews.exists():
            return None
        avg = reviews.aggregate(avg=models.Avg("rating"))["avg"]
        return round(avg, 1) if avg else None

    def get_rating(self, obj):
        from django.db.models import Avg
        from apps.reviews.models import Review

        result = Review.objects.filter(farm__farmer=obj).aggregate(avg=Avg("rating"))
        avg = result.get("avg")
        return round(avg, 1) if avg else None


class ConsumerProfileSerializer(serializers.ModelSerializer):
    """Serializer for consumer profile data."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = ConsumerProfile
        fields = [
            "id",
            "user",
            "delivery_address",
            "city",
            "state",
            "zip_code",
            "latitude",
            "longitude",
            "dietary_preferences",
            "receive_newsletter",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChangePasswordSerializer(serializers.Serializer):
    """Validates and processes password changes."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, min_length=8, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
