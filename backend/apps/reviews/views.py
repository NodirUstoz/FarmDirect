"""Views for reviews and replies."""

from django.db.models import Avg, Count, Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Review, ReviewReply
from .serializers import (
    ReviewSerializer,
    ReviewCreateSerializer,
    ReviewReplySerializer,
    ReviewStatsSerializer,
)


class IsReviewAuthor(permissions.BasePermission):
    """Only the review author can update or delete."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """CRUD operations for reviews."""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewAuthor]

    def get_queryset(self):
        qs = Review.objects.select_related(
            "author", "farm", "product"
        ).prefetch_related("replies__author")

        # Optional filtering
        farm_id = self.request.query_params.get("farm")
        product_id = self.request.query_params.get("product")
        if farm_id:
            qs = qs.filter(farm_id=farm_id)
        if product_id:
            qs = qs.filter(product_id=product_id)

        return qs.filter(is_approved=True)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ReviewCreateSerializer
        return ReviewSerializer

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Return aggregated review stats, optionally filtered by farm or product."""
        qs = Review.objects.filter(is_approved=True)
        farm_id = request.query_params.get("farm")
        product_id = request.query_params.get("product")
        if farm_id:
            qs = qs.filter(farm_id=farm_id)
        if product_id:
            qs = qs.filter(product_id=product_id)

        aggregation = qs.aggregate(
            average_rating=Avg("rating"),
            total_reviews=Count("id"),
        )
        # Rating distribution
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = qs.filter(rating=i).count()

        data = {
            "average_rating": round(aggregation["average_rating"] or 0, 1),
            "total_reviews": aggregation["total_reviews"],
            "rating_distribution": distribution,
        }
        serializer = ReviewStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="helpful")
    def mark_helpful(self, request, pk=None):
        """Increment the helpful counter on a review."""
        review = self.get_object()
        review.helpful_count += 1
        review.save(update_fields=["helpful_count"])
        return Response({"helpful_count": review.helpful_count})

    @action(detail=True, methods=["post"], url_path="reply")
    def reply(self, request, pk=None):
        """Add a reply to a review (typically from the farmer)."""
        review = self.get_object()
        serializer = ReviewReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(review=review, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
