"""
URLs para el módulo de Desempeño
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CatalogoKPIViewSet, MisKPIsViewSet, KPIsEquipoViewSet,
    EvaluacionViewSet, RetroalimentacionViewSet
)

router = DefaultRouter()
router.register('catalogo-kpis', CatalogoKPIViewSet, basename='catalogo-kpis')
router.register('mis-kpis', MisKPIsViewSet, basename='mis-kpis')
router.register('equipo-kpis', KPIsEquipoViewSet, basename='equipo-kpis')
router.register('evaluaciones', EvaluacionViewSet, basename='evaluaciones')
router.register('retroalimentacion', RetroalimentacionViewSet, basename='retroalimentacion')

app_name = 'desempeno'

urlpatterns = [
    path('', include(router.urls)),
]
