"""Views for farm management and public farm browsing."""

from django.db.models import Count
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Farm, FarmPhoto, FarmCertification, HarvestCalendar
from .serializers import (
    FarmListSerializer,
    FarmDetailSerializer,
    FarmCreateUpdateSerializer,
    FarmPhotoSerializer,
    FarmCertificationSerializer,
    HarvestCalendarSerializer,
)


class IsFarmerOwner(permissions.BasePermission):
    """Only the farmer who owns the farm can modify it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.is_farmer
            and obj.farmer.user == request.user
        )


class FarmViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for farms.
    - Anyone can list / retrieve.
    - Farmers can create / update / delete their own farms.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsFarmerOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "city", "state"]
    ordering_fields = ["name", "created_at", "is_featured"]
    filterset_fields = ["state", "is_active", "is_featured", "accepts_delivery", "accepts_pickup"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Farm.objects.select_related("farmer__user").annotate(
            certification_count=Count("certifications", distinct=True),
            product_count=Count("products", distinct=True),
        )
        if self.action == "list":
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return FarmListSerializer
        if self.action in ("create", "update", "partial_update"):
            return FarmCreateUpdateSerializer
        return FarmDetailSerializer

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user.farmer_profile)

    # ---- Nested actions ----

    @action(detail=True, methods=["get"])
    def harvest_calendar(self, request, slug=None):
        """Return the harvest calendar for this farm."""
        farm = self.get_object()
        entries = farm.harvest_entries.all()
        serializer = HarvestCalendarSerializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def certifications(self, request, slug=None):
        """Return all certifications for this farm."""
        farm = self.get_object()
        certs = farm.certifications.all()
        serializer = FarmCertificationSerializer(certs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def photos(self, request, slug=None):
        """Return the photo gallery for this farm."""
        farm = self.get_object()
        photos = farm.photos.all()
        serializer = FarmPhotoSerializer(photos, many=True)
        return Response(serializer.data)


class FarmCertificationViewSet(viewsets.ModelViewSet):
    """Manage certifications for the authenticated farmer's farms."""

    serializer_class = FarmCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FarmCertification.objects.filter(
            farm__farmer__user=self.request.user
        )

    def perform_create(self, serializer):
        farm_id = self.request.data.get("farm")
        farm = Farm.objects.get(pk=farm_id, farmer__user=self.request.user)
        serializer.save(farm=farm)


class HarvestCalendarViewSet(viewsets.ModelViewSet):
    """Manage harvest calendar entries for the authenticated farmer."""

    serializer_class = HarvestCalendarSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HarvestCalendar.objects.filter(
            farm__farmer__user=self.request.user
        )

    def perform_create(self, serializer):
        farm_id = self.request.data.get("farm")
        farm = Farm.objects.get(pk=farm_id, farmer__user=self.request.user)
        serializer.save(farm=farm)


class FarmPhotoViewSet(viewsets.ModelViewSet):
    """Manage photos for the authenticated farmer's farms."""

    serializer_class = FarmPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FarmPhoto.objects.filter(farm__farmer__user=self.request.user)

    def perform_create(self, serializer):
        farm_id = self.request.data.get("farm")
        farm = Farm.objects.get(pk=farm_id, farmer__user=self.request.user)
        serializer.save(farm=farm)
