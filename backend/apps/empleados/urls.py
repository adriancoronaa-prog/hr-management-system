from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpleadoViewSet

router = DefaultRouter()
router.register('', EmpleadoViewSet, basename='empleados')

urlpatterns = [
    path('', include(router.urls)),
]
