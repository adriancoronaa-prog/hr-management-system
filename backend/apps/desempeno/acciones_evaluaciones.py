"""
Acciones de IA para evaluaciones de desempeno formales
Acciones 85-92
"""
from typing import Dict
from django.utils import timezone
from django.db import models
from django.db.models import Avg, Count, Max


def registrar_acciones_evaluaciones():
    """Registra acciones de evaluaciones"""
    from apps.chat.acciones_registry import registrar_accion
    from .models import (
        Evaluacion, CatalogoCompetencia, EvaluacionCompetencia,
        RetroalimentacionContinua
    )

    # ============================================================
    # ACCION 85: Ver catalogo de competencias
    # ============================================================
    def ver_catalogo_competencias(usuario, params: Dict, contexto: Dict) -> Dict:
        """Lista las competencias disponibles"""
        empresa_id = params.get('empresa_id') or contexto.get('empresa_id')
        categoria = params.get('categoria')

        qs = CatalogoCompetencia.objects.filter(activo=True)

        # Globales + de la empresa
        if empresa_id:
            qs = qs.filter(models.Q(empresa_id=empresa_id) | models.Q(empresa__isnull=True))

        if categoria:
            qs = qs.filter(categoria=categoria)

        competencias = qs.order_by('categoria', 'nombre')

        if not competencias.exists():
            return {'exito': True, 'mensaje': 'No hay competencias configuradas.', 'datos': []}

        mensaje = "**Catalogo de Competencias**\n\n"

        categoria_actual = None
        for c in competencias:
            if c.categoria != categoria_actual:
                categoria_actual = c.categoria
                mensaje += f"\n**{c.get_categoria_display()}:**\n"

            obligatoria = " *" if c.es_obligatoria else ""
            mensaje += f"  - {c.nombre}{obligatoria}\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': [{'id': str(c.id), 'nombre': c.nombre, 'categoria': c.categoria} for c in competencias]
        }

    registrar_accion(
        nombre='ver_catalogo_competencias',
        descripcion='Lista las competencias disponibles para evaluar',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'categoria': '(Opcional) Filtrar por categoria',
            'empresa_id': '(Opcional) Empresa especifica'
        },
        ejemplo='Ver catalogo de competencias',
        funcion=ver_catalogo_competencias
    )

    # ============================================================
    # ACCION 86: Crear evaluacion de desempeno
    # ============================================================
    def crear_evaluacion(usuario, params: Dict, contexto: Dict) -> Dict:
        """Crea una nueva evaluacion de desempeno"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id')
        tipo = params.get('tipo', 'trimestral')
        modalidad = params.get('modalidad', '90')

        if not empleado_id:
            return {'exito': False, 'mensaje': 'Para que empleado es la evaluacion?'}

        try:
            empleado = Empleado.objects.get(id=empleado_id)
            if not usuario.es_super_admin and empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso a este empleado.'}
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}

        # Determinar evaluador
        evaluador = None
        if hasattr(usuario, 'empleado') and usuario.empleado:
            evaluador = usuario.empleado
        elif empleado.jefe_directo:
            evaluador = empleado.jefe_directo

        # Generar periodo
        hoy = timezone.now().date()
        if tipo == 'trimestral':
            q = (hoy.month - 1) // 3 + 1
            periodo = f"{hoy.year}-Q{q}"
        elif tipo == 'semestral':
            s = 1 if hoy.month <= 6 else 2
            periodo = f"{hoy.year}-S{s}"
        elif tipo == 'anual':
            periodo = str(hoy.year)
        else:
            periodo = f"{hoy.year}-{hoy.month:02d}"

        # Verificar si ya existe
        if Evaluacion.objects.filter(empleado=empleado, periodo=params.get('periodo', periodo), tipo=tipo).exists():
            return {
                'exito': False,
                'mensaje': f'Ya existe una evaluacion {tipo} para el periodo {params.get("periodo", periodo)}.'
            }

        evaluacion = Evaluacion.objects.create(
            empleado=empleado,
            evaluador=evaluador,
            tipo=tipo,
            periodo=params.get('periodo', periodo),
            fecha_inicio=params.get('fecha_inicio', hoy.replace(day=1)),
            fecha_fin=params.get('fecha_fin', hoy),
            modalidad=modalidad,
            incluye_autoevaluacion=modalidad in ['180', '360'],
            incluye_pares=modalidad == '360',
            incluye_subordinados=modalidad == '360',
            estado='borrador',
            created_by=usuario
        )

        # Agregar competencias obligatorias
        competencias = CatalogoCompetencia.objects.filter(
            activo=True,
            es_obligatoria=True
        ).filter(
            models.Q(empresa=empleado.empresa) | models.Q(empresa__isnull=True)
        )

        for comp in competencias:
            EvaluacionCompetencia.objects.create(
                evaluacion=evaluacion,
                competencia=comp,
                nivel_esperado=3
            )

        mensaje = f"Evaluacion creada para {empleado.nombre_completo}\n\n"
        mensaje += f"- Tipo: {evaluacion.get_tipo_display()}\n"
        mensaje += f"- Periodo: {evaluacion.periodo}\n"
        mensaje += f"- Modalidad: {modalidad} grados\n"
        if evaluacion.incluye_autoevaluacion:
            mensaje += "- Incluye autoevaluacion\n"
        if evaluacion.incluye_pares:
            mensaje += "- Incluye evaluacion de pares\n"
        mensaje += f"- Competencias a evaluar: {competencias.count()}\n"
        mensaje += f"\nEstado: Borrador. Usa 'iniciar evaluacion' cuando este lista."

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {'evaluacion_id': str(evaluacion.id)}
        }

    registrar_accion(
        nombre='crear_evaluacion',
        descripcion='Crea una nueva evaluacion de desempeno para un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'empleado_id': 'ID del empleado a evaluar',
            'tipo': '(Opcional) mensual/trimestral/semestral/anual (default: trimestral)',
            'modalidad': '(Opcional) 90/180/360 (default: 90)',
            'periodo': '(Opcional) Periodo personalizado'
        },
        ejemplo='Crear evaluacion trimestral para Juan',
        funcion=crear_evaluacion
    )

    # ============================================================
    # ACCION 87: Evaluar competencia
    # ============================================================
    def evaluar_competencia(usuario, params: Dict, contexto: Dict) -> Dict:
        """Evalua una competencia especifica en una evaluacion"""
        evaluacion_id = params.get('evaluacion_id')
        competencia_id = params.get('competencia_id')
        nivel = params.get('nivel')

        if not evaluacion_id:
            return {'exito': False, 'mensaje': 'En que evaluacion?'}
        if not competencia_id:
            return {'exito': False, 'mensaje': 'Que competencia evaluas?'}
        if nivel is None:
            return {'exito': False, 'mensaje': 'Que nivel asignas? (1-5)'}

        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
            if not usuario.es_super_admin and evaluacion.empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso.'}
        except Evaluacion.DoesNotExist:
            return {'exito': False, 'mensaje': 'Evaluacion no encontrada.'}

        try:
            eval_comp = EvaluacionCompetencia.objects.get(
                evaluacion=evaluacion,
                competencia_id=competencia_id
            )
        except EvaluacionCompetencia.DoesNotExist:
            return {'exito': False, 'mensaje': 'Competencia no asignada a esta evaluacion.'}

        nivel = int(nivel)
        if nivel < 1 or nivel > 5:
            return {'exito': False, 'mensaje': 'El nivel debe ser entre 1 y 5.'}

        eval_comp.nivel_obtenido = nivel
        eval_comp.comentarios = params.get('comentarios', '')
        eval_comp.ejemplos_conducta = params.get('ejemplos', '')

        if hasattr(usuario, 'empleado') and usuario.empleado:
            eval_comp.evaluador = usuario.empleado
            if usuario.empleado.id == evaluacion.empleado.id:
                eval_comp.evaluador_tipo = 'autoevaluacion'
            elif evaluacion.empleado.jefe_directo and usuario.empleado.id == evaluacion.empleado.jefe_directo.id:
                eval_comp.evaluador_tipo = 'jefe'
            else:
                eval_comp.evaluador_tipo = 'par'

        eval_comp.save()

        brecha = eval_comp.brecha
        brecha_texto = ""
        if brecha is not None:
            if brecha > 0:
                brecha_texto = f" (+{brecha} sobre lo esperado)"
            elif brecha < 0:
                brecha_texto = f" ({brecha} bajo lo esperado)"
            else:
                brecha_texto = " (= Cumple expectativa)"

        mensaje = f"Competencia evaluada: **{eval_comp.competencia.nombre}**\n"
        mensaje += f"- Nivel esperado: {eval_comp.nivel_esperado}/5\n"
        mensaje += f"- Nivel obtenido: {nivel}/5{brecha_texto}\n"

        # Mostrar progreso
        total = evaluacion.competencias_evaluadas.count()
        evaluadas = evaluacion.competencias_evaluadas.filter(nivel_obtenido__isnull=False).count()
        mensaje += f"\nProgreso: {evaluadas}/{total} competencias evaluadas"

        return {'exito': True, 'mensaje': mensaje, 'datos': {'brecha': brecha}}

    registrar_accion(
        nombre='evaluar_competencia',
        descripcion='Evalua una competencia especifica en una evaluacion',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'evaluacion_id': 'ID de la evaluacion',
            'competencia_id': 'ID de la competencia',
            'nivel': 'Nivel obtenido (1-5)',
            'comentarios': '(Opcional) Comentarios',
            'ejemplos': '(Opcional) Ejemplos de conducta observada'
        },
        ejemplo='Evaluar comunicacion de Juan con nivel 4',
        funcion=evaluar_competencia
    )

    # ============================================================
    # ACCION 88: Ver evaluacion
    # ============================================================
    def ver_evaluacion(usuario, params: Dict, contexto: Dict) -> Dict:
        """Muestra el detalle de una evaluacion"""
        evaluacion_id = params.get('evaluacion_id')
        empleado_id = params.get('empleado_id')

        if not evaluacion_id and not empleado_id:
            return {'exito': False, 'mensaje': 'Que evaluacion quieres ver? Dame el ID o el empleado.'}

        try:
            if evaluacion_id:
                evaluacion = Evaluacion.objects.select_related('empleado', 'evaluador').get(id=evaluacion_id)
            else:
                # Ultima evaluacion del empleado
                evaluacion = Evaluacion.objects.select_related('empleado', 'evaluador').filter(
                    empleado_id=empleado_id
                ).order_by('-fecha_fin').first()

                if not evaluacion:
                    return {'exito': False, 'mensaje': 'El empleado no tiene evaluaciones.'}

            if not usuario.es_super_admin and evaluacion.empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso.'}
        except Evaluacion.DoesNotExist:
            return {'exito': False, 'mensaje': 'Evaluacion no encontrada.'}

        mensaje = f"**Evaluacion de {evaluacion.empleado.nombre_completo}**\n"
        mensaje += f"Periodo: {evaluacion.periodo} | Tipo: {evaluacion.get_tipo_display()}\n"
        mensaje += f"Estado: {evaluacion.get_estado_display()}\n\n"

        # Puntuaciones
        mensaje += "**Puntuaciones:**\n"
        if evaluacion.puntuacion_kpis:
            mensaje += f"- KPIs: {evaluacion.puntuacion_kpis}%\n"
        if evaluacion.puntuacion_competencias:
            mensaje += f"- Competencias: {evaluacion.puntuacion_competencias}%\n"
        if evaluacion.puntuacion_final:
            mensaje += f"- **Final: {evaluacion.puntuacion_final}%**\n"

        # Clasificacion 9-box
        if evaluacion.clasificacion_9box:
            mensaje += f"\nClasificacion: **{evaluacion.clasificacion_9box}**\n"

        # Competencias
        competencias = evaluacion.competencias_evaluadas.select_related('competencia').all()
        if competencias.exists():
            evaluadas_count = competencias.filter(nivel_obtenido__isnull=False).count()
            mensaje += f"\n**Competencias ({evaluadas_count}/{competencias.count()}):**\n"
            for c in competencias[:5]:
                nivel = f"{c.nivel_obtenido}/5" if c.nivel_obtenido else "Pendiente"
                emoji = ""
                if c.nivel_obtenido:
                    if c.nivel_obtenido >= c.nivel_esperado:
                        emoji = "+"
                    else:
                        emoji = "-"
                mensaje += f"  {emoji} {c.competencia.nombre}: {nivel}\n"

            if competencias.count() > 5:
                mensaje += f"  ... y {competencias.count() - 5} mas\n"

        # Retroalimentacion
        if evaluacion.logros:
            mensaje += f"\n**Logros:** {evaluacion.logros[:100]}...\n"
        if evaluacion.areas_mejora:
            mensaje += f"**Areas de mejora:** {evaluacion.areas_mejora[:100]}...\n"

        return {
            'exito': True,
            'mensaje': mensaje,
            'datos': {
                'id': str(evaluacion.id),
                'empleado': evaluacion.empleado.nombre_completo,
                'periodo': evaluacion.periodo,
                'puntuacion_final': float(evaluacion.puntuacion_final) if evaluacion.puntuacion_final else None,
                'estado': evaluacion.estado
            }
        }

    registrar_accion(
        nombre='ver_evaluacion',
        descripcion='Muestra el detalle de una evaluacion de desempeno',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'evaluacion_id': '(Opcional) ID de la evaluacion',
            'empleado_id': '(Opcional) ID del empleado (muestra la ultima)'
        },
        ejemplo='Ver evaluacion de Juan',
        funcion=ver_evaluacion
    )

    # ============================================================
    # ACCION 89: Dar retroalimentacion
    # ============================================================
    def dar_retroalimentacion(usuario, params: Dict, contexto: Dict) -> Dict:
        """Registra retroalimentacion continua para un empleado"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id')
        tipo = params.get('tipo', 'general')
        contenido = params.get('contenido')

        if not empleado_id:
            return {'exito': False, 'mensaje': 'Para que empleado es la retroalimentacion?'}
        if not contenido:
            return {'exito': False, 'mensaje': 'Cual es el contenido de la retroalimentacion?'}

        try:
            empleado = Empleado.objects.get(id=empleado_id)
            if not usuario.es_super_admin and empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso.'}
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}

        autor = usuario.empleado if hasattr(usuario, 'empleado') else None

        retro = RetroalimentacionContinua.objects.create(
            empleado=empleado,
            autor=autor,
            tipo=tipo,
            contenido=contenido,
            es_privado=params.get('privado', False),
            requiere_seguimiento=params.get('seguimiento', False)
        )

        emoji = {
            'reconocimiento': '(reconocimiento)',
            'mejora': '(mejora)',
            'coaching': '(coaching)',
            'objetivo': '(objetivo)',
            'general': '(general)'
        }.get(tipo, '')

        mensaje = f"{emoji} Retroalimentacion registrada para {empleado.nombre_completo}\n\n"
        mensaje += f"- Tipo: {retro.get_tipo_display()}\n"
        mensaje += f"- Contenido: {contenido[:100]}{'...' if len(contenido) > 100 else ''}\n"
        if retro.requiere_seguimiento:
            mensaje += "- Requiere seguimiento\n"

        return {'exito': True, 'mensaje': mensaje, 'datos': {'id': str(retro.id)}}

    registrar_accion(
        nombre='dar_retroalimentacion',
        descripcion='Registra retroalimentacion continua para un empleado (fuera de evaluaciones formales)',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'empleado_id': 'ID del empleado',
            'tipo': '(Opcional) reconocimiento/mejora/coaching/objetivo/general',
            'contenido': 'Texto de la retroalimentacion',
            'privado': '(Opcional) true si es solo para RRHH/jefe',
            'seguimiento': '(Opcional) true si requiere seguimiento'
        },
        ejemplo='Dar reconocimiento a Juan por su trabajo en el proyecto',
        funcion=dar_retroalimentacion
    )

    # ============================================================
    # ACCION 90: Ver retroalimentaciones de empleado
    # ============================================================
    def ver_retroalimentaciones(usuario, params: Dict, contexto: Dict) -> Dict:
        """Lista las retroalimentaciones de un empleado"""
        from apps.empleados.models import Empleado

        empleado_id = params.get('empleado_id')

        if not empleado_id:
            # Si es empleado, ve las suyas
            if hasattr(usuario, 'empleado') and usuario.empleado:
                empleado_id = usuario.empleado.id
            else:
                return {'exito': False, 'mensaje': 'De que empleado quieres ver las retroalimentaciones?'}

        try:
            empleado = Empleado.objects.get(id=empleado_id)
        except Empleado.DoesNotExist:
            return {'exito': False, 'mensaje': 'Empleado no encontrado.'}

        # Filtrar privadas si no es admin/rrhh/jefe
        qs = RetroalimentacionContinua.objects.filter(empleado=empleado)

        es_admin = usuario.es_super_admin or usuario.rol in ['administrador', 'rrhh']
        es_jefe = hasattr(usuario, 'empleado') and usuario.empleado and hasattr(empleado, 'jefe_directo') and empleado.jefe_directo and usuario.empleado.id == empleado.jefe_directo.id

        if not (es_admin or es_jefe):
            qs = qs.filter(es_privado=False)

        retroalimentaciones = qs.select_related('autor').order_by('-created_at')[:10]

        if not retroalimentaciones.exists():
            return {
                'exito': True,
                'mensaje': f'{empleado.nombre_completo} no tiene retroalimentaciones registradas.',
                'datos': []
            }

        mensaje = f"**Retroalimentaciones de {empleado.nombre_completo}**\n\n"

        for r in retroalimentaciones:
            autor = r.autor.nombre_completo if r.autor else 'Sistema'
            fecha = r.created_at.strftime('%d/%m/%Y')

            mensaje += f"**{r.get_tipo_display()}** - {fecha}\n"
            mensaje += f"   Por: {autor}\n"
            mensaje += f"   {r.contenido[:80]}{'...' if len(r.contenido) > 80 else ''}\n\n"

        return {'exito': True, 'mensaje': mensaje, 'datos': []}

    registrar_accion(
        nombre='ver_retroalimentaciones',
        descripcion='Lista las retroalimentaciones continuas de un empleado',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'empleado_id': '(Opcional) ID del empleado. Si no se da, muestra las propias.'
        },
        ejemplo='Ver retroalimentaciones de Juan',
        funcion=ver_retroalimentaciones
    )

    # ============================================================
    # ACCION 91: Clasificar en matriz de talento
    # ============================================================
    def clasificar_matriz_talento(usuario, params: Dict, contexto: Dict) -> Dict:
        """Clasifica a un empleado en la matriz 9-box"""
        evaluacion_id = params.get('evaluacion_id')
        desempeno = params.get('desempeno')
        potencial = params.get('potencial')

        if not evaluacion_id:
            return {'exito': False, 'mensaje': 'Que evaluacion quieres clasificar?'}
        if not desempeno:
            return {'exito': False, 'mensaje': 'Cual es el nivel de desempeno? (bajo/medio/alto)'}
        if not potencial:
            return {'exito': False, 'mensaje': 'Cual es el nivel de potencial? (bajo/medio/alto)'}

        if desempeno not in ['bajo', 'medio', 'alto']:
            return {'exito': False, 'mensaje': 'Desempeno debe ser: bajo, medio o alto'}
        if potencial not in ['bajo', 'medio', 'alto']:
            return {'exito': False, 'mensaje': 'Potencial debe ser: bajo, medio o alto'}

        try:
            evaluacion = Evaluacion.objects.select_related('empleado').get(id=evaluacion_id)
            if not usuario.es_super_admin and evaluacion.empleado.empresa not in usuario.empresas.all():
                return {'exito': False, 'mensaje': 'No tienes acceso.'}
        except Evaluacion.DoesNotExist:
            return {'exito': False, 'mensaje': 'Evaluacion no encontrada.'}

        evaluacion.clasificacion_desempeno = desempeno
        evaluacion.clasificacion_potencial = potencial
        evaluacion.save()

        clasificacion = evaluacion.clasificacion_9box

        mensaje = f"{evaluacion.empleado.nombre_completo} clasificado en matriz de talento\n\n"
        mensaje += f"- Desempeno: {desempeno.capitalize()}\n"
        mensaje += f"- Potencial: {potencial.capitalize()}\n"
        mensaje += f"- **Clasificacion: {clasificacion}**\n"

        # Recomendaciones segun clasificacion
        recomendaciones = {
            'Estrella': 'Retener y desarrollar para roles de liderazgo',
            'Alto Desempeno': 'Mantener motivado con nuevos desafios',
            'Futuro Lider': 'Invertir en desarrollo de habilidades actuales',
            'Colaborador Clave': 'Mantener y reconocer contribuciones',
            'Enigma': 'Investigar barreras al desempeno',
            'Accion Requerida': 'Plan de mejora inmediato o considerar cambio de rol'
        }

        if clasificacion in recomendaciones:
            mensaje += f"\nRecomendacion: {recomendaciones[clasificacion]}"

        return {'exito': True, 'mensaje': mensaje, 'datos': {'clasificacion': clasificacion}}

    registrar_accion(
        nombre='clasificar_matriz_talento',
        descripcion='Clasifica a un empleado en la matriz de talento 9-box',
        permisos=['es_admin', 'es_rrhh'],
        parametros={
            'evaluacion_id': 'ID de la evaluacion',
            'desempeno': 'bajo/medio/alto',
            'potencial': 'bajo/medio/alto'
        },
        ejemplo='Clasificar a Juan como alto desempeno y alto potencial',
        funcion=clasificar_matriz_talento
    )

    # ============================================================
    # ACCION 92: Ver matriz de talento del equipo
    # ============================================================
    def ver_matriz_talento_equipo(usuario, params: Dict, contexto: Dict) -> Dict:
        """Muestra la matriz de talento del equipo"""
        empresa_id = params.get('empresa_id') or contexto.get('empresa_id')
        periodo = params.get('periodo')

        # Obtener evaluaciones con clasificacion
        qs = Evaluacion.objects.filter(
            clasificacion_desempeno__isnull=False,
            clasificacion_potencial__isnull=False
        ).exclude(
            clasificacion_desempeno='',
            clasificacion_potencial=''
        ).select_related('empleado', 'empleado__empresa')

        if not usuario.es_super_admin:
            qs = qs.filter(empleado__empresa__in=usuario.empresas.all())

        if empresa_id:
            qs = qs.filter(empleado__empresa_id=empresa_id)

        if periodo:
            qs = qs.filter(periodo=periodo)
        else:
            # Ultima evaluacion de cada empleado
            ultimas = Evaluacion.objects.filter(
                clasificacion_desempeno__isnull=False
            ).exclude(
                clasificacion_desempeno=''
            ).values('empleado').annotate(max_fecha=Max('fecha_fin'))

            qs = qs.filter(
                fecha_fin__in=[u['max_fecha'] for u in ultimas]
            )

        evaluaciones = qs.order_by('clasificacion_desempeno', 'clasificacion_potencial')

        if not evaluaciones.exists():
            return {
                'exito': True,
                'mensaje': 'No hay empleados clasificados en la matriz de talento.',
                'datos': []
            }

        # Agrupar por clasificacion
        matriz = {}
        for e in evaluaciones:
            clas = e.clasificacion_9box
            if clas and clas not in matriz:
                matriz[clas] = []
            if clas:
                matriz[clas].append(e.empleado.nombre_completo)

        mensaje = "**Matriz de Talento (9-Box)**\n\n"

        orden = ['Estrella', 'Alto Desempeno', 'Futuro Lider', 'Experto Tecnico',
                 'Colaborador Clave', 'Efectivo', 'Enigma', 'En Desarrollo', 'Accion Requerida']

        for clas in orden:
            if clas in matriz:
                mensaje += f"**{clas}** ({len(matriz[clas])})\n"
                for nombre in matriz[clas][:3]:
                    mensaje += f"   - {nombre}\n"
                if len(matriz[clas]) > 3:
                    mensaje += f"   ... y {len(matriz[clas]) - 3} mas\n"
                mensaje += "\n"

        return {'exito': True, 'mensaje': mensaje, 'datos': matriz}

    registrar_accion(
        nombre='ver_matriz_talento_equipo',
        descripcion='Muestra la distribucion del equipo en la matriz de talento 9-box',
        permisos=['es_admin', 'es_rrhh', 'es_jefe'],
        parametros={
            'empresa_id': '(Opcional) Filtrar por empresa',
            'periodo': '(Opcional) Periodo especifico'
        },
        ejemplo='Ver matriz de talento del equipo',
        funcion=ver_matriz_talento_equipo
    )

    print("[OK] Acciones de Evaluaciones registradas (85-92)")
