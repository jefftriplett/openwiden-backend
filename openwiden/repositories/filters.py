from django.db.models import QuerySet
from django_filters import rest_framework as filters
from django_filters.constants import EMPTY_VALUES

from openwiden.repositories import models
from openwiden import enums


class ProgrammingLanguagesFilter(filters.Filter):
    def filter(self, qs: "QuerySet[models.Repository]", value: str) -> "QuerySet[models.Repository]":
        if value in EMPTY_VALUES:
            return qs
        return qs.filter(**{f"{self.field_name}__keys__overlap": value.split(",")}).order_by("-open_issues_count")


class Repository(filters.FilterSet):
    vcs = filters.ChoiceFilter(choices=enums.VersionControlService.choices)

    stars_count_gte = filters.NumberFilter(field_name="stars_count", lookup_expr="gte")
    open_issues_count_gte = filters.NumberFilter(field_name="open_issues_count", lookup_expr="gte")
    forks_count_gte = filters.NumberFilter(field_name="forks_count", lookup_expr="gte")

    created_at = filters.DateFromToRangeFilter()
    updated_at = filters.DateFromToRangeFilter()

    programming_languages = ProgrammingLanguagesFilter()

    class Meta:
        model = models.Repository
        fields = (
            "vcs",
            "stars_count_gte",
            "open_issues_count_gte",
            "forks_count_gte",
            "created_at",
            "updated_at",
            "programming_languages",
        )
