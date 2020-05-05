from rest_framework_nested import routers
from django.urls import path, include

from openwiden.repositories import views as repository_views
from openwiden.users import views as user_views
from openwiden.webhooks import views as webhook_views

router = routers.DefaultRouter()

# Repositories
router.register("repositories", repository_views.Repository, basename="repository")
repository_router = routers.NestedSimpleRouter(router, "repositories", lookup="repository")
repository_router.register("issues", repository_views.Issue, basename="issue")

# User
router.register("users", user_views.UserViewSet, basename="user")
router.register("user/repositories", repository_views.UserRepositories, basename="user-repos")

urlpatterns = [
    path("auth/", include(("config.urls.v1.auth", "auth"), namespace="auth")),
    path("user/", user_views.user_by_token_view, name="user"),
    path("webhooks/<webhook_id>/receive/", webhook_views.repository_webhook_view, name="repository-webhook"),
]

urlpatterns += router.urls
urlpatterns += repository_router.urls
