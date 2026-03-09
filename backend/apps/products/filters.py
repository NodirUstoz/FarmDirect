"""Filter sets for product listings."""

import django_filters

from .models import FarmProduct


class ProductFilter(django_filters.FilterSet):
    """Advanced filtering for the product catalog."""

    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(field_name="category__slug")
    farm = django_filters.CharFilter(field_name="farm__slug")
    season = django_filters.CharFilter(
        field_name="seasonal_availability__season", distinct=True
    )
    is_organic = django_filters.BooleanFilter()
    is_non_gmo = django_filters.BooleanFilter()
    is_pesticide_free = django_filters.BooleanFilter()
    in_stock = django_filters.BooleanFilter(
        method="filter_in_stock", label="In stock"
    )
    on_sale = django_filters.BooleanFilter(
        method="filter_on_sale", label="On sale"
    )

    class Meta:
        model = FarmProduct
        fields = [
            "category",
            "farm",
            "is_organic",
            "is_non_gmo",
            "is_pesticide_free",
            "is_featured",
            "unit",
        ]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)

    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.filter(
                compare_at_price__isnull=False,
                compare_at_price__gt=models.F("price"),
            )
        return queryset

    def filter_on_sale(self, queryset, name, value):
        from django.db.models import F

        if value:
            return queryset.filter(
                compare_at_price__isnull=False,
                compare_at_price__gt=F("price"),
            )
        return queryset
