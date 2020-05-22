import typing as t

from openwiden import exceptions
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="OpenWiden API",
        default_version="v1",
        description="OpenWiden - An Open Source Project Search Platform.",
        contact=openapi.Contact(email="stefanitsky.mozdor@gmail.com"),
        license=openapi.License(name="GNU General Public License v3"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def exception_handler(exception, context) -> t.Optional[Response]:
    """
    Custom exception handler.
    """
    if isinstance(exception, exceptions.ServiceException):
        return Response(data=exception.description, status=status.HTTP_400_BAD_REQUEST)
    else:
        return drf_exception_handler(exception, context)
