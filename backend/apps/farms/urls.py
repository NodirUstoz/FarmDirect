"""URL routes for the farms app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "farms"

router = DefaultRouter()
router.register(r"", views.FarmViewSet, basename="farm")
router.register(r"certifications", views.FarmCertificationViewSet, basename="certification")
router.register(r"harvest-calendar", views.HarvestCalendarViewSet, basename="harvest-calendar")
router.register(r"photos", views.FarmPhotoViewSet, basename="farm-photo")

urlpatterns = [
    path("", include(router.urls)),
]
