from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import OAuthLoginView, OAuthCompleteView, UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


app_name = "users"


router = DefaultRouter()
router.register("", UserViewSet, basename="user")


urlpatterns = [
    path("login/<str:provider>/", OAuthLoginView.as_view(), name="login"),
    path("complete/<str:provider>/", OAuthCompleteView.as_view(), name="complete"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
urlpatterns += router.urls
