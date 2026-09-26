from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "auth/",
        include("authentication.urls")
    ),

    path(
        "",
        include("core.urls")
    ),

    path(
        "app/",
        include("domain_app.urls")
    ),

    path(
        "ai/",
        include("ai_agent.urls")
    ),
]