# Estado del Proyecto - Sistema RRHH

**Ultima actualizacion:** 2025-12-02

## Resumen

Sistema de RRHH para empresas mexicanas con backend Django 5 + DRF y Chat IA como interfaz principal.

**Estado actual:** ✅ LISTO PARA FRONTEND | 69 acciones IA | 4 flujos guiados | 9 modulos | 99.2% tests passing

---

## Modulos Implementados

### Core y Autenticacion
- [x] Usuarios con roles (Admin, RRHH/Empleador, Empleado)
- [x] Autenticacion JWT
- [x] Multi-empresa (usuarios pueden pertenecer a multiples empresas)
- [x] **Tokens de activacion y reset de password**
- [x] **Solicitudes de cambio de datos sensibles**
- [x] **12 acciones IA para gestion de usuarios y perfil**

### Empleados
- [x] CRUD completo de empleados
- [x] Estructura jerarquica (jefe_directo)
- [x] Calculo de antiguedad
- [x] Estados: activo, baja, incapacidad
- [x] Gestion de bajas/terminaciones laborales
- [x] Archivo de extrabajadores
- [x] Reactivacion de empleados (recontratacion)
- [x] **Expediente digital (DocumentoEmpleado) - 22 tipos de documentos**

### Nomina
- [x] Periodos de nomina (semanal, quincenal, mensual)
- [x] Calculo de ISR segun tablas SAT
- [x] Calculo de cuotas IMSS
- [x] Incidencias (faltas, horas extra, bonos, incapacidades)
- [x] Generacion de recibos
- [x] Flujo: borrador -> calculado -> autorizado -> pagado
- [x] **Notificacion automatica a empleados al autorizar nomina**

### Vacaciones
- [x] Calculo segun LFT (dias por antiguedad)
- [x] Solicitudes con flujo de aprobacion
- [x] Periodos vacacionales por empleado

### Prestaciones
- [x] Planes de prestaciones por empresa
- [x] Aguinaldo, prima vacacional
- [x] Prestaciones adicionales configurables

### Desempeno/KPIs
- [x] Catalogo de KPIs
- [x] Asignacion de KPIs a empleados
- [x] Registro de avances
- [x] Solicitud de cambios (empleado -> jefe)
- [x] Aprobacion/rechazo de cambios

### Documentos RAG
- [x] Modelo Documento (politicas, reglamentos, manuales)
- [x] Modelo FragmentoDocumento (para embeddings)
- [x] Extraccion de texto (PDF, DOCX, TXT)
- [x] Fragmentacion inteligente con solapamiento
- [x] Generacion de embeddings (sentence-transformers)
- [x] Busqueda semantica por similitud coseno
- [x] Permisos: solo Admin/RRHH pueden ver documentos
- [x] API REST completa (DocumentoViewSet)
- [x] Procesamiento automatico al subir documento
- [x] Integracion RAG en chat (fallback cuando no hay accion)

### Chat IA
- [x] Integracion con API de Anthropic (Claude)
- [x] **Sistema de 48 acciones registradas**
- [x] Contexto por empresa/empleado
- [x] Historial de conversaciones
- [x] RAG: busqueda en documentos cuando no hay accion
- [x] **Soporte para archivos adjuntos (PDF, DOCX, TXT, imagenes)**
- [x] **4 flujos guiados para procesos complejos**
- [x] **Expediente digital de empleados**
- [x] **Deteccion automatica de tipo de documento**

### Notificaciones (NUEVO)
- [x] Modelo ConfiguracionNotificaciones (preferencias usuario)
- [x] Modelo Notificacion (registro de envios)
- [x] EmailService para envio de correos HTML
- [x] 7 plantillas de email responsive
- [x] Tipos: solicitud, aprobacion, rechazo, alerta, nomina, sistema
- [x] Prioridades: baja, media, alta, urgente
- [x] Management command para alertas de vencimiento
- [x] 4 acciones IA para notificaciones

### Solicitudes (NUEVO)
- [x] Modelo Solicitud generico (relacionado con ContentType)
- [x] Tipos: vacaciones, permiso, kpi, salario, baja, otro
- [x] Estados: borrador, pendiente, aprobada, rechazada, cancelada
- [x] Flujo de aprobacion a jefe directo
- [x] Notificacion automatica al enviar/aprobar/rechazar
- [x] 4 acciones IA para solicitudes

### Reportes
- [x] Dashboard empresa
- [x] Dashboard empleado
- [x] Calculo de liquidacion/finiquito
- [x] Generacion de PDFs
- [x] **Exportacion a Excel (empleados, nomina, incidencias, solicitudes)**

### Integraciones (NUEVO)
- [x] Google Calendar (sincronizar vacaciones, cumpleanos, aniversarios)
- [x] Sistema de Auditoria (registro de cambios)
- [x] Busqueda avanzada de empleados

---

## Acciones IA Registradas (69 total)

| Modulo | Cantidad | Acciones |
|--------|----------|----------|
| Empleados | 13 | buscar_empleado, crear_empleado, ver_perfil_empleado, obtener_subordinados, obtener_organigrama, asignar_jefe, dar_baja_empleado, ver_extrabajadores, ver_historial_empleado, reactivar_empleado, ver_expediente, verificar_documentos_pendientes, busqueda_avanzada_empleados |
| Nomina | 9 | crear_periodo_nomina, ver_periodos_nomina, registrar_incidencia, ver_incidencias, calcular_nomina, ver_pre_nomina, ver_mi_recibo, autorizar_nomina, generar_dispersion |
| Documentos | 4 | buscar_en_documentos, listar_documentos, consultar_documento, subir_documento |
| Reportes | 8 | dashboard_empresa, dashboard_empleado, calcular_liquidacion, generar_pdf_empleado, exportar_empleados_excel, exportar_nomina_excel, exportar_incidencias_excel, exportar_solicitudes_excel |
| Desempeno | 7 | asignar_kpi, ver_mis_kpis, ver_kpis_equipo, registrar_avance_kpi, solicitar_cambio_kpi, aprobar_cambio_kpi, resumen_desempeno_equipo |
| Notificaciones | 4 | ver_mis_notificaciones, ver_solicitudes_pendientes, configurar_notificaciones, marcar_notificaciones_leidas |
| Solicitudes | 4 | crear_solicitud, aprobar_solicitud, rechazar_solicitud, ver_mis_solicitudes |
| Integraciones | 6 | configurar_google_calendar, sincronizar_calendario, ver_eventos_calendario, estado_google_calendar, ver_auditoria, historial_objeto |
| **Usuarios/Perfil** | **12** | ver_mi_perfil, actualizar_mi_perfil, cambiar_mi_password, solicitar_cambio_datos, mis_solicitudes_cambio, listar_solicitudes_cambio, aprobar_cambio_datos, rechazar_cambio_datos, listar_usuarios, crear_usuario, activar_usuario, reenviar_activacion |

---

## Gestion de Usuarios y Perfil (NUEVO)

### Modelos Nuevos

| Modelo | Descripcion |
|--------|-------------|
| TokenUsuario | Tokens para activacion de cuenta y reset de password |
| SolicitudCambioDatos | Solicitudes de cambio de datos sensibles del empleado |

### TokenUsuario
```python
TokenUsuario:
- usuario: ForeignKey(Usuario)
- token: CharField(64) - token seguro generado con secrets
- tipo: activacion/reset
- usado: Boolean
- expira_en: DateTimeField
- created_at: DateTimeField
- usado_en: DateTimeField

# Metodos de clase
TokenUsuario.crear_token_activacion(usuario, horas_valido=48)
TokenUsuario.crear_token_reset(usuario, horas_valido=24)

# Propiedades
token.es_valido  # No usado y no expirado
token.usar()     # Marca como usado
```

### SolicitudCambioDatos
```python
SolicitudCambioDatos:
- empleado: ForeignKey(Empleado)
- tipo_cambio: rfc/curp/nss/cuenta_bancaria/direccion/telefono/email_personal/contacto_emergencia
- datos_actuales: JSONField
- datos_nuevos: JSONField
- justificacion: TextField
- documento_soporte: FileField (opcional)
- estado: pendiente/aprobada/rechazada
- revisado_por: ForeignKey(Usuario)
- fecha_revision: DateTimeField
- comentario_revision: TextField

# Metodos
solicitud.aprobar(usuario, comentario)  # Aplica cambios automaticamente
solicitud.rechazar(usuario, comentario)
```

### UsuarioService
Ubicacion: `apps/usuarios/services.py`

| Metodo | Descripcion |
|--------|-------------|
| crear_usuario() | Crea usuario y envia email de activacion |
| activar_cuenta(token) | Activa cuenta con token |
| solicitar_reset_password(email) | Envia email de reset |
| resetear_password(token, password) | Resetea password con token |
| cambiar_password(usuario, actual, nuevo) | Cambia password autenticado |
| actualizar_perfil(usuario, datos) | Actualiza datos del perfil |
| reenviar_activacion(email) | Reenvia email de activacion |
| crear_solicitud_cambio() | Crea solicitud de cambio de datos |
| aprobar_solicitud_cambio() | Aprueba y aplica cambio |
| rechazar_solicitud_cambio() | Rechaza solicitud |
| listar_solicitudes_cambio() | Lista segun permisos |
| obtener_mi_perfil() | Obtiene perfil completo |

### Endpoints REST Nuevos

| Endpoint | Metodo | Auth | Descripcion |
|----------|--------|------|-------------|
| /api/usuarios/activar/ | POST | No | Activar cuenta con token |
| /api/usuarios/solicitar-reset/ | POST | No | Solicitar reset de password |
| /api/usuarios/reset-password/ | POST | No | Resetear password con token |
| /api/usuarios/reenviar-activacion/ | POST | No | Reenviar email de activacion |
| /api/usuarios/cambiar-password/ | POST | Si | Cambiar password |
| /api/usuarios/perfil/ | GET | Si | Obtener mi perfil completo |
| /api/usuarios/perfil/actualizar/ | PATCH | Si | Actualizar mi perfil |

### Templates de Email Nuevos

| Template | Uso |
|----------|-----|
| activacion.html | Email de activacion de cuenta |
| reset_password.html | Email de reset de password |
| password_cambiado.html | Notificacion de password cambiado |

### Acciones IA de Usuarios (12)

| Categoria | Accion | Descripcion |
|-----------|--------|-------------|
| Perfil | ver_mi_perfil | Ver mi perfil completo |
| Perfil | actualizar_mi_perfil | Actualizar nombre, preferencias |
| Perfil | cambiar_mi_password | Cambiar password |
| Cambios | solicitar_cambio_datos | Solicitar cambio de RFC, CURP, etc |
| Cambios | mis_solicitudes_cambio | Ver mis solicitudes |
| RRHH | listar_solicitudes_cambio | Ver solicitudes pendientes |
| RRHH | aprobar_cambio_datos | Aprobar solicitud |
| RRHH | rechazar_cambio_datos | Rechazar solicitud |
| Admin | listar_usuarios | Listar usuarios del sistema |
| Admin | crear_usuario | Crear nuevo usuario |
| Admin | activar_usuario | Activar/desactivar usuario |
| Admin | reenviar_activacion | Reenviar email de activacion |

---

## Sistema de Notificaciones

### Tipos de Notificacion
| Tipo | Descripcion |
|------|-------------|
| solicitud | Solicitud pendiente de aprobacion |
| aprobacion | Solicitud aprobada |
| rechazo | Solicitud rechazada |
| alerta | Documentos por vencer |
| recordatorio | Recordatorios generales |
| confirmacion | Confirmacion de acciones |
| nomina | Recibos de nomina disponibles |
| documento | Documentos agregados/actualizados |
| sistema | Notificaciones del sistema |

### Prioridades
- baja: Informativo
- media: Normal
- alta: Importante
- urgente: Requiere atencion inmediata

### Plantillas de Email (10 total)
| Template | Uso |
|----------|-----|
| base_email.html | Template base con estilos |
| solicitud_aprobacion.html | Notificar jefe de solicitud pendiente |
| confirmacion_aprobacion.html | Notificar empleado de aprobacion |
| notificacion_rechazo.html | Notificar empleado de rechazo |
| alerta_vencimiento.html | Documentos proximos a vencer |
| recibo_nomina.html | Recibo de nomina disponible |
| bienvenida.html | Bienvenida a nuevo empleado |
| notificacion_general.html | Template generico |
| **activacion.html** | Activacion de cuenta de usuario |
| **reset_password.html** | Restablecer password |
| **password_cambiado.html** | Notificacion de password cambiado |

### Configuracion por Usuario
```python
ConfiguracionNotificaciones:
- recibir_solicitudes: bool
- recibir_alertas: bool
- recibir_confirmaciones: bool
- recibir_nomina: bool
- frecuencia_email: inmediato/diario/semanal/nunca
- hora_envio: TimeField (para resumenes)
```

---

## Sistema de Solicitudes

### Modelo Solicitud
```python
Solicitud:
- tipo: vacaciones/permiso/incapacidad/kpi/salario/documento/baja/otro
- titulo: CharField
- descripcion: TextField
- prioridad: baja/media/alta/urgente
- solicitante: ForeignKey(Empleado)
- aprobador: ForeignKey(Usuario)
- estado: borrador/pendiente/aprobada/rechazada/cancelada
- content_type/object_id: GenericForeignKey (objeto relacionado)
- datos: JSONField (datos especificos)
```

### Flujo de Solicitud
1. Empleado crea solicitud (estado: borrador)
2. Empleado envia solicitud (estado: pendiente)
3. Sistema notifica al jefe (email + notificacion in-app)
4. Jefe aprueba/rechaza
5. Sistema notifica al empleado del resultado

### Metodos de Solicitud
```python
solicitud.enviar()      # Cambia a pendiente, notifica jefe
solicitud.aprobar()     # Cambia a aprobada, notifica empleado
solicitud.rechazar()    # Cambia a rechazada, notifica empleado
solicitud.cancelar()    # Cancela solicitud
```

---

## Configuracion de Email

### Settings (config/settings.py)
```python
# Desarrollo (console backend - muestra en terminal)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Produccion (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'RRHH Sistema <noreply@rrhh.local>'
FRONTEND_URL = 'http://localhost:5173'
```

### Variables de Entorno (.env)
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=RRHH Sistema <noreply@tudominio.com>
FRONTEND_URL=https://tu-app.com
```

---

## Management Commands

### Alertas de Vencimiento
```powershell
# Enviar alertas de documentos que vencen en los proximos 30 dias
python manage.py enviar_alertas_diarias

# Solo mostrar que se enviaria (dry run)
python manage.py enviar_alertas_diarias --dry-run

# Cambiar dias de anticipacion
python manage.py enviar_alertas_diarias --dias=15
```

### Configurar en Cron (Linux/Mac)
```bash
# Ejecutar todos los dias a las 9:00 AM
0 9 * * * cd /path/to/project && python manage.py enviar_alertas_diarias
```

### Configurar en Task Scheduler (Windows)
1. Abrir Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 9:00 AM
4. Action: Start a program
5. Program: python
6. Arguments: manage.py enviar_alertas_diarias
7. Start in: C:\path\to\backend

---

## Nuevas Apps

### apps/notificaciones/
```
notificaciones/
  __init__.py
  admin.py
  apps.py
  models.py              # ConfiguracionNotificaciones, Notificacion
  email_service.py       # EmailService
  services.py            # NotificacionService
  acciones_ia.py         # 4 acciones
  management/
    commands/
      enviar_alertas_diarias.py
  templates/
    emails/
      base_email.html
      solicitud_aprobacion.html
      confirmacion_aprobacion.html
      notificacion_rechazo.html
      alerta_vencimiento.html
      recibo_nomina.html
      bienvenida.html
      notificacion_general.html
```

### apps/solicitudes/
```
solicitudes/
  __init__.py
  admin.py
  apps.py
  models.py              # Solicitud
  services.py            # SolicitudService
  acciones_ia.py         # 4 acciones
```

---

## Migraciones Nuevas

```powershell
# Migraciones creadas
apps/notificaciones/migrations/0001_initial.py
apps/solicitudes/migrations/0001_initial.py
apps/usuarios/migrations/0002_solicitudcambiodatos_tokenusuario.py
apps/integraciones/migrations/0003_configurationgooglecalendar_eventosincronizado_registroauditoria.py

# Aplicar
python manage.py migrate
```

---

## Google Calendar

### Configuracion
Para usar Google Calendar, configura las variables de entorno:
```
GOOGLE_CLIENT_ID=tu-client-id
GOOGLE_CLIENT_SECRET=tu-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/integraciones/google/callback/
```

### Modelos
| Modelo | Descripcion |
|--------|-------------|
| ConfiguracionGoogleCalendar | Configuracion OAuth por empresa |
| EventoSincronizado | Registro de eventos sincronizados |

### Tipos de Eventos Sincronizables
- Vacaciones (color verde)
- Cumpleanos (color amarillo)
- Aniversarios laborales (color verde oscuro)
- Incapacidades (opcional)

### Acciones IA
- `configurar_google_calendar` - Configura la integracion
- `sincronizar_calendario` - Sincroniza cumpleanos/aniversarios
- `ver_eventos_calendario` - Lista eventos del mes
- `estado_google_calendar` - Muestra estado de la integracion

---

## Reportes Excel

### Servicio de Exportacion
Ubicacion: `apps/reportes/excel_service.py`

Genera archivos Excel con formato profesional:
- Encabezados con estilo
- Anchos de columna automaticos
- Totales calculados

### Reportes Disponibles
| Reporte | Accion IA | Filtros |
|---------|-----------|---------|
| Empleados | exportar_empleados_excel | estado, departamento |
| Nomina | exportar_nomina_excel | periodo_id |
| Incidencias | exportar_incidencias_excel | mes, ano |
| Solicitudes | exportar_solicitudes_excel | estado, tipo |

---

## Sistema de Auditoria

### Modelo RegistroAuditoria
Registra todas las acciones importantes del sistema:
- Quien (usuario)
- Que (modelo, objeto_id)
- Cuando (timestamp)
- Detalles (datos_anteriores, datos_nuevos)
- Metadatos (IP, user_agent)

### Tipos de Acciones
- crear, modificar, eliminar
- aprobar, rechazar
- login, logout
- exportar, consultar

### Acciones IA
- `ver_auditoria` - Lista registros de auditoria
- `historial_objeto` - Historial de un objeto especifico

---

## Flujos Guiados (4 total)

| Flujo | Descripcion | Pasos | Triggers |
|-------|-------------|-------|----------|
| baja_empleado | Baja de empleado con documentos y liquidacion | 8 | "dar de baja", "despedir", "renuncia de" |
| crear_empleado | Alta de nuevo empleado completo | 13 | "nuevo empleado", "contratar", "dar de alta" |
| registrar_incidencia | Registrar falta/permiso/incapacidad | 9 | "registrar incidencia", "reportar falta", "incapacidad" |
| subir_documento | Subir documento a expediente | 4 | "subir documento", "cargar archivo" |

---

## Integracion de Notificaciones

### Acciones que Envian Notificaciones

| Accion | Notificacion |
|--------|--------------|
| autorizar_nomina | Notifica a empleados que su recibo esta disponible |
| dar_baja_empleado | Notifica al jefe directo de la baja |
| Solicitud.enviar() | Notifica al jefe que hay solicitud pendiente |
| Solicitud.aprobar() | Notifica al empleado de la aprobacion |
| Solicitud.rechazar() | Notifica al empleado del rechazo |

---

## Pruebas del Sistema

### Test Completo
```powershell
cd "C:\Users\adria\Downloads\Programa de RRHH - Grupo CA\backend"
python test_sistema_completo.py
```

### Verificar Acciones
```powershell
python manage.py shell -c "from apps.chat.acciones_registry import ACCIONES_REGISTRADAS; print(f'Total: {len(ACCIONES_REGISTRADAS)}')"
```

---

## Ultima Prueba del Sistema

**Fecha:** 2025-12-02
**Script:** test_sistema_completo.py
**Resultado:** 118 pasaron / 2 warnings / 1 fallaron (99.2% exito)
**Estado:** ✅ LISTO PARA FRONTEND

### Resultados Detallados
```
Total de pruebas: 121
Acciones IA registradas: 69
Modulos principales: 9
Flujos guiados: 4
Tipos de documento: 22
Templates de email: 10
Endpoints REST usuarios: 10
```

### Modulos Verificados
- [x] Acciones IA registradas (69 total)
- [x] Ejecucion de acciones clave (buscar_empleado, dashboard_empresa, etc.)
- [x] Flujo de Nomina completo
- [x] Flujo de Solicitudes
- [x] Sistema de Notificaciones (templates OK)
- [x] Expediente Digital (22 tipos de documentos)
- [x] Chat IA + RAG
- [x] Email Service (10 plantillas)
- [x] Management Commands (enviar_alertas_diarias)
- [x] Flujos Guiados (4 de 4)
- [x] Google Calendar (configuracion, sincronizacion)
- [x] Reportes Excel (4 tipos)
- [x] Sistema de Auditoria
- [x] **Gestion de Usuarios y Perfil (12 acciones)**
- [x] **Tokens de activacion/reset**
- [x] **Solicitudes de cambio de datos**
- [x] **UsuarioService completo**
- [x] **Endpoints REST de usuarios (10)**

### Acciones por Modulo
| Modulo | Cantidad | Status |
|--------|----------|--------|
| Empleados | 13 | ✅ |
| Nomina | 9 | ✅ |
| Documentos | 4 | ✅ |
| Reportes | 8 | ✅ |
| Desempeno | 7 | ✅ |
| Notificaciones | 4 | ✅ |
| Solicitudes | 4 | ✅ |
| Integraciones | 6 | ✅ |
| Usuarios/Perfil | 12 | ✅ |
| **TOTAL** | **69** | ✅ |

### Warnings (no criticos)
- buscar_empleado: Admin sin empresa asignada no puede buscar empleados (comportamiento correcto de permisos)
- ver_perfil_empleado: Admin sin acceso a empleado de otra empresa (comportamiento correcto)

### Error Menor (1)
- NotificacionService.crear() no existe - el servicio usa metodos especificos (enviar_notificacion, enviar_email)

---

## Comandos Utiles

```powershell
# Iniciar servidor (PowerShell)
cd "C:\Users\adria\Downloads\Programa de RRHH - Grupo CA\backend"
$env:USE_SQLITE="True"; $env:DEBUG="True"; python manage.py runserver

# Aplicar migraciones pendientes
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Ver acciones registradas
python manage.py shell -c "from apps.chat.acciones_registry import ACCIONES_REGISTRADAS; [print(a) for a in sorted(ACCIONES_REGISTRADAS.keys())]"

# Test alertas diarias (dry run)
python manage.py enviar_alertas_diarias --dry-run
```

---

## Que Falta por Implementar

### Prioridad Alta
- [x] ~~Endpoints REST para documentos RAG~~
- [x] ~~Gestion de bajas de empleados~~
- [x] ~~Flujos guiados + archivos en chat~~
- [x] ~~Expediente digital de empleados~~
- [x] ~~Sistema de notificaciones por email~~
- [x] ~~Sistema de solicitudes con flujo de aprobacion~~
- [x] ~~Prueba completa del sistema end-to-end~~
- [x] ~~Integracion Google Calendar~~
- [x] ~~Reportes Excel exportables~~
- [x] ~~Sistema de auditoria~~
- [x] ~~Busqueda avanzada de empleados~~
- [ ] Frontend para chat con archivos (drag & drop)
- [ ] Frontend para expedientes digitales
- [ ] Frontend para notificaciones
- [ ] Frontend para solicitudes
- [ ] Frontend para Google Calendar

### Prioridad Media
- [ ] Contratos laborales (modulo existe pero basico)
- [ ] Evaluaciones de desempeno formales
- [ ] Timbrado CFDI real
- [ ] OAuth completo para Google Calendar (flujo web)

### Prioridad Baja
- [ ] Integracion bancaria real
- [ ] App movil
- [ ] Portal de autoservicio empleados

---

## Stack Tecnico

| Componente | Tecnologia |
|------------|------------|
| Backend | Django 5.1.2, Django REST Framework 3.15.2 |
| Auth | JWT (SimpleJWT) |
| DB | SQLite (dev), PostgreSQL (prod) |
| IA | Anthropic Claude API (claude-sonnet-4) |
| Embeddings | sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) |
| Extraccion | PyPDF2, python-docx |
| Email | Django Email (console dev, SMTP prod) |
| Python | 3.14 (recomendado: 3.12/3.13 para produccion) |
