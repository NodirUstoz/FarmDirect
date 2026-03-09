"""Views for order management."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, DeliverySchedule
from .serializers import (
    OrderCreateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderStatusUpdateSerializer,
    DeliveryScheduleSerializer,
)
from .tasks import send_order_confirmation


class IsOrderOwner(permissions.BasePermission):
    """Customers see their own orders; farmers see orders containing their products."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Customer who placed the order
        if obj.customer == user:
            return True
        # Farmer whose products are in the order
        if user.is_farmer:
            return obj.items.filter(farm__farmer__user=user).exists()
        return False


class OrderViewSet(viewsets.ModelViewSet):
    """
    Orders: create, list, retrieve, update status.
    """

    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related("items", "delivery_schedule")

        if user.is_farmer:
            # Farmers see orders that contain their products
            qs = qs.filter(items__farm__farmer__user=user).distinct()
        else:
            qs = qs.filter(customer=user)

        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "list":
            return OrderListSerializer
        return OrderDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Fire async confirmation email
        send_order_confirmation.delay(str(order.id))

        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        """Update order status with transition validation."""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(
            data=request.data, context={"order": order}
        )
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data["status"]
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderDetailSerializer(order).data)

    @action(detail=True, methods=["get", "patch"], url_path="delivery")
    def delivery(self, request, pk=None):
        """View or update delivery schedule for an order."""
        order = self.get_object()

        if request.method == "GET":
            try:
                schedule = order.delivery_schedule
            except DeliverySchedule.DoesNotExist:
                return Response(
                    {"message": "No delivery schedule for this order."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(DeliveryScheduleSerializer(schedule).data)

        # PATCH
        try:
            schedule = order.delivery_schedule
        except DeliverySchedule.DoesNotExist:
            return Response(
                {"message": "No delivery schedule to update."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DeliveryScheduleSerializer(
            schedule, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel an order if it has not been delivered yet."""
        order = self.get_object()
        non_cancellable = {
            Order.Status.DELIVERED,
            Order.Status.PICKED_UP,
            Order.Status.REFUNDED,
            Order.Status.CANCELLED,
        }
        if order.status in non_cancellable:
            return Response(
                {"message": "This order cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.save(update_fields=["stock_quantity"])

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderDetailSerializer(order).data)
