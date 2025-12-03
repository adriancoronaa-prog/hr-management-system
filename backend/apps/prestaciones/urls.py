from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanPrestacionesViewSet, AjusteIndividualViewSet, PrestacionAdicionalViewSet

router = DefaultRouter()
router.register('planes', PlanPrestacionesViewSet, basename='planes')
router.register('ajustes', AjusteIndividualViewSet, basename='ajustes')
router.register('adicionales', PrestacionAdicionalViewSet, basename='adicionales')

urlpatterns = [
    path('', include(router.urls)),
]
