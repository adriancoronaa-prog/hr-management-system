from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PeriodoNominaViewSet, 
    ReciboNominaViewSet,
    IncidenciaNominaViewSet,
    ParametrosIMSSViewSet
)

router = DefaultRouter()
router.register('periodos', PeriodoNominaViewSet, basename='periodo-nomina')
router.register('recibos', ReciboNominaViewSet, basename='recibo-nomina')
router.register('incidencias', IncidenciaNominaViewSet, basename='incidencia')
router.register('parametros-imss', ParametrosIMSSViewSet, basename='parametros-imss')

urlpatterns = [
    path('', include(router.urls)),
]
