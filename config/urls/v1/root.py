from rest_framework_nested import routers
from django.urls import path, include

from openwiden.repositories import views as repository_views
from openwiden.users import views as user_views
from openwiden.webhooks import views as webhook_views, urls as webhook_urls

app_name = "v1"

router = routers.DefaultRouter()

# Repositories
router.register("repositories", repository_views.Repository, basename="repo")
repository_router = routers.NestedSimpleRouter(router, "repositories", lookup="repository")
repository_router.register("issues", repository_views.Issue, basename="repo-issue")

# User
router.register("users", user_views.UserViewSet, basename="user")
router.register("user/repositories", repository_views.UserRepositories, basename="user-repo")

urlpatterns = [
    path("auth/", include("config.urls.v1.auth", namespace="auth")),
    path("webhooks/<str:id>/receive/", webhook_views.repository_webhook_view, name="repo-webhook-receive"),
    path("webhooks/", include(webhook_urls, namespace="webhooks")),
]

urlpatterns += router.urls
urlpatterns += repository_router.urls
