from django.apps import AppConfig


class DesempenoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.desempeno'
    verbose_name = 'Desempeno y KPIs'

    def ready(self):
        """Registra las acciones de IA"""
        # Importar acciones existentes de KPIs
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
        except Exception as e:
            print(f"Error registrando acciones de desempeno KPIs: {e}")

        # Importar nuevas acciones de evaluaciones
        try:
            from .acciones_evaluaciones import registrar_acciones_evaluaciones
            registrar_acciones_evaluaciones()
        except Exception as e:
            print(f"Error registrando acciones de evaluaciones: {e}")
