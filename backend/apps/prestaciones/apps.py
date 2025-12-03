from django.apps import AppConfig


class PrestacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.prestaciones'
    verbose_name = 'Gestion de Prestaciones'

    def ready(self):
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
        except Exception as e:
            print(f"Error registrando acciones de prestaciones: {e}")
