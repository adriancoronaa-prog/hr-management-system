"""
Acciones de IA para el modulo de prestaciones
"""
from typing import Dict
from datetime import date


def registrar_acciones():
    """Registra todas las acciones de prestaciones"""
    from apps.chat.acciones_registry import registrar_accion
    from .models import (
        PlanPrestaciones, PrestacionAdicional, AjusteIndividual,
        CATEGORIAS_PRESTACION, TIPOS_PRESTACION_CATALOGO
    )

    # ============================================================
    # ACCION 70: Ver catalogo de prestaciones
    # ============================================================
    def ver_catalogo_prestaciones(usuario, params: Dict, contexto: Dict) -> Dict:
        """Muestra el catalogo de prestaciones disponibles"""
        categorias_con_tipos = {}
        for codigo, nombre, categoria in TIPOS_PRESTACION_CATALOGO:
            if categoria not in categorias_con_tipos:
                cat_nombre = dict(CATEGORIAS_PRESTACION).get(categoria, categoria)
                categorias_con_tipos[categoria] = {
                    'nombre': cat_nombre,
                    'tipos': []
                }
            categorias_con_tipos[categoria]['tipos'].append({
                'codigo': codigo,
                'nombre': nombre
            })

        mensaje = "**Catalogo de Prestaciones Adicionales**\n\n"
        for cat_codigo, cat_data in categorias_con_tipos.items():
            mensaje += f"**{cat_data['nombre']}:**\n"
            for tipo in cat_data['tipos']:
                mensaje += f"  - {tipo['nombre']}\n"
            mensaje += "\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': categorias_con_tipos
        }

    registrar_accion(
        nombre='ver_catalogo_prestaciones',
        descripcion='Muestra el catalogo de tipos de prestaciones adicionales disponibles',
        permisos=['es_admin', 'es_rrhh'],
        parametros={},
        ejemplo='Muestrame el catalogo de prestaciones',
        funcion=ver_catalogo_prestaciones
    )

    # ============================================================
    # ACCION 71: Ver planes de prestaciones
    # ============================================================
    def ver_planes_prestaciones(usuario, params: Dict, contexto: Dict) -> Dict:
        """Lista los planes de prestaciones de la empresa"""
        empresa_id = params.get('empresa_id') or contexto.get('empresa_id')

        qs = PlanPrestaciones.objects.prefetch_related('prestaciones_adicionales')

        if not usuario.es_super_admin:
            qs = qs.filter(empresa__in=usuario.empresas.all())

        if empresa_id:
            qs = qs.filter(empresa_id=empresa_id)

        planes = qs.filter(activo=True)

        if not planes.exists():
            return {
                'exito': True,
                'mensaje': 'No hay planes de prestaciones configurados.',
                'datos': []
            }

        mensaje = "**Planes de Prestaciones**\n\n"
        datos = []

        for plan in planes:
            mensaje += f"**{plan.nombre}** ({plan.empresa.razon_social})\n"
            if plan.es_default:
                mensaje += "  Plan por defecto\n"
            mensaje += f"  - Vacaciones extra: +{plan.vacaciones_dias_extra} dias\n"
            mensaje += f"  - Prima vacacional: {plan.prima_vacacional_porcentaje}%\n"
            mensaje += f"  - Aguinaldo: {plan.aguinaldo_dias} dias\n"

            adicionales = plan.prestaciones_adicionales.filter(activo=True)
            if adicionales.exists():
                mensaje += f"  - Prestaciones adicionales: {adicionales.count()}\n"
                for prest in adicionales[:5]:
                    mensaje += f"    - {prest.nombre}\n"
                if adicionales.count() > 5:
                    mensaje += f"    ... y {adicionales.count() - 5} mas\n"
            mensaje += "\n"

            datos.append({
                'id': plan.id,
                'nombre': plan.nombre,
                'empresa': plan.empresa.razon_social,
                'es_default': plan.es_default,
                'vacaciones_extra': plan.vacaciones_dias_extra,
                'prima_vacacional': plan.prima_vacacional_porcentaje,
                'aguinaldo_dias': plan.aguinaldo_dias,
                'prestaciones_adicionales': adicionales.count()
            })

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': datos
        }

    registrar_accion(
        nombre='ver_planes_prestaciones',
        descripcion='Lista los planes de prestaciones de la empresa',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empresa_id': '(Opcional) ID de la empresa especifica'
        },
        ejemplo='Ver planes de prestaciones',
        funcion=ver_planes_prestaciones
    )

    # ============================================================
    # ACCION 72: Crear plan de prestaciones
    # ============================================================
    def crear_plan_prestaciones(usuario, params: Dict, contexto: Dict) -> Dict:
        """Crea un nuevo plan de prestaciones"""
        empresa_id = params.get('empresa_id') or contexto.get('empresa_id')
        nombre = params.get('nombre')

        if not empresa_id:
            return {'exito': False, 'mensaje': 'Para que empresa quieres crear el plan?'}
        if not nombre:
            return {'exito': False, 'mensaje': 'Que nombre tendra el plan? (ej: "Plan Ejecutivo")'}

        from apps.empresas.models import Empresa
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            if not usuario.es_super_admin and empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a esta empresa.'}
        except Empresa.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empresa no encontrada.'}

        plan = PlanPrestaciones.objects.create(
            empresa=empresa,
            nombre=nombre,
            vacaciones_dias_extra=params.get('vacaciones_extra', 0),
            prima_vacacional_porcentaje=params.get('prima_vacacional', 25),
            aguinaldo_dias=params.get('aguinaldo_dias', 15),
            es_default=params.get('es_default', False),
            created_by=usuario
        )

        mensaje = f"Plan **{plan.nombre}** creado para {empresa.razon_social}.\n\n"
        mensaje += "Configuracion:\n"
        mensaje += f"- Vacaciones extra: +{plan.vacaciones_dias_extra} dias sobre ley\n"
        mensaje += f"- Prima vacacional: {plan.prima_vacacional_porcentaje}%\n"
        mensaje += f"- Aguinaldo: {plan.aguinaldo_dias} dias\n\n"
        mensaje += "Deseas agregar prestaciones adicionales al plan? (vales, seguros, etc.)"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {'plan_id': plan.id, 'nombre': plan.nombre}
        }

    registrar_accion(
        nombre='crear_plan_prestaciones',
        descripcion='Crea un nuevo plan de prestaciones para una empresa',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empresa_id': 'ID de la empresa',
            'nombre': 'Nombre del plan',
            'vacaciones_extra': '(Opcional) Dias extra sobre ley (default: 0)',
            'prima_vacacional': '(Opcional) Porcentaje prima vacacional (default: 25)',
            'aguinaldo_dias': '(Opcional) Dias de aguinaldo (default: 15)',
            'es_default': '(Opcional) Si es el plan por defecto (default: false)'
        },
        ejemplo='Crear plan de prestaciones ejecutivo para la empresa',
        funcion=crear_plan_prestaciones
    )

    # ============================================================
    # ACCION 73: Agregar prestacion adicional a plan
    # ============================================================
    def agregar_prestacion_plan(usuario, params: Dict, contexto: Dict) -> Dict:
        """Agrega una prestacion adicional a un plan"""
        plan_id = params.get('plan_id')
        tipo_prestacion = params.get('tipo_prestacion')

        if not plan_id:
            return {'exito': False, 'mensaje': 'A que plan deseas agregar la prestacion? Dame el ID o nombre.'}

        try:
            plan = PlanPrestaciones.objects.get(id=plan_id)
            if not usuario.es_super_admin and plan.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este plan.'}
        except PlanPrestaciones.DoesNotExist:
            return {'exito': False, 'mensaje': 'Plan no encontrado.'}

        if not tipo_prestacion:
            # Mostrar catalogo
            tipos_disponibles = "\n".join([f"- {codigo}: {nombre}" for codigo, nombre, _ in TIPOS_PRESTACION_CATALOGO[:15]])
            return {
                'exito': False,
                'mensaje': f'Que tipo de prestacion deseas agregar?\n\nAlgunos ejemplos:\n{tipos_disponibles}\n\n... usa "ver catalogo de prestaciones" para ver todos.'
            }

        # Buscar tipo en catalogo
        tipo_info = next((t for t in TIPOS_PRESTACION_CATALOGO if t[0] == tipo_prestacion), None)

        # Obtener valor y convertir a string
        valor_raw = params.get('valor', '0')
        valor_str = str(valor_raw) if valor_raw else '0'

        prestacion = PrestacionAdicional.objects.create(
            plan=plan,
            tipo_prestacion=tipo_prestacion if tipo_info else None,
            nombre=tipo_info[1] if tipo_info else params.get('nombre', tipo_prestacion),
            categoria=tipo_info[2] if tipo_info else params.get('categoria', 'otro'),
            tipo_valor=params.get('tipo_valor', 'monto'),
            valor=valor_str,
            periodicidad=params.get('periodicidad', 'mensual'),
            descripcion=params.get('descripcion', ''),
            proveedor=params.get('proveedor', ''),
            tope_mensual=params.get('tope_mensual'),
            tope_anual=params.get('tope_anual'),
            porcentaje_empresa=params.get('porcentaje_empresa'),
            porcentaje_empleado=params.get('porcentaje_empleado'),
            aplica_a_dependientes=params.get('aplica_dependientes', False),
            numero_dependientes=params.get('num_dependientes')
        )

        mensaje = f"Prestacion **{prestacion.nombre}** agregada al plan {plan.nombre}.\n\n"
        if prestacion.valor and prestacion.valor != '0':
            mensaje += f"- Valor: ${prestacion.valor} ({prestacion.get_periodicidad_display()})\n"
        if prestacion.proveedor:
            mensaje += f"- Proveedor: {prestacion.proveedor}\n"
        mensaje += "\nDeseas agregar otra prestacion?"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {'prestacion_id': prestacion.id}
        }

    registrar_accion(
        nombre='agregar_prestacion_plan',
        descripcion='Agrega una prestacion adicional a un plan existente',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'plan_id': 'ID del plan',
            'tipo_prestacion': 'Tipo del catalogo (vales_despensa, sgmm, etc.)',
            'nombre': '(Opcional si hay tipo) Nombre personalizado',
            'valor': '(Opcional) Monto o porcentaje',
            'periodicidad': '(Opcional) mensual/anual/unica',
            'proveedor': '(Opcional) Nombre del proveedor',
            'tope_mensual': '(Opcional) Tope mensual en pesos',
            'porcentaje_empresa': '(Opcional) % que aporta la empresa',
            'porcentaje_empleado': '(Opcional) % que aporta el empleado'
        },
        ejemplo='Agregar vales de despensa al plan',
        funcion=agregar_prestacion_plan
    )

    # ============================================================
    # ACCION 74: Ver prestaciones de un empleado
    # ============================================================
    def ver_prestaciones_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
        """Muestra las prestaciones que tiene un empleado"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id') or contexto.get('empleado_id')

        if not empleado_id:
            return {'exito': False, 'mensaje': 'De que empleado quieres ver las prestaciones?'}

        try:
            empleado = Empleado.objects.select_related('plan_prestaciones', 'empresa').get(id=empleado_id)
            if not usuario.es_super_admin and empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este empleado.'}
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}

        plan = empleado.plan_prestaciones
        if not plan:
            # Buscar plan default de la empresa
            plan = PlanPrestaciones.objects.filter(empresa=empleado.empresa, es_default=True).first()

        mensaje = f"**Prestaciones de {empleado.nombre_completo}**\n\n"

        if not plan:
            mensaje += "No tiene plan de prestaciones asignado.\n"
            mensaje += "Prestaciones minimas de ley:\n"
            mensaje += "- Vacaciones: segun LFT\n"
            mensaje += "- Prima vacacional: 25%\n"
            mensaje += "- Aguinaldo: 15 dias\n"
            return {'exito': True, 'mensaje': mensaje, 'datos': {'plan': None}}

        mensaje += f"**Plan:** {plan.nombre}\n\n"
        mensaje += "**Prestaciones de Ley (mejoradas):**\n"
        mensaje += f"- Vacaciones: +{plan.vacaciones_dias_extra} dias extra sobre ley\n"
        mensaje += f"- Prima vacacional: {plan.prima_vacacional_porcentaje}%\n"
        mensaje += f"- Aguinaldo: {plan.aguinaldo_dias} dias\n\n"

        # Prestaciones adicionales
        adicionales = plan.prestaciones_adicionales.filter(activo=True)
        if adicionales.exists():
            mensaje += "**Prestaciones Adicionales:**\n"
            for prest in adicionales:
                mensaje += f"- {prest.nombre}"
                if prest.valor and prest.valor != '0':
                    mensaje += f": ${prest.valor}"
                    if prest.periodicidad != 'unica':
                        mensaje += f" ({prest.get_periodicidad_display()})"
                mensaje += "\n"

        # Ajustes individuales
        ajustes = empleado.ajustes_prestaciones.filter(activo=True)
        if ajustes.exists():
            mensaje += "\n**Ajustes Individuales:**\n"
            for ajuste in ajustes:
                mensaje += f"- {ajuste.concepto}: "
                if ajuste.tipo_ajuste == 'reemplaza':
                    mensaje += f"{ajuste.valor} (reemplaza valor del plan)\n"
                else:
                    mensaje += f"+{ajuste.valor} (adicional al plan)\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {
                'plan_id': plan.id,
                'plan_nombre': plan.nombre,
                'adicionales': adicionales.count(),
                'ajustes': ajustes.count()
            }
        }

    registrar_accion(
        nombre='ver_prestaciones_empleado',
        descripcion='Muestra las prestaciones que tiene asignadas un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'empleado_id': 'ID del empleado'
        },
        ejemplo='Ver prestaciones del empleado Juan',
        funcion=ver_prestaciones_empleado
    )

    # ============================================================
    # ACCION 75: Ver mis prestaciones (empleado)
    # ============================================================
    def ver_mis_prestaciones(usuario, params: Dict, contexto: Dict) -> Dict:
        """El empleado ve sus propias prestaciones"""
        if not hasattr(usuario, 'empleado') or not usuario.empleado:
            return {'exito': False, 'mensaje': 'No tienes un perfil de empleado vinculado.'}

        # Reutilizar la funcion anterior
        return ver_prestaciones_empleado(usuario, {'empleado_id': usuario.empleado.id}, contexto)

    registrar_accion(
        nombre='ver_mis_prestaciones',
        descripcion='Muestra las prestaciones del empleado actual',
        permisos=['es_empleado', 'es_jefe', 'es_rrhh', 'es_admin'],
        parametros={},
        ejemplo='Ver mis prestaciones',
        funcion=ver_mis_prestaciones
    )

    # ============================================================
    # ACCION 76: Asignar plan a empleado
    # ============================================================
    def asignar_plan_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
        """Asigna un plan de prestaciones a un empleado"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id')
        plan_id = params.get('plan_id')

        if not empleado_id:
            return {'exito': False, 'mensaje': 'A que empleado quieres asignar el plan?'}
        if not plan_id:
            return {'exito': False, 'mensaje': 'Que plan deseas asignar? Usa "ver planes de prestaciones" para ver opciones.'}

        try:
            empleado = Empleado.objects.get(id=empleado_id)
            plan = PlanPrestaciones.objects.get(id=plan_id)

            if not usuario.es_super_admin:
                if empleado.empresa not in usuario.empresas.all():
                    return {'exito': False, 'mensaje': 'No tienes acceso a este empleado.'}
                if plan.empresa != empleado.empresa:
                    return {'exito': False, 'mensaje': 'El plan no pertenece a la empresa del empleado.'}
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}
        except PlanPrestaciones.DoesNotExist:
            return {'exito': False, 'mensaje': 'Plan no encontrado.'}

        plan_anterior = empleado.plan_prestaciones
        empleado.plan_prestaciones = plan
        empleado.save()

        mensaje = f"Plan **{plan.nombre}** asignado a {empleado.nombre_completo}.\n"
        if plan_anterior:
            mensaje += f"(Plan anterior: {plan_anterior.nombre})\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {'empleado_id': empleado.id, 'plan_id': plan.id}
        }

    registrar_accion(
        nombre='asignar_plan_empleado',
        descripcion='Asigna un plan de prestaciones a un empleado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'plan_id': 'ID del plan a asignar'
        },
        ejemplo='Asignar plan ejecutivo al empleado Juan',
        funcion=asignar_plan_empleado
    )

    # ============================================================
    # ACCION 77: Crear ajuste individual
    # ============================================================
    def crear_ajuste_individual(usuario, params: Dict, contexto: Dict) -> Dict:
        """Crea un ajuste individual de prestaciones para un empleado"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id')
        concepto = params.get('concepto')
        valor = params.get('valor')

        if not empleado_id:
            return {'exito': False, 'mensaje': 'Para que empleado es el ajuste?'}
        if not concepto:
            return {
                'exito': False,
                'mensaje': 'Que concepto ajustaras?\nOpciones: vacaciones, aguinaldo, prima_vacacional, otro'
            }
        if valor is None:
            return {'exito': False, 'mensaje': 'Cual es el valor del ajuste?'}

        try:
            empleado = Empleado.objects.get(id=empleado_id)
            if not usuario.es_super_admin and empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este empleado.'}
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}

        # Obtener fecha_inicio
        fecha_inicio = params.get('fecha_inicio')
        if not fecha_inicio:
            fecha_inicio = date.today()

        ajuste = AjusteIndividual.objects.create(
            empleado=empleado,
            concepto=concepto,
            tipo_ajuste=params.get('tipo_ajuste', 'suma'),
            valor=str(valor),
            motivo=params.get('motivo', ''),
            fecha_inicio=fecha_inicio,
            fecha_fin=params.get('fecha_fin'),
            created_by=usuario
        )

        tipo_texto = "reemplaza el valor del plan" if ajuste.tipo_ajuste == 'reemplaza' else "se suma al plan"

        mensaje = f"Ajuste creado para {empleado.nombre_completo}:\n"
        mensaje += f"- Concepto: {ajuste.concepto}\n"
        mensaje += f"- Valor: {ajuste.valor} ({tipo_texto})\n"
        if ajuste.motivo:
            mensaje += f"- Motivo: {ajuste.motivo}\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {'ajuste_id': ajuste.id}
        }

    registrar_accion(
        nombre='crear_ajuste_individual',
        descripcion='Crea un ajuste individual de prestaciones para un empleado (vacaciones extra negociadas, etc.)',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'concepto': 'vacaciones/aguinaldo/prima_vacacional/otro',
            'valor': 'Valor numerico del ajuste',
            'tipo_ajuste': '(Opcional) suma/reemplaza (default: suma)',
            'motivo': '(Opcional) Motivo del ajuste (negociacion, promocion, etc.)',
            'fecha_inicio': '(Opcional) Desde cuando aplica',
            'fecha_fin': '(Opcional) Hasta cuando aplica'
        },
        ejemplo='Dar 5 dias extra de vacaciones a Juan por negociacion',
        funcion=crear_ajuste_individual
    )

    print("[OK] Acciones de Prestaciones registradas")
