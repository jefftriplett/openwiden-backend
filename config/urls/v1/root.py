from rest_framework_nested import routers
from django.urls import path, include

from openwiden.repositories import views as repository_views
from openwiden.users import views as user_views

router = routers.DefaultRouter()

# Repositories
router.register("repositories", repository_views.Repository, basename="repository")
repository_router = routers.NestedSimpleRouter(router, "repositories", lookup="repository")
repository_router.register("issues", repository_views.Issue, basename="issue")

# Programming languages
router.register("programming_languages", repository_views.ProgrammingLanguage, basename="programming_language")

# User
router.register("users", user_views.UserViewSet, basename="user")

urlpatterns = [
    path("auth/", include(("config.urls.v1.auth", "auth"), namespace="auth")),
    path("user/", user_views.user_by_token_view, name="user"),
]

urlpatterns += router.urls
urlpatterns += repository_router.urls
