from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario
from .services import UsuarioService


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer para login que incluye datos del usuario"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['usuario'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'nombre': self.user.first_name,
            'apellidos': self.user.last_name,
            'rol': self.user.rol,
            'empresas': [
                {'id': str(e.id), 'nombre': e.razon_social}
                for e in self.user.empresas.filter(activa=True)
            ]
        }
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioSerializer(serializers.ModelSerializer):
    empresas = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'rol', 'empresas']
    
    def get_empresas(self, obj):
        return [
            {'id': str(e.id), 'nombre': e.razon_social}
            for e in obj.empresas.filter(activa=True)
        ]


class MeView(APIView):
    """Retorna datos del usuario autenticado"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


# ============ ENDPOINTS PUBLICOS ============

class ActivarCuentaView(APIView):
    """Activa una cuenta de usuario usando el token"""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Token requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = UsuarioService.activar_cuenta(token)

        if resultado['exito']:
            return Response({
                'mensaje': resultado['mensaje'],
                'email': resultado['usuario'].email
            })
        else:
            return Response(
                {'error': resultado['mensaje']},
                status=status.HTTP_400_BAD_REQUEST
            )


class SolicitarResetPasswordView(APIView):
    """Solicita reset de password"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response(
                {'error': 'Email requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = UsuarioService.solicitar_reset_password(email)
        return Response({'mensaje': resultado['mensaje']})


class ResetearPasswordView(APIView):
    """Resetea password usando token"""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        nuevo_password = request.data.get('password')

        if not token or not nuevo_password:
            return Response(
                {'error': 'Token y password son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(nuevo_password) < 8:
            return Response(
                {'error': 'El password debe tener al menos 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = UsuarioService.resetear_password(token, nuevo_password)

        if resultado['exito']:
            return Response({'mensaje': resultado['mensaje']})
        else:
            return Response(
                {'error': resultado['mensaje']},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReenviarActivacionView(APIView):
    """Reenvia email de activacion"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response(
                {'error': 'Email requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = UsuarioService.reenviar_activacion(email)

        if resultado['exito']:
            return Response({'mensaje': resultado['mensaje']})
        else:
            return Response(
                {'error': resultado['mensaje']},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============ ENDPOINTS AUTENTICADOS ============

class CambiarPasswordView(APIView):
    """Cambia el password del usuario autenticado"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password_actual = request.data.get('password_actual')
        password_nuevo = request.data.get('password_nuevo')

        if not password_actual or not password_nuevo:
            return Response(
                {'error': 'Password actual y nuevo son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password_nuevo) < 8:
            return Response(
                {'error': 'El nuevo password debe tener al menos 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = UsuarioService.cambiar_password(
            request.user,
            password_actual,
            password_nuevo
        )

        if resultado['exito']:
            return Response({'mensaje': resultado['mensaje']})
        else:
            return Response(
                {'error': resultado['mensaje']},
                status=status.HTTP_400_BAD_REQUEST
            )


class ActualizarPerfilView(APIView):
    """Actualiza perfil del usuario"""
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        resultado = UsuarioService.actualizar_perfil(request.user, request.data)
        return Response(resultado)


class MiPerfilView(APIView):
    """Obtiene el perfil completo del usuario"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        perfil = UsuarioService.obtener_mi_perfil(request.user)
        return Response(perfil)
