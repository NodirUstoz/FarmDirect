"""URL routes for the products app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "products"

router = DefaultRouter()
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"", views.FarmProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
