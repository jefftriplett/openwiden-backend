from rest_framework_nested import routers
from django.urls import path, include

from openwiden.repositories import views as repository_views
from openwiden.users import views as users_views
from openwiden.webhooks import views as webhook_views, urls as webhook_urls

app_name = "v1"

router = routers.DefaultRouter()

# Repositories
router.register("repositories", repository_views.Repository, basename="repo")
repository_router = routers.NestedSimpleRouter(router, "repositories", lookup="repository")
repository_router.register("issues", repository_views.Issue, basename="repo-issue")
router.register("user/repositories", repository_views.UserRepositories, basename="user-repo")

# Users
router.register("users", users_views.UserViewSet, basename="user")

auth_urlpatterns = [
    path("auth/login/<str:vcs>/", users_views.oauth_login_view, name="login"),
    path("auth/complete/<str:vcs>/", users_views.oauth_complete_view, name="complete"),
    path("auth/refresh_token/", users_views.token_refresh_view, name="refresh_token"),
]

urlpatterns = [
    path("webhooks/<str:id>/receive/", webhook_views.repository_webhook_view, name="repo-webhook-receive"),
    path("webhooks/", include(webhook_urls, namespace="webhooks")),
]

urlpatterns += auth_urlpatterns
urlpatterns += router.urls
urlpatterns += repository_router.urls
