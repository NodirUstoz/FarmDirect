"""Models for farms, certifications, and harvest calendars."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import FarmerProfile


class Farm(models.Model):
    """Represents a farm that sells through the marketplace."""

    farmer = models.ForeignKey(
        FarmerProfile,
        on_delete=models.CASCADE,
        related_name="farms",
    )
    name = models.CharField(_("farm name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=220, unique=True)
    description = models.TextField(_("description"))
    short_description = models.CharField(
        _("short description"), max_length=300, blank=True
    )
    cover_image = models.ImageField(
        _("cover image"),
        upload_to="farms/covers/%Y/%m/",
        blank=True,
        null=True,
    )
    logo = models.ImageField(
        _("logo"),
        upload_to="farms/logos/%Y/%m/",
        blank=True,
        null=True,
    )
    address = models.TextField(_("address"))
    city = models.CharField(_("city"), max_length=100)
    state = models.CharField(_("state / province"), max_length=100)
    zip_code = models.CharField(_("ZIP / postal code"), max_length=20)
    latitude = models.DecimalField(
        _("latitude"), max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        _("longitude"), max_digits=9, decimal_places=6, blank=True, null=True
    )
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    email = models.EmailField(_("email"), blank=True)
    website = models.URLField(_("website"), blank=True)

    delivery_radius_miles = models.PositiveIntegerField(
        _("delivery radius (miles)"), default=50
    )
    accepts_pickup = models.BooleanField(_("accepts farm pickup"), default=True)
    accepts_delivery = models.BooleanField(_("accepts delivery"), default=True)
    minimum_order_amount = models.DecimalField(
        _("minimum order amount"),
        max_digits=8,
        decimal_places=2,
        default=0,
    )

    is_active = models.BooleanField(_("active"), default=True)
    is_featured = models.BooleanField(_("featured"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("farm")
        verbose_name_plural = _("farms")
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return self.name


class FarmPhoto(models.Model):
    """Gallery photos for a farm."""

    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(_("image"), upload_to="farms/gallery/%Y/%m/")
    caption = models.CharField(_("caption"), max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("farm photo")
        verbose_name_plural = _("farm photos")
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.farm.name} - Photo {self.pk}"


class FarmCertification(models.Model):
    """Certifications held by a farm (organic, GAP, etc.)."""

    class CertificationType(models.TextChoices):
        ORGANIC_USDA = "organic_usda", _("USDA Organic")
        ORGANIC_EU = "organic_eu", _("EU Organic")
        GAP = "gap", _("Good Agricultural Practices (GAP)")
        NON_GMO = "non_gmo", _("Non-GMO Project Verified")
        FAIR_TRADE = "fair_trade", _("Fair Trade Certified")
        ANIMAL_WELFARE = "animal_welfare", _("Animal Welfare Approved")
        BIODYNAMIC = "biodynamic", _("Biodynamic")
        PESTICIDE_FREE = "pesticide_free", _("Pesticide-Free")
        NATURALLY_GROWN = "naturally_grown", _("Certified Naturally Grown")
        OTHER = "other", _("Other")

    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="certifications"
    )
    certification_type = models.CharField(
        _("certification type"),
        max_length=30,
        choices=CertificationType.choices,
    )
    name = models.CharField(
        _("certification name"),
        max_length=200,
        help_text=_("Full name or description of the certification."),
    )
    certifying_body = models.CharField(
        _("certifying body"), max_length=200, blank=True
    )
    certificate_number = models.CharField(
        _("certificate number"), max_length=100, blank=True
    )
    issued_date = models.DateField(_("issued date"))
    expiry_date = models.DateField(_("expiry date"), blank=True, null=True)
    document = models.FileField(
        _("certificate document"),
        upload_to="farms/certifications/%Y/%m/",
        blank=True,
        null=True,
    )
    is_verified = models.BooleanField(_("verified"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("farm certification")
        verbose_name_plural = _("farm certifications")
        ordering = ["-issued_date"]
        unique_together = ["farm", "certification_type", "certificate_number"]

    def __str__(self):
        return f"{self.farm.name} - {self.get_certification_type_display()}"

    @property
    def is_expired(self):
        if self.expiry_date is None:
            return False
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()


class HarvestCalendar(models.Model):
    """Tracks what a farm plans to harvest and when."""

    class Season(models.TextChoices):
        SPRING = "spring", _("Spring")
        SUMMER = "summer", _("Summer")
        FALL = "fall", _("Fall")
        WINTER = "winter", _("Winter")
        YEAR_ROUND = "year_round", _("Year-round")

    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="harvest_entries"
    )
    product_name = models.CharField(_("product name"), max_length=200)
    season = models.CharField(
        _("season"), max_length=20, choices=Season.choices
    )
    start_month = models.PositiveSmallIntegerField(
        _("start month"),
        help_text=_("1 = January, 12 = December"),
    )
    end_month = models.PositiveSmallIntegerField(
        _("end month"),
        help_text=_("1 = January, 12 = December"),
    )
    expected_harvest_date = models.DateField(
        _("expected harvest date"), blank=True, null=True
    )
    notes = models.TextField(_("notes"), blank=True)
    is_available = models.BooleanField(_("currently available"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("harvest calendar entry")
        verbose_name_plural = _("harvest calendar entries")
        ordering = ["start_month"]

    def __str__(self):
        return f"{self.farm.name} - {self.product_name} ({self.get_season_display()})"
