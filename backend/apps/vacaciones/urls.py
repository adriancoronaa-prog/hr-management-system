from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudVacacionesViewSet

router = DefaultRouter()
router.register('solicitudes', SolicitudVacacionesViewSet, basename='solicitudes')

urlpatterns = [
    path('', include(router.urls)),
]
