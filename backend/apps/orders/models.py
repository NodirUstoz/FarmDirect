"""Models for orders, order items, and delivery scheduling."""

import uuid

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.farms.models import Farm
from apps.products.models import FarmProduct


class Order(models.Model):
    """A customer order, potentially spanning multiple farms."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        PROCESSING = "processing", _("Processing")
        READY = "ready", _("Ready for Delivery / Pickup")
        OUT_FOR_DELIVERY = "out_for_delivery", _("Out for Delivery")
        DELIVERED = "delivered", _("Delivered")
        PICKED_UP = "picked_up", _("Picked Up")
        CANCELLED = "cancelled", _("Cancelled")
        REFUNDED = "refunded", _("Refunded")

    class DeliveryMethod(models.TextChoices):
        DELIVERY = "delivery", _("Delivery")
        PICKUP = "pickup", _("Farm Pickup")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        _("order number"), max_length=30, unique=True, editable=False
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    delivery_method = models.CharField(
        _("delivery method"),
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.DELIVERY,
    )

    # Delivery address (snapshot at order time)
    delivery_address = models.TextField(_("delivery address"), blank=True)
    delivery_city = models.CharField(_("delivery city"), max_length=100, blank=True)
    delivery_state = models.CharField(_("delivery state"), max_length=100, blank=True)
    delivery_zip = models.CharField(_("delivery ZIP"), max_length=20, blank=True)

    subtotal = models.DecimalField(
        _("subtotal"), max_digits=10, decimal_places=2, default=0
    )
    delivery_fee = models.DecimalField(
        _("delivery fee"), max_digits=8, decimal_places=2, default=0
    )
    tax = models.DecimalField(
        _("tax"), max_digits=8, decimal_places=2, default=0
    )
    total = models.DecimalField(
        _("total"), max_digits=10, decimal_places=2, default=0
    )
    discount = models.DecimalField(
        _("discount"), max_digits=8, decimal_places=2, default=0
    )

    stripe_payment_intent_id = models.CharField(
        _("Stripe payment intent ID"), max_length=200, blank=True
    )
    paid_at = models.DateTimeField(_("paid at"), blank=True, null=True)
    notes = models.TextField(_("customer notes"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        from django.utils import timezone

        prefix = timezone.now().strftime("FD%Y%m%d")
        random_part = uuid.uuid4().hex[:6].upper()
        return f"{prefix}-{random_part}"

    def calculate_totals(self):
        """Recalculate order totals from line items."""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total = self.subtotal + self.delivery_fee + self.tax - self.discount
        self.save(update_fields=["subtotal", "total"])


class OrderItem(models.Model):
    """A single line item within an order."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        FarmProduct,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    farm = models.ForeignKey(
        Farm,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
    )
    # Snapshot fields so the record survives product changes / deletion
    product_name = models.CharField(_("product name"), max_length=200)
    product_price = models.DecimalField(
        _("unit price"), max_digits=10, decimal_places=2
    )
    product_unit = models.CharField(_("unit"), max_length=20)
    quantity = models.PositiveIntegerField(
        _("quantity"), validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def line_total(self):
        return self.product_price * self.quantity


class DeliverySchedule(models.Model):
    """Scheduling and tracking for order delivery."""

    class TimeSlot(models.TextChoices):
        MORNING = "morning", _("Morning (8 AM - 12 PM)")
        AFTERNOON = "afternoon", _("Afternoon (12 PM - 4 PM)")
        EVENING = "evening", _("Evening (4 PM - 8 PM)")

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="delivery_schedule"
    )
    scheduled_date = models.DateField(_("scheduled date"))
    time_slot = models.CharField(
        _("time slot"),
        max_length=20,
        choices=TimeSlot.choices,
        default=TimeSlot.MORNING,
    )
    actual_delivery_time = models.DateTimeField(
        _("actual delivery time"), blank=True, null=True
    )
    delivery_notes = models.TextField(_("delivery notes"), blank=True)
    driver_name = models.CharField(_("driver name"), max_length=100, blank=True)
    tracking_number = models.CharField(
        _("tracking number"), max_length=100, blank=True
    )
    is_confirmed = models.BooleanField(_("confirmed"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("delivery schedule")
        verbose_name_plural = _("delivery schedules")
        ordering = ["scheduled_date", "time_slot"]

    def __str__(self):
        return (
            f"Delivery for {self.order.order_number} on "
            f"{self.scheduled_date} ({self.get_time_slot_display()})"
        )
