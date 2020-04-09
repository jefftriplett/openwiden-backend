from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework_nested import routers

from openwiden.views import schema_view
from openwiden.repositories import views
from users.views import UserRetrieveByTokenView
from users.urls import users_urls, auth_urls

router = routers.DefaultRouter()
router.register("repositories", views.Repository, basename="repository")
router.register("programming_languages", views.ProgrammingLanguage, basename="programming_language")

repository_router = routers.NestedSimpleRouter(router, "repositories", lookup="repository")
repository_router.register("issues", views.Issue, basename="issue")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("api/v1/", include(repository_router.urls)),
    path("auth/", include((auth_urls, "auth"), namespace="auth")),
    path("user/", UserRetrieveByTokenView.as_view(), name="user"),
    path("users/", include((users_urls, "users"), namespace="users")),
    # The 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# API documentation
urlpatterns += [
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    re_path(r"^docs/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]
