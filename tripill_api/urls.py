from django.urls import include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib import admin
from routers import routers

schema_view = get_schema_view(
    openapi.Info(
        title="Tripill Api",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    re_path(r'^documents/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path('api/v1/', include(routers.url_patterns)),
    re_path('admin/', admin.site.urls),
]
