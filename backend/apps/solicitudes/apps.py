from django.apps import AppConfig


class SolicitudesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.solicitudes'
    verbose_name = 'Solicitudes'

    def ready(self):
        """Registra las acciones de IA"""
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
            print("[OK] Acciones de Solicitudes registradas")
        except Exception as e:
            print(f"[WARN] Error registrando acciones de solicitudes: {e}")
