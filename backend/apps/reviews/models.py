"""Models for product and farm reviews."""

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.farms.models import Farm
from apps.products.models import FarmProduct


class Review(models.Model):
    """A customer review for a product or farm."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name="reviews",
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        FarmProduct,
        on_delete=models.CASCADE,
        related_name="reviews",
        blank=True,
        null=True,
    )
    rating = models.PositiveSmallIntegerField(
        _("rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    title = models.CharField(_("title"), max_length=200, blank=True)
    body = models.TextField(_("review body"))
    image = models.ImageField(
        _("image"),
        upload_to="reviews/%Y/%m/",
        blank=True,
        null=True,
    )
    is_verified_purchase = models.BooleanField(
        _("verified purchase"), default=False
    )
    is_approved = models.BooleanField(_("approved"), default=True)
    helpful_count = models.PositiveIntegerField(_("helpful votes"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(farm__isnull=False, product__isnull=True)
                    | models.Q(farm__isnull=True, product__isnull=False)
                ),
                name="review_farm_or_product",
            )
        ]

    def __str__(self):
        target = self.farm.name if self.farm else self.product.name
        return f"Review by {self.author.get_full_name()} on {target} ({self.rating}/5)"


class ReviewReply(models.Model):
    """Farmer or admin reply to a review."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="replies"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_replies",
    )
    body = models.TextField(_("reply body"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("review reply")
        verbose_name_plural = _("review replies")
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by {self.author.get_full_name()} on review {self.review.pk}"
