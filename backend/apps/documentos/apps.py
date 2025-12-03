from django.apps import AppConfig


class DocumentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.documentos'
    verbose_name = 'Documentos y RAG'

    def ready(self):
        """Registra las acciones de IA"""
        try:
            from .acciones_ia import registrar_acciones
            registrar_acciones()
        except Exception as e:
            print(f"Error registrando acciones de documentos: {e}")
