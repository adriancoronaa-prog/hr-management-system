"""
Servicio de integracion con Google Calendar
"""
import json
import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Scopes necesarios
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """Servicio para interactuar con Google Calendar API"""

    def __init__(self, config):
        """
        Args:
            config: ConfiguracionGoogleCalendar instance
        """
        self.config = config
        self.service = None
        self._inicializar_servicio()

    def _inicializar_servicio(self):
        """Inicializa el servicio de Google Calendar"""
        if not self.config or not self.config.credentials_json:
            return

        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            creds_data = json.loads(self.config.credentials_json)
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

            # Refrescar si expiro
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Guardar credenciales actualizadas
                self.config.credentials_json = creds.to_json()
                self.config.save()

            self.service = build('calendar', 'v3', credentials=creds)

        except Exception as e:
            logger.error(f"Error inicializando Google Calendar: {e}")
            self.config.error_ultimo = str(e)
            self.config.save()

    @classmethod
    def obtener_url_autorizacion(cls, empresa_id: str, redirect_uri: str) -> str:
        """Genera URL para autorizar acceso a Google Calendar"""
        from google_auth_oauthlib.flow import Flow

        client_config = {
            "web": {
                "client_id": getattr(settings, 'GOOGLE_CLIENT_ID', ''),
                "client_secret": getattr(settings, 'GOOGLE_CLIENT_SECRET', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }

        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = redirect_uri

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=empresa_id
        )

        return authorization_url

    @classmethod
    def procesar_callback(cls, authorization_response: str, redirect_uri: str) -> Dict:
        """Procesa el callback de OAuth y retorna las credenciales"""
        from google_auth_oauthlib.flow import Flow

        client_config = {
            "web": {
                "client_id": getattr(settings, 'GOOGLE_CLIENT_ID', ''),
                "client_secret": getattr(settings, 'GOOGLE_CLIENT_SECRET', ''),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }

        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = redirect_uri

        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        return {
            'credentials_json': credentials.to_json(),
            'refresh_token': credentials.refresh_token or ''
        }

    def crear_evento(
        self,
        titulo: str,
        fecha_inicio: date,
        fecha_fin: date,
        descripcion: str = '',
        todo_el_dia: bool = True,
        color_id: str = None
    ) -> Optional[str]:
        """
        Crea un evento en Google Calendar

        Returns:
            ID del evento creado o None si fallo
        """
        if not self.service:
            return None

        calendar_id = self.config.calendar_id or 'primary'

        if todo_el_dia:
            evento = {
                'summary': titulo,
                'description': descripcion,
                'start': {'date': fecha_inicio.strftime('%Y-%m-%d')},
                'end': {'date': fecha_fin.strftime('%Y-%m-%d')},
            }
        else:
            evento = {
                'summary': titulo,
                'description': descripcion,
                'start': {
                    'dateTime': datetime.combine(fecha_inicio, datetime.min.time()).isoformat(),
                    'timeZone': 'America/Mexico_City'
                },
                'end': {
                    'dateTime': datetime.combine(fecha_fin, datetime.min.time()).isoformat(),
                    'timeZone': 'America/Mexico_City'
                },
            }

        if color_id:
            evento['colorId'] = color_id

        try:
            from googleapiclient.errors import HttpError
            result = self.service.events().insert(
                calendarId=calendar_id,
                body=evento
            ).execute()

            return result.get('id')

        except Exception as e:
            logger.error(f"Error creando evento: {e}")
            return None

    def actualizar_evento(self, event_id: str, **kwargs) -> bool:
        """Actualiza un evento existente"""
        if not self.service:
            return False

        calendar_id = self.config.calendar_id or 'primary'

        try:
            # Obtener evento actual
            evento = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Actualizar campos
            for key, value in kwargs.items():
                if key in ['titulo', 'summary']:
                    evento['summary'] = value
                elif key in ['descripcion', 'description']:
                    evento['description'] = value

            self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=evento
            ).execute()

            return True

        except Exception as e:
            logger.error(f"Error actualizando evento: {e}")
            return False

    def eliminar_evento(self, event_id: str) -> bool:
        """Elimina un evento"""
        if not self.service:
            return False

        calendar_id = self.config.calendar_id or 'primary'

        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True

        except Exception as e:
            logger.error(f"Error eliminando evento: {e}")
            return False

    def listar_eventos(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Dict]:
        """Lista eventos en un rango de fechas"""
        if not self.service:
            return []

        calendar_id = self.config.calendar_id or 'primary'

        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=fecha_inicio.isoformat() + 'Z',
                timeMax=fecha_fin.isoformat() + 'Z',
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])

        except Exception as e:
            logger.error(f"Error listando eventos: {e}")
            return []


class SincronizadorCalendario:
    """Sincroniza eventos del sistema con Google Calendar"""

    def __init__(self, empresa):
        self.empresa = empresa
        self.config = getattr(empresa, 'config_google_calendar', None)
        self.service = GoogleCalendarService(self.config) if self.config else None

    def sincronizar_vacaciones(self, solicitud_vacaciones) -> Optional[str]:
        """Sincroniza una solicitud de vacaciones aprobada"""
        if not self.service or not self.config.sincronizar_vacaciones:
            return None

        from .models import EventoSincronizado

        empleado = solicitud_vacaciones.empleado

        # Crear evento
        titulo = f"Vacaciones - {empleado.nombre_completo}"
        descripcion = f"Vacaciones de {empleado.nombre_completo}\nDepartamento: {empleado.departamento or 'N/A'}"

        event_id = self.service.crear_evento(
            titulo=titulo,
            fecha_inicio=solicitud_vacaciones.fecha_inicio,
            fecha_fin=solicitud_vacaciones.fecha_fin + timedelta(days=1),
            descripcion=descripcion,
            todo_el_dia=True,
            color_id='2'  # Verde
        )

        if event_id:
            EventoSincronizado.objects.create(
                empresa=self.empresa,
                empleado=empleado,
                tipo='vacaciones',
                titulo=titulo,
                descripcion=descripcion,
                fecha_inicio=solicitud_vacaciones.fecha_inicio,
                fecha_fin=solicitud_vacaciones.fecha_fin,
                google_event_id=event_id,
                google_calendar_id=self.config.calendar_id or 'primary',
                sincronizado=True,
                fecha_sincronizacion=timezone.now()
            )

        return event_id

    def sincronizar_cumpleanos_anual(self) -> int:
        """Sincroniza cumpleanos de todos los empleados activos"""
        if not self.service or not self.config.sincronizar_cumpleanos:
            return 0

        from apps.empleados.models import Empleado
        from .models import EventoSincronizado

        empleados = Empleado.objects.filter(
            empresa=self.empresa,
            estado='activo',
            fecha_nacimiento__isnull=False
        )

        ano_actual = date.today().year
        eventos_creados = 0

        for emp in empleados:
            # Verificar si ya existe para este ano
            existe = EventoSincronizado.objects.filter(
                empleado=emp,
                tipo='cumpleanos',
                fecha_inicio__year=ano_actual
            ).exists()

            if existe:
                continue

            # Crear evento de cumpleanos
            try:
                fecha_cumple = date(ano_actual, emp.fecha_nacimiento.month, emp.fecha_nacimiento.day)
            except ValueError:
                # 29 de febrero en ano no bisiesto
                fecha_cumple = date(ano_actual, 3, 1)

            titulo = f"Cumpleanos - {emp.nombre_completo}"

            event_id = self.service.crear_evento(
                titulo=titulo,
                fecha_inicio=fecha_cumple,
                fecha_fin=fecha_cumple + timedelta(days=1),
                descripcion=f"Cumpleanos de {emp.nombre_completo}",
                todo_el_dia=True,
                color_id='5'  # Amarillo
            )

            if event_id:
                EventoSincronizado.objects.create(
                    empresa=self.empresa,
                    empleado=emp,
                    tipo='cumpleanos',
                    titulo=titulo,
                    fecha_inicio=fecha_cumple,
                    fecha_fin=fecha_cumple,
                    google_event_id=event_id,
                    google_calendar_id=self.config.calendar_id or 'primary',
                    sincronizado=True,
                    fecha_sincronizacion=timezone.now()
                )
                eventos_creados += 1

        return eventos_creados

    def sincronizar_aniversarios_anual(self) -> int:
        """Sincroniza aniversarios laborales"""
        if not self.service or not self.config.sincronizar_aniversarios:
            return 0

        from apps.empleados.models import Empleado
        from .models import EventoSincronizado

        empleados = Empleado.objects.filter(
            empresa=self.empresa,
            estado='activo',
            fecha_ingreso__isnull=False
        )

        ano_actual = date.today().year
        eventos_creados = 0

        for emp in empleados:
            anos_servicio = ano_actual - emp.fecha_ingreso.year
            if anos_servicio < 1:
                continue

            existe = EventoSincronizado.objects.filter(
                empleado=emp,
                tipo='aniversario',
                fecha_inicio__year=ano_actual
            ).exists()

            if existe:
                continue

            try:
                fecha_aniv = date(ano_actual, emp.fecha_ingreso.month, emp.fecha_ingreso.day)
            except ValueError:
                fecha_aniv = date(ano_actual, 3, 1)

            titulo = f"Aniversario {anos_servicio} anos - {emp.nombre_completo}"

            event_id = self.service.crear_evento(
                titulo=titulo,
                fecha_inicio=fecha_aniv,
                fecha_fin=fecha_aniv + timedelta(days=1),
                descripcion=f"{emp.nombre_completo} cumple {anos_servicio} anos en la empresa",
                todo_el_dia=True,
                color_id='10'  # Verde oscuro
            )

            if event_id:
                EventoSincronizado.objects.create(
                    empresa=self.empresa,
                    empleado=emp,
                    tipo='aniversario',
                    titulo=titulo,
                    fecha_inicio=fecha_aniv,
                    fecha_fin=fecha_aniv,
                    google_event_id=event_id,
                    google_calendar_id=self.config.calendar_id or 'primary',
                    sincronizado=True,
                    fecha_sincronizacion=timezone.now()
                )
                eventos_creados += 1

        return eventos_creados


class AuditoriaService:
    """Servicio para registrar auditoria"""

    @classmethod
    def registrar(
        cls,
        usuario,
        accion: str,
        descripcion: str,
        objeto=None,
        datos_anteriores=None,
        datos_nuevos=None,
        request=None
    ):
        """Registra una accion en la auditoria"""
        from .models import RegistroAuditoria
        from django.contrib.contenttypes.models import ContentType

        registro = RegistroAuditoria(
            usuario=usuario,
            accion=accion,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
        )

        if objeto:
            registro.content_type = ContentType.objects.get_for_model(objeto)
            registro.object_id = str(objeto.pk)
            registro.modelo = objeto.__class__.__name__

        if request:
            registro.ip_address = cls._get_client_ip(request)
            registro.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        registro.save()
        return registro

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    @classmethod
    def obtener_historial(cls, objeto=None, usuario=None, limite=50):
        """Obtiene historial de auditoria"""
        from .models import RegistroAuditoria
        from django.contrib.contenttypes.models import ContentType

        qs = RegistroAuditoria.objects.all()

        if objeto:
            ct = ContentType.objects.get_for_model(objeto)
            qs = qs.filter(content_type=ct, object_id=str(objeto.pk))

        if usuario:
            qs = qs.filter(usuario=usuario)

        return qs[:limite]
