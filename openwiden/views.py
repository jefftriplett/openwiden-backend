import typing as t

from openwiden import exceptions
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


openapi_info = openapi.Info(
    title="OpenWiden API",
    default_version="v1",
    description="OpenWiden - An Open Source Project Search Platform.",
    contact=openapi.Contact(email="stefanitsky.mozdor@gmail.com"),
    license=openapi.License(name="GNU General Public License v3"),
)

schema_view = get_schema_view(info=openapi_info, public=True, permission_classes=(permissions.AllowAny,),)


def exception_handler(exception, context) -> t.Optional[Response]:
    """
    Custom exception handler.
    """
    if isinstance(exception, exceptions.ServiceException):
        return Response(data=exception.detail, status=exception.status_code)
    else:
        return drf_exception_handler(exception, context)
