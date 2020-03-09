from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from openwiden.views import schema_view
from repositories.views import RepositoryViewSet

router = DefaultRouter()
router.register("repositories", RepositoryViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/v1/", include((router.urls, "api-v1"), namespace="api-v1")),
    path("api/v1/", include(router.urls)),
    path("users/", include("users.urls", namespace="users")),
    # The 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# API documentation
urlpatterns += [
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    re_path(r"^docs/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]
