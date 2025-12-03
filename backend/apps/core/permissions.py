"""
Sistema de Permisos basado en Roles
Admin > Empleador/RRHH > Empleado
"""
from rest_framework import permissions
from functools import wraps
from django.http import JsonResponse


class EsAdmin(permissions.BasePermission):
    """Solo administradores"""
    message = "Solo administradores pueden realizar esta acción"
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.es_admin


class EsEmpleadorOAdmin(permissions.BasePermission):
    """Empleadores/RRHH o administradores"""
    message = "Solo RRHH o administradores pueden realizar esta acción"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.es_admin or request.user.es_empleador


class EsEmpleadoAutenticado(permissions.BasePermission):
    """Cualquier usuario autenticado (incluye empleados)"""
    message = "Debes estar autenticado"
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class AccesoEmpresa(permissions.BasePermission):
    """
    Verifica acceso a una empresa específica
    Usa el parámetro 'empresa_id' de la URL o query params
    """
    message = "No tienes acceso a esta empresa"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.es_admin:
            return True
        
        # Buscar empresa_id en diferentes lugares
        empresa_id = (
            view.kwargs.get('empresa_id') or 
            view.kwargs.get('pk') or
            request.query_params.get('empresa') or
            request.data.get('empresa')
        )
        
        if not empresa_id:
            return True  # Si no hay empresa específica, permitir
        
        return request.user.tiene_acceso_empresa(int(empresa_id))


class AccesoEmpleado(permissions.BasePermission):
    """
    Verifica acceso a un empleado específico
    - Admin: acceso total
    - Empleador: solo empleados de sus empresas
    - Empleado: solo a sí mismo
    """
    message = "No tienes acceso a este empleado"
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        return request.user.tiene_acceso_empleado(obj)


class SoloLecturaSiEmpleado(permissions.BasePermission):
    """
    Empleados solo pueden leer, no modificar
    Admin y Empleador pueden todo
    """
    message = "No tienes permiso para modificar este recurso"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para admin y empleador
        return request.user.es_admin or request.user.es_empleador


class AccesoNomina(permissions.BasePermission):
    """
    Permisos específicos para nómina
    - Ver recibos: empleado puede ver los suyos
    - Procesar nómina: solo admin y empleador
    """
    message = "No tienes acceso a esta información de nómina"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Admin y empleador pueden todo
        if request.user.es_admin or request.user.es_empleador:
            return True
        
        # Empleado solo puede ver (GET)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.es_admin:
            return True
        
        if request.user.es_empleador:
            # Verificar que la empresa del recibo esté en sus empresas
            if hasattr(obj, 'periodo'):
                return request.user.tiene_acceso_empresa(obj.periodo.empresa_id)
            if hasattr(obj, 'empresa'):
                return request.user.tiene_acceso_empresa(obj.empresa_id)
            return True
        
        # Empleado solo puede ver sus propios recibos
        if request.user.es_empleado and request.user.empleado:
            if hasattr(obj, 'empleado'):
                return obj.empleado_id == request.user.empleado_id
        
        return False


class AccesoChat(permissions.BasePermission):
    """
    Permisos para el chat
    - Todos pueden chatear
    - Pero las acciones administrativas requieren rol adecuado
    """
    message = "No tienes permiso para esta acción del chat"
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Usuario solo puede ver sus propias conversaciones
        if hasattr(obj, 'usuario'):
            return obj.usuario_id == request.user.id
        
        return True


class AccesoConfiguracion(permissions.BasePermission):
    """Solo admin puede configurar integraciones"""
    message = "Solo administradores pueden configurar integraciones"
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.es_admin


# ============ MIXINS PARA VIEWSETS ============

class EmpresaFilterMixin:
    """
    Mixin que filtra automáticamente querysets por empresas accesibles
    """
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return qs.none()
        
        if user.es_admin:
            return qs
        
        # Filtrar por empresas accesibles
        empresas_ids = user.get_empresas_acceso().values_list('id', flat=True)
        
        # Intentar diferentes campos de relación con empresa
        if hasattr(qs.model, 'empresa'):
            return qs.filter(empresa_id__in=empresas_ids)
        elif hasattr(qs.model, 'empleado'):
            return qs.filter(empleado__empresa_id__in=empresas_ids)
        elif hasattr(qs.model, 'periodo'):
            return qs.filter(periodo__empresa_id__in=empresas_ids)
        
        return qs


class EmpleadoFilterMixin:
    """
    Mixin que filtra por empleado si el usuario es empleado
    """
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return qs.none()
        
        if user.es_admin or user.es_empleador:
            # Admin y empleador ven según empresas
            if user.es_empleador:
                empresas_ids = user.get_empresas_acceso().values_list('id', flat=True)
                if hasattr(qs.model, 'empresa'):
                    return qs.filter(empresa_id__in=empresas_ids)
                elif hasattr(qs.model, 'empleado'):
                    return qs.filter(empleado__empresa_id__in=empresas_ids)
            return qs
        
        # Empleado solo ve lo suyo
        if user.es_empleado and user.empleado:
            if hasattr(qs.model, 'empleado'):
                return qs.filter(empleado_id=user.empleado_id)
            # Si es el modelo Empleado directamente
            if qs.model.__name__ == 'Empleado':
                return qs.filter(id=user.empleado_id)
        
        return qs.none()


# ============ DECORADORES PARA VISTAS ============

def requiere_admin(view_func):
    """Decorador que requiere rol de admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.es_admin:
            return JsonResponse(
                {'error': 'Solo administradores pueden realizar esta acción'},
                status=403
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_empleador(view_func):
    """Decorador que requiere rol de empleador o admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Autenticación requerida'}, status=401)
        if not (request.user.es_admin or request.user.es_empleador):
            return JsonResponse(
                {'error': 'Solo RRHH o administradores pueden realizar esta acción'},
                status=403
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def requiere_acceso_empresa(view_func):
    """Decorador que verifica acceso a empresa"""
    @wraps(view_func)
    def wrapper(request, empresa_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Autenticación requerida'}, status=401)
        
        if empresa_id and not request.user.tiene_acceso_empresa(empresa_id):
            return JsonResponse(
                {'error': 'No tienes acceso a esta empresa'},
                status=403
            )
        return view_func(request, empresa_id=empresa_id, *args, **kwargs)
    return wrapper


# ============ MATRIZ DE PERMISOS DOCUMENTADA ============
"""
MATRIZ DE PERMISOS POR ROL:

Recurso              | Admin | Empleador | Empleado
---------------------|-------|-----------|----------
Empresas CRUD        |  ✅   |    ❌     |    ❌
Empresas Ver         |  ✅   |    ✅*    |    ✅**
Empleados CRUD       |  ✅   |    ✅*    |    ❌
Empleados Ver        |  ✅   |    ✅*    |    ✅**
Vacaciones CRUD      |  ✅   |    ✅*    |    ✅***
Vacaciones Aprobar   |  ✅   |    ✅*    |    ❌
Nómina Procesar      |  ✅   |    ✅*    |    ❌
Nómina Ver Recibos   |  ✅   |    ✅*    |    ✅**
Prestaciones CRUD    |  ✅   |    ✅*    |    ❌
Prestaciones Ver     |  ✅   |    ✅*    |    ✅**
Chat                 |  ✅   |    ✅     |    ✅
Chat Acciones Admin  |  ✅   |    ✅     |    ❌
Documentos Subir     |  ✅   |    ✅*    |    ✅**
Documentos Ver       |  ✅   |    ✅*    |    ✅**
Integraciones Config |  ✅   |    ❌     |    ❌
Reportes             |  ✅   |    ✅*    |    ❌

* Solo empresas asignadas
** Solo su propia información
*** Solo puede solicitar, no aprobar
"""
