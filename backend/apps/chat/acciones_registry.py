"""
Registro central de acciones disponibles para la IA
Cada módulo registra sus acciones aquí
"""
from typing import Dict, List, Callable, Any

# Registro global de acciones
ACCIONES_REGISTRADAS: Dict[str, Dict] = {}


def registrar_accion(
    nombre: str,
    descripcion: str,
    permisos: List[str],
    parametros: Dict[str, str],
    ejemplo: str,
    funcion: Callable,
    confirmacion_requerida: bool = False
):
    """Registra una acción disponible para la IA"""
    ACCIONES_REGISTRADAS[nombre] = {
        'nombre': nombre,
        'descripcion': descripcion,
        'permisos': permisos,
        'parametros': parametros,
        'ejemplo': ejemplo,
        'funcion': funcion,
        'confirmacion_requerida': confirmacion_requerida,
    }


def obtener_acciones_disponibles(usuario) -> Dict[str, Dict]:
    """Retorna las acciones que el usuario puede ejecutar según sus permisos"""
    from .permisos import usuario_tiene_permiso
    
    acciones = {}
    for nombre, accion in ACCIONES_REGISTRADAS.items():
        if usuario_tiene_permiso(usuario, accion['permisos']):
            acciones[nombre] = {
                'descripcion': accion['descripcion'],
                'parametros': accion['parametros'],
                'ejemplo': accion['ejemplo'],
            }
    return acciones


def ejecutar_accion(nombre: str, usuario, parametros: Dict, contexto: Dict = None) -> Dict:
    """Ejecuta una acción validando permisos"""
    from .permisos import usuario_tiene_permiso, validar_acceso_recurso
    
    if nombre not in ACCIONES_REGISTRADAS:
        return {'success': False, 'error': f'Acción "{nombre}" no existe'}
    
    accion = ACCIONES_REGISTRADAS[nombre]
    
    # Validar permisos generales
    if not usuario_tiene_permiso(usuario, accion['permisos']):
        return {'success': False, 'error': 'No tienes permisos para esta acción'}
    
    # Ejecutar la función
    try:
        resultado = accion['funcion'](usuario, parametros, contexto or {})
        return resultado
    except Exception as e:
        return {'success': False, 'error': str(e)}


def generar_prompt_acciones(usuario) -> str:
    """Genera el texto de acciones disponibles para el prompt del sistema"""
    acciones = obtener_acciones_disponibles(usuario)
    
    if not acciones:
        return "No tienes acciones disponibles."
    
    lineas = ["ACCIONES DISPONIBLES PARA ESTE USUARIO:"]
    for nombre, info in acciones.items():
        lineas.append(f"\n- {nombre}: {info['descripcion']}")
        lineas.append(f"  Parámetros: {info['parametros']}")
        lineas.append(f"  Ejemplo: \"{info['ejemplo']}\"")
    
    return "\n".join(lineas)
