"""URL routes for the reviews app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "reviews"

router = DefaultRouter()
router.register(r"", views.ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
]
