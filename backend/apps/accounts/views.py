"""Views for user accounts, registration, and profile management."""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import FarmerProfile, ConsumerProfile
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    FarmerProfileSerializer,
    ConsumerProfileSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user account (consumer or farmer)."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Return tokens along with user data so the client can log in immediately
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileView(APIView):
    """Retrieve or update the authenticated user's profile."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data

        # Attach role-specific profile
        if user.is_farmer and hasattr(user, "farmer_profile"):
            data["farmer_profile"] = FarmerProfileSerializer(
                user.farmer_profile
            ).data
        elif user.is_consumer and hasattr(user, "consumer_profile"):
            data["consumer_profile"] = ConsumerProfileSerializer(
                user.consumer_profile
            ).data

        return Response(data)

    def patch(self, request):
        user = request.user
        serializer = UserProfileUpdateSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)


class FarmerProfileView(generics.RetrieveUpdateAPIView):
    """View and edit farmer-specific profile fields."""

    serializer_class = FarmerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = FarmerProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"farm_name": f"{self.request.user.first_name}'s Farm"},
        )
        return profile


class ConsumerProfileView(generics.RetrieveUpdateAPIView):
    """View and edit consumer-specific profile fields."""

    serializer_class = ConsumerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = ConsumerProfile.objects.get_or_create(
            user=self.request.user,
        )
        return profile


class ChangePasswordView(APIView):
    """Allow authenticated users to change their password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Blacklist the refresh token so the user is logged out."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": True, "message": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": True, "message": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
