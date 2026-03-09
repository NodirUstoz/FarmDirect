"""URL routes for the accounts app."""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/farmer/", views.FarmerProfileView.as_view(), name="farmer-profile"),
    path("profile/consumer/", views.ConsumerProfileView.as_view(), name="consumer-profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
]
