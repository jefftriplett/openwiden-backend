from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from openwiden.users import views

urlpatterns = [
    path("login/<str:provider>/", views.OAuthLoginView.as_view(), name="login"),
    path("complete/<str:provider>/", views.OAuthCompleteView.as_view(), name="complete"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
