"""User and profile models for the FarmDirect platform."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model with role-based access."""

    class Role(models.TextChoices):
        CONSUMER = "consumer", _("Consumer")
        FARMER = "farmer", _("Farmer")
        ADMIN = "admin", _("Admin")

    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        default=Role.CONSUMER,
    )
    phone = models.CharField(_("phone number"), max_length=20, blank=True)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(_("date of birth"), blank=True, null=True)
    email_verified = models.BooleanField(_("email verified"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_farmer(self):
        return self.role == self.Role.FARMER

    @property
    def is_consumer(self):
        return self.role == self.Role.CONSUMER


class FarmerProfile(models.Model):
    """Extended profile information for farmers."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="farmer_profile",
    )
    bio = models.TextField(_("bio"), blank=True)
    farm_name = models.CharField(_("farm name"), max_length=200)
    farm_address = models.TextField(_("farm address"))
    city = models.CharField(_("city"), max_length=100)
    state = models.CharField(_("state / province"), max_length=100)
    zip_code = models.CharField(_("ZIP / postal code"), max_length=20)
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    longitude = models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    farm_size_acres = models.DecimalField(
        _("farm size (acres)"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    years_farming = models.PositiveIntegerField(
        _("years of farming experience"),
        default=0,
    )
    website = models.URLField(_("website"), blank=True)
    is_verified = models.BooleanField(_("verified farmer"), default=False)
    verified_at = models.DateTimeField(_("verified at"), blank=True, null=True)
    stripe_account_id = models.CharField(
        _("Stripe account ID"),
        max_length=100,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("farmer profile")
        verbose_name_plural = _("farmer profiles")

    def __str__(self):
        return f"{self.farm_name} ({self.user.get_full_name()})"


class ConsumerProfile(models.Model):
    """Extended profile information for consumers."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consumer_profile",
    )
    delivery_address = models.TextField(_("delivery address"), blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state / province"), max_length=100, blank=True)
    zip_code = models.CharField(_("ZIP / postal code"), max_length=20, blank=True)
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    longitude = models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    dietary_preferences = models.JSONField(
        _("dietary preferences"),
        default=list,
        blank=True,
        help_text=_("List of dietary preferences (e.g. vegan, gluten-free)."),
    )
    receive_newsletter = models.BooleanField(
        _("receive newsletter"),
        default=True,
    )
    stripe_customer_id = models.CharField(
        _("Stripe customer ID"),
        max_length=100,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("consumer profile")
        verbose_name_plural = _("consumer profiles")

    def __str__(self):
        return f"Consumer: {self.user.get_full_name()}"
