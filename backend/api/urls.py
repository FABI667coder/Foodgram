from django.urls import include, path, re_path
from rest_framework.authtoken import views


urlpatterns = [
    path("", include("djoser.urls")),
    re_path(r"auth/", include("djoser.urls.authtoken")),
]