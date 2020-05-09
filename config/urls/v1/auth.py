from django.urls import path
from openwiden.users import views

app_name = "auth"

urlpatterns = [
    path("login/<str:vcs>/", views.oauth_login_view, name="login"),
    path("complete/<str:vcs>/", views.oauth_complete_view, name="complete"),
    path("refresh_token/", views.token_refresh_view, name="refresh_token"),
]
