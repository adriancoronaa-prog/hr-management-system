"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # APIs
    path('api/usuarios/', include('apps.usuarios.urls')),
    path('api/empresas/', include('apps.empresas.urls')),
    path('api/empleados/', include('apps.empleados.urls')),
    path('api/contratos/', include('apps.contratos.urls')),
    path('api/vacaciones/', include('apps.vacaciones.urls')),
    path('api/prestaciones/', include('apps.prestaciones.urls')),
    path('api/documentos/', include('apps.documentos.urls')),
    path('api/nomina/', include('apps.nomina.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/integraciones/', include('apps.integraciones.urls')),
    path('api/reportes/', include('apps.reportes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)