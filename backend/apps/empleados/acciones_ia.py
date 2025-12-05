"""
Acciones de IA para el módulo de empleados
"""
from typing import Dict
from decimal import Decimal
from datetime import date


def registrar_acciones():
    """Registra las acciones de empleados en el registro central"""
    from apps.chat.acciones_registry import registrar_accion
    
    registrar_accion(
        nombre='buscar_empleado',
        descripcion='Busca empleados por nombre, CURP, RFC o cualquier dato',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'busqueda': 'Texto a buscar (nombre, CURP, RFC, etc.)',
            'empresa_id': '(Opcional) Filtrar por empresa',
            'solo_activos': '(Opcional) Solo empleados activos, default: true',
        },
        ejemplo='Busca al empleado Juan Pérez',
        funcion=buscar_empleado
    )
    
    registrar_accion(
        nombre='crear_empleado',
        descripcion='Crea un nuevo empleado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'nombre': 'Nombre(s) del empleado',
            'apellido_paterno': 'Apellido paterno',
            'apellido_materno': '(Opcional) Apellido materno',
            'empresa_id': 'ID de la empresa',
            'fecha_ingreso': 'Fecha de ingreso (YYYY-MM-DD)',
            'salario_diario': 'Salario diario',
            'puesto': '(Opcional) Puesto',
            'departamento': '(Opcional) Departamento',
            'curp': '(Opcional) CURP',
            'rfc': '(Opcional) RFC',
            'nss_imss': '(Opcional) NSS del IMSS',
            'jefe_directo_id': '(Opcional) ID del jefe directo',
        },
        ejemplo='Crea un empleado llamado Juan Pérez con salario de $500 diarios',
        funcion=crear_empleado,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='obtener_subordinados',
        descripcion='Obtiene los subordinados directos o indirectos de un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'empleado_id': '(Opcional) ID del empleado, si no se especifica usa el usuario actual',
            'incluir_indirectos': '(Opcional) Incluir subordinados indirectos, default: false',
        },
        ejemplo='Muéstrame mi equipo',
        funcion=obtener_subordinados
    )
    
    registrar_accion(
        nombre='obtener_organigrama',
        descripcion='Muestra la estructura organizacional de una empresa',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empresa_id': '(Opcional) ID de la empresa',
        },
        ejemplo='Muéstrame el organigrama de la empresa',
        funcion=obtener_organigrama
    )
    
    registrar_accion(
        nombre='ver_perfil_empleado',
        descripcion='Muestra información detallada de un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'empleado_id': '(Opcional) ID del empleado, si no se especifica muestra el propio',
        },
        ejemplo='Muéstrame mi perfil',
        funcion=ver_perfil_empleado
    )
    
    registrar_accion(
        nombre='asignar_jefe',
        descripcion='Asigna un jefe directo a un empleado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'jefe_id': 'ID del nuevo jefe directo',
        },
        ejemplo='Asigna a María como jefa de Juan',
        funcion=asignar_jefe,
        confirmacion_requerida=True
    )

    # Acciones de bajas
    registrar_accion(
        nombre='dar_baja_empleado',
        descripcion='Da de baja a un empleado (termina relación laboral)',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_nombre': 'Nombre del empleado a dar de baja',
            'tipo_baja': 'Tipo: renuncia_voluntaria, despido_justificado, despido_injustificado, termino_contrato, jubilacion, mutuo_acuerdo, fallecimiento',
            'motivo': '(Opcional) Motivo detallado de la baja',
            'fecha_baja': '(Opcional) Fecha de baja YYYY-MM-DD, default: hoy',
        },
        ejemplo='Da de baja a Juan Pérez por renuncia voluntaria',
        funcion=dar_baja_empleado,
        confirmacion_requerida=True
    )

    registrar_accion(
        nombre='ver_extrabajadores',
        descripcion='Lista los empleados dados de baja (archivo de extrabajadores)',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'año': '(Opcional) Filtrar por año de baja',
            'tipo_baja': '(Opcional) Filtrar por tipo de baja',
        },
        ejemplo='Muéstrame los extrabajadores del 2024',
        funcion=ver_extrabajadores
    )

    registrar_accion(
        nombre='ver_historial_empleado',
        descripcion='Muestra historial completo de un empleado (activo o dado de baja)',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_nombre': 'Nombre del empleado',
        },
        ejemplo='Muéstrame el historial de Juan Pérez',
        funcion=ver_historial_empleado
    )

    registrar_accion(
        nombre='reactivar_empleado',
        descripcion='Reactiva un empleado dado de baja (recontratación)',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_nombre': 'Nombre del extrabajador a reactivar',
            'nuevo_salario': '(Opcional) Nuevo salario diario',
            'nuevo_puesto': '(Opcional) Nuevo puesto',
            'fecha_reingreso': '(Opcional) Fecha de reingreso YYYY-MM-DD, default: hoy',
        },
        ejemplo='Reactiva a María García con salario de $600 diarios',
        funcion=reactivar_empleado,
        confirmacion_requerida=True
    )

    # Acciones de expediente
    registrar_accion(
        nombre='ver_expediente',
        descripcion='Muestra los documentos del expediente de un empleado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_nombre': 'Nombre del empleado',
            'tipo_documento': '(Opcional) Filtrar por tipo: ine, curp, contrato, etc.',
        },
        ejemplo='Muéstrame el expediente de Juan Pérez',
        funcion=ver_expediente
    )

    registrar_accion(
        nombre='verificar_documentos_pendientes',
        descripcion='Lista documentos faltantes en expedientes de empleados',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_nombre': '(Opcional) Nombre del empleado, si no se especifica muestra de todos',
        },
        ejemplo='¿Qué documentos le faltan a María García?',
        funcion=verificar_documentos_pendientes
    )

    # ============================================================
    # ACCION 59: Busqueda avanzada de empleados
    # ============================================================
    registrar_accion(
        nombre='busqueda_avanzada_empleados',
        descripcion='Busqueda avanzada de empleados con multiples filtros',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'busqueda': '(Opcional) Texto libre (nombre, RFC, CURP, email)',
            'departamento': '(Opcional) Filtrar por departamento',
            'puesto': '(Opcional) Filtrar por puesto',
            'estado': '(Opcional) activo, baja, incapacidad',
            'salario_min': '(Opcional) Salario diario minimo',
            'salario_max': '(Opcional) Salario diario maximo',
            'jefe': '(Opcional) Nombre del jefe directo',
            'antiguedad_min': '(Opcional) Antiguedad minima en anos',
        },
        ejemplo='Busca empleados del departamento de ventas con salario mayor a 500',
        funcion=busqueda_avanzada_empleados
    )

    registrar_acciones_usuarios()


# ============ IMPLEMENTACIÓN DE FUNCIONES ============

def buscar_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Busca empleados según criterios"""
    from apps.empleados.models import Empleado
    from apps.chat.permisos import obtener_subordinados as get_subs
    from django.db.models import Q
    
    busqueda = params.get('busqueda', '')
    empresa_id = params.get('empresa_id') or (contexto.get('empresa_contexto').id if contexto.get('empresa_contexto') else None)
    solo_activos = params.get('solo_activos', True)
    
    # Filtro base según permisos
    if usuario.rol in ['admin', 'administrador'] or usuario.is_staff:
        empleados = Empleado.objects.all()
    elif usuario.rol in ['empleador', 'rrhh']:
        empleados = Empleado.objects.all()  # RRHH ve todos (luego filtrar por empresa asignada)
    elif hasattr(usuario, 'empleado') and usuario.empleado:
        # Jefe solo ve su equipo
        subordinados = get_subs(usuario.empleado, incluir_indirectos=True)
        ids = [s.id for s in subordinados] + [usuario.empleado.id]
        empleados = Empleado.objects.filter(id__in=ids)
    else:
        return {'success': False, 'error': 'No tienes acceso a empleados'}
    
    # Aplicar filtros
    if empresa_id:
        empleados = empleados.filter(empresa_id=empresa_id)
    
    if solo_activos:
        empleados = empleados.filter(estado='activo')
    
    if busqueda:
        empleados = empleados.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido_paterno__icontains=busqueda) |
            Q(apellido_materno__icontains=busqueda) |
            Q(curp__icontains=busqueda) |
            Q(rfc__icontains=busqueda) |
            Q(puesto__icontains=busqueda) |
            Q(departamento__icontains=busqueda)
        )
    
    lista = [{
        'id': str(e.id),
        'nombre': e.nombre_completo,
        'puesto': e.puesto or 'Sin puesto',
        'departamento': e.departamento or 'Sin departamento',
        'empresa': e.empresa.razon_social if e.empresa else 'Sin empresa',
        'antiguedad': f"{e.antiguedad['anos']} años, {e.antiguedad['meses']} meses",
        'jefe': e.jefe_directo.nombre_completo if e.jefe_directo else 'Sin jefe asignado',
    } for e in empleados[:20]]
    
    return {
        'success': True,
        'mensaje': f'Se encontraron {empleados.count()} empleados',
        'total': empleados.count(),
        'empleados': lista
    }


def crear_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Crea un nuevo empleado"""
    from apps.empleados.models import Empleado
    from apps.empresas.models import Empresa
    
    empresa_id = params.get('empresa_id') or (contexto.get('empresa_contexto').id if contexto.get('empresa_contexto') else None)
    
    if not empresa_id:
        return {'success': False, 'error': 'Debes especificar la empresa'}
    
    try:
        empresa = Empresa.objects.get(pk=empresa_id)
    except Empresa.DoesNotExist:
        return {'success': False, 'error': 'Empresa no encontrada'}
    
    # Parsear fecha
    fecha_ingreso = params.get('fecha_ingreso', date.today())
    if isinstance(fecha_ingreso, str):
        from datetime import datetime
        fecha_ingreso = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
    
    # Parsear salario
    salario = params.get('salario_diario')
    if salario:
        salario = Decimal(str(salario))
    
    try:
        empleado = Empleado.objects.create(
            empresa=empresa,
            nombre=params.get('nombre', ''),
            apellido_paterno=params.get('apellido_paterno', ''),
            apellido_materno=params.get('apellido_materno', ''),
            fecha_ingreso=fecha_ingreso,
            salario_diario=salario,
            puesto=params.get('puesto', ''),
            departamento=params.get('departamento', ''),
            curp=params.get('curp', ''),
            rfc=params.get('rfc', ''),
            nss_imss=params.get('nss_imss', ''),
            jefe_directo_id=params.get('jefe_directo_id'),
        )
        
        return {
            'success': True,
            'mensaje': f'Empleado "{empleado.nombre_completo}" creado exitosamente',
            'empleado_id': str(empleado.id)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def obtener_subordinados(usuario, params: Dict, contexto: Dict) -> Dict:
    """Obtiene subordinados de un empleado"""
    from apps.empleados.models import Empleado
    from apps.chat.permisos import obtener_subordinados as get_subs
    
    empleado_id = params.get('empleado_id')
    incluir_indirectos = params.get('incluir_indirectos', False)
    
    # Determinar empleado base
    if empleado_id:
        try:
            empleado = Empleado.objects.get(pk=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
    elif hasattr(usuario, 'empleado') and usuario.empleado:
        empleado = usuario.empleado
    else:
        return {'success': False, 'error': 'No se especificó empleado'}
    
    subordinados = get_subs(empleado, incluir_indirectos)
    
    lista = [{
        'id': str(s.id),
        'nombre': s.nombre_completo,
        'puesto': s.puesto or 'Sin puesto',
        'departamento': s.departamento or 'Sin departamento',
        'es_subordinado_directo': s.jefe_directo_id == empleado.id if s.jefe_directo_id else False,
    } for s in subordinados]
    
    return {
        'success': True,
        'mensaje': f'{empleado.nombre_completo} tiene {len(subordinados)} subordinados',
        'jefe': empleado.nombre_completo,
        'subordinados': lista
    }


def obtener_organigrama(usuario, params: Dict, contexto: Dict) -> Dict:
    """Obtiene estructura organizacional"""
    from apps.empleados.models import Empleado
    
    empresa_id = params.get('empresa_id') or (contexto.get('empresa_contexto').id if contexto.get('empresa_contexto') else None)
    
    if not empresa_id:
        return {'success': False, 'error': 'Debes especificar la empresa'}
    
    empleados = Empleado.objects.filter(empresa_id=empresa_id, estado='activo')
    
    # Encontrar raíces (sin jefe)
    raices = empleados.filter(jefe_directo__isnull=True)
    
    def construir_arbol(empleado, nivel=0):
        subordinados = empleados.filter(jefe_directo=empleado)
        return {
            'id': str(empleado.id),
            'nombre': empleado.nombre_completo,
            'puesto': empleado.puesto or 'Sin puesto',
            'nivel': nivel,
            'subordinados': [construir_arbol(s, nivel+1) for s in subordinados]
        }
    
    organigrama = [construir_arbol(r) for r in raices]
    
    return {
        'success': True,
        'mensaje': f'Organigrama con {empleados.count()} empleados',
        'organigrama': organigrama
    }


def ver_perfil_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra perfil detallado de un empleado"""
    from apps.empleados.models import Empleado
    from apps.chat.permisos import validar_acceso_recurso
    
    empleado_id = params.get('empleado_id')
    
    if empleado_id:
        try:
            empleado = Empleado.objects.get(pk=empleado_id)
        except Empleado.DoesNotExist:
            return {'success': False, 'error': 'Empleado no encontrado'}
        
        # Validar acceso
        if not validar_acceso_recurso(usuario, empleado, 'ver'):
            return {'success': False, 'error': 'No tienes acceso a este empleado'}
    elif hasattr(usuario, 'empleado') and usuario.empleado:
        empleado = usuario.empleado
    else:
        return {'success': False, 'error': 'No se especificó empleado'}
    
    perfil = {
        'id': str(empleado.id),
        'nombre_completo': empleado.nombre_completo,
        'curp': empleado.curp or 'No registrado',
        'rfc': empleado.rfc or 'No registrado',
        'nss_imss': empleado.nss_imss or 'No registrado',
        'empresa': empleado.empresa.razon_social if empleado.empresa else 'Sin empresa',
        'puesto': empleado.puesto or 'Sin puesto',
        'departamento': empleado.departamento or 'Sin departamento',
        'fecha_ingreso': empleado.fecha_ingreso.strftime('%d/%m/%Y'),
        'antiguedad': f"{empleado.antiguedad['anos']} años, {empleado.antiguedad['meses']} meses, {empleado.antiguedad['dias']} días",
        'salario_diario': f"${empleado.salario_diario:,.2f}" if empleado.salario_diario else 'No registrado',
        'salario_mensual': f"${empleado.salario_mensual:,.2f}" if empleado.salario_mensual else 'No registrado',
        'jefe_directo': empleado.jefe_directo.nombre_completo if empleado.jefe_directo else 'Sin jefe asignado',
        'subordinados_directos': empleado.subordinados.count(),
        'estado': empleado.estado,
    }
    
    return {
        'success': True,
        'mensaje': f'Perfil de {empleado.nombre_completo}',
        'perfil': perfil
    }


def asignar_jefe(usuario, params: Dict, contexto: Dict) -> Dict:
    """Asigna un jefe directo a un empleado"""
    from apps.empleados.models import Empleado
    
    empleado_id = params.get('empleado_id')
    jefe_id = params.get('jefe_id')
    
    if not empleado_id or not jefe_id:
        return {'success': False, 'error': 'Debes especificar empleado y jefe'}
    
    try:
        empleado = Empleado.objects.get(pk=empleado_id)
        jefe = Empleado.objects.get(pk=jefe_id)
    except Empleado.DoesNotExist:
        return {'success': False, 'error': 'Empleado o jefe no encontrado'}
    
    # Validar que no sea el mismo
    if empleado.id == jefe.id:
        return {'success': False, 'error': 'Un empleado no puede ser su propio jefe'}
    
    # Validar que no cree ciclo
    actual = jefe.jefe_directo
    while actual:
        if actual.id == empleado.id:
            return {'success': False, 'error': 'Esta asignación crearía un ciclo en la jerarquía'}
        actual = actual.jefe_directo
    
    empleado.jefe_directo = jefe
    empleado.save()
    
    return {
        'success': True,
        'mensaje': f'{empleado.nombre_completo} ahora reporta a {jefe.nombre_completo}'
    }

# ============ ACCIONES DE USUARIOS ============

def registrar_acciones_usuarios():
    """Registra las acciones de usuarios"""
    from apps.chat.acciones_registry import registrar_accion
    
    registrar_accion(
        nombre='crear_usuario',
        descripcion='Crea un nuevo usuario del sistema con rol específico',
        permisos=['es_admin'],
        parametros={
            'email': 'Email del usuario',
            'password': 'Contraseña temporal',
            'rol': 'Rol: administrador, empleador, o empleado',
            'empleado_id': '(Opcional) ID del empleado a vincular',
        },
        ejemplo='Crea un usuario para juan@empresa.com con rol empleado',
        funcion=crear_usuario,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='vincular_usuario_empleado',
        descripcion='Vincula un usuario existente a un empleado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'usuario_id': 'ID del usuario',
            'empleado_id': 'ID del empleado',
        },
        ejemplo='Vincula el usuario juan@empresa.com al empleado Juan Pérez',
        funcion=vincular_usuario_empleado,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='cambiar_rol_usuario',
        descripcion='Cambia el rol de un usuario',
        permisos=['es_admin'],
        parametros={
            'usuario_id': 'ID o email del usuario',
            'nuevo_rol': 'Nuevo rol: administrador, empleador, o empleado',
        },
        ejemplo='Cambia el rol de juan@empresa.com a empleador',
        funcion=cambiar_rol_usuario,
        confirmacion_requerida=True
    )
    
    registrar_accion(
        nombre='listar_usuarios',
        descripcion='Lista los usuarios del sistema',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'rol': '(Opcional) Filtrar por rol',
            'solo_activos': '(Opcional) Solo usuarios activos, default: true',
        },
        ejemplo='Muéstrame todos los usuarios administradores',
        funcion=listar_usuarios
    )


def crear_usuario(usuario, params: Dict, contexto: Dict) -> Dict:
    """Crea un nuevo usuario"""
    from apps.usuarios.models import Usuario
    from apps.empleados.models import Empleado
    
    email = params.get('email')
    password = params.get('password', 'Temporal123!')
    rol = params.get('rol', 'empleado')
    empleado_id = params.get('empleado_id')
    
    if not email:
        return {'success': False, 'error': 'El email es requerido'}
    
    # Validar rol
    roles_validos = ['administrador', 'empleador', 'empleado']
    if rol not in roles_validos:
        return {'success': False, 'error': f'Rol inválido. Opciones: {roles_validos}'}
    
    # Verificar que no exista
    if Usuario.objects.filter(email=email).exists():
        return {'success': False, 'error': f'Ya existe un usuario con el email {email}'}
    
    try:
        # Crear usuario
        nuevo_usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            rol=rol
        )
        
        mensaje = f'Usuario {email} creado con rol {rol}'
        
        # Vincular a empleado si se especifica
        if empleado_id:
            try:
                empleado = Empleado.objects.get(pk=empleado_id)
                empleado.usuario = nuevo_usuario
                empleado.save()
                mensaje += f' y vinculado a {empleado.nombre_completo}'
            except Empleado.DoesNotExist:
                mensaje += ' (empleado no encontrado para vincular)'
        
        return {
            'success': True,
            'mensaje': mensaje,
            'usuario_id': str(nuevo_usuario.id),
            'email': email,
            'rol': rol
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def vincular_usuario_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Vincula un usuario a un empleado"""
    from apps.usuarios.models import Usuario
    from apps.empleados.models import Empleado
    
    usuario_id = params.get('usuario_id')
    empleado_id = params.get('empleado_id')
    
    if not usuario_id or not empleado_id:
        return {'success': False, 'error': 'Se requiere usuario_id y empleado_id'}
    
    try:
        # Buscar usuario por ID o email
        try:
            user = Usuario.objects.get(pk=usuario_id)
        except (Usuario.DoesNotExist, ValueError):
            user = Usuario.objects.get(email=usuario_id)
        
        empleado = Empleado.objects.get(pk=empleado_id)
        
        # Verificar que el empleado no tenga otro usuario
        if hasattr(empleado, 'usuario') and empleado.usuario and empleado.usuario.id != user.id:
            return {
                'success': False, 
                'error': f'El empleado ya está vinculado a {empleado.usuario.email}'
            }
        
        # Vincular
        empleado.usuario = user
        empleado.save()
        
        return {
            'success': True,
            'mensaje': f'Usuario {user.email} vinculado a {empleado.nombre_completo}'
        }
    except Usuario.DoesNotExist:
        return {'success': False, 'error': 'Usuario no encontrado'}
    except Empleado.DoesNotExist:
        return {'success': False, 'error': 'Empleado no encontrado'}


def cambiar_rol_usuario(usuario, params: Dict, contexto: Dict) -> Dict:
    """Cambia el rol de un usuario"""
    from apps.usuarios.models import Usuario
    
    usuario_id = params.get('usuario_id')
    nuevo_rol = params.get('nuevo_rol')
    
    if not usuario_id or not nuevo_rol:
        return {'success': False, 'error': 'Se requiere usuario_id y nuevo_rol'}
    
    roles_validos = ['administrador', 'empleador', 'empleado']
    if nuevo_rol not in roles_validos:
        return {'success': False, 'error': f'Rol inválido. Opciones: {roles_validos}'}
    
    try:
        # Buscar por ID o email
        try:
            user = Usuario.objects.get(pk=usuario_id)
        except (Usuario.DoesNotExist, ValueError):
            user = Usuario.objects.get(email=usuario_id)
        
        rol_anterior = user.rol
        user.rol = nuevo_rol
        user.save()
        
        return {
            'success': True,
            'mensaje': f'Rol de {user.email} cambiado de {rol_anterior} a {nuevo_rol}'
        }
    except Usuario.DoesNotExist:
        return {'success': False, 'error': 'Usuario no encontrado'}


def listar_usuarios(usuario, params: Dict, contexto: Dict) -> Dict:
    """Lista usuarios del sistema"""
    from apps.usuarios.models import Usuario
    
    rol = params.get('rol')
    solo_activos = params.get('solo_activos', True)
    
    usuarios = Usuario.objects.all()
    
    if rol:
        usuarios = usuarios.filter(rol=rol)
    
    if solo_activos:
        usuarios = usuarios.filter(is_active=True)
    
    lista = [{
        'id': str(u.id),
        'email': u.email,
        'rol': u.rol,
        'is_active': u.is_active,
        'tiene_empleado': hasattr(u, 'empleado') and u.empleado is not None,
        'empleado_nombre': u.empleado.nombre_completo if hasattr(u, 'empleado') and u.empleado else None,
    } for u in usuarios[:50]]

    return {
        'success': True,
        'mensaje': f'Se encontraron {usuarios.count()} usuarios',
        'total': usuarios.count(),
        'usuarios': lista
    }


# ============ ACCIONES DE BAJAS ============

def _buscar_empleado_por_nombre(nombre: str, empresa_contexto, incluir_bajas=False):
    """Busca un empleado por nombre (helper)"""
    from apps.empleados.models import Empleado
    from django.db.models import Q

    filtro = Q(nombre__icontains=nombre) | Q(apellido_paterno__icontains=nombre) | Q(apellido_materno__icontains=nombre)

    # Buscar por nombre completo también
    partes = nombre.split()
    if len(partes) >= 2:
        filtro |= Q(nombre__icontains=partes[0], apellido_paterno__icontains=partes[1])

    empleados = Empleado.objects.filter(filtro)

    if empresa_contexto:
        empleados = empleados.filter(empresa=empresa_contexto)

    if not incluir_bajas:
        empleados = empleados.filter(estado='activo')

    return empleados


def dar_baja_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Da de baja a un empleado"""
    from apps.empleados.models import Empleado
    from datetime import datetime

    empleado_nombre = params.get('empleado_nombre')
    tipo_baja = params.get('tipo_baja', 'renuncia_voluntaria')
    motivo = params.get('motivo', '')
    fecha_baja = params.get('fecha_baja')

    if not empleado_nombre:
        return {'success': False, 'error': 'Debes especificar el nombre del empleado'}

    # Validar tipo de baja
    tipos_validos = [t[0] for t in Empleado.TipoBaja.choices]
    if tipo_baja not in tipos_validos:
        return {'success': False, 'error': f'Tipo de baja inválido. Opciones: {tipos_validos}'}

    # Buscar empleado
    empresa_contexto = contexto.get('empresa_contexto')
    empleados = _buscar_empleado_por_nombre(empleado_nombre, empresa_contexto)

    if not empleados.exists():
        return {'success': False, 'error': f'No se encontró empleado activo con nombre "{empleado_nombre}"'}

    if empleados.count() > 1:
        nombres = [e.nombre_completo for e in empleados[:5]]
        return {
            'success': False,
            'error': f'Se encontraron múltiples empleados: {", ".join(nombres)}. Sé más específico.'
        }

    empleado = empleados.first()

    # Parsear fecha
    if fecha_baja:
        if isinstance(fecha_baja, str):
            fecha_baja = datetime.strptime(fecha_baja, '%Y-%m-%d').date()
    else:
        fecha_baja = date.today()

    # Calcular liquidación
    try:
        from apps.reportes.services import MetricasEmpleado
        # Determinar si es despido injustificado para liquidación completa
        es_despido_injustificado = tipo_baja == 'despido_injustificado'
        metricas = MetricasEmpleado(empleado)
        liquidacion = metricas.calcular_liquidacion(fecha_baja, es_despido_injustificado)
        monto_liquidacion = liquidacion.get('total', Decimal('0'))
    except Exception as e:
        monto_liquidacion = Decimal('0')
        liquidacion = {'error': str(e)}

    # Actualizar empleado
    empleado.estado = 'baja'
    empleado.fecha_baja = fecha_baja
    empleado.tipo_baja = tipo_baja
    empleado.motivo_baja = motivo
    empleado.monto_liquidacion = monto_liquidacion
    empleado.fecha_ultimo_dia_laborado = fecha_baja
    empleado.save()

    tipo_baja_display = dict(Empleado.TipoBaja.choices).get(tipo_baja, tipo_baja)

    # Notificar al jefe directo sobre la baja
    try:
        from apps.notificaciones.services import NotificacionService
        if empleado.jefe_directo and empleado.jefe_directo.usuario:
            NotificacionService.crear_notificacion(
                destinatario=empleado.jefe_directo.usuario,
                tipo='sistema',
                titulo=f'Baja de empleado: {empleado.nombre_completo}',
                mensaje=f'{empleado.nombre_completo} ha sido dado de baja ({tipo_baja_display}). Fecha: {fecha_baja.strftime("%d/%m/%Y")}',
                objeto_relacionado=empleado,
                prioridad='alta',
            )
    except Exception:
        pass  # Notificaciones opcionales

    return {
        'success': True,
        'mensaje': f'{empleado.nombre_completo} dado de baja exitosamente',
        'empleado': empleado.nombre_completo,
        'tipo_baja': tipo_baja_display,
        'fecha_baja': fecha_baja.strftime('%d/%m/%Y'),
        'antiguedad': f"{empleado.antiguedad['anos']} años, {empleado.antiguedad['meses']} meses",
        'monto_liquidacion': f"${monto_liquidacion:,.2f}",
        'detalles_liquidacion': liquidacion
    }


def ver_extrabajadores(usuario, params: Dict, contexto: Dict) -> Dict:
    """Lista empleados dados de baja"""
    from apps.empleados.models import Empleado

    año = params.get('año') or params.get('anio')
    tipo_baja = params.get('tipo_baja')
    empresa_contexto = contexto.get('empresa_contexto')

    empleados = Empleado.objects.filter(estado='baja')

    if empresa_contexto:
        empleados = empleados.filter(empresa=empresa_contexto)

    if año:
        empleados = empleados.filter(fecha_baja__year=int(año))

    if tipo_baja:
        empleados = empleados.filter(tipo_baja=tipo_baja)

    empleados = empleados.order_by('-fecha_baja')

    if not empleados.exists():
        return {
            'success': True,
            'mensaje': 'No hay extrabajadores registrados con los filtros especificados',
            'extrabajadores': []
        }

    lista = []
    for e in empleados[:50]:
        tipo_display = dict(Empleado.TipoBaja.choices).get(e.tipo_baja, e.tipo_baja or 'No especificado')
        lista.append({
            'id': str(e.id),
            'nombre': e.nombre_completo,
            'puesto': e.puesto or 'Sin puesto',
            'departamento': e.departamento or 'Sin departamento',
            'fecha_ingreso': e.fecha_ingreso.strftime('%d/%m/%Y'),
            'fecha_baja': e.fecha_baja.strftime('%d/%m/%Y') if e.fecha_baja else 'N/A',
            'tipo_baja': tipo_display,
            'antiguedad': f"{e.antiguedad['anos']} años, {e.antiguedad['meses']} meses",
            'monto_liquidacion': f"${e.monto_liquidacion:,.2f}" if e.monto_liquidacion else 'No registrado',
            'liquidacion_pagada': 'Sí' if e.liquidacion_pagada else 'No',
        })

    # Formatear mensaje
    lineas = [f"**Extrabajadores ({len(lista)} encontrados)**\n"]
    for ex in lista[:20]:
        lineas.append(f"- **{ex['nombre']}** ({ex['puesto']})")
        lineas.append(f"  Baja: {ex['fecha_baja']} | {ex['tipo_baja']}")
        lineas.append(f"  Antigüedad: {ex['antiguedad']} | Liquidación: {ex['monto_liquidacion']}")

    return {
        'success': True,
        'mensaje': '\n'.join(lineas),
        'total': empleados.count(),
        'extrabajadores': lista
    }


def ver_historial_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra historial completo de un empleado"""
    from apps.empleados.models import Empleado
    from apps.nomina.models import ReciboNomina, IncidenciaNomina
    from apps.desempeno.models import AsignacionKPI
    from apps.vacaciones.models import SolicitudVacaciones

    empleado_nombre = params.get('empleado_nombre')

    if not empleado_nombre:
        return {'success': False, 'error': 'Debes especificar el nombre del empleado'}

    empresa_contexto = contexto.get('empresa_contexto')
    empleados = _buscar_empleado_por_nombre(empleado_nombre, empresa_contexto, incluir_bajas=True)

    if not empleados.exists():
        return {'success': False, 'error': f'No se encontró empleado con nombre "{empleado_nombre}"'}

    if empleados.count() > 1:
        nombres = [f"{e.nombre_completo} ({e.estado})" for e in empleados[:5]]
        return {
            'success': False,
            'error': f'Se encontraron múltiples empleados: {", ".join(nombres)}. Sé más específico.'
        }

    empleado = empleados.first()

    # Datos básicos
    historial = {
        'empleado': {
            'id': str(empleado.id),
            'nombre': empleado.nombre_completo,
            'estado': empleado.estado,
            'puesto': empleado.puesto or 'Sin puesto',
            'departamento': empleado.departamento or 'Sin departamento',
            'fecha_ingreso': empleado.fecha_ingreso.strftime('%d/%m/%Y'),
            'antiguedad': f"{empleado.antiguedad['anos']} años, {empleado.antiguedad['meses']} meses, {empleado.antiguedad['dias']} días",
            'salario_diario': f"${empleado.salario_diario:,.2f}" if empleado.salario_diario else 'No registrado',
        }
    }

    # Si está de baja, agregar info
    if empleado.estado == 'baja':
        tipo_display = dict(Empleado.TipoBaja.choices).get(empleado.tipo_baja, 'No especificado')
        historial['baja'] = {
            'fecha_baja': empleado.fecha_baja.strftime('%d/%m/%Y') if empleado.fecha_baja else 'N/A',
            'tipo_baja': tipo_display,
            'motivo': empleado.motivo_baja or 'No especificado',
            'monto_liquidacion': f"${empleado.monto_liquidacion:,.2f}" if empleado.monto_liquidacion else 'No calculado',
            'liquidacion_pagada': 'Sí' if empleado.liquidacion_pagada else 'No',
        }

    # Últimos recibos de nómina
    recibos = ReciboNomina.objects.filter(empleado=empleado).order_by('-periodo__fecha_fin')[:12]
    historial['recibos_nomina'] = [{
        'periodo': r.periodo.nombre if hasattr(r.periodo, 'nombre') else str(r.periodo),
        'fecha': r.periodo.fecha_fin.strftime('%d/%m/%Y') if r.periodo.fecha_fin else 'N/A',
        'neto': f"${r.neto_a_pagar:,.2f}" if r.neto_a_pagar else '$0.00',
    } for r in recibos]

    # KPIs históricos
    kpis = AsignacionKPI.objects.filter(empleado=empleado).order_by('-fecha_inicio')[:10]
    historial['kpis'] = [{
        'nombre': k.nombre_personalizado or 'KPI',
        'periodo': k.periodo or 'N/A',
        'meta': f"{k.meta:,.0f}" if k.meta else 'N/A',
        'logrado': f"{k.valor_logrado:,.0f}" if k.valor_logrado else '0',
        'porcentaje': f"{k.porcentaje_cumplimiento:.1f}%" if k.porcentaje_cumplimiento else '0%',
        'estado': k.estado,
    } for k in kpis]

    # Incidencias
    incidencias = IncidenciaNomina.objects.filter(empleado=empleado).order_by('-fecha_inicio')[:10]
    historial['incidencias'] = [{
        'tipo': i.tipo,
        'fecha': i.fecha_inicio.strftime('%d/%m/%Y') if i.fecha_inicio else 'N/A',
        'cantidad': i.cantidad or 1,
        'descripcion': i.descripcion or '',
    } for i in incidencias]

    # Vacaciones
    vacaciones = SolicitudVacaciones.objects.filter(empleado=empleado).order_by('-fecha_inicio')[:10]
    historial['vacaciones'] = [{
        'fecha_inicio': v.fecha_inicio.strftime('%d/%m/%Y') if v.fecha_inicio else 'N/A',
        'fecha_fin': v.fecha_fin.strftime('%d/%m/%Y') if v.fecha_fin else 'N/A',
        'dias': v.dias_solicitados if hasattr(v, 'dias_solicitados') else 'N/A',
        'estado': v.estado,
    } for v in vacaciones]

    # Formatear mensaje
    lineas = [f"**Historial de {empleado.nombre_completo}**\n"]
    lineas.append(f"Estado: **{empleado.estado.upper()}**")
    lineas.append(f"Puesto: {empleado.puesto} | Depto: {empleado.departamento}")
    lineas.append(f"Antigüedad: {historial['empleado']['antiguedad']}")

    if empleado.estado == 'baja':
        lineas.append(f"\n**Información de baja:**")
        lineas.append(f"Fecha: {historial['baja']['fecha_baja']} | Tipo: {historial['baja']['tipo_baja']}")
        lineas.append(f"Liquidación: {historial['baja']['monto_liquidacion']}")

    if historial['recibos_nomina']:
        lineas.append(f"\n**Últimos {len(historial['recibos_nomina'])} recibos de nómina:**")
        for r in historial['recibos_nomina'][:5]:
            lineas.append(f"  - {r['fecha']}: {r['neto']}")

    if historial['kpis']:
        lineas.append(f"\n**KPIs ({len(historial['kpis'])}):**")
        for k in historial['kpis'][:3]:
            lineas.append(f"  - {k['nombre']}: {k['porcentaje']} de meta")

    return {
        'success': True,
        'mensaje': '\n'.join(lineas),
        'historial': historial
    }


def reactivar_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
    """Reactiva un empleado dado de baja"""
    from apps.empleados.models import Empleado
    from datetime import datetime

    empleado_nombre = params.get('empleado_nombre')
    nuevo_salario = params.get('nuevo_salario')
    nuevo_puesto = params.get('nuevo_puesto')
    fecha_reingreso = params.get('fecha_reingreso')

    if not empleado_nombre:
        return {'success': False, 'error': 'Debes especificar el nombre del extrabajador'}

    empresa_contexto = contexto.get('empresa_contexto')

    # Buscar solo en empleados dados de baja
    empleados = Empleado.objects.filter(estado='baja')
    if empresa_contexto:
        empleados = empleados.filter(empresa=empresa_contexto)

    # Filtrar por nombre
    from django.db.models import Q
    filtro = Q(nombre__icontains=empleado_nombre) | Q(apellido_paterno__icontains=empleado_nombre)
    empleados = empleados.filter(filtro)

    if not empleados.exists():
        return {'success': False, 'error': f'No se encontró extrabajador con nombre "{empleado_nombre}"'}

    if empleados.count() > 1:
        nombres = [e.nombre_completo for e in empleados[:5]]
        return {
            'success': False,
            'error': f'Se encontraron múltiples extrabajadores: {", ".join(nombres)}. Sé más específico.'
        }

    empleado = empleados.first()

    # Parsear fecha de reingreso
    if fecha_reingreso:
        if isinstance(fecha_reingreso, str):
            fecha_reingreso = datetime.strptime(fecha_reingreso, '%Y-%m-%d').date()
    else:
        fecha_reingreso = date.today()

    # Guardar datos anteriores para historial
    baja_anterior = {
        'fecha_baja': empleado.fecha_baja.strftime('%d/%m/%Y') if empleado.fecha_baja else 'N/A',
        'tipo_baja': empleado.tipo_baja,
        'antiguedad_anterior': f"{empleado.antiguedad['anos']} años, {empleado.antiguedad['meses']} meses",
    }

    # Reactivar empleado
    empleado.estado = 'activo'
    empleado.fecha_ingreso = fecha_reingreso  # Nueva fecha de ingreso

    # Limpiar datos de baja (pero mantener historial en motivo)
    historial_nota = f"RECONTRATACIÓN {fecha_reingreso.strftime('%d/%m/%Y')}. Baja anterior: {baja_anterior['fecha_baja']} ({baja_anterior['tipo_baja']}). Antigüedad anterior: {baja_anterior['antiguedad_anterior']}."
    if empleado.motivo_baja:
        empleado.motivo_baja = f"{empleado.motivo_baja}\n\n{historial_nota}"
    else:
        empleado.motivo_baja = historial_nota

    # Actualizar salario y puesto si se especifican
    if nuevo_salario:
        empleado.salario_diario = Decimal(str(nuevo_salario))

    if nuevo_puesto:
        empleado.puesto = nuevo_puesto

    empleado.save()

    return {
        'success': True,
        'mensaje': f'{empleado.nombre_completo} reactivado exitosamente',
        'empleado': empleado.nombre_completo,
        'fecha_reingreso': fecha_reingreso.strftime('%d/%m/%Y'),
        'puesto': empleado.puesto,
        'salario_diario': f"${empleado.salario_diario:,.2f}" if empleado.salario_diario else 'No especificado',
        'nota': 'La antigüedad se reinicia desde la fecha de reingreso. El historial anterior se conserva.'
    }


# ============ ACCIONES DE EXPEDIENTE ============

def ver_expediente(usuario, params: Dict, contexto: Dict) -> Dict:
    """Muestra el expediente de un empleado"""
    from apps.empleados.models import Empleado, DocumentoEmpleado

    empleado_nombre = params.get('empleado_nombre')
    tipo_doc = params.get('tipo_documento')
    empresa = contexto.get('empresa_contexto')

    if not empleado_nombre:
        return {'success': False, 'error': 'Debes especificar el nombre del empleado'}

    # Buscar empleado
    empleados = _buscar_empleado_por_nombre(empleado_nombre, empresa, incluir_bajas=True)

    if not empleados.exists():
        return {'success': False, 'error': f'No encontré a {empleado_nombre}'}

    if empleados.count() > 1:
        nombres = [e.nombre_completo for e in empleados[:5]]
        return {
            'success': False,
            'error': f'Se encontraron múltiples empleados: {", ".join(nombres)}. Sé más específico.'
        }

    empleado = empleados.first()

    # Obtener documentos
    docs = DocumentoEmpleado.objects.filter(empleado=empleado)
    if tipo_doc:
        docs = docs.filter(tipo=tipo_doc)

    docs = docs.order_by('tipo', '-created_at')

    # Agrupar por categoría
    personales = docs.filter(tipo__in=['ine', 'curp', 'rfc', 'comprobante_domicilio', 'acta_nacimiento', 'nss', 'foto'])
    laborales = docs.filter(tipo__in=['contrato', 'alta_imss', 'mod_salario', 'carta_renuncia', 'carta_despido', 'finiquito', 'constancia'])
    incidencias_docs = docs.filter(tipo__in=['incapacidad', 'permiso', 'acta_admin'])
    nomina_docs = docs.filter(tipo__in=['recibo', 'cfdi'])
    otros = docs.filter(tipo__in=['evaluacion', 'capacitacion', 'otro'])

    def format_docs(queryset):
        return [{
            'tipo': d.get_tipo_display(),
            'nombre': d.nombre,
            'fecha': d.created_at.strftime('%d/%m/%Y'),
            'estatus': d.estatus,
            'id': str(d.id),
        } for d in queryset]

    documentos = {
        'personales': format_docs(personales),
        'laborales': format_docs(laborales),
        'incidencias': format_docs(incidencias_docs),
        'nomina': format_docs(nomina_docs),
        'otros': format_docs(otros),
    }

    # Formatear mensaje
    lineas = [f"**Expediente de {empleado.nombre_completo}**\n"]

    if documentos['personales']:
        lineas.append("**Documentos Personales:**")
        for d in documentos['personales']:
            lineas.append(f"  - {d['tipo']}: {d['nombre']} ({d['fecha']})")

    if documentos['laborales']:
        lineas.append("\n**Documentos Laborales:**")
        for d in documentos['laborales']:
            lineas.append(f"  - {d['tipo']}: {d['nombre']} ({d['fecha']})")

    if documentos['incidencias']:
        lineas.append("\n**Incidencias/Permisos:**")
        for d in documentos['incidencias']:
            lineas.append(f"  - {d['tipo']}: {d['nombre']} ({d['fecha']})")

    if not docs.exists():
        lineas.append("_No hay documentos en el expediente_")

    lineas.append(f"\n**Total:** {docs.count()} documentos")

    return {
        'success': True,
        'mensaje': '\n'.join(lineas),
        'empleado': empleado.nombre_completo,
        'documentos': documentos,
        'total': docs.count(),
    }


def verificar_documentos_pendientes(usuario, params: Dict, contexto: Dict) -> Dict:
    """Verifica qué documentos faltan en expedientes"""
    from apps.empleados.models import Empleado, DocumentoEmpleado

    DOCUMENTOS_REQUERIDOS = ['ine', 'curp', 'rfc', 'comprobante_domicilio', 'contrato']

    empleado_nombre = params.get('empleado_nombre')
    empresa = contexto.get('empresa_contexto')

    if empleado_nombre:
        empleados = _buscar_empleado_por_nombre(empleado_nombre, empresa, incluir_bajas=False)
        if not empleados.exists():
            return {'success': False, 'error': f'No encontré a {empleado_nombre}'}
    else:
        empleados = Empleado.objects.filter(estado='activo')
        if empresa:
            empleados = empleados.filter(empresa=empresa)

    resultado = []
    for emp in empleados[:50]:  # Limitar a 50
        docs_existentes = DocumentoEmpleado.objects.filter(
            empleado=emp
        ).values_list('tipo', flat=True)

        faltantes = [d for d in DOCUMENTOS_REQUERIDOS if d not in docs_existentes]

        if faltantes:
            resultado.append({
                'empleado': emp.nombre_completo,
                'empleado_id': str(emp.id),
                'faltantes': faltantes,
                'faltantes_display': [DocumentoEmpleado.TipoDocumento(d).label for d in faltantes],
            })

    if not resultado:
        return {
            'success': True,
            'mensaje': '✅ Todos los expedientes están completos',
            'pendientes': []
        }

    # Formatear mensaje
    lineas = [f"📋 **Documentos pendientes ({len(resultado)} empleados)**\n"]
    for r in resultado[:20]:
        lineas.append(f"**{r['empleado']}:**")
        for f in r['faltantes_display']:
            lineas.append(f"  - ❌ {f}")

    return {
        'success': True,
        'mensaje': '\n'.join(lineas),
        'total_empleados': len(resultado),
        'pendientes': resultado,
    }


def busqueda_avanzada_empleados(usuario, params: Dict, contexto: Dict) -> Dict:
    """Busqueda avanzada de empleados con multiples filtros"""
    from apps.empleados.models import Empleado
    from django.db.models import Q
    from datetime import date
    from dateutil.relativedelta import relativedelta

    empresa = contexto.get('empresa_contexto')
    if not empresa:
        return {'success': False, 'error': 'No hay empresa en contexto'}

    # Parametros de busqueda
    busqueda = params.get('busqueda', '')
    departamento = params.get('departamento')
    puesto = params.get('puesto')
    estado = params.get('estado')
    salario_min = params.get('salario_min')
    salario_max = params.get('salario_max')
    jefe_nombre = params.get('jefe')
    antiguedad_min = params.get('antiguedad_min')

    empleados = Empleado.objects.filter(empresa=empresa)

    # Busqueda por texto
    if busqueda:
        empleados = empleados.filter(
            Q(nombre__icontains=busqueda) |
            Q(apellido_paterno__icontains=busqueda) |
            Q(apellido_materno__icontains=busqueda) |
            Q(rfc__icontains=busqueda) |
            Q(curp__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    # Filtros especificos
    if departamento:
        empleados = empleados.filter(departamento__icontains=departamento)

    if puesto:
        empleados = empleados.filter(puesto__icontains=puesto)

    if estado:
        empleados = empleados.filter(estado=estado)

    if salario_min:
        empleados = empleados.filter(salario_diario__gte=Decimal(salario_min))

    if salario_max:
        empleados = empleados.filter(salario_diario__lte=Decimal(salario_max))

    if jefe_nombre:
        empleados = empleados.filter(
            Q(jefe_directo__nombre__icontains=jefe_nombre) |
            Q(jefe_directo__apellido_paterno__icontains=jefe_nombre)
        )

    # Filtrar por antiguedad minima
    if antiguedad_min:
        try:
            anos = int(antiguedad_min)
            fecha_limite = date.today() - relativedelta(years=anos)
            empleados = empleados.filter(fecha_ingreso__lte=fecha_limite)
        except (ValueError, TypeError):
            pass

    empleados = empleados.select_related('jefe_directo').order_by('apellido_paterno', 'nombre')[:50]

    if not empleados.exists():
        return {
            'success': True,
            'mensaje': 'No se encontraron empleados con los filtros especificados',
            'datos': {'total': 0, 'empleados': []}
        }

    lista = []
    for e in empleados:
        # Calcular antiguedad
        antiguedad = 'N/A'
        if e.fecha_ingreso:
            dias = (date.today() - e.fecha_ingreso).days
            anos = dias // 365
            meses = (dias % 365) // 30
            antiguedad = f"{anos}a {meses}m"

        lista.append({
            'id': str(e.id),
            'nombre': e.nombre_completo,
            'puesto': e.puesto or 'N/A',
            'departamento': e.departamento or 'N/A',
            'estado': e.estado,
            'antiguedad': antiguedad,
            'salario_diario': float(e.salario_diario) if e.salario_diario else 0,
            'jefe': e.jefe_directo.nombre_completo if e.jefe_directo else 'N/A',
        })

    # Construir mensaje
    filtros_usados = []
    if busqueda:
        filtros_usados.append(f"busqueda='{busqueda}'")
    if departamento:
        filtros_usados.append(f"depto='{departamento}'")
    if puesto:
        filtros_usados.append(f"puesto='{puesto}'")
    if estado:
        filtros_usados.append(f"estado='{estado}'")
    if salario_min or salario_max:
        filtros_usados.append(f"salario ${salario_min or 0}-${salario_max or 'max'}")
    if jefe_nombre:
        filtros_usados.append(f"jefe='{jefe_nombre}'")
    if antiguedad_min:
        filtros_usados.append(f"antiguedad>={antiguedad_min} anos")

    filtros_str = ', '.join(filtros_usados) if filtros_usados else 'sin filtros'

    return {
        'success': True,
        'mensaje': f'Se encontraron {len(lista)} empleados ({filtros_str})',
        'datos': {
            'total': len(lista),
            'empleados': lista,
            'filtros_aplicados': filtros_usados
        }
    }
