from django.urls import path
from rest_framework_nested import routers

from . import views

app_name = "openwiden.users"

# Auth
auth_urlpatterns = [
    path("auth/login/<str:vcs>/", views.oauth_login_view, name="login"),
    path("auth/complete/<str:vcs>/", views.oauth_complete_view, name="complete"),
    path("auth/refresh_token/", views.token_refresh_view, name="refresh_token"),
]

# Users
router = routers.SimpleRouter()
router.register("users", views.UserViewSet, basename="user")
user_urlpatterns = router.urls

# All
urlpatterns = auth_urlpatterns + user_urlpatterns
