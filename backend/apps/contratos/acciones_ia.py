"""
Acciones de IA para el modulo de Contratos
Acciones 78-84
"""
from typing import Dict
from datetime import date, timedelta


def registrar_acciones():
    """Registra todas las acciones de contratos"""
    from apps.chat.acciones_registry import registrar_accion
    from .models import Contrato, Adenda

    # ============================================================
    # ACCION 78: Ver contratos de un empleado
    # ============================================================
    def ver_contratos_empleado(usuario, params: Dict, contexto: Dict) -> Dict:
        """Ver todos los contratos de un empleado especifico"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id') or contexto.get('empleado_id')

        if not empleado_id:
            return {'exito': False, 'mensaje': 'De que empleado quieres ver los contratos?'}

        try:
            empleado = Empleado.objects.select_related('empresa').get(id=empleado_id)
            if usuario.rol not in ['admin', 'administrador'] and empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este empleado.'}
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}

        contratos = Contrato.objects.filter(empleado=empleado).order_by('-fecha_inicio')

        if not contratos.exists():
            return {
                'exito': True,
                'mensaje': f'{empleado.nombre_completo} no tiene contratos registrados.',
                'datos': []
            }

        mensaje = f"**Contratos de {empleado.nombre_completo}**\n\n"
        datos = []

        for contrato in contratos:
            estado_emoji = {
                'vigente': '🟢',
                'vencido': '🔴',
                'renovado': '🔄',
                'cancelado': '⚫',
                'terminado': '⬛'
            }.get(contrato.estado, '⚪')

            mensaje += f"{estado_emoji} **{contrato.get_tipo_contrato_display()}**\n"
            mensaje += f"   Inicio: {contrato.fecha_inicio}"
            if contrato.fecha_fin:
                mensaje += f" | Fin: {contrato.fecha_fin}"
                if contrato.es_vigente and contrato.dias_para_vencer:
                    mensaje += f" ({contrato.dias_para_vencer} dias)"
            else:
                mensaje += " | Sin fecha fin (indefinido)"
            mensaje += f"\n   Estado: {contrato.get_estado_display()}"
            if contrato.puesto:
                mensaje += f" | Puesto: {contrato.puesto}"
            mensaje += "\n\n"

            datos.append({
                'id': contrato.id,
                'tipo': contrato.tipo_contrato,
                'fecha_inicio': str(contrato.fecha_inicio),
                'fecha_fin': str(contrato.fecha_fin) if contrato.fecha_fin else None,
                'estado': contrato.estado,
                'puesto': contrato.puesto,
                'dias_para_vencer': contrato.dias_para_vencer
            })

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': datos
        }

    registrar_accion(
        nombre='ver_contratos_empleado',
        descripcion='Ver todos los contratos de un empleado especifico',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'empleado_id': 'ID del empleado'
        },
        ejemplo='Ver contratos del empleado con ID 45',
        funcion=ver_contratos_empleado
    )

    # ============================================================
    # ACCION 79: Ver contratos por vencer
    # ============================================================
    def ver_contratos_por_vencer(usuario, params: Dict, contexto: Dict) -> Dict:
        """Lista contratos que vencen en los proximos dias"""
        dias = params.get('dias', 30)
        empresa_id = params.get('empresa_id') or contexto.get('empresa_id')

        hoy = date.today()
        fecha_limite = hoy + timedelta(days=dias)

        qs = Contrato.objects.filter(
            estado=Contrato.Estado.VIGENTE,
            fecha_fin__isnull=False,
            fecha_fin__lte=fecha_limite,
            fecha_fin__gte=hoy
        ).select_related('empleado', 'empleado__empresa').order_by('fecha_fin')

        if usuario.rol not in ['admin', 'administrador']:
            qs = qs.filter(empleado__empresa__in=usuario.empresas.all())

        if empresa_id:
            qs = qs.filter(empleado__empresa_id=empresa_id)

        contratos = list(qs)

        if not contratos:
            return {
                'exito': True,
                'mensaje': f'No hay contratos que venzan en los proximos {dias} dias.',
                'datos': []
            }

        mensaje = f"**Contratos por vencer en los proximos {dias} dias**\n\n"
        datos = []

        # Agrupar por urgencia
        urgentes = [c for c in contratos if c.dias_para_vencer <= 7]
        proximos = [c for c in contratos if 7 < c.dias_para_vencer <= 15]
        otros = [c for c in contratos if c.dias_para_vencer > 15]

        if urgentes:
            mensaje += "🚨 **URGENTES (7 dias o menos):**\n"
            for c in urgentes:
                mensaje += f"  - {c.empleado.nombre_completo} ({c.empleado.empresa.razon_social})\n"
                mensaje += f"    Vence: {c.fecha_fin} ({c.dias_para_vencer} dias)\n"
                datos.append({
                    'id': c.id, 'empleado': c.empleado.nombre_completo,
                    'empresa': c.empleado.empresa.razon_social,
                    'fecha_fin': str(c.fecha_fin), 'dias': c.dias_para_vencer,
                    'urgencia': 'urgente'
                })

        if proximos:
            mensaje += "\n⚠️ **Proximos (8-15 dias):**\n"
            for c in proximos:
                mensaje += f"  - {c.empleado.nombre_completo} ({c.empleado.empresa.razon_social})\n"
                mensaje += f"    Vence: {c.fecha_fin} ({c.dias_para_vencer} dias)\n"
                datos.append({
                    'id': c.id, 'empleado': c.empleado.nombre_completo,
                    'empresa': c.empleado.empresa.razon_social,
                    'fecha_fin': str(c.fecha_fin), 'dias': c.dias_para_vencer,
                    'urgencia': 'proximo'
                })

        if otros:
            mensaje += "\n🔔 **Pendientes (mas de 15 dias):**\n"
            for c in otros:
                mensaje += f"  - {c.empleado.nombre_completo} - Vence: {c.fecha_fin}\n"
                datos.append({
                    'id': c.id, 'empleado': c.empleado.nombre_completo,
                    'empresa': c.empleado.empresa.razon_social,
                    'fecha_fin': str(c.fecha_fin), 'dias': c.dias_para_vencer,
                    'urgencia': 'normal'
                })

        mensaje += f"\n**Total: {len(contratos)} contratos por vencer**"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': datos
        }

    registrar_accion(
        nombre='ver_contratos_por_vencer',
        descripcion='Lista contratos que vencen en los proximos dias',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'dias': '(Opcional) Dias para buscar vencimientos (default 30)',
            'empresa_id': '(Opcional) ID de la empresa especifica'
        },
        ejemplo='Muestra contratos que vencen en 15 dias',
        funcion=ver_contratos_por_vencer
    )

    # ============================================================
    # ACCION 80: Crear contrato
    # ============================================================
    def crear_contrato(usuario, params: Dict, contexto: Dict) -> Dict:
        """Crea un nuevo contrato laboral para un empleado"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id') or contexto.get('empleado_id')
        tipo_contrato = params.get('tipo_contrato')
        fecha_inicio = params.get('fecha_inicio')
        salario_diario = params.get('salario_diario')

        if not empleado_id:
            return {'exito': False, 'mensaje': 'Para que empleado es el contrato?'}
        if not tipo_contrato:
            tipos = ", ".join([f"{t[0]}" for t in Contrato.TipoContrato.choices])
            return {'exito': False, 'mensaje': f'Que tipo de contrato sera?\nOpciones: {tipos}'}
        if not fecha_inicio:
            return {'exito': False, 'mensaje': 'Cual es la fecha de inicio? (YYYY-MM-DD)'}
        if not salario_diario:
            return {'exito': False, 'mensaje': 'Cual es el salario diario?'}

        try:
            empleado = Empleado.objects.select_related('empresa').get(id=empleado_id)
            if usuario.rol not in ['admin', 'administrador'] and empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este empleado.'}
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}

        # Verificar contrato vigente
        contrato_vigente = Contrato.objects.filter(
            empleado=empleado,
            estado=Contrato.Estado.VIGENTE
        ).first()

        if contrato_vigente:
            return {
                'exito': False,
                'mensaje': f'El empleado ya tiene un contrato vigente (ID: {contrato_vigente.id}).\n'
                          f'Debes renovarlo o terminarlo primero.'
            }

        # Validar tipo
        if tipo_contrato not in [t[0] for t in Contrato.TipoContrato.choices]:
            tipos = ", ".join([f"{t[0]}" for t in Contrato.TipoContrato.choices])
            return {'exito': False, 'mensaje': f'Tipo invalido. Opciones: {tipos}'}

        contrato = Contrato.objects.create(
            empleado=empleado,
            tipo_contrato=tipo_contrato,
            fecha_inicio=fecha_inicio,
            fecha_fin=params.get('fecha_fin'),
            puesto=params.get('puesto', ''),
            departamento=params.get('departamento', ''),
            salario_diario=salario_diario,
            salario_mensual=params.get('salario_mensual'),
            jornada=params.get('jornada', ''),
            horario=params.get('horario', ''),
            condiciones_especiales=params.get('condiciones_especiales', ''),
            created_by=usuario
        )

        mensaje = f"✅ Contrato creado para {empleado.nombre_completo}\n\n"
        mensaje += f"**Tipo:** {contrato.get_tipo_contrato_display()}\n"
        mensaje += f"**Inicio:** {contrato.fecha_inicio}\n"
        if contrato.fecha_fin:
            mensaje += f"**Fin:** {contrato.fecha_fin}\n"
        mensaje += f"**Salario diario:** ${contrato.salario_diario}\n"
        if contrato.puesto:
            mensaje += f"**Puesto:** {contrato.puesto}\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {'contrato_id': contrato.id}
        }

    registrar_accion(
        nombre='crear_contrato',
        descripcion='Crea un nuevo contrato laboral para un empleado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'empleado_id': 'ID del empleado',
            'tipo_contrato': 'Tipo: indefinido, temporal, obra, tiempo, capacitacion, prueba',
            'fecha_inicio': 'Fecha de inicio (YYYY-MM-DD)',
            'fecha_fin': '(Opcional) Fecha de fin',
            'puesto': '(Opcional) Puesto del empleado',
            'departamento': '(Opcional) Departamento',
            'salario_diario': 'Salario diario',
            'salario_mensual': '(Opcional) Salario mensual',
            'jornada': '(Opcional) diurna, nocturna, mixta',
            'horario': '(Opcional) Horario (ej: 9:00 - 18:00)',
            'condiciones_especiales': '(Opcional) Condiciones especiales'
        },
        ejemplo='Crea contrato indefinido para empleado 45 con salario diario de 500',
        funcion=crear_contrato
    )

    # ============================================================
    # ACCION 81: Renovar contrato
    # ============================================================
    def renovar_contrato(usuario, params: Dict, contexto: Dict) -> Dict:
        """Renueva un contrato existente creando uno nuevo vinculado"""
        contrato_id = params.get('contrato_id')
        fecha_inicio = params.get('fecha_inicio')

        if not contrato_id:
            return {'exito': False, 'mensaje': 'Cual es el ID del contrato a renovar?'}
        if not fecha_inicio:
            return {'exito': False, 'mensaje': 'Desde que fecha inicia el nuevo contrato?'}

        try:
            contrato = Contrato.objects.select_related('empleado', 'empleado__empresa').get(id=contrato_id)
            if usuario.rol not in ['admin', 'administrador'] and contrato.empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este contrato.'}
        except Contrato.DoesNotExist:
            return {'exito': False, 'mensaje': 'Contrato no encontrado.'}

        if contrato.estado not in [Contrato.Estado.VIGENTE, Contrato.Estado.VENCIDO]:
            return {
                'exito': False,
                'mensaje': f'El contrato tiene estado "{contrato.get_estado_display()}" y no puede renovarse.'
            }

        # Preparar kwargs para renovacion
        kwargs = {'created_by': usuario}
        if params.get('nuevo_salario_diario'):
            kwargs['salario_diario'] = params['nuevo_salario_diario']
        if params.get('nuevo_puesto'):
            kwargs['puesto'] = params['nuevo_puesto']
        if params.get('tipo_contrato'):
            kwargs['tipo_contrato'] = params['tipo_contrato']

        nuevo_contrato = contrato.renovar(
            fecha_inicio=fecha_inicio,
            fecha_fin=params.get('fecha_fin'),
            **kwargs
        )

        mensaje = f"✅ Contrato renovado para {contrato.empleado.nombre_completo}\n\n"
        mensaje += f"**Contrato anterior:** ID {contrato.id} (ahora estado: Renovado)\n"
        mensaje += f"**Nuevo contrato:** ID {nuevo_contrato.id}\n"
        mensaje += f"**Tipo:** {nuevo_contrato.get_tipo_contrato_display()}\n"
        mensaje += f"**Inicio:** {nuevo_contrato.fecha_inicio}\n"
        if nuevo_contrato.fecha_fin:
            mensaje += f"**Fin:** {nuevo_contrato.fecha_fin}\n"
        mensaje += f"**Salario diario:** ${nuevo_contrato.salario_diario}\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {
                'contrato_anterior_id': contrato.id,
                'nuevo_contrato_id': nuevo_contrato.id
            }
        }

    registrar_accion(
        nombre='renovar_contrato',
        descripcion='Renueva un contrato existente creando uno nuevo vinculado',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'contrato_id': 'ID del contrato a renovar',
            'fecha_inicio': 'Fecha inicio del nuevo contrato',
            'fecha_fin': '(Opcional) Fecha fin del nuevo contrato',
            'nuevo_salario_diario': '(Opcional) Nuevo salario diario',
            'nuevo_puesto': '(Opcional) Nuevo puesto',
            'tipo_contrato': '(Opcional) Nuevo tipo de contrato'
        },
        ejemplo='Renueva el contrato 12 desde el 1 de enero 2025',
        funcion=renovar_contrato
    )

    # ============================================================
    # ACCION 82: Crear adenda
    # ============================================================
    def crear_adenda(usuario, params: Dict, contexto: Dict) -> Dict:
        """Crea una adenda para modificar un contrato existente"""
        contrato_id = params.get('contrato_id')
        tipo = params.get('tipo')
        fecha_aplicacion = params.get('fecha_aplicacion')
        descripcion = params.get('descripcion')

        if not contrato_id:
            return {'exito': False, 'mensaje': 'A que contrato se aplicara la adenda?'}
        if not tipo:
            tipos = ", ".join([t[0] for t in Adenda.TipoAdenda.choices])
            return {'exito': False, 'mensaje': f'Que tipo de adenda es?\nOpciones: {tipos}'}
        if not fecha_aplicacion:
            return {'exito': False, 'mensaje': 'Desde que fecha aplica la adenda?'}
        if not descripcion:
            return {'exito': False, 'mensaje': 'Describe los cambios de la adenda.'}

        try:
            contrato = Contrato.objects.select_related('empleado').get(id=contrato_id)
            if usuario.rol not in ['admin', 'administrador'] and contrato.empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este contrato.'}
        except Contrato.DoesNotExist:
            return {'exito': False, 'mensaje': 'Contrato no encontrado.'}

        if contrato.estado != Contrato.Estado.VIGENTE:
            return {
                'exito': False,
                'mensaje': 'Solo se pueden crear adendas para contratos vigentes.'
            }

        # Validar tipo
        if tipo not in [t[0] for t in Adenda.TipoAdenda.choices]:
            tipos = ", ".join([t[0] for t in Adenda.TipoAdenda.choices])
            return {'exito': False, 'mensaje': f'Tipo invalido. Opciones: {tipos}'}

        # Guardar valores anteriores
        valores_anteriores = {}
        valores_nuevos = params.get('valores_nuevos', {})

        for campo in valores_nuevos.keys():
            if hasattr(contrato, campo):
                valores_anteriores[campo] = str(getattr(contrato, campo))

        adenda = Adenda.objects.create(
            contrato=contrato,
            tipo=tipo,
            fecha_aplicacion=fecha_aplicacion,
            descripcion=descripcion,
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos,
            created_by=usuario
        )

        mensaje = f"✅ Adenda creada para contrato de {contrato.empleado.nombre_completo}\n\n"
        mensaje += f"**Tipo:** {adenda.get_tipo_display()}\n"
        mensaje += f"**Fecha aplicacion:** {adenda.fecha_aplicacion}\n"
        mensaje += f"**Descripcion:** {adenda.descripcion}\n"

        if valores_nuevos:
            mensaje += "\n**Cambios:**\n"
            for campo, valor in valores_nuevos.items():
                anterior = valores_anteriores.get(campo, 'N/A')
                mensaje += f"  - {campo}: {anterior} → {valor}\n"

        # Aplicar inmediatamente si se solicita
        if params.get('aplicar_inmediatamente', False):
            adenda.aplicar()
            mensaje += "\n✅ Cambios aplicados al contrato."

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {'adenda_id': adenda.id, 'aplicada': adenda.aplicada}
        }

    registrar_accion(
        nombre='crear_adenda',
        descripcion='Crea una adenda para modificar un contrato existente',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'contrato_id': 'ID del contrato',
            'tipo': 'Tipo: cambio_salario, cambio_puesto, cambio_horario, cambio_departamento, extension, condiciones, otro',
            'fecha_aplicacion': 'Fecha en que aplica (YYYY-MM-DD)',
            'descripcion': 'Descripcion de los cambios',
            'valores_nuevos': '(Opcional) Dict con nuevos valores {campo: valor}',
            'aplicar_inmediatamente': '(Opcional) true para aplicar cambios al contrato'
        },
        ejemplo='Crear adenda de cambio de salario para contrato 12 con nuevo salario de 600 diarios',
        funcion=crear_adenda
    )

    # ============================================================
    # ACCION 83: Ver historial de contrato
    # ============================================================
    def ver_historial_contrato(usuario, params: Dict, contexto: Dict) -> Dict:
        """Ver historial completo de un contrato incluyendo renovaciones y adendas"""
        contrato_id = params.get('contrato_id')

        if not contrato_id:
            return {'exito': False, 'mensaje': 'Cual es el ID del contrato?'}

        try:
            contrato = Contrato.objects.select_related('empleado', 'empleado__empresa').get(id=contrato_id)
            if usuario.rol not in ['admin', 'administrador'] and contrato.empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este contrato.'}
        except Contrato.DoesNotExist:
            return {'exito': False, 'mensaje': 'Contrato no encontrado.'}

        # Encontrar contrato original
        original = contrato.contrato_original

        mensaje = f"**Historial de Contrato - {contrato.empleado.nombre_completo}**\n\n"

        # Construir cadena de contratos
        cadena = []
        actual = original
        while actual:
            cadena.append(actual)
            actual = Contrato.objects.filter(contrato_anterior=actual).first()

        mensaje += f"**Total renovaciones:** {len(cadena) - 1}\n\n"

        for i, c in enumerate(cadena):
            es_actual = c.id == contrato.id
            marker = "👉 " if es_actual else ""

            mensaje += f"{marker}**{'Contrato Original' if i == 0 else f'Renovacion {i}'}** (ID: {c.id})\n"
            mensaje += f"   Tipo: {c.get_tipo_contrato_display()}\n"
            mensaje += f"   Periodo: {c.fecha_inicio} - {c.fecha_fin or 'Indefinido'}\n"
            mensaje += f"   Estado: {c.get_estado_display()}\n"
            mensaje += f"   Salario: ${c.salario_diario}/dia\n"

            # Adendas de este contrato
            adendas = c.adendas.all()
            if adendas.exists():
                mensaje += f"   Adendas: {adendas.count()}\n"
                for adenda in adendas:
                    estado = "✅" if adenda.aplicada else "⏳"
                    mensaje += f"     {estado} {adenda.get_tipo_display()} ({adenda.fecha_aplicacion})\n"

            mensaje += "\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {
                'contrato_original_id': original.id,
                'total_renovaciones': len(cadena) - 1,
                'cadena_ids': [c.id for c in cadena]
            }
        }

    registrar_accion(
        nombre='ver_historial_contrato',
        descripcion='Ver historial completo de un contrato incluyendo renovaciones y adendas',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'contrato_id': 'ID del contrato'
        },
        ejemplo='Muestra el historial del contrato 12',
        funcion=ver_historial_contrato
    )

    # ============================================================
    # ACCION 84: Ver mi contrato (para empleados)
    # ============================================================
    def ver_mi_contrato(usuario, params: Dict, contexto: Dict) -> Dict:
        """Ver el contrato vigente del empleado actual"""
        if not hasattr(usuario, 'empleado') or not usuario.empleado:
            return {'exito': False, 'mensaje': 'No tienes un perfil de empleado vinculado.'}

        empleado = usuario.empleado
        contrato = Contrato.objects.filter(
            empleado=empleado,
            estado=Contrato.Estado.VIGENTE
        ).first()

        if not contrato:
            return {
                'exito': True,
                'mensaje': 'No tienes un contrato vigente registrado en el sistema.',
                'datos': None
            }

        mensaje = f"**Tu Contrato Actual**\n\n"
        mensaje += f"**Tipo:** {contrato.get_tipo_contrato_display()}\n"
        mensaje += f"**Estado:** {contrato.get_estado_display()}\n"
        mensaje += f"**Fecha inicio:** {contrato.fecha_inicio}\n"

        if contrato.fecha_fin:
            mensaje += f"**Fecha fin:** {contrato.fecha_fin}\n"
            if contrato.dias_para_vencer:
                if contrato.dias_para_vencer > 0:
                    mensaje += f"**Dias restantes:** {contrato.dias_para_vencer}\n"
                else:
                    mensaje += "⚠️ **Tu contrato esta vencido**\n"
        else:
            mensaje += "**Duracion:** Indefinida\n"

        if contrato.puesto:
            mensaje += f"**Puesto:** {contrato.puesto}\n"
        if contrato.departamento:
            mensaje += f"**Departamento:** {contrato.departamento}\n"
        if contrato.jornada:
            mensaje += f"**Jornada:** {contrato.jornada}\n"
        if contrato.horario:
            mensaje += f"**Horario:** {contrato.horario}\n"

        # Renovaciones anteriores
        if contrato.contrato_anterior:
            mensaje += f"\n*Este contrato es renovacion del contrato anterior.*\n"
            mensaje += f"*Total de contratos en tu historial: {len([c for c in [contrato.contrato_original] if c]) + contrato.numero_renovaciones + 1}*"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {
                'contrato_id': contrato.id,
                'tipo': contrato.tipo_contrato,
                'estado': contrato.estado,
                'fecha_inicio': str(contrato.fecha_inicio),
                'fecha_fin': str(contrato.fecha_fin) if contrato.fecha_fin else None,
                'dias_para_vencer': contrato.dias_para_vencer
            }
        }

    registrar_accion(
        nombre='ver_mi_contrato',
        descripcion='Ver el contrato vigente del empleado actual',
        permisos=['es_empleado', 'es_jefe', 'es_rrhh', 'es_admin'],
        parametros={},
        ejemplo='Muestra mi contrato actual',
        funcion=ver_mi_contrato
    )

    print("[OK] Acciones de Contratos registradas (78-84)")
