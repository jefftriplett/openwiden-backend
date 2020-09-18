from typing import List

from django.core.checks import Error, register
from django.apps import apps

from openwiden.apps import BaseAppConfig


@register()
def check_apps_unique_ids(app_configs, **kwargs) -> List[Error]:
    errors = []

    unique_apps = {}
    for app in apps.get_app_configs():
        if issubclass(app.__class__, BaseAppConfig):
            unique_id = getattr(app, "unique_id", None)
            app_class_name = app.__class__.__name__
            if unique_id is None:
                errors.append(Error(f"{app_class_name} has no unique_id"))
            else:
                if unique_id in unique_apps:
                    errors.append(
                        Error(
                            f"{app_class_name} with unique_id = {unique_id} clashes "
                            f"with {unique_apps.get(unique_id)} with the same unique_id"
                        )
                    )
                unique_apps[unique_id] = app_class_name

    return errors
