from django_filters import rest_framework as filters

from .models import Repository


class RepositoryFilter(filters.FilterSet):
    version_control_service = filters.CharFilter(field_name="version_control_service", lookup_expr="host")

    star_count_gte = filters.NumberFilter(field_name="star_count", lookup_expr="gte")
    open_issues_count_gte = filters.NumberFilter(field_name="open_issues_count", lookup_expr="gte")
    forks_count_gte = filters.NumberFilter(field_name="forks_count", lookup_expr="gte")

    created_at = filters.DateFromToRangeFilter()
    updated_at = filters.DateFromToRangeFilter()

    programming_language = filters.CharFilter(field_name="programming_languages", lookup_expr="has_key")

    class Meta:
        model = Repository
        fields = (
            "version_control_service",
            "star_count_gte",
            "open_issues_count_gte",
            "forks_count_gte",
            "created_at",
            "updated_at",
            "programming_language",
        )
