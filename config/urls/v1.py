from openwiden.repositories import views
from rest_framework_nested import routers
from django.urls import path, include

from openwiden.users.views import UserRetrieveByTokenView
from openwiden.users.urls import users_urls, auth_urls

router = routers.DefaultRouter()

# Repositories
router.register("repositories", views.Repository, basename="repository")
repository_router = routers.NestedSimpleRouter(router, "repositories", lookup="repository")
repository_router.register("issues", views.Issue, basename="issue")
# Programming languages
router.register("programming_languages", views.ProgrammingLanguage, basename="programming_language")

urlpatterns = [
    path("auth/", include((auth_urls, "auth"), namespace="auth")),
    path("user/", UserRetrieveByTokenView.as_view(), name="user"),
    path("users/", include((users_urls, "users"), namespace="users")),
]

urlpatterns += router.urls
urlpatterns += repository_router.urls
