from django.apps import AppConfig


class DesempenoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.desempeno'
    verbose_name = 'Desempeño y KPIs'
    
    def ready(self):
        """Registra las acciones de IA"""
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
        except Exception as e:
            print(f"⚠️ Error registrando acciones de desempeño: {e}")
