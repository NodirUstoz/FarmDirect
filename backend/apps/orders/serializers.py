"""Serializers for orders and delivery scheduling."""

from rest_framework import serializers

from .models import Order, OrderItem, DeliverySchedule
from apps.products.models import FarmProduct


class DeliveryScheduleSerializer(serializers.ModelSerializer):
    time_slot_display = serializers.CharField(
        source="get_time_slot_display", read_only=True
    )

    class Meta:
        model = DeliverySchedule
        fields = [
            "id",
            "scheduled_date",
            "time_slot",
            "time_slot_display",
            "actual_delivery_time",
            "delivery_notes",
            "driver_name",
            "tracking_number",
            "is_confirmed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "actual_delivery_time",
            "driver_name",
            "tracking_number",
            "is_confirmed",
            "created_at",
            "updated_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "farm",
            "product_name",
            "product_price",
            "product_unit",
            "quantity",
            "line_total",
        ]
        read_only_fields = [
            "id",
            "product_name",
            "product_price",
            "product_unit",
            "farm",
        ]


class OrderItemCreateSerializer(serializers.Serializer):
    """Used inside OrderCreateSerializer to accept cart items."""

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            FarmProduct.objects.get(pk=value, is_active=True)
        except FarmProduct.DoesNotExist:
            raise serializers.ValidationError("Product not found or inactive.")
        return value


class OrderCreateSerializer(serializers.Serializer):
    """Create a new order from a list of cart items."""

    items = OrderItemCreateSerializer(many=True, min_length=1)
    delivery_method = serializers.ChoiceField(
        choices=Order.DeliveryMethod.choices,
        default=Order.DeliveryMethod.DELIVERY,
    )
    delivery_address = serializers.CharField(required=False, allow_blank=True)
    delivery_city = serializers.CharField(required=False, allow_blank=True)
    delivery_state = serializers.CharField(required=False, allow_blank=True)
    delivery_zip = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    # Delivery scheduling
    scheduled_date = serializers.DateField(required=False)
    time_slot = serializers.ChoiceField(
        choices=DeliverySchedule.TimeSlot.choices,
        required=False,
        default=DeliverySchedule.TimeSlot.MORNING,
    )

    def validate(self, attrs):
        if attrs.get("delivery_method") == Order.DeliveryMethod.DELIVERY:
            if not attrs.get("delivery_address"):
                raise serializers.ValidationError(
                    {"delivery_address": "Delivery address is required."}
                )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        scheduled_date = validated_data.pop("scheduled_date", None)
        time_slot = validated_data.pop("time_slot", DeliverySchedule.TimeSlot.MORNING)
        user = self.context["request"].user

        order = Order.objects.create(
            customer=user,
            delivery_method=validated_data.get("delivery_method"),
            delivery_address=validated_data.get("delivery_address", ""),
            delivery_city=validated_data.get("delivery_city", ""),
            delivery_state=validated_data.get("delivery_state", ""),
            delivery_zip=validated_data.get("delivery_zip", ""),
            notes=validated_data.get("notes", ""),
        )

        for item_data in items_data:
            product = FarmProduct.objects.get(pk=item_data["product_id"])
            OrderItem.objects.create(
                order=order,
                product=product,
                farm=product.farm,
                product_name=product.name,
                product_price=product.price,
                product_unit=product.get_unit_display(),
                quantity=item_data["quantity"],
            )
            # Decrement stock
            product.stock_quantity = max(
                0, product.stock_quantity - item_data["quantity"]
            )
            product.save(update_fields=["stock_quantity"])

        order.calculate_totals()

        # Create delivery schedule if applicable
        if scheduled_date and order.delivery_method == Order.DeliveryMethod.DELIVERY:
            DeliverySchedule.objects.create(
                order=order,
                scheduled_date=scheduled_date,
                time_slot=time_slot,
            )

        return order


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight order representation for list views."""

    item_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "status_display",
            "delivery_method",
            "subtotal",
            "delivery_fee",
            "tax",
            "discount",
            "total",
            "item_count",
            "created_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full order detail with items and delivery schedule."""

    items = OrderItemSerializer(many=True, read_only=True)
    delivery_schedule = DeliveryScheduleSerializer(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    delivery_method_display = serializers.CharField(
        source="get_delivery_method_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer",
            "status",
            "status_display",
            "delivery_method",
            "delivery_method_display",
            "delivery_address",
            "delivery_city",
            "delivery_state",
            "delivery_zip",
            "subtotal",
            "delivery_fee",
            "tax",
            "discount",
            "total",
            "stripe_payment_intent_id",
            "paid_at",
            "notes",
            "items",
            "delivery_schedule",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "customer",
            "subtotal",
            "total",
            "stripe_payment_intent_id",
            "paid_at",
            "created_at",
            "updated_at",
        ]


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Update only the order status."""

    status = serializers.ChoiceField(choices=Order.Status.choices)

    def validate_status(self, value):
        order = self.context.get("order")
        if not order:
            return value

        valid_transitions = {
            Order.Status.PENDING: [Order.Status.CONFIRMED, Order.Status.CANCELLED],
            Order.Status.CONFIRMED: [Order.Status.PROCESSING, Order.Status.CANCELLED],
            Order.Status.PROCESSING: [Order.Status.READY, Order.Status.CANCELLED],
            Order.Status.READY: [
                Order.Status.OUT_FOR_DELIVERY,
                Order.Status.PICKED_UP,
                Order.Status.CANCELLED,
            ],
            Order.Status.OUT_FOR_DELIVERY: [Order.Status.DELIVERED],
        }

        allowed = valid_transitions.get(order.status, [])
        if value not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition from '{order.get_status_display()}' to "
                f"'{dict(Order.Status.choices).get(value)}'."
            )
        return value
