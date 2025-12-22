"""
Vistas del módulo core
"""
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """
    Health check endpoint para Railway/monitoreo.
    Verifica que Django responde y la BD está conectada.
    """
    status = {
        'status': 'healthy',
        'service': 'rrhh-backend',
    }

    # Verificar conexión a base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        status['database'] = 'connected'
    except Exception as e:
        status['status'] = 'unhealthy'
        status['database'] = f'error: {str(e)}'
        return JsonResponse(status, status=503)

    return JsonResponse(status)
