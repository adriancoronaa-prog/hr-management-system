from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudVacacionesViewSet, PeriodoVacacionalViewSet

router = DefaultRouter()
router.register('solicitudes', SolicitudVacacionesViewSet, basename='solicitudes')
router.register('periodos', PeriodoVacacionalViewSet, basename='periodos')

urlpatterns = [
    path('', include(router.urls)),
]
