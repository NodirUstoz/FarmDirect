"""Views for the product catalog and categories."""

from django.db.models import Count
from rest_framework import viewsets, generics, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, FarmProduct, SeasonalAvailability
from .serializers import (
    CategorySerializer,
    FarmProductListSerializer,
    FarmProductDetailSerializer,
    FarmProductCreateUpdateSerializer,
    SeasonalAvailabilitySerializer,
)
from .filters import ProductFilter


class IsProductOwner(permissions.BasePermission):
    """Only the farmer who owns the product can modify it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.is_farmer
            and obj.farm.farmer.user == request.user
        )


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Browse product categories."""

    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Category.objects.filter(is_active=True).annotate(
            product_count=Count("products", distinct=True)
        )
        # Top-level categories only for list
        if self.action == "list":
            qs = qs.filter(parent__isnull=True)
        return qs


class FarmProductViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for farm products.
    - Public read access.
    - Farmers can create / update / delete their own products.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProductOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "farm__name"]
    ordering_fields = ["price", "name", "created_at", "stock_quantity"]

    def get_queryset(self):
        qs = FarmProduct.objects.select_related("farm", "category").prefetch_related(
            "images", "seasonal_availability"
        )
        if self.action == "list":
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return FarmProductListSerializer
        if self.action in ("create", "update", "partial_update"):
            return FarmProductCreateUpdateSerializer
        return FarmProductDetailSerializer

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Return featured products."""
        qs = self.get_queryset().filter(is_featured=True)[:12]
        serializer = FarmProductListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def seasonal(self, request):
        """Return products available in the current season."""
        from django.utils import timezone

        current_month = timezone.now().month
        qs = self.get_queryset().filter(
            seasonal_availability__start_month__lte=current_month,
            seasonal_availability__end_month__gte=current_month,
        ).distinct()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = FarmProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FarmProductListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-farm/(?P<farm_slug>[^/.]+)")
    def by_farm(self, request, farm_slug=None):
        """Return all products from a specific farm."""
        qs = self.get_queryset().filter(farm__slug=farm_slug)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = FarmProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FarmProductListSerializer(qs, many=True)
        return Response(serializer.data)
