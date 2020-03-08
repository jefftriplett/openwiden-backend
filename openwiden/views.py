from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas import get_schema_view


schema_view = get_schema_view(
    title="OpenWiden",
    description="OpenWiden API documentation.",
    version="1.0.0",
    permission_classes=(permissions.AllowAny,),
    renderer_classes=(JSONOpenAPIRenderer,),
)


class SwaggerView(TemplateView):
    template_name = "swagger.html"
    extra_context = {"schema_url": "openapi-schema"}


swagger_view = SwaggerView.as_view()
