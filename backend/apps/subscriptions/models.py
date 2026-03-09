"""Models for subscription boxes, plans, and recurring orders."""

import uuid

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.farms.models import Farm
from apps.products.models import FarmProduct, Category


class SubscriptionPlan(models.Model):
    """Defines a recurring subscription plan (e.g. Weekly Small Box)."""

    class Frequency(models.TextChoices):
        WEEKLY = "weekly", _("Weekly")
        BIWEEKLY = "biweekly", _("Every Two Weeks")
        MONTHLY = "monthly", _("Monthly")

    class Size(models.TextChoices):
        SMALL = "small", _("Small")
        MEDIUM = "medium", _("Medium")
        LARGE = "large", _("Large")
        FAMILY = "family", _("Family")

    name = models.CharField(_("plan name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=220, unique=True)
    description = models.TextField(_("description"))
    frequency = models.CharField(
        _("frequency"),
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )
    size = models.CharField(
        _("box size"),
        max_length=20,
        choices=Size.choices,
        default=Size.MEDIUM,
    )
    price = models.DecimalField(
        _("price"),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    compare_at_price = models.DecimalField(
        _("compare at price"),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
    )
    item_count = models.PositiveIntegerField(
        _("number of items"),
        default=8,
        help_text=_("Approximate number of items included."),
    )
    image = models.ImageField(
        _("image"),
        upload_to="subscriptions/plans/%Y/%m/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("subscription plan")
        verbose_name_plural = _("subscription plans")
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class SubscriptionBox(models.Model):
    """A specific box configuration for a subscriber."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        PAUSED = "paused", _("Paused")
        CANCELLED = "cancelled", _("Cancelled")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription_boxes",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    preferred_categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name="subscription_preferences",
        help_text=_("Product categories the subscriber prefers."),
    )
    preferred_farms = models.ManyToManyField(
        Farm,
        blank=True,
        related_name="subscription_preferences",
        help_text=_("Farms the subscriber prefers."),
    )
    exclude_items = models.JSONField(
        _("excluded items"),
        default=list,
        blank=True,
        help_text=_("List of product names or IDs to exclude."),
    )
    delivery_address = models.TextField(_("delivery address"))
    delivery_city = models.CharField(_("city"), max_length=100)
    delivery_state = models.CharField(_("state"), max_length=100)
    delivery_zip = models.CharField(_("ZIP"), max_length=20)
    delivery_notes = models.TextField(_("delivery notes"), blank=True)

    next_delivery_date = models.DateField(
        _("next delivery date"), blank=True, null=True
    )
    stripe_subscription_id = models.CharField(
        _("Stripe subscription ID"), max_length=200, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("subscription box")
        verbose_name_plural = _("subscription boxes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.plan.name}"


class SubscriptionOrder(models.Model):
    """An individual delivery generated from a subscription."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PREPARING = "preparing", _("Being Prepared")
        SHIPPED = "shipped", _("Shipped")
        DELIVERED = "delivered", _("Delivered")
        SKIPPED = "skipped", _("Skipped")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        SubscriptionBox,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    delivery_date = models.DateField(_("delivery date"))
    products = models.ManyToManyField(
        FarmProduct,
        through="SubscriptionOrderItem",
        related_name="subscription_orders",
    )
    total = models.DecimalField(
        _("total"), max_digits=10, decimal_places=2, default=0
    )
    notes = models.TextField(_("notes"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("subscription order")
        verbose_name_plural = _("subscription orders")
        ordering = ["-delivery_date"]

    def __str__(self):
        return f"Sub order {self.pk} for {self.subscription}"


class SubscriptionOrderItem(models.Model):
    """Line item in a subscription order."""

    subscription_order = models.ForeignKey(
        SubscriptionOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        FarmProduct,
        on_delete=models.SET_NULL,
        null=True,
    )
    product_name = models.CharField(_("product name"), max_length=200)
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("subscription order item")
        verbose_name_plural = _("subscription order items")

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
