from django.urls import path

from users.views import OAuthLoginView, OAuthCompleteView


app_name = "users"


urlpatterns = [
    path("login/<str:provider>/", OAuthLoginView.as_view(), name="login"),
    path("complete/<str:provider>/", OAuthCompleteView.as_view(), name="complete"),
]
