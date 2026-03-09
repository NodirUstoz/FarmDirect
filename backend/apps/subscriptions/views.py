"""Views for subscription plans and customer subscription boxes."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SubscriptionPlan, SubscriptionBox, SubscriptionOrder
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionBoxSerializer,
    SubscriptionBoxCreateSerializer,
    SubscriptionBoxUpdateSerializer,
    SubscriptionOrderSerializer,
)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Browse available subscription plans."""

    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class SubscriptionBoxViewSet(viewsets.ModelViewSet):
    """Manage subscription boxes for the authenticated customer."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SubscriptionBox.objects.filter(
            customer=self.request.user
        ).select_related("plan").prefetch_related("orders")

    def get_serializer_class(self):
        if self.action == "create":
            return SubscriptionBoxCreateSerializer
        if self.action in ("update", "partial_update"):
            return SubscriptionBoxUpdateSerializer
        return SubscriptionBoxSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], url_path="pause")
    def pause(self, request, pk=None):
        """Pause an active subscription."""
        box = self.get_object()
        if box.status != SubscriptionBox.Status.ACTIVE:
            return Response(
                {"message": "Only active subscriptions can be paused."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        box.status = SubscriptionBox.Status.PAUSED
        box.save(update_fields=["status", "updated_at"])
        return Response(SubscriptionBoxSerializer(box).data)

    @action(detail=True, methods=["post"], url_path="resume")
    def resume(self, request, pk=None):
        """Resume a paused subscription."""
        box = self.get_object()
        if box.status != SubscriptionBox.Status.PAUSED:
            return Response(
                {"message": "Only paused subscriptions can be resumed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        box.status = SubscriptionBox.Status.ACTIVE
        box.save(update_fields=["status", "updated_at"])
        return Response(SubscriptionBoxSerializer(box).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_subscription(self, request, pk=None):
        """Cancel a subscription."""
        box = self.get_object()
        if box.status == SubscriptionBox.Status.CANCELLED:
            return Response(
                {"message": "Subscription is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        box.status = SubscriptionBox.Status.CANCELLED
        box.save(update_fields=["status", "updated_at"])
        return Response(SubscriptionBoxSerializer(box).data)

    @action(detail=True, methods=["get"], url_path="orders")
    def orders(self, request, pk=None):
        """List all orders generated from this subscription."""
        box = self.get_object()
        orders = box.orders.all()
        serializer = SubscriptionOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="skip-next")
    def skip_next(self, request, pk=None):
        """Skip the next delivery for this subscription."""
        box = self.get_object()
        next_order = box.orders.filter(
            status=SubscriptionOrder.Status.PENDING
        ).first()

        if not next_order:
            return Response(
                {"message": "No upcoming delivery to skip."},
                status=status.HTTP_404_NOT_FOUND,
            )

        next_order.status = SubscriptionOrder.Status.SKIPPED
        next_order.save(update_fields=["status", "updated_at"])
        return Response(SubscriptionOrderSerializer(next_order).data)
