"""
Views para integraciones OAuth (Google Calendar, etc.)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.conf import settings
from django.http import HttpResponseRedirect
import logging

from .models import ConfiguracionGoogleCalendar
from .google_calendar import GoogleCalendarService

logger = logging.getLogger(__name__)


class GoogleCalendarAuthView(APIView):
    """Obtiene la URL de autorizacion OAuth para Google Calendar"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.query_params.get('empresa_id')

        if not empresa_id:
            return Response({'error': 'empresa_id es requerido'}, status=400)

        if request.user.rol not in ['admin', 'administrador']:
            if not request.user.empresas.filter(id=empresa_id).exists():
                return Response({'error': 'No tienes acceso a esta empresa'}, status=403)

        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            return Response(
                {'error': 'Credenciales de Google no configuradas en el servidor'},
                status=500
            )

        try:
            auth_url = GoogleCalendarService.obtener_url_autorizacion(
                empresa_id=str(empresa_id),
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )
            return Response({'auth_url': auth_url})
        except Exception as e:
            logger.error(f"Error generando URL OAuth: {e}")
            return Response({'error': str(e)}, status=500)


class GoogleCalendarAuthorizeView(APIView):
    """Redirige directamente a Google para autorizacion"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.query_params.get('empresa_id')

        if not empresa_id:
            return Response({'error': 'empresa_id es requerido'}, status=400)

        if request.user.rol not in ['admin', 'administrador']:
            if not request.user.empresas.filter(id=empresa_id).exists():
                return Response({'error': 'No tienes acceso'}, status=403)

        try:
            auth_url = GoogleCalendarService.obtener_url_autorizacion(
                empresa_id=str(empresa_id),
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )
            return HttpResponseRedirect(auth_url)
        except Exception as e:
            logger.error(f"Error en redirect OAuth: {e}")
            return Response({'error': str(e)}, status=500)


class GoogleCalendarCallbackView(APIView):
    """Callback de Google OAuth"""
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get('code')
        state = request.query_params.get('state')  # empresa_id
        error = request.query_params.get('error')

        frontend_url = settings.FRONTEND_URL

        if error:
            logger.error(f"OAuth error: {error}")
            return HttpResponseRedirect(f"{frontend_url}/configuracion?error={error}")

        if not code or not state:
            return HttpResponseRedirect(f"{frontend_url}/configuracion?error=missing_params")

        try:
            from apps.empresas.models import Empresa
            empresa = Empresa.objects.get(id=state)
        except Empresa.DoesNotExist:
            return HttpResponseRedirect(f"{frontend_url}/configuracion?error=empresa_not_found")

        try:
            authorization_response = request.build_absolute_uri()

            resultado = GoogleCalendarService.procesar_callback(
                authorization_response=authorization_response,
                redirect_uri=settings.GOOGLE_REDIRECT_URI
            )

            config, created = ConfiguracionGoogleCalendar.objects.get_or_create(
                empresa=empresa,
                defaults={
                    'credentials_json': resultado['credentials_json'],
                    'refresh_token': resultado['refresh_token'],
                    'activo': True
                }
            )

            if not created:
                config.credentials_json = resultado['credentials_json']
                if resultado['refresh_token']:
                    config.refresh_token = resultado['refresh_token']
                config.activo = True
                config.error_ultimo = ''
                config.save()

            logger.info(f"Google Calendar autorizado para {empresa.razon_social}")
            return HttpResponseRedirect(f"{frontend_url}/configuracion?success=google_calendar")

        except Exception as e:
            logger.error(f"Error en callback OAuth: {e}")
            return HttpResponseRedirect(f"{frontend_url}/configuracion?error=oauth_failed")


class GoogleCalendarStatusView(APIView):
    """Estado de la conexion con Google Calendar"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.query_params.get('empresa_id')

        if not empresa_id:
            return Response({'error': 'empresa_id es requerido'}, status=400)

        try:
            from apps.empresas.models import Empresa
            empresa = Empresa.objects.get(id=empresa_id)
            config = empresa.config_google_calendar

            service = GoogleCalendarService(config)
            conectado = service.service is not None

            return Response({
                'configurado': True,
                'activo': config.activo,
                'conectado': conectado,
                'ultima_sincronizacion': config.ultima_sincronizacion,
                'calendar_id': config.calendar_id,
                'error': config.error_ultimo if not conectado else None
            })

        except ConfiguracionGoogleCalendar.DoesNotExist:
            return Response({
                'configurado': False,
                'activo': False,
                'conectado': False
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class GoogleCalendarDisconnectView(APIView):
    """Desconecta Google Calendar"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        empresa_id = request.data.get('empresa_id')

        if not empresa_id:
            return Response({'error': 'empresa_id es requerido'}, status=400)

        if request.user.rol not in ['admin', 'administrador']:
            if not request.user.empresas.filter(id=empresa_id).exists():
                return Response({'error': 'No tienes acceso'}, status=403)

        try:
            from apps.empresas.models import Empresa
            config = Empresa.objects.get(id=empresa_id).config_google_calendar
            config.credentials_json = ''
            config.refresh_token = ''
            config.activo = False
            config.save()

            return Response({'mensaje': 'Google Calendar desconectado'})
        except Exception as e:
            return Response({'error': str(e)}, status=404)
