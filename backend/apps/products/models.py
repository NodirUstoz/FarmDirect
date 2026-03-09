"""Models for the product catalog, categories, and seasonal availability."""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from apps.farms.models import Farm


class Category(models.Model):
    """Product category (e.g. Vegetables, Fruits, Dairy)."""

    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(_("slug"), max_length=120, unique=True)
    description = models.TextField(_("description"), blank=True)
    image = models.ImageField(
        _("image"),
        upload_to="categories/%Y/%m/",
        blank=True,
        null=True,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
    )
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["sort_order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class FarmProduct(models.Model):
    """A product listed by a farm."""

    class Unit(models.TextChoices):
        POUND = "lb", _("Pound")
        OUNCE = "oz", _("Ounce")
        KILOGRAM = "kg", _("Kilogram")
        GRAM = "g", _("Gram")
        EACH = "each", _("Each")
        BUNCH = "bunch", _("Bunch")
        DOZEN = "dozen", _("Dozen")
        PINT = "pint", _("Pint")
        QUART = "quart", _("Quart")
        GALLON = "gallon", _("Gallon")
        BASKET = "basket", _("Basket")
        FLAT = "flat", _("Flat")
        CASE = "case", _("Case")

    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="products"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True,
    )
    name = models.CharField(_("product name"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=220)
    description = models.TextField(_("description"))
    short_description = models.CharField(
        _("short description"), max_length=300, blank=True
    )
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    compare_at_price = models.DecimalField(
        _("compare at price"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Original price before discount, if applicable."),
    )
    unit = models.CharField(
        _("unit"), max_length=20, choices=Unit.choices, default=Unit.POUND
    )
    stock_quantity = models.PositiveIntegerField(_("stock quantity"), default=0)
    low_stock_threshold = models.PositiveIntegerField(
        _("low stock threshold"), default=10
    )
    image = models.ImageField(
        _("main image"),
        upload_to="products/%Y/%m/",
        blank=True,
        null=True,
    )

    is_organic = models.BooleanField(_("organic"), default=False)
    is_non_gmo = models.BooleanField(_("non-GMO"), default=False)
    is_pesticide_free = models.BooleanField(_("pesticide-free"), default=False)

    is_active = models.BooleanField(_("active"), default=True)
    is_featured = models.BooleanField(_("featured"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("farm product")
        verbose_name_plural = _("farm products")
        ordering = ["-is_featured", "-created_at"]
        unique_together = ["farm", "slug"]

    def __str__(self):
        return f"{self.name} ({self.farm.name})"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def on_sale(self):
        return self.compare_at_price is not None and self.compare_at_price > self.price


class ProductImage(models.Model):
    """Additional images for a product."""

    product = models.ForeignKey(
        FarmProduct, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(_("image"), upload_to="products/gallery/%Y/%m/")
    alt_text = models.CharField(_("alt text"), max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(_("sort order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")
        ordering = ["sort_order"]


class SeasonalAvailability(models.Model):
    """Defines when a product is seasonally available."""

    class Season(models.TextChoices):
        SPRING = "spring", _("Spring")
        SUMMER = "summer", _("Summer")
        FALL = "fall", _("Fall")
        WINTER = "winter", _("Winter")
        YEAR_ROUND = "year_round", _("Year-round")

    product = models.ForeignKey(
        FarmProduct,
        on_delete=models.CASCADE,
        related_name="seasonal_availability",
    )
    season = models.CharField(
        _("season"), max_length=20, choices=Season.choices
    )
    start_month = models.PositiveSmallIntegerField(
        _("start month"), help_text=_("1 = January, 12 = December")
    )
    end_month = models.PositiveSmallIntegerField(
        _("end month"), help_text=_("1 = January, 12 = December")
    )
    year = models.PositiveIntegerField(
        _("year"), blank=True, null=True, help_text=_("Leave blank for recurring.")
    )
    notes = models.CharField(_("notes"), max_length=300, blank=True)
    is_pre_order = models.BooleanField(
        _("pre-order available"), default=False
    )
    expected_date = models.DateField(
        _("expected availability date"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("seasonal availability")
        verbose_name_plural = _("seasonal availabilities")
        ordering = ["start_month"]

    def __str__(self):
        return f"{self.product.name} - {self.get_season_display()}"
