from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat'
    verbose_name = 'Chat IA'
    
    def ready(self):
        """Registra todas las acciones de IA al iniciar"""
        try:
            # Importar y registrar acciones de cada módulo
            from apps.empleados.acciones_ia import registrar_acciones as reg_empleados
            from apps.reportes.acciones_ia import registrar_acciones as reg_reportes
            
            reg_empleados()
            reg_reportes()
            
            print("[OK] Acciones de IA registradas correctamente")
        except Exception as e:
            print(f"[WARN] Error registrando acciones de IA: {e}")
