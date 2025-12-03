"""
Servicio de Chat con IA para RRHH
Versión síncrona con arquitectura de acciones modulares
"""
import json
import re
import os
import time
import httpx
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Optional, Tuple

from .acciones_registry import (
    ejecutar_accion, 
    generar_prompt_acciones,
    obtener_acciones_disponibles
)
from .permisos import obtener_contexto_permisos


SYSTEM_PROMPT_BASE = """Eres un asistente de Recursos Humanos para empresas mexicanas. Tu nombre es "Asistente RRHH".

PERSONALIDAD:
- Eres proactivo y guías al usuario paso a paso
- Preguntas la información que falta antes de ejecutar acciones
- Ofreces siguientes pasos después de completar acciones
- Eres experto en legislación laboral mexicana (LFT, IMSS, SAT)

CAPACIDADES:
- Gestionar empresas, empleados, contratos y documentos
- Calcular nómina, vacaciones, aguinaldo, finiquitos y liquidaciones
- Responder preguntas sobre la Ley Federal del Trabajo (LFT)
- Generar reportes y PDFs
- Consultar estructura organizacional (jefes, subordinados)
- Administrar KPIs y evaluaciones de desempeño
- Gestionar expedientes digitales de empleados
- Recibir y procesar archivos adjuntos

CAPACIDAD DE ARCHIVOS:
- El usuario puede subir archivos en cualquier momento
- Cuando recibas un archivo, lo verás como [ARCHIVO ADJUNTO: nombre.ext]
- Podrás leer el contenido de PDFs, Word y TXT
- Los archivos se guardan automáticamente en el expediente del empleado en contexto
- Confirma al usuario que recibiste y procesaste el archivo

REGLAS:
- Siempre responde en español
- Usa formato de moneda mexicana ($X,XXX.XX)
- Fechas en formato dd/mm/yyyy
- SIEMPRE valida permisos antes de ejecutar acciones
- Si no tienes información suficiente, PREGUNTA antes de actuar
- Confirma antes de acciones destructivas (eliminar, dar de baja)

FLUJOS GUIADOS - Para procesos importantes, guía paso a paso:

BAJA DE EMPLEADO:
1. Confirmar empleado (mostrar sus datos)
2. Preguntar tipo de baja
3. Preguntar último día laborado
4. Solicitar carta de renuncia/documento (puede subirlo)
5. Calcular y mostrar liquidación
6. Ofrecer generar finiquito PDF
7. Confirmar y ejecutar baja

ALTA DE EMPLEADO:
1. Pedir datos básicos (nombre, RFC, CURP)
2. Pedir datos laborales (puesto, salario, fecha ingreso)
3. Preguntar jefe directo
4. Solicitar documentos (INE, CURP, comprobante) - puede subirlos
5. Confirmar y crear

INCIDENCIAS:
1. Confirmar empleado
2. Tipo de incidencia
3. Fechas
4. Solicitar documento soporte (incapacidad IMSS, permiso)
5. Si es incapacidad: pedir folio IMSS
6. Confirmar y registrar

IMPORTANTE SOBRE PARÁMETROS:
- Cuando una acción acepta "empleado_nombre", PASA EL NOMBRE DIRECTAMENTE sin buscar primero
- La acción buscará al empleado automáticamente por nombre
- NO ejecutes "buscar_empleado" antes de otras acciones si ya tienes el nombre

IMPORTANTE SOBRE ARCHIVOS:
- Cuando el usuario suba un archivo durante un flujo, agradece y confirma que tipo detectaste
- Ejemplo: "Recibi la carta de renuncia de Juan. La he guardado en su expediente."
- Si no puedes leer el contenido, indicalo pero guarda el archivo igual
- Ofrece subir mas documentos si el expediente esta incompleto

ANALISIS DE IMAGENES (Vision):
Cuando recibas una imagen de documento mexicano, extrae TODA la informacion visible:

Para INE/IFE:
- Nombre completo (nombre, apellido paterno, apellido materno)
- CURP
- Clave de elector
- Fecha de nacimiento
- Sexo
- Domicilio completo
- Vigencia

Para Constancia RFC (SAT):
- RFC completo
- Nombre o razon social
- Regimen fiscal
- Codigo postal
- Fecha de inscripcion

Para Comprobante de domicilio:
- Nombre del titular
- Direccion completa (calle, numero, colonia, CP, ciudad, estado)
- Fecha del comprobante
- Tipo de servicio

Para NSS/IMSS:
- Numero de Seguro Social (11 digitos)
- Nombre del asegurado
- CURP

Para cualquier otro documento:
- Extrae todos los datos visibles de forma estructurada
- Indica el tipo de documento identificado

Despues de extraer, ofrece guardar los datos en el sistema si corresponde a un empleado.

FORMATO DE RESPUESTA PARA ACCIONES:
Cuando detectes que el usuario quiere realizar una acción, incluye un bloque JSON:
```action
{
    "accion": "nombre_de_la_accion",
    "parametros": {
        "param1": "valor1"
    },
    "requiere_confirmacion": true/false,
    "mensaje_confirmacion": "¿Confirmas esta acción?"
}
```

Para consultas informativas, responde directamente sin JSON.
Usa emojis para hacer la conversación amigable: 📋 👤 💼 📄 ✅ ❌ 💰 🏥 📎
"""


class AsistenteRRHH:
    """Asistente de IA para RRHH - Versión Síncrona"""
    
    def __init__(self, usuario, empresa_contexto=None):
        self.usuario = usuario
        self.empresa_contexto = empresa_contexto
        self.api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.modelo = 'claude-sonnet-4-20250514'
        self.contexto_permisos = obtener_contexto_permisos(usuario)
    
    def procesar_mensaje(self, mensaje: str, conversacion_id=None, archivo=None) -> Dict:
        """Procesa un mensaje del usuario, opcionalmente con archivo adjunto"""
        from .models import Conversacion, Mensaje
        from .archivo_service import ProcesadorArchivoChat

        inicio = time.time()

        # Obtener o crear conversacion
        if conversacion_id:
            try:
                conversacion = Conversacion.objects.get(pk=conversacion_id, usuario=self.usuario)
            except Conversacion.DoesNotExist:
                conversacion = self._crear_conversacion()
        else:
            conversacion = self._crear_conversacion()

        # Procesar archivo si existe
        archivo_info = None
        contenido_archivo = ""
        imagen_base64 = None
        imagen_media_type = None

        if archivo:
            resultado_archivo = ProcesadorArchivoChat.procesar(archivo)

            if not resultado_archivo['success']:
                return {
                    'error': resultado_archivo['error'],
                    'conversacion_id': str(conversacion.id)
                }

            archivo_info = resultado_archivo

            # Si es imagen, preparar para Vision
            if archivo_info.get('es_imagen'):
                imagen_base64, imagen_media_type = ProcesadorArchivoChat.imagen_bytes_a_base64(archivo)

        # Guardar mensaje del usuario
        mensaje_usuario = Mensaje.objects.create(
            conversacion=conversacion,
            rol='user',
            contenido=mensaje,
            archivo_adjunto=archivo if archivo else None,
            archivo_nombre=archivo_info['nombre'] if archivo_info else '',
            tipo_archivo=archivo_info['tipo'] if archivo_info else '',
        )

        # Extraer texto del archivo despues de guardar (solo para no-imagenes)
        if archivo and mensaje_usuario.archivo_adjunto and not archivo_info.get('es_imagen'):
            try:
                contenido_archivo = ProcesadorArchivoChat.extraer_texto(
                    mensaje_usuario.archivo_adjunto.path,
                    archivo_info['tipo']
                )
                mensaje_usuario.archivo_contenido_texto = contenido_archivo[:10000]
                mensaje_usuario.save()
            except Exception as e:
                print(f"Error extrayendo texto: {e}")

        # Incluir informacion del archivo en el contexto para la IA
        mensaje_para_ia = mensaje
        if archivo_info:
            if archivo_info.get('es_imagen'):
                # Para imagenes, indicar que se esta enviando imagen
                if not mensaje.strip():
                    mensaje_para_ia = "Analiza esta imagen y extrae toda la informacion relevante (nombres, fechas, numeros, direcciones, etc.)"
                mensaje_para_ia += f"\n\n[IMAGEN ADJUNTA: {archivo_info['nombre']}]"
            else:
                mensaje_para_ia += f"\n\n[ARCHIVO ADJUNTO: {archivo_info['nombre']} ({archivo_info['tipo']})]"
                if contenido_archivo:
                    mensaje_para_ia += f"\n[CONTENIDO DEL ARCHIVO:]\n{contenido_archivo[:3000]}"

        # Si hay empleado en contexto y archivo, asociar al expediente
        if archivo and conversacion.empleado_contexto:
            self._guardar_documento_expediente(
                conversacion.empleado_contexto,
                archivo_info,
                contenido_archivo,
                mensaje_usuario,
                conversacion.flujo_activo
            )

        # Construir contexto
        contexto = self._construir_contexto(conversacion)

        # Llamar a Claude API (con imagen si es el caso)
        respuesta_ia = self._llamar_claude(
            mensaje_para_ia,
            contexto,
            imagen_base64=imagen_base64,
            imagen_media_type=imagen_media_type
        )
        
        # Parsear respuesta para detectar acciones
        texto_respuesta, accion = self._parsear_respuesta(respuesta_ia)
        
        # Ejecutar acción si existe y no requiere confirmación
        resultado_accion = None
        if accion and not accion.get('requiere_confirmacion', True):
            resultado_accion = self._ejecutar_accion(accion)
            if resultado_accion.get('success'):
                texto_respuesta += f"\n\n✅ {resultado_accion.get('mensaje', 'Acción completada')}"
                # Mostrar datos adicionales si existen
                texto_respuesta += self._formatear_datos_accion(resultado_accion)
            else:
                texto_respuesta += f"\n\n❌ Error: {resultado_accion.get('error', 'Error desconocido')}"

        # Si no hubo acción, intentar buscar en documentos RAG
        elif not accion:
            respuesta_rag = self._intentar_respuesta_rag(mensaje)
            if respuesta_rag:
                texto_respuesta = respuesta_rag
        
        tiempo_ms = int((time.time() - inicio) * 1000)
        
        # Guardar respuesta del asistente
        mensaje_asistente = Mensaje.objects.create(
            conversacion=conversacion,
            rol='assistant',
            contenido=texto_respuesta,
            accion_ejecutada=accion.get('accion', '') if accion else '',
            resultado_accion=self._serializar_resultado(resultado_accion),
            tiempo_respuesta_ms=tiempo_ms
        )
        
        # Actualizar título si es primera interacción
        if conversacion.mensajes.count() <= 2:
            conversacion.titulo = mensaje[:100]
            conversacion.save()
        
        return {
            'conversacion_id': str(conversacion.id),
            'mensaje_id': str(mensaje_asistente.id),
            'respuesta': texto_respuesta,
            'accion_pendiente': accion if accion and accion.get('requiere_confirmacion') else None,
            'resultado_accion': resultado_accion,
            'tiempo_ms': tiempo_ms
        }
    
    def _crear_conversacion(self):
        """Crea una nueva conversación"""
        from .models import Conversacion
        return Conversacion.objects.create(
            usuario=self.usuario,
            empresa_contexto=self.empresa_contexto
        )
    
    def _construir_contexto(self, conversacion) -> str:
        """Construye el contexto completo para la IA"""
        partes = []
        
        # Info del usuario
        partes.append(f"USUARIO: {self.usuario.email}")
        partes.append(f"ROL: {self.usuario.rol}")
        partes.append(f"PERMISOS: {json.dumps(self.contexto_permisos, ensure_ascii=False, default=str)}")
        
        # Empresa en contexto
        if self.empresa_contexto:
            partes.append(f"EMPRESA ACTUAL: {self.empresa_contexto.razon_social} (ID: {self.empresa_contexto.id})")
        
        # Info del empleado si aplica
        if hasattr(self.usuario, 'empleado') and self.usuario.empleado:
            emp = self.usuario.empleado
            partes.append(f"\nINFO EMPLEADO:")
            partes.append(f"- Nombre: {emp.nombre_completo}")
            partes.append(f"- Puesto: {emp.puesto}")
            partes.append(f"- Departamento: {emp.departamento}")
            partes.append(f"- Antigüedad: {emp.antiguedad}")
            if emp.jefe_directo:
                partes.append(f"- Jefe: {emp.jefe_directo.nombre_completo}")
            if emp.subordinados.exists():
                subs = [s.nombre_completo for s in emp.subordinados.all()[:5]]
                partes.append(f"- Subordinados: {', '.join(subs)}")
        
        # Acciones disponibles
        partes.append(f"\n{generar_prompt_acciones(self.usuario)}")
        
        # Historial reciente
        mensajes = conversacion.mensajes.order_by('-created_at')[:10]
        if mensajes.exists():
            partes.append("\nHISTORIAL RECIENTE:")
            for msg in reversed(list(mensajes)):
                rol = "Usuario" if msg.rol == 'user' else "Asistente"
                partes.append(f"{rol}: {msg.contenido[:300]}")
        
        return "\n".join(partes)
    
    def _llamar_claude(self, mensaje: str, contexto: str,
                        imagen_base64: str = None, imagen_media_type: str = None) -> str:
        """Llama a la API de Claude de forma sincrona, opcionalmente con imagen (Vision)"""
        if not self.api_key:
            return "Error: API key de Anthropic no configurada. Contacta al administrador."

        try:
            # Construir contenido del mensaje
            if imagen_base64 and imagen_media_type:
                # Mensaje con imagen (Vision)
                content = [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": imagen_media_type,
                            "data": imagen_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": mensaje
                    }
                ]
            else:
                # Mensaje solo texto
                content = mensaje

            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "content-type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.modelo,
                        "max_tokens": 4096,
                        "system": SYSTEM_PROMPT_BASE + f"\n\nCONTEXTO ACTUAL:\n{contexto}",
                        "messages": [{"role": "user", "content": content}]
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    return data['content'][0]['text']
                else:
                    return f"Error al comunicar con IA: {response.status_code} - {response.text}"

        except httpx.TimeoutException:
            return "Error: La solicitud tardo demasiado. Intenta de nuevo."
        except Exception as e:
            return f"Error de conexion con IA: {str(e)}"
    
    def _parsear_respuesta(self, respuesta: str) -> Tuple[str, Optional[Dict]]:
        """Extrae texto y acción de la respuesta"""
        accion = None
        texto = respuesta
        
        patron = r'```action\s*(.*?)\s*```'
        match = re.search(patron, respuesta, re.DOTALL)
        
        if match:
            try:
                accion = json.loads(match.group(1))
                texto = re.sub(patron, '', respuesta, flags=re.DOTALL).strip()
            except json.JSONDecodeError:
                pass
        
        return texto, accion
    
    def _ejecutar_accion(self, accion: Dict) -> Dict:
        """Ejecuta una acción usando el registro central"""
        import json
        
        nombre = accion.get('accion', '')
        parametros = accion.get('parametros', {})
        
        contexto = {
            'empresa_contexto': self.empresa_contexto,
            'usuario': self.usuario,
        }
        
        resultado = ejecutar_accion(nombre, self.usuario, parametros, contexto)
        
        # Forzar serialización de UUIDs a strings
        try:
            resultado_serializado = json.loads(json.dumps(resultado, default=str))
            return resultado_serializado
        except Exception as e:
            return {'success': False, 'error': f'Error de serialización: {str(e)}'}
    
    def confirmar_accion(self, conversacion_id, accion: Dict) -> Dict:
        """Confirma y ejecuta una acción pendiente"""
        from .models import Conversacion, Mensaje
        
        conversacion = Conversacion.objects.get(pk=conversacion_id, usuario=self.usuario)
        
        resultado = self._ejecutar_accion(accion)
        
        # Guardar mensaje de resultado
        if resultado.get('success'):
            contenido = f"✅ {resultado.get('mensaje', 'Acción completada')}"
        else:
            contenido = f"❌ Error: {resultado.get('error', 'Error desconocido')}"
        
        Mensaje.objects.create(
            conversacion=conversacion,
            rol='assistant',
            contenido=contenido,
            accion_ejecutada=accion.get('accion'),
            resultado_accion=resultado
        )
        
        return resultado
    
    def cancelar_accion(self, conversacion_id) -> Dict:
        """Cancela una acción pendiente"""
        from .models import Conversacion, Mensaje
        
        conversacion = Conversacion.objects.get(pk=conversacion_id, usuario=self.usuario)
        
        Mensaje.objects.create(
            conversacion=conversacion,
            rol='assistant',
            contenido='❌ Acción cancelada por el usuario.'
        )
        
        return {'success': True, 'mensaje': 'Acción cancelada'}
    
    def _serializar_resultado(self, resultado):
        """Convierte resultado a JSON serializable (UUIDs a strings)"""
        if resultado is None:
            return None
        import json
        return json.loads(json.dumps(resultado, default=str))
    
    def _formatear_datos_accion(self, resultado: Dict) -> str:
        """Formatea datos adicionales del resultado de una acción"""
        extras = []
        
        # Lista de empleados
        # Lista de empleados
        if 'empleados' in resultado and isinstance(resultado['empleados'], list) and resultado['empleados']:
            extras.append("\n\n**Empleados encontrados:**")
            for emp in resultado['empleados'][:10]:
                extras.append(f"• {emp.get('nombre', 'N/A')} - {emp.get('puesto', 'Sin puesto')} ({emp.get('departamento', '')})")
        
        # Lista de periodos
        if 'periodos' in resultado and resultado['periodos']:
            extras.append("\n\n**Periodos de nómina:**")
            for p in resultado['periodos'][:10]:
                extras.append(f"• {p.get('nombre', 'N/A')} | {p.get('fecha_inicio', '')} - {p.get('fecha_fin', '')} | Estado: {p.get('estado', 'N/A')}")
        
        # Lista de incidencias
        if 'incidencias' in resultado and resultado['incidencias']:
            extras.append("\n\n**Incidencias:**")
            for i in resultado['incidencias'][:10]:
                extras.append(f"• {i.get('empleado', 'N/A')} - {i.get('tipo', '')} ({i.get('fecha', '')}) - {i.get('cantidad', 1)} hrs/días")
        
        # Recibos de nómina
        if 'recibos' in resultado and resultado['recibos']:
            extras.append("\n\n**Recibos:**")
            for r in resultado['recibos'][:10]:
                extras.append(f"• {r.get('empleado', 'N/A')} | Días: {r.get('dias', 0)} | Neto: ${r.get('neto', 0):,.2f}")


        # Lista de usuarios
        if 'usuarios' in resultado and resultado['usuarios']:
            extras.append("\n\n**Usuarios:**")
            for usr in resultado['usuarios'][:10]:
                extras.append(f"• {usr.get('email', 'N/A')} - Rol: {usr.get('rol', 'N/A')}")
        
        # Organigrama
        if 'organigrama' in resultado and resultado['organigrama']:
            extras.append("\n\n**Organigrama:**")
            for nodo in resultado['organigrama']:
                extras.append(self._formatear_nodo_organigrama(nodo, 0))
        
        # KPIs
        if 'kpis' in resultado and resultado['kpis']:
            extras.append("\n\n**KPIs:**")
            for kpi in resultado['kpis'][:10]:
                progreso = f"{kpi.get('porcentaje', 0):.1f}%" if kpi.get('porcentaje') else "Sin avance"
                extras.append(f"• {kpi.get('nombre', 'KPI')} - Meta: {kpi.get('meta', 0):,.0f} | {progreso}")
        
        # Perfil de empleado
        if 'perfil' in resultado:
            p = resultado['perfil']
            extras.append(f"\n\n**Perfil:** {p.get('nombre_completo', '')}")
            extras.append(f"• Puesto: {p.get('puesto', 'N/A')}")
            extras.append(f"• Departamento: {p.get('departamento', 'N/A')}")
            extras.append(f"• Antigüedad: {p.get('antiguedad', 'N/A')}")
            extras.append(f"• Salario: {p.get('salario_mensual', 'N/A')}")
        
        # Solicitudes pendientes
        if 'solicitudes' in resultado and resultado['solicitudes']:
            extras.append("\n\n**Solicitudes pendientes:**")
            for sol in resultado['solicitudes']:
                extras.append(f"• {sol.get('empleado', 'N/A')} - {sol.get('nombre_kpi', 'KPI')}")
        
        return "\n".join(extras)
    
    def _formatear_nodo_organigrama(self, nodo: Dict, nivel: int) -> str:
        """Formatea un nodo del organigrama con indentación"""
        indent = "  " * nivel
        linea = f"{indent}{'└── ' if nivel > 0 else ''}{nodo.get('nombre', 'N/A')} ({nodo.get('puesto', 'Sin puesto')})"

        resultado = [linea]
        for sub in nodo.get('subordinados', []):
            resultado.append(self._formatear_nodo_organigrama(sub, nivel + 1))

        return "\n".join(resultado)

    # ============ MÉTODOS RAG ============

    def _intentar_respuesta_rag(self, mensaje: str) -> Optional[str]:
        """
        Intenta responder usando documentos RAG si la respuesta de Claude
        parece genérica o no tiene información específica.
        """
        contexto_rag = self._buscar_en_documentos(mensaje)
        if contexto_rag:
            return self._responder_con_contexto_rag(mensaje, contexto_rag)
        return None

    def _buscar_en_documentos(self, consulta: str) -> Optional[str]:
        """Busca información relevante en documentos RAG"""
        try:
            from apps.documentos.services import BuscadorSemantico

            if not self.empresa_contexto:
                return None

            resultados = BuscadorSemantico.buscar(
                query=consulta,
                usuario=self.usuario,
                empresa_id=str(self.empresa_contexto.id),
                top_k=3,
                umbral_similitud=0.3
            )

            if not resultados:
                return None

            # Construir contexto con los fragmentos encontrados
            contexto_partes = ["INFORMACIÓN ENCONTRADA EN DOCUMENTOS DE LA EMPRESA:"]
            for r in resultados:
                contexto_partes.append(f"\n[Fuente: {r['documento_titulo']}]")
                contexto_partes.append(r['contenido'])

            if len(contexto_partes) > 1:
                return "\n".join(contexto_partes)
            return None

        except ImportError:
            # sentence-transformers no instalado
            return None
        except Exception as e:
            print(f"Error buscando en documentos: {e}")
            return None

    def _responder_con_contexto_rag(self, mensaje: str, contexto_rag: str) -> Optional[str]:
        """Genera respuesta usando contexto de documentos"""
        if not self.api_key:
            return None

        try:
            prompt_rag = f"""Basándote en la siguiente información de los documentos de la empresa, responde la pregunta del usuario.

{contexto_rag}

PREGUNTA DEL USUARIO: {mensaje}

INSTRUCCIONES:
- Responde basándote SOLO en la información proporcionada arriba
- Si la información no es suficiente para responder completamente, indícalo
- Cita el documento fuente cuando sea relevante (ej: "Según el Reglamento...")
- Responde en español de forma clara y concisa
- No inventes información que no esté en los documentos"""

            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "content-type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.modelo,
                        "max_tokens": 2048,
                        "messages": [{"role": "user", "content": prompt_rag}]
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    respuesta = data['content'][0]['text']
                    return f"📄 *Información de documentos de la empresa:*\n\n{respuesta}"

        except Exception as e:
            print(f"Error en respuesta RAG: {e}")
        return None

    # ============ MÉTODOS EXPEDIENTE ============

    def _guardar_documento_expediente(self, empleado, archivo_info: Dict, contenido: str,
                                       mensaje, flujo_activo: str = ''):
        """Guarda un documento en el expediente del empleado"""
        try:
            from apps.empleados.models import DocumentoEmpleado
            from .archivo_service import ProcesadorArchivoChat

            # Detectar tipo de documento
            tipo_doc = ProcesadorArchivoChat.detectar_tipo_documento(
                archivo_info['nombre'],
                contenido,
                flujo_activo
            )

            DocumentoEmpleado.objects.create(
                empleado=empleado,
                tipo=tipo_doc,
                nombre=archivo_info['nombre'],
                archivo=mensaje.archivo_adjunto,
                tipo_archivo=archivo_info['tipo'],
                tamaño_bytes=archivo_info['tamaño'],
                contenido_texto=contenido[:10000] if contenido else '',
                mensaje_chat=mensaje,
            )

            return True
        except Exception as e:
            print(f"Error guardando documento en expediente: {e}")
            return False

    def establecer_empleado_contexto(self, conversacion_id: str, empleado_id: str):
        """Establece el empleado en contexto para la conversación"""
        from .models import Conversacion
        from apps.empleados.models import Empleado

        try:
            conversacion = Conversacion.objects.get(pk=conversacion_id, usuario=self.usuario)
            empleado = Empleado.objects.get(pk=empleado_id)

            # Verificar que el usuario tenga acceso al empleado
            if self.empresa_contexto and empleado.empresa != self.empresa_contexto:
                return {'success': False, 'error': 'No tienes acceso a este empleado'}

            conversacion.empleado_contexto = empleado
            conversacion.save()

            return {
                'success': True,
                'mensaje': f'Contexto establecido: {empleado.nombre_completo}',
                'empleado': empleado.nombre_completo
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def iniciar_flujo(self, conversacion_id: str, flujo_id: str, datos_iniciales: Dict = None):
        """Inicia un flujo guiado en la conversación"""
        from .models import Conversacion
        from .flujos import obtener_flujo

        try:
            conversacion = Conversacion.objects.get(pk=conversacion_id, usuario=self.usuario)
            flujo = obtener_flujo(flujo_id)

            if not flujo:
                return {'success': False, 'error': f'Flujo "{flujo_id}" no existe'}

            conversacion.flujo_activo = flujo_id
            conversacion.paso_actual = 0
            conversacion.datos_flujo = datos_iniciales or {}
            conversacion.save()

            return {
                'success': True,
                'flujo': flujo['nombre'],
                'primer_paso': flujo['pasos'][0] if flujo['pasos'] else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def cancelar_flujo(self, conversacion_id: str):
        """Cancela el flujo activo"""
        from .models import Conversacion

        try:
            conversacion = Conversacion.objects.get(pk=conversacion_id, usuario=self.usuario)
            conversacion.flujo_activo = ''
            conversacion.paso_actual = 0
            conversacion.datos_flujo = {}
            conversacion.save()

            return {'success': True, 'mensaje': 'Flujo cancelado'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
