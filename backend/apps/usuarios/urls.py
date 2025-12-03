from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    MeView,
    ActivarCuentaView,
    SolicitarResetPasswordView,
    ResetearPasswordView,
    ReenviarActivacionView,
    CambiarPasswordView,
    ActualizarPerfilView,
    MiPerfilView,
)

urlpatterns = [
    # Auth
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),

    # Endpoints publicos
    path('activar/', ActivarCuentaView.as_view(), name='activar_cuenta'),
    path('solicitar-reset/', SolicitarResetPasswordView.as_view(), name='solicitar_reset'),
    path('reset-password/', ResetearPasswordView.as_view(), name='reset_password'),
    path('reenviar-activacion/', ReenviarActivacionView.as_view(), name='reenviar_activacion'),

    # Endpoints autenticados
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('perfil/', MiPerfilView.as_view(), name='mi_perfil'),
    path('perfil/actualizar/', ActualizarPerfilView.as_view(), name='actualizar_perfil'),
]
