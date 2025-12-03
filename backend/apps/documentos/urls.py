from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaDocumentoViewSet, DocumentoEmpleadoViewSet, DocumentoViewSet

router = DefaultRouter()
router.register('categorias', CategoriaDocumentoViewSet, basename='categorias')
router.register('empleado', DocumentoEmpleadoViewSet, basename='documentos-empleado')
router.register('rag', DocumentoViewSet, basename='documentos-rag')

urlpatterns = [
    path('', include(router.urls)),
]
