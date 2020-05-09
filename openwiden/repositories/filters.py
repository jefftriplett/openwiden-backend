from django_filters import rest_framework as filters

from openwiden.repositories import models
from openwiden import enums


class Repository(filters.FilterSet):
    vcs = filters.ChoiceFilter(choices=enums.VersionControlService.choices)

    stars_count_gte = filters.NumberFilter(field_name="stars_count", lookup_expr="gte")
    open_issues_count_gte = filters.NumberFilter(field_name="open_issues_count", lookup_expr="gte")
    forks_count_gte = filters.NumberFilter(field_name="forks_count", lookup_expr="gte")

    created_at = filters.DateFromToRangeFilter()
    updated_at = filters.DateFromToRangeFilter()

    class Meta:
        model = models.Repository
        fields = (
            "vcs",
            "stars_count_gte",
            "open_issues_count_gte",
            "forks_count_gte",
            "created_at",
            "updated_at",
        )
