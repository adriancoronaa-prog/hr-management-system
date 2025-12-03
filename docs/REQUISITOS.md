# Requisitos Funcionales - RRHH Multi-empresa

## 1. Gestión Multi-empresa

### 1.1 Alta de Empresa
**Como** administrador del sistema  
**Quiero** registrar una nueva empresa  
**Para** gestionar sus empleados y configuraciones de forma independiente

**Criterios de aceptación:**
- Campos obligatorios: RFC, razón social, régimen fiscal, domicilio fiscal
- Campos opcionales: logo, representante legal, teléfono, email
- Al crear empresa, se genera automáticamente un plan de prestaciones "Estándar" basado en Ley Federal del Trabajo
- Validación de RFC único en el sistema
- Opción de copiar configuración de otra empresa existente

**Datos de empresa:**
```
- RFC (único, validación formato)
- Razón social
- Nombre comercial
- Régimen fiscal
- Domicilio fiscal completo
  - Calle y número
  - Colonia
  - Código postal
  - Municipio/Alcaldía
  - Estado
- Representante legal
- Teléfono
- Email
- Logo (imagen)
- Fecha de registro en sistema
- Estado (activa/inactiva)
```

### 1.2 Baja de Empresa
**Como** administrador del sistema  
**Quiero** dar de baja una empresa  
**Para** que ya no aparezca en las opciones activas

**Criterios de aceptación:**
- Soft delete (no se elimina físicamente)
- NO se puede dar de baja si tiene empleados activos
- Opción de migrar empleados a otra empresa antes de dar de baja
- Se preserva el histórico para reportes
- Requiere confirmación con motivo

### 1.3 Selector de Empresa
**Como** usuario de RRHH  
**Quiero** cambiar entre empresas sin cerrar sesión  
**Para** gestionar todas las empresas de forma ágil

**Criterios de aceptación:**
- Selector visible en header de la aplicación
- Cambio instantáneo sin recarga de página
- Opción "Todas las empresas" para vista consolidada
- Recordar última empresa seleccionada por usuario

---

## 2. Gestión de Empleados

### 2.1 Alta de Empleado (con fecha retroactiva)
**Como** usuario de RRHH  
**Quiero** registrar un empleado con su fecha real de ingreso (aunque sea pasada)  
**Para** que el sistema calcule correctamente antigüedad y prestaciones

**Criterios de aceptación:**
- Fecha de ingreso puede ser cualquier fecha pasada
- Al guardar, el sistema calcula automáticamente:
  - Antigüedad (años, meses, días)
  - Vacaciones generadas por periodo
  - Próximo aniversario laboral
- Si fecha es retroactiva, mostrar wizard para registrar historial de vacaciones
- Opciones de registro de historial:
  - Detallado (fechas exactas)
  - Simplificado (solo días por año)
  - Saldo actual (solo días pendientes)
  - Importar desde Excel

**Datos del empleado:**

```
DATOS PERSONALES
- Nombre(s)
- Apellido paterno
- Apellido materno
- CURP (validación formato)
- RFC (validación formato)
- NSS / Número IMSS
- Fecha de nacimiento
- Género
- Estado civil
- Nacionalidad
- Lugar de nacimiento

CONTACTO
- Teléfono personal
- Teléfono casa
- Email personal
- Email corporativo
- Dirección completa
  - Calle y número
  - Colonia
  - Código postal
  - Municipio
  - Estado

CONTACTO DE EMERGENCIA
- Nombre completo
- Parentesco
- Teléfono 1
- Teléfono 2

DATOS BANCARIOS
- Banco
- CLABE interbancaria
- Número de cuenta

DATOS LABORALES
- Empresa (FK)
- Fecha de ingreso ← PUEDE SER RETROACTIVA
- Fecha de ingreso al sistema (automática)
- Puesto
- Departamento
- Jefe directo (FK empleado)
- Tipo de contrato
- Jornada laboral (diurna/nocturna/mixta)
- Horario
- Modalidad (presencial/remoto/híbrido)
- Centro de trabajo
- Plan de prestaciones (FK)

DATOS SALARIALES
- Salario diario
- Salario mensual (calculado)
- Salario diario integrado (calculado)

ESTADO
- Estado: activo/baja/incapacidad
- Fecha de baja (si aplica)
- Motivo de baja
- Foto de perfil
```

### 2.2 Cálculos Automáticos al Alta
**Como** sistema  
**Quiero** calcular automáticamente todos los datos derivados  
**Para** que RRHH no tenga que hacer cálculos manuales

**Cálculos:**
```
ANTIGÜEDAD
- Años completos = floor((fecha_actual - fecha_ingreso) / 365)
- Meses = floor(días_restantes / 30)
- Días = días_restantes % 30

VACACIONES POR PERIODO
Para cada año desde ingreso hasta hoy:
  - Año 1: días según plan (mínimo 12 LFT)
  - Año 2: días según plan (mínimo 14 LFT)
  - Año 3: días según plan (mínimo 16 LFT)
  - Año 4: días según plan (mínimo 18 LFT)
  - Año 5: días según plan (mínimo 20 LFT)
  - Año 6-10: días según plan (mínimo 22 LFT)
  - Año 11-15: días según plan (mínimo 24 LFT)
  - ...continúa +2 días cada 5 años

SALDO DE VACACIONES
- Días generados (suma todos los periodos)
- Días tomados (registrados)
- Días disponibles = generados - tomados

PRÓXIMO ANIVERSARIO
- fecha_ingreso + (años_completos + 1) años

AGUINALDO PROPORCIONAL (año en curso)
- días_aguinaldo × (días_trabajados_año / 365)
```

### 2.3 Edición de Empleado
**Como** usuario de RRHH  
**Quiero** modificar datos de un empleado  
**Para** mantener la información actualizada

**Criterios de aceptación:**
- Todos los campos editables excepto CURP (requiere autorización especial)
- Cambio de empresa genera nuevo registro de historial
- Cambio de salario genera registro en histórico salarial
- Auditoría de cambios (quién, cuándo, qué cambió)

### 2.4 Baja de Empleado
**Como** usuario de RRHH  
**Quiero** registrar la baja de un empleado  
**Para** el cálculo de finiquito y mantener histórico

**Criterios de aceptación:**
- Campos: fecha de baja, motivo, tipo (renuncia/despido/término contrato)
- Calcular automáticamente:
  - Días de vacaciones pendientes
  - Prima vacacional pendiente
  - Aguinaldo proporcional
  - Prima de antigüedad (si aplica)
- Generar reporte de finiquito
- Empleado pasa a estado "baja" pero se conserva en sistema

---

## 3. Gestión de Contratos

### 3.1 Alta de Contrato
**Como** usuario de RRHH  
**Quiero** registrar contratos laborales  
**Para** tener control de la relación laboral

**Tipos de contrato (México):**
- Indefinido
- Temporal
- Por obra determinada
- Por tiempo determinado
- Capacitación inicial
- Periodo de prueba

**Datos del contrato:**
```
- Empleado (FK)
- Tipo de contrato
- Fecha de inicio
- Fecha de fin (si aplica)
- Puesto
- Salario
- Jornada
- Horario
- Condiciones especiales
- Documento adjunto (PDF)
- Estado (vigente/vencido/renovado)
- Contrato anterior (FK, para renovaciones)
```

### 3.2 Alertas de Vencimiento
**Como** usuario de RRHH  
**Quiero** recibir alertas de contratos por vencer  
**Para** gestionar renovaciones a tiempo

**Criterios de aceptación:**
- Alerta a 30 días del vencimiento
- Alerta a 15 días del vencimiento
- Alerta a 7 días del vencimiento
- Notificación por email y en sistema
- Dashboard con contratos por vencer

---

## 4. Gestión de Vacaciones

### 4.1 Solicitud de Vacaciones
**Como** empleado (o RRHH en su nombre)  
**Quiero** solicitar días de vacaciones  
**Para** programar mi descanso

**Criterios de aceptación:**
- Seleccionar rango de fechas
- Mostrar días disponibles antes de solicitar
- Validar que no exceda saldo disponible
- Mostrar calendario con ausencias del equipo
- Seleccionar sustituto (opcional)
- Estado inicial: pendiente de aprobación

### 4.2 Aprobación de Vacaciones
**Como** usuario de RRHH (o jefe directo)  
**Quiero** aprobar o rechazar solicitudes  
**Para** gestionar las ausencias del equipo

**Criterios de aceptación:**
- Ver solicitudes pendientes por empresa
- Aprobar/rechazar con comentarios
- Notificar al empleado del resultado
- Actualizar calendario de equipo
- Descontar días del saldo al aprobar

### 4.3 Registro Retroactivo de Vacaciones
**Como** usuario de RRHH  
**Quiero** registrar vacaciones ya tomadas en el pasado  
**Para** mantener el historial correcto al dar de alta empleados

**Criterios de aceptación:**
- Marcar como "registro histórico"
- No requiere flujo de aprobación
- Puede ser fecha anterior al ingreso al sistema
- Opción de registro masivo por periodo

### 4.4 Calendario de Vacaciones
**Como** usuario de RRHH  
**Quiero** ver un calendario con las vacaciones del equipo  
**Para** planificar y evitar conflictos

**Criterios de aceptación:**
- Vista mensual/semanal
- Filtrar por empresa/departamento
- Código de colores por estado (aprobada, pendiente, rechazada)
- Mostrar festivos
- Exportar a Excel/PDF

---

## 5. Gestión de Prestaciones

### 5.1 Configurar Plan de Prestaciones
**Como** administrador  
**Quiero** crear planes de prestaciones por empresa  
**Para** ofrecer beneficios diferenciados

**Estructura del plan:**
```
PRESTACIONES DE LEY (configurables superior a mínimo)
├── Vacaciones
│   ├── Método: según_ley / personalizado
│   └── Tabla de días por antigüedad
├── Prima vacacional
│   └── Porcentaje (mínimo 25%)
├── Aguinaldo
│   └── Días (mínimo 15)
└── Prima dominical
    └── Porcentaje (mínimo 25%)

PRESTACIONES ADICIONALES
├── Vales de despensa
│   ├── Activo: sí/no
│   ├── Monto mensual
│   └── Proveedor
├── Seguro de gastos médicos
│   ├── Activo: sí/no
│   ├── Tipo de cobertura
│   └── Aseguradora
├── Fondo de ahorro
│   ├── Activo: sí/no
│   ├── Porcentaje empleado
│   └── Porcentaje empresa
├── Bono de puntualidad
│   ├── Activo: sí/no
│   └── Monto mensual
├── Bono de asistencia
│   ├── Activo: sí/no
│   └── Monto mensual
├── Ayuda de transporte
│   ├── Activo: sí/no
│   └── Monto mensual
├── Ayuda de comedor
│   ├── Activo: sí/no
│   └── Monto mensual
└── Otras (configurables)
```

### 5.2 Asignar Plan a Empleado
**Como** usuario de RRHH  
**Quiero** asignar un plan de prestaciones a cada empleado  
**Para** que el sistema calcule correctamente sus beneficios

**Criterios de aceptación:**
- Plan por defecto al dar de alta
- Posibilidad de cambiar plan
- Histórico de cambios de plan

### 5.3 Ajustes Individuales
**Como** usuario de RRHH  
**Quiero** hacer ajustes individuales a las prestaciones de un empleado  
**Para** casos especiales (negociaciones, promociones)

**Criterios de aceptación:**
- Sobrescribir cualquier valor del plan
- Registrar motivo del ajuste
- Fecha de vigencia (inicio/fin)
- Aprobación requerida
- Histórico de ajustes

### 5.4 Comparativa con Ley
**Como** usuario de RRHH  
**Quiero** ver la comparativa del plan vs Ley Federal del Trabajo  
**Para** asegurar cumplimiento y comunicar beneficios

**Criterios de aceptación:**
- Tabla comparativa: Ley vs Plan vs Individual
- Indicador visual de "superior a ley"
- Exportar para comunicar a empleados

---

## 6. Gestión Documental

### 6.1 Subir Documento
**Como** usuario de RRHH  
**Quiero** subir documentos al expediente del empleado  
**Para** tener toda la información centralizada

**Criterios de aceptación:**
- Drag & drop o selector
- Múltiples archivos simultáneos
- Formatos: PDF, JPG, PNG, DOCX (configurable)
- Límite de tamaño: 10MB por archivo (configurable)
- Asignar categoría obligatoria
- Fecha de vencimiento (opcional)
- Notas/descripción

### 6.2 Categorías de Documentos
**Como** administrador  
**Quiero** configurar categorías de documentos por empresa  
**Para** organizar los expedientes según necesidades

**Categorías sugeridas:**
```
- Identificación (INE, pasaporte)
- CURP
- RFC / Constancia de situación fiscal
- Comprobante de domicilio
- Acta de nacimiento
- Contratos laborales
- IMSS (alta, constancias)
- INFONAVIT
- Nóminas
- Constancias laborales
- Certificados de cursos
- Evaluaciones de desempeño
- Otros
```

**Configuración por categoría:**
- Nombre
- Descripción
- ¿Requiere fecha de vencimiento?
- ¿Es obligatorio?
- Orden de visualización

### 6.3 Alertas de Vencimiento de Documentos
**Como** usuario de RRHH  
**Quiero** recibir alertas de documentos por vencer  
**Para** solicitar actualización a tiempo

**Criterios de aceptación:**
- Alerta configurable (30, 15, 7 días)
- Notificación en sistema y email
- Dashboard con documentos por vencer/vencidos

### 6.4 Visualización y Descarga
**Como** usuario de RRHH  
**Quiero** ver y descargar documentos del expediente  
**Para** consultar información sin salir del sistema

**Criterios de aceptación:**
- Vista previa en navegador (PDF, imágenes)
- Descarga individual
- Descarga masiva (ZIP del expediente completo)
- Filtros por categoría, fecha, estado

---

## 7. Calendario Laboral

### 7.1 Configurar Días Festivos
**Como** administrador  
**Quiero** configurar los días festivos oficiales  
**Para** que el sistema los considere en cálculos

**Días festivos oficiales México (precargados):**
```
- 1 de enero (Año Nuevo)
- Primer lunes de febrero (Constitución)
- Tercer lunes de marzo (Natalicio de Benito Juárez)
- 1 de mayo (Día del Trabajo)
- 16 de septiembre (Independencia)
- Tercer lunes de noviembre (Revolución)
- 1 de diciembre cada 6 años (Transmisión del Poder Ejecutivo)
- 25 de diciembre (Navidad)
```

**Funcionalidades:**
- Agregar días festivos adicionales por empresa
- Marcar días no laborables específicos
- Copiar configuración entre años

### 7.2 Vista de Calendario
**Como** usuario de RRHH  
**Quiero** ver el calendario laboral  
**Para** planificar y consultar disponibilidad

**Criterios de aceptación:**
- Vista mensual/anual
- Mostrar: festivos, vacaciones aprobadas, incapacidades
- Filtrar por empresa/departamento/empleado
- Código de colores por tipo de evento

---

## 8. Reportes y Dashboard

### 8.1 Dashboard Principal
**Como** usuario de RRHH  
**Quiero** ver un resumen ejecutivo  
**Para** tener visibilidad rápida del estado de RRHH

**Widgets:**
```
- Total empleados (por empresa y global)
- Empleados activos/baja este mes
- Contratos por vencer (próximos 30 días)
- Solicitudes de vacaciones pendientes
- Documentos por vencer
- Cumpleaños del mes
- Aniversarios laborales del mes
- Alertas activas
```

### 8.2 Reportes
**Como** usuario de RRHH  
**Quiero** generar reportes  
**Para** análisis y cumplimiento

**Reportes disponibles:**
```
EMPLEADOS
- Plantilla actual (por empresa/consolidado)
- Altas y bajas (periodo)
- Antigüedad promedio
- Rotación de personal

VACACIONES
- Saldo de vacaciones (todos los empleados)
- Vacaciones por vencer
- Histórico de vacaciones tomadas

CONTRATOS
- Contratos vigentes
- Contratos por vencer
- Histórico de renovaciones

DOCUMENTOS
- Expedientes incompletos
- Documentos por vencer/vencidos

PRESTACIONES
- Comparativa de planes
- Costo de prestaciones por empleado
```

**Formatos de exportación:**
- Excel (.xlsx)
- PDF
- Vista en pantalla con filtros

---

## 9. Portal de Autoservicio (Empleados)

### 9.1 Acceso de Empleado
**Como** empleado  
**Quiero** acceder a mi información  
**Para** consultar mis datos y hacer trámites

**Funcionalidades:**
```
- Ver mis datos personales
- Actualizar datos de contacto
- Ver mi antigüedad y prestaciones
- Consultar saldo de vacaciones
- Solicitar vacaciones
- Ver estado de solicitudes
- Descargar recibos de nómina
- Descargar constancias
- Ver mi contrato vigente
```

### 9.2 Actualización de Datos
**Como** empleado  
**Quiero** actualizar mis datos de contacto  
**Para** mantener mi información vigente

**Datos editables por empleado:**
- Teléfono personal
- Email personal
- Dirección
- Contacto de emergencia

**Datos NO editables (requieren RRHH):**
- Nombre, CURP, RFC
- Datos bancarios
- Datos laborales

---

## 10. Administración del Sistema

### 10.1 Gestión de Usuarios
**Como** administrador  
**Quiero** gestionar usuarios del sistema  
**Para** controlar accesos

**Roles:**
- Super Admin: todo el sistema
- Admin RRHH: gestión completa de empresas asignadas
- Empleado: solo autoservicio

### 10.2 Auditoría
**Como** administrador  
**Quiero** ver el log de actividades  
**Para** auditar cambios importantes

**Eventos auditados:**
- Login/logout
- Creación/edición/eliminación de registros
- Cambios en configuración
- Aprobaciones/rechazos

---

## Notas de Implementación

### Prioridad de Desarrollo

**P0 - MVP:**
- Multi-empresa básico
- Alta de empleados (con retroactivo)
- Cálculo de vacaciones
- Gestión de contratos básica

**P1 - Core:**
- Planes de prestaciones
- Gestión documental
- Calendario
- Dashboard básico

**P2 - Completo:**
- Portal autoservicio
- Reportes avanzados
- Alertas por email
- Auditoría

**P3 - Nice to have:**
- App móvil
- Integraciones (nómina, IMSS)
- Firma electrónica
