"""FarmDirect URL Configuration."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Admin
    path("api/admin/", admin.site.urls),

    # Auth (JWT)
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # App routes
    path("api/auth/", include("apps.accounts.urls")),
    path("api/farms/", include("apps.farms.urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
    path("api/reviews/", include("apps.reviews.urls")),

    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "FarmDirect Administration"
admin.site.site_title = "FarmDirect Admin"
admin.site.index_title = "Dashboard"
