"""
URLs para el Chat con IA
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversacionViewSet, ChatView, DocumentoProcesadoViewSet

router = DefaultRouter()
router.register(r'conversaciones', ConversacionViewSet, basename='conversacion')
router.register(r'documentos', DocumentoProcesadoViewSet, basename='documento')

app_name = 'chat'

urlpatterns = [
    path('', include(router.urls)),
    path('mensaje/', ChatView.as_view(), name='mensaje'),
]