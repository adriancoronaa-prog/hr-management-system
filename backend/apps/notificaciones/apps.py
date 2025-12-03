from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notificaciones'
    verbose_name = 'Notificaciones'

    def ready(self):
        """Registra las acciones de IA"""
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
            print("[OK] Acciones de Notificaciones registradas")
        except Exception as e:
            print(f"[WARN] Error registrando acciones de notificaciones: {e}")
