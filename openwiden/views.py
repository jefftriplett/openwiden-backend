from rest_framework import permissions
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
