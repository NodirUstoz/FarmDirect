"""URL routes for the subscriptions app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "subscriptions"

router = DefaultRouter()
router.register(r"plans", views.SubscriptionPlanViewSet, basename="plan")
router.register(r"boxes", views.SubscriptionBoxViewSet, basename="box")

urlpatterns = [
    path("", include(router.urls)),
]
