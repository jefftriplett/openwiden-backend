from django.urls import path

from . import views

app_name = "openwiden.webhooks"

urlpatterns = [
    path("github/<int:id>/receive/", views.github_webhook_view, name="github"),
]
