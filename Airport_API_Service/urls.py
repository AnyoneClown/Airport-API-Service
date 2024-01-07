from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/airport/", include("airport.urls", namespace="airport")),
    path("api/users/", include("user.urls", namespace="user")),
    path("api/", include("djoser.urls")),
    path("api/users/", include("djoser.urls.jwt")),
    path("__debug__/", include("debug_toolbar.urls")),
]
