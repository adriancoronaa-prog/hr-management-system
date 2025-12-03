"""
Acciones de IA para el módulo de Documentos y RAG
"""
from typing import Dict


def registrar_acciones():
    """Registra las acciones de documentos en el registro central"""
    from apps.chat.acciones_registry import registrar_accion

    # === BÚSQUEDA SEMÁNTICA ===
    registrar_accion(
        nombre='buscar_en_documentos',
        descripcion='Busca información en los documentos de la empresa (políticas, reglamentos, manuales) usando búsqueda semántica',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'consulta': 'Texto a buscar (pregunta o tema)',
            'empresa_id': '(Opcional) ID de empresa específica',
            'max_resultados': '(Opcional) Número máximo de resultados (default: 5)',
        },
        ejemplo='Busca en los documentos qué dice sobre las vacaciones',
        funcion=accion_buscar_en_documentos
    )

    # === LISTAR DOCUMENTOS ===
    registrar_accion(
        nombre='listar_documentos',
        descripcion='Lista los documentos disponibles que puedes consultar',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'tipo': '(Opcional) Filtrar por tipo: politica, reglamento, manual, procedimiento, formato, comunicado',
            'empresa_id': '(Opcional) ID de empresa específica',
        },
        ejemplo='Muestra los documentos disponibles',
        funcion=accion_listar_documentos
    )

    # === CONSULTAR DOCUMENTO ESPECÍFICO ===
    registrar_accion(
        nombre='consultar_documento',
        descripcion='Consulta información sobre un documento específico o su contenido',
        permisos=['es_admin', 'es_rrhh', 'es_jefe', 'es_empleado'],
        parametros={
            'documento_id': '(Opcional) ID del documento',
            'documento_titulo': '(Opcional) Título o nombre del documento',
            'pregunta': 'Pregunta específica sobre el documento',
        },
        ejemplo='Qué dice el reglamento interno sobre el código de vestimenta',
        funcion=accion_consultar_documento
    )

    # === SUBIR DOCUMENTO (PLACEHOLDER) ===
    registrar_accion(
        nombre='subir_documento',
        descripcion='Información sobre cómo subir un documento al sistema',
        permisos=['es_admin', 'es_rrhh'],
        parametros={},
        ejemplo='Cómo subo un documento',
        funcion=accion_subir_documento
    )


# ============ IMPLEMENTACIÓN DE FUNCIONES ============

def accion_buscar_en_documentos(usuario, params: Dict, contexto: Dict) -> Dict:
    """Busca en documentos usando RAG"""
    from .services import BuscadorSemantico

    consulta = params.get('consulta') or params.get('query') or params.get('texto')
    if not consulta:
        return {
            'success': False,
            'error': 'Se requiere una consulta o pregunta para buscar'
        }

    empresa_id = params.get('empresa_id') or contexto.get('empresa_id')
    max_resultados = int(params.get('max_resultados', 5))

    try:
        resultados = BuscadorSemantico.buscar(
            query=consulta,
            usuario=usuario,
            empresa_id=empresa_id,
            top_k=max_resultados,
            umbral_similitud=0.25  # Umbral más bajo para más resultados
        )

        if not resultados:
            return {
                'success': True,
                'mensaje': f'No encontré información relevante sobre "{consulta}" en los documentos disponibles.',
                'resultados': [],
                'sugerencia': 'Intenta reformular tu pregunta o usa términos más específicos.'
            }

        # Formatear respuesta
        lineas = [f'**Resultados de búsqueda para:** "{consulta}"\n']

        for i, r in enumerate(resultados, 1):
            similitud_pct = int(r['similitud'] * 100)
            lineas.append(f"**{i}. {r['documento_titulo']}** (Relevancia: {similitud_pct}%)")

            # Mostrar contenido resumido
            contenido = r['contenido']
            if len(contenido) > 300:
                contenido = contenido[:300] + "..."
            lineas.append(f"> {contenido}")
            lineas.append("")

        return {
            'success': True,
            'mensaje': '\n'.join(lineas),
            'resultados': resultados,
            'total_encontrados': len(resultados)
        }

    except ImportError as e:
        return {
            'success': False,
            'error': f'Falta dependencia para búsqueda semántica: {str(e)}',
            'sugerencia': 'Instalar: pip install sentence-transformers'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error en la búsqueda: {str(e)}'
        }


def accion_listar_documentos(usuario, params: Dict, contexto: Dict) -> Dict:
    """Lista documentos disponibles para el usuario"""
    from .models import Documento, NivelAcceso
    from django.db.models import Q

    empresa_id = params.get('empresa_id') or contexto.get('empresa_id')
    tipo = params.get('tipo')

    # Construir filtro base
    filtro = Q(activo=True)

    # Filtro por tipo
    if tipo:
        filtro &= Q(tipo=tipo)

    # Filtro por empresa
    if empresa_id:
        filtro &= Q(empresa_id=empresa_id) | Q(empresa__isnull=True)
    else:
        # Documentos globales o de empresas del usuario
        empresas_usuario = usuario.empresas.all()
        filtro &= Q(empresa__isnull=True) | Q(empresa__in=empresas_usuario)

    # Filtro por nivel de acceso
    if usuario.rol == 'administrador':
        pass  # Ve todo
    elif usuario.rol == 'empleador':
        filtro &= Q(tipo_acceso__in=[
            NivelAcceso.PUBLICO, NivelAcceso.EMPRESA, NivelAcceso.RRHH
        ]) | Q(created_by=usuario)
    else:
        filtro &= Q(tipo_acceso__in=[
            NivelAcceso.PUBLICO, NivelAcceso.EMPRESA
        ]) | Q(created_by=usuario)

    documentos = Documento.objects.filter(filtro).order_by('tipo', 'titulo')

    if not documentos.exists():
        return {
            'success': True,
            'mensaje': 'No hay documentos disponibles.',
            'documentos': []
        }

    # Agrupar por tipo
    por_tipo = {}
    for doc in documentos:
        tipo_label = doc.get_tipo_display()
        if tipo_label not in por_tipo:
            por_tipo[tipo_label] = []
        por_tipo[tipo_label].append({
            'id': str(doc.id),
            'titulo': doc.titulo,
            'descripcion': doc.descripcion[:100] + '...' if len(doc.descripcion) > 100 else doc.descripcion,
            'procesado': doc.procesado,
            'version': doc.version,
        })

    # Formatear respuesta
    lineas = [f'**Documentos disponibles ({documentos.count()} total)**\n']

    tipo_emojis = {
        'Política': '📋',
        'Reglamento': '📜',
        'Manual': '📘',
        'Procedimiento': '📝',
        'Formato': '📄',
        'Plantilla de Contrato': '📃',
        'Comunicado': '📢',
        'Otro': '📎',
    }

    for tipo_label, docs in por_tipo.items():
        emoji = tipo_emojis.get(tipo_label, '📎')
        lineas.append(f"\n{emoji} **{tipo_label}** ({len(docs)})")
        for doc in docs:
            estado = "✅" if doc['procesado'] else "⏳"
            version = f" (v{doc['version']})" if doc['version'] else ""
            lineas.append(f"   {estado} {doc['titulo']}{version}")

    return {
        'success': True,
        'mensaje': '\n'.join(lineas),
        'documentos': list(por_tipo.values()),
        'total': documentos.count()
    }


def accion_consultar_documento(usuario, params: Dict, contexto: Dict) -> Dict:
    """Consulta un documento específico o busca por título"""
    from .models import Documento
    from .services import BuscadorSemantico
    from django.db.models import Q

    documento_id = params.get('documento_id')
    documento_titulo = params.get('documento_titulo') or params.get('titulo') or params.get('nombre')
    pregunta = params.get('pregunta') or params.get('consulta')

    documento = None

    # Buscar por ID
    if documento_id:
        try:
            documento = Documento.objects.get(pk=documento_id, activo=True)
        except Documento.DoesNotExist:
            return {
                'success': False,
                'error': f'No se encontró el documento con ID {documento_id}'
            }

    # Buscar por título
    elif documento_titulo:
        # Búsqueda flexible por título
        documentos = Documento.objects.filter(
            Q(titulo__icontains=documento_titulo) |
            Q(descripcion__icontains=documento_titulo),
            activo=True
        )

        # Filtrar por acceso
        documentos = [d for d in documentos if d.puede_ver(usuario)]

        if not documentos:
            return {
                'success': False,
                'error': f'No se encontró ningún documento que coincida con "{documento_titulo}"'
            }

        if len(documentos) == 1:
            documento = documentos[0]
        else:
            # Múltiples coincidencias
            lineas = [f'Encontré {len(documentos)} documentos que coinciden:\n']
            for doc in documentos[:5]:
                lineas.append(f"- **{doc.titulo}** ({doc.get_tipo_display()})")
            lineas.append("\nEspecifica el título exacto o usa el ID del documento.")

            return {
                'success': True,
                'mensaje': '\n'.join(lineas),
                'documentos': [{'id': str(d.id), 'titulo': d.titulo} for d in documentos[:5]]
            }

    else:
        return {
            'success': False,
            'error': 'Debes especificar documento_id, documento_titulo o hacer una pregunta'
        }

    # Verificar acceso
    if not documento.puede_ver(usuario):
        return {
            'success': False,
            'error': 'No tienes acceso a este documento'
        }

    # Si hay una pregunta, buscar en el documento
    if pregunta and documento.procesado:
        # Buscar fragmentos relevantes solo en este documento
        from .models import FragmentoDocumento
        from .services import GeneradorEmbeddings, BuscadorSemantico

        try:
            query_embedding = GeneradorEmbeddings.generar_embedding(pregunta)

            fragmentos = FragmentoDocumento.objects.filter(
                documento=documento,
                embedding__isnull=False
            )

            resultados = []
            for frag in fragmentos:
                similitud = BuscadorSemantico.similitud_coseno(query_embedding, frag.embedding)
                if similitud >= 0.2:
                    resultados.append({
                        'contenido': frag.contenido,
                        'similitud': similitud
                    })

            resultados.sort(key=lambda x: x['similitud'], reverse=True)

            if resultados:
                lineas = [f'**{documento.titulo}**\n']
                lineas.append(f'Pregunta: "{pregunta}"\n')
                lineas.append('**Información relevante encontrada:**\n')

                for r in resultados[:3]:
                    lineas.append(f"> {r['contenido']}")
                    lineas.append("")

                return {
                    'success': True,
                    'mensaje': '\n'.join(lineas),
                    'documento': documento.titulo,
                    'fragmentos_encontrados': len(resultados)
                }

        except Exception as e:
            pass  # Si falla la búsqueda semántica, mostrar info general

    # Información general del documento
    lineas = [f'**{documento.titulo}**\n']

    if documento.descripcion:
        lineas.append(f"*{documento.descripcion}*\n")

    lineas.append(f"- **Tipo:** {documento.get_tipo_display()}")
    lineas.append(f"- **Acceso:** {documento.get_tipo_acceso_display()}")

    if documento.version:
        lineas.append(f"- **Versión:** {documento.version}")

    if documento.fecha_vigencia:
        lineas.append(f"- **Vigencia:** {documento.fecha_vigencia}")

    if documento.tags:
        lineas.append(f"- **Tags:** {documento.tags}")

    lineas.append(f"- **Procesado para búsqueda:** {'Sí' if documento.procesado else 'No'}")

    if documento.procesado:
        lineas.append(f"- **Fragmentos indexados:** {documento.total_fragmentos}")

    # Mostrar preview del contenido si está disponible
    if documento.contenido_texto:
        preview = documento.contenido_texto[:500]
        if len(documento.contenido_texto) > 500:
            preview += "..."
        lineas.append(f"\n**Vista previa:**\n> {preview}")

    return {
        'success': True,
        'mensaje': '\n'.join(lineas),
        'documento': {
            'id': str(documento.id),
            'titulo': documento.titulo,
            'tipo': documento.tipo,
            'procesado': documento.procesado,
        }
    }


def accion_subir_documento(usuario, params: Dict, contexto: Dict) -> Dict:
    """Placeholder - indica cómo subir documentos"""
    mensaje = """**Subir documentos al sistema**

Para subir documentos de políticas, reglamentos o manuales:

1. **Desde la interfaz web:**
   - Ve a Configuración > Documentos
   - Haz clic en "Subir documento"
   - Selecciona el archivo (PDF, DOCX o TXT)
   - Completa los metadatos (título, tipo, nivel de acceso)
   - El sistema procesará automáticamente el documento para búsqueda

2. **Formatos soportados:**
   - PDF
   - Word (DOCX)
   - Texto plano (TXT)

3. **Niveles de acceso:**
   - **Público:** Todos los empleados pueden verlo
   - **Empresa:** Solo empleados de la empresa
   - **RRHH:** Solo administradores y RRHH
   - **Privado:** Solo quien lo subió

Una vez subido, podrás buscar información en el documento usando:
- "Busca en los documentos qué dice sobre..."
- "Consulta el reglamento interno sobre..."
"""

    return {
        'success': True,
        'mensaje': mensaje,
        'requiere_interfaz_web': True
    }
