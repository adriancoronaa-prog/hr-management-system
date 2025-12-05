"""
Sistema de permisos para acciones de IA
"""
from typing import List, Optional


def usuario_tiene_permiso(usuario, permisos_requeridos: List[str]) -> bool:
    """
    Verifica si el usuario tiene al menos uno de los permisos requeridos
    
    Permisos disponibles:
    - es_admin: Usuario administrador del sistema
    - es_rrhh: Usuario de RRHH (rol empleador)
    - es_empleado: Usuario empleado
    - es_jefe: Usuario que tiene subordinados
    - es_dueno: Es dueño del recurso (ej: su propio perfil)
    - publico: Cualquier usuario autenticado
    """
    if not permisos_requeridos or 'publico' in permisos_requeridos:
        return True
    
    for permiso in permisos_requeridos:
        if _verificar_permiso(usuario, permiso):
            return True
    
    return False


def _verificar_permiso(usuario, permiso: str) -> bool:
    """Verifica un permiso específico"""
    if permiso == 'es_admin':
        return usuario.is_staff or usuario.is_superuser or usuario.rol in ['admin', 'administrador']

    if permiso == 'es_rrhh':
        return usuario.rol in ['admin', 'administrador', 'empleador', 'rrhh']
    
    if permiso == 'es_empleado':
        return hasattr(usuario, 'empleado') and usuario.empleado is not None
    
    if permiso == 'es_jefe':
        if hasattr(usuario, 'empleado') and usuario.empleado:
            return usuario.empleado.subordinados.exists()
        return False
    
    return False


def validar_acceso_recurso(usuario, recurso, tipo_acceso: str = 'ver') -> bool:
    """
    Valida si el usuario puede acceder a un recurso específico
    
    tipo_acceso: 'ver', 'editar', 'eliminar'
    """
    # Admin puede todo
    if usuario.is_staff or usuario.is_superuser or usuario.rol in ['admin', 'administrador']:
        return True
    
    # Obtener el modelo del recurso
    modelo = type(recurso).__name__
    
    if modelo == 'Empleado':
        return _validar_acceso_empleado(usuario, recurso, tipo_acceso)
    elif modelo == 'Empresa':
        return _validar_acceso_empresa(usuario, recurso, tipo_acceso)
    
    return False


def _validar_acceso_empleado(usuario, empleado, tipo_acceso: str) -> bool:
    """Valida acceso a un empleado"""
    # Si es el mismo empleado
    if hasattr(usuario, 'empleado') and usuario.empleado:
        if usuario.empleado.id == empleado.id:
            return True
        
        # Si es jefe del empleado
        if _es_jefe_de(usuario.empleado, empleado):
            return True
    
    # Si es RRHH de la misma empresa
    if usuario.rol in ['empleador', 'rrhh']:
        empresas_usuario = _obtener_empresas_usuario(usuario)
        if empleado.empresa_id in empresas_usuario:
            return True
    
    return False


def _validar_acceso_empresa(usuario, empresa, tipo_acceso: str) -> bool:
    """Valida acceso a una empresa"""
    if usuario.rol in ['empleador', 'rrhh']:
        empresas_usuario = _obtener_empresas_usuario(usuario)
        return empresa.id in empresas_usuario
    
    if hasattr(usuario, 'empleado') and usuario.empleado:
        return usuario.empleado.empresa_id == empresa.id
    
    return False


def _es_jefe_de(posible_jefe, empleado) -> bool:
    """Verifica si posible_jefe es jefe directo o indirecto de empleado"""
    actual = empleado.jefe_directo
    niveles = 0
    max_niveles = 10  # Prevenir loops infinitos
    
    while actual and niveles < max_niveles:
        if actual.id == posible_jefe.id:
            return True
        actual = actual.jefe_directo
        niveles += 1
    
    return False


def _obtener_empresas_usuario(usuario) -> list:
    """Obtiene IDs de empresas a las que el usuario tiene acceso"""
    # Por ahora retorna todas si es admin/rrhh
    # Luego se puede refinar con una tabla de asignación
    if usuario.rol in ['admin', 'administrador', 'empleador', 'rrhh']:
        from apps.empresas.models import Empresa
        return list(Empresa.objects.values_list('id', flat=True))
    
    if hasattr(usuario, 'empleado') and usuario.empleado:
        return [usuario.empleado.empresa_id]
    
    return []


def obtener_subordinados(empleado, incluir_indirectos: bool = False) -> list:
    """Obtiene la lista de subordinados de un empleado"""
    from apps.empleados.models import Empleado
    
    subordinados = list(empleado.subordinados.filter(estado='activo'))
    
    if incluir_indirectos:
        for sub in subordinados.copy():
            subordinados.extend(obtener_subordinados(sub, True))
    
    return subordinados


def obtener_contexto_permisos(usuario) -> dict:
    """Genera un diccionario con el contexto de permisos del usuario"""
    contexto = {
        'es_admin': usuario.is_staff or usuario.is_superuser or usuario.rol in ['admin', 'administrador'],
        'es_rrhh': usuario.rol in ['admin', 'administrador', 'empleador', 'rrhh'],
        'rol': usuario.rol,
        'empresas_acceso': _obtener_empresas_usuario(usuario),
    }
    
    if hasattr(usuario, 'empleado') and usuario.empleado:
        emp = usuario.empleado
        contexto['empleado_id'] = str(emp.id)
        contexto['empresa_id'] = str(emp.empresa_id)
        contexto['es_jefe'] = emp.subordinados.exists()
        contexto['subordinados_ids'] = [str(s.id) for s in obtener_subordinados(emp)]
    
    return contexto
