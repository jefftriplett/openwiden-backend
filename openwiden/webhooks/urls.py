from django.urls import path

from . import views

app_name = "openwiden.webhooks"

urlpatterns = [
    path("github/<uuid:id>/receive/", views.GithubWebhookView.as_view(), name="github"),
    path("gitlab/<uuid:id>/receive/", views.GitlabWebhookView.as_view(), name="gitlab"),
]
