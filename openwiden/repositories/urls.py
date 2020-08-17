from django.urls import path

from . import views

app_name = "repositories"

urlpatterns = [
    path("programming_languages/", views.programming_languages_view, name="programming_languages",),
]
