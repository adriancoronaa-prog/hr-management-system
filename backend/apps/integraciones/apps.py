from django.apps import AppConfig


class IntegracionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integraciones'
    verbose_name = 'Integraciones Externas'

    def ready(self):
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
        except Exception as e:
            print(f"Error registrando acciones de integraciones: {e}")
