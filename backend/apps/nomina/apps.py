from django.apps import AppConfig


class NominaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.nomina'
    verbose_name = 'Nómina'
    
    def ready(self):
        """Registra las acciones de IA"""
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
            print("[OK] Acciones de Nomina registradas")
        except Exception as e:
            print(f"[WARN] Error registrando acciones de nomina: {e}")
