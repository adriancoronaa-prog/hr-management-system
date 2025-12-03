from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet

router = DefaultRouter()
router.register('', ContratoViewSet, basename='contratos')

urlpatterns = [
    path('', include(router.urls)),
]
