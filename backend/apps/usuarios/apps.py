from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Gestion de Usuarios'

    def ready(self):
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
        except Exception as e:
            print(f"Error registrando acciones de usuarios: {e}")
