from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularRedocView,
    SpectacularAPIView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/airport/", include("airport.urls", namespace="airport")),
    path("api/users/", include("user.urls", namespace="user")),
    path("api/", include("djoser.urls")),
    path("api/users/", include("djoser.urls.jwt")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path(
        "api/doc/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
