# Modelo de Datos - RRHH Multi-empresa

## Diagrama Entidad-Relación (Simplificado)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────────┐
│   Empresa   │──────<│  Empleado   │>──────│  PlanPrestaciones   │
└─────────────┘       └─────────────┘       └─────────────────────┘
      │                     │                         │
      │                     │                         │
      ▼                     ▼                         ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────────────┐
│ Categoria   │       │  Contrato   │       │ PlanPrestacionDet.  │
│ Documento   │       └─────────────┘       └─────────────────────┘
└─────────────┘             │                         │
      │                     │                         │
      ▼                     ▼                         ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────────────┐
│ Documento   │       │ Periodo     │       │ PrestacionAdicional │
│ Empleado    │       │ Vacacional  │       └─────────────────────┘
└─────────────┘       └─────────────┘
                            │
                            ▼
                      ┌─────────────┐
                      │ Solicitud   │
                      │ Vacaciones  │
                      └─────────────┘
```

---

## Tablas del Sistema

### 1. Empresas

```sql
-- Empresas registradas en el sistema
CREATE TABLE empresas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Datos fiscales
    rfc VARCHAR(13) UNIQUE NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    regimen_fiscal VARCHAR(100),
    
    -- Domicilio fiscal
    calle VARCHAR(255),
    numero_exterior VARCHAR(20),
    numero_interior VARCHAR(20),
    colonia VARCHAR(100),
    codigo_postal VARCHAR(5),
    municipio VARCHAR(100),
    estado VARCHAR(50),
    
    -- Contacto
    representante_legal VARCHAR(255),
    telefono VARCHAR(20),
    email VARCHAR(255),
    
    -- Configuración
    logo_url TEXT,
    activa BOOLEAN DEFAULT TRUE,
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id)
);

CREATE INDEX idx_empresas_rfc ON empresas(rfc);
CREATE INDEX idx_empresas_activa ON empresas(activa);
```

### 2. Empleados

```sql
-- Empleados de todas las empresas
CREATE TABLE empleados (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    plan_prestaciones_id UUID REFERENCES planes_prestaciones(id),
    
    -- Datos personales
    nombre VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    curp VARCHAR(18) UNIQUE,
    rfc VARCHAR(13),
    nss_imss VARCHAR(11),
    fecha_nacimiento DATE,
    genero VARCHAR(20),
    estado_civil VARCHAR(30),
    nacionalidad VARCHAR(50) DEFAULT 'Mexicana',
    lugar_nacimiento VARCHAR(100),
    
    -- Contacto
    telefono_personal VARCHAR(20),
    telefono_casa VARCHAR(20),
    email_personal VARCHAR(255),
    email_corporativo VARCHAR(255),
    
    -- Dirección
    direccion_calle VARCHAR(255),
    direccion_numero VARCHAR(20),
    direccion_colonia VARCHAR(100),
    direccion_cp VARCHAR(5),
    direccion_municipio VARCHAR(100),
    direccion_estado VARCHAR(50),
    
    -- Contacto de emergencia
    emergencia_nombre VARCHAR(255),
    emergencia_parentesco VARCHAR(50),
    emergencia_telefono1 VARCHAR(20),
    emergencia_telefono2 VARCHAR(20),
    
    -- Datos bancarios (cifrados en producción)
    banco VARCHAR(100),
    clabe VARCHAR(18),
    numero_cuenta VARCHAR(20),
    
    -- Datos laborales
    fecha_ingreso DATE NOT NULL,  -- ← PUEDE SER RETROACTIVA
    fecha_ingreso_sistema TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    puesto VARCHAR(100),
    departamento VARCHAR(100),
    jefe_directo_id UUID REFERENCES empleados(id),
    tipo_contrato VARCHAR(50),
    jornada VARCHAR(20), -- diurna, nocturna, mixta
    horario_entrada TIME,
    horario_salida TIME,
    modalidad VARCHAR(20), -- presencial, remoto, hibrido
    centro_trabajo VARCHAR(255),
    
    -- Datos salariales
    salario_diario DECIMAL(12,2),
    salario_mensual DECIMAL(12,2) GENERATED ALWAYS AS (salario_diario * 30) STORED,
    
    -- Estado
    estado VARCHAR(20) DEFAULT 'activo', -- activo, baja, incapacidad
    fecha_baja DATE,
    motivo_baja TEXT,
    tipo_baja VARCHAR(50), -- renuncia, despido, termino_contrato
    
    -- Foto
    foto_url TEXT,
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id)
);

CREATE INDEX idx_empleados_empresa ON empleados(empresa_id);
CREATE INDEX idx_empleados_estado ON empleados(estado);
CREATE INDEX idx_empleados_fecha_ingreso ON empleados(fecha_ingreso);
CREATE INDEX idx_empleados_curp ON empleados(curp);
```

### 3. Contratos

```sql
-- Contratos laborales
CREATE TABLE contratos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empleado_id UUID NOT NULL REFERENCES empleados(id),
    
    -- Datos del contrato
    tipo_contrato VARCHAR(50) NOT NULL,
    -- indefinido, temporal, obra_determinada, tiempo_determinado, 
    -- capacitacion_inicial, periodo_prueba
    
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE, -- NULL para indefinido
    
    puesto VARCHAR(100),
    salario_diario DECIMAL(12,2),
    jornada VARCHAR(20),
    horario_entrada TIME,
    horario_salida TIME,
    condiciones_especiales TEXT,
    
    -- Documento
    documento_url TEXT,
    
    -- Estado
    estado VARCHAR(20) DEFAULT 'vigente', -- vigente, vencido, renovado, cancelado
    
    -- Renovación
    contrato_anterior_id UUID REFERENCES contratos(id),
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id)
);

CREATE INDEX idx_contratos_empleado ON contratos(empleado_id);
CREATE INDEX idx_contratos_estado ON contratos(estado);
CREATE INDEX idx_contratos_fecha_fin ON contratos(fecha_fin);
```

### 4. Planes de Prestaciones

```sql
-- Planes de prestaciones por empresa
CREATE TABLE planes_prestaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    
    nombre VARCHAR(100) NOT NULL, -- "Plan Estándar", "Plan Ejecutivo"
    descripcion TEXT,
    es_default BOOLEAN DEFAULT FALSE, -- Plan por defecto para nuevos empleados
    activo BOOLEAN DEFAULT TRUE,
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id)
);

CREATE INDEX idx_planes_empresa ON planes_prestaciones(empresa_id);
CREATE UNIQUE INDEX idx_planes_default ON planes_prestaciones(empresa_id) 
    WHERE es_default = TRUE AND activo = TRUE;
```

### 5. Catálogo de Tipos de Prestación

```sql
-- Catálogo de tipos de prestación (de ley y adicionales)
CREATE TABLE tipos_prestacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    codigo VARCHAR(50) UNIQUE NOT NULL,
    -- VACACIONES, PRIMA_VACACIONAL, AGUINALDO, PRIMA_DOMINICAL, etc.
    
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    es_de_ley BOOLEAN DEFAULT FALSE,
    tipo_valor VARCHAR(20), -- DIAS, PORCENTAJE, MONTO, TABLA, TEXTO
    valor_ley TEXT, -- Valor según LFT (puede ser JSON para tablas)
    
    activo BOOLEAN DEFAULT TRUE,
    orden INT DEFAULT 0
);

-- Datos iniciales
INSERT INTO tipos_prestacion (codigo, nombre, es_de_ley, tipo_valor, valor_ley) VALUES
('VACACIONES', 'Vacaciones', TRUE, 'TABLA', 
 '{"1":12,"2":14,"3":16,"4":18,"5":20,"6":22,"11":24,"16":26,"21":28,"26":30,"31":32}'),
('PRIMA_VACACIONAL', 'Prima Vacacional', TRUE, 'PORCENTAJE', '25'),
('AGUINALDO', 'Aguinaldo', TRUE, 'DIAS', '15'),
('PRIMA_DOMINICAL', 'Prima Dominical', TRUE, 'PORCENTAJE', '25');
```

### 6. Detalle del Plan de Prestaciones

```sql
-- Configuración de cada prestación en un plan
CREATE TABLE plan_prestacion_detalle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES planes_prestaciones(id),
    tipo_prestacion_id UUID NOT NULL REFERENCES tipos_prestacion(id),
    
    -- Valor personalizado (superior o igual a ley)
    valor_personalizado TEXT, -- Puede ser número, JSON para tablas, etc.
    
    -- Para vacaciones: tabla personalizada
    -- Ejemplo: {"1":15,"2":17,"3":19,"4":21,"5":23,"6":25,...}
    configuracion_json JSONB,
    
    notas TEXT,
    
    UNIQUE(plan_id, tipo_prestacion_id)
);

CREATE INDEX idx_plan_detalle_plan ON plan_prestacion_detalle(plan_id);
```

### 7. Prestaciones Adicionales

```sql
-- Prestaciones adicionales (no de ley) configuradas en un plan
CREATE TABLE prestaciones_adicionales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES planes_prestaciones(id),
    
    nombre VARCHAR(100) NOT NULL, -- "Vales de despensa", "SGMM", etc.
    descripcion TEXT,
    
    tipo_valor VARCHAR(20), -- MONTO_FIJO, PORCENTAJE_SALARIO, TEXTO
    valor VARCHAR(100), -- "2000", "10", "Cobertura básica"
    periodicidad VARCHAR(20), -- MENSUAL, ANUAL, UNICA
    
    -- Configuración adicional
    configuracion_json JSONB,
    
    activo BOOLEAN DEFAULT TRUE,
    orden INT DEFAULT 0
);

CREATE INDEX idx_prestaciones_adicionales_plan ON prestaciones_adicionales(plan_id);
```

### 8. Ajustes Individuales por Empleado

```sql
-- Ajustes individuales que sobrescriben el plan
CREATE TABLE ajustes_individuales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empleado_id UUID NOT NULL REFERENCES empleados(id),
    
    -- Puede ser ajuste a prestación de ley o adicional
    tipo_prestacion_id UUID REFERENCES tipos_prestacion(id),
    prestacion_adicional_id UUID REFERENCES prestaciones_adicionales(id),
    
    -- Tipo de ajuste
    tipo_ajuste VARCHAR(20), -- REEMPLAZA, SUMA, RESTA
    valor_ajuste TEXT,
    
    motivo TEXT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE, -- NULL = permanente
    
    aprobado_por UUID REFERENCES usuarios(id),
    fecha_aprobacion TIMESTAMP,
    
    activo BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id),
    
    -- Al menos uno debe estar presente
    CONSTRAINT chk_tipo_prestacion CHECK (
        tipo_prestacion_id IS NOT NULL OR prestacion_adicional_id IS NOT NULL
    )
);

CREATE INDEX idx_ajustes_empleado ON ajustes_individuales(empleado_id);
```

### 9. Periodos Vacacionales

```sql
-- Periodos vacacionales generados por empleado
CREATE TABLE periodos_vacacionales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empleado_id UUID NOT NULL REFERENCES empleados(id),
    
    numero_periodo INT NOT NULL, -- 1, 2, 3, ...
    fecha_inicio_periodo DATE NOT NULL, -- Aniversario de inicio
    fecha_fin_periodo DATE NOT NULL, -- Un día antes del siguiente aniversario
    
    dias_derecho INT NOT NULL, -- Días que le corresponden según plan
    dias_tomados INT DEFAULT 0,
    dias_pendientes INT GENERATED ALWAYS AS (dias_derecho - dias_tomados) STORED,
    
    -- Vencimiento (6 meses después del aniversario según LFT Art. 81)
    fecha_vencimiento DATE,
    
    -- Para registros de alta retroactiva
    es_historico BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(empleado_id, numero_periodo)
);

CREATE INDEX idx_periodos_empleado ON periodos_vacacionales(empleado_id);
CREATE INDEX idx_periodos_vencimiento ON periodos_vacacionales(fecha_vencimiento);
```

### 10. Solicitudes de Vacaciones

```sql
-- Solicitudes de vacaciones
CREATE TABLE solicitudes_vacaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empleado_id UUID NOT NULL REFERENCES empleados(id),
    periodo_vacacional_id UUID REFERENCES periodos_vacacionales(id),
    
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dias_solicitados INT NOT NULL,
    
    -- Para registros históricos (alta retroactiva)
    es_historico BOOLEAN DEFAULT FALSE,
    
    estado VARCHAR(20) DEFAULT 'pendiente',
    -- pendiente, aprobada, rechazada, cancelada
    
    -- Aprobación
    aprobado_por UUID REFERENCES usuarios(id),
    fecha_aprobacion TIMESTAMP,
    comentarios_aprobacion TEXT,
    
    -- Datos adicionales
    sustituto_id UUID REFERENCES empleados(id),
    notas TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id)
);

CREATE INDEX idx_solicitudes_empleado ON solicitudes_vacaciones(empleado_id);
CREATE INDEX idx_solicitudes_estado ON solicitudes_vacaciones(estado);
CREATE INDEX idx_solicitudes_fechas ON solicitudes_vacaciones(fecha_inicio, fecha_fin);
```

### 11. Categorías de Documentos

```sql
-- Categorías de documentos configurables por empresa
CREATE TABLE categorias_documento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID REFERENCES empresas(id), -- NULL = categoría global
    
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    
    requiere_vencimiento BOOLEAN DEFAULT FALSE,
    es_obligatorio BOOLEAN DEFAULT FALSE,
    
    activo BOOLEAN DEFAULT TRUE,
    orden INT DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categorias_empresa ON categorias_documento(empresa_id);

-- Categorías por defecto (globales)
INSERT INTO categorias_documento (nombre, requiere_vencimiento, es_obligatorio, orden) VALUES
('Identificación oficial', TRUE, TRUE, 1),
('CURP', FALSE, TRUE, 2),
('RFC / Constancia fiscal', FALSE, TRUE, 3),
('Comprobante de domicilio', TRUE, FALSE, 4),
('Acta de nacimiento', FALSE, FALSE, 5),
('Contratos laborales', FALSE, TRUE, 6),
('IMSS', FALSE, FALSE, 7),
('Nóminas', FALSE, FALSE, 8),
('Constancias y certificados', TRUE, FALSE, 9),
('Otros', FALSE, FALSE, 100);
```

### 12. Documentos de Empleados

```sql
-- Documentos del expediente del empleado
CREATE TABLE documentos_empleado (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empleado_id UUID NOT NULL REFERENCES empleados(id),
    categoria_id UUID NOT NULL REFERENCES categorias_documento(id),
    
    nombre_archivo VARCHAR(255) NOT NULL,
    nombre_original VARCHAR(255),
    archivo_url TEXT NOT NULL, -- URL en S3 o almacenamiento
    tipo_mime VARCHAR(100),
    tamaño_bytes BIGINT,
    
    fecha_vencimiento DATE,
    notas TEXT,
    
    -- Versionado
    version INT DEFAULT 1,
    documento_padre_id UUID REFERENCES documentos_empleado(id),
    
    activo BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id)
);

CREATE INDEX idx_documentos_empleado ON documentos_empleado(empleado_id);
CREATE INDEX idx_documentos_categoria ON documentos_empleado(categoria_id);
CREATE INDEX idx_documentos_vencimiento ON documentos_empleado(fecha_vencimiento) 
    WHERE fecha_vencimiento IS NOT NULL;
```

### 13. Días Festivos

```sql
-- Días festivos por año y empresa
CREATE TABLE dias_festivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID REFERENCES empresas(id), -- NULL = aplica a todas
    
    fecha DATE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    es_oficial BOOLEAN DEFAULT TRUE, -- Día oficial LFT vs adicional empresa
    
    activo BOOLEAN DEFAULT TRUE,
    
    UNIQUE(empresa_id, fecha)
);

CREATE INDEX idx_festivos_fecha ON dias_festivos(fecha);
CREATE INDEX idx_festivos_empresa ON dias_festivos(empresa_id);
```

### 14. Usuarios del Sistema

```sql
-- Usuarios del sistema
CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    nombre VARCHAR(100),
    apellidos VARCHAR(100),
    
    rol VARCHAR(20) NOT NULL, -- super_admin, admin_rrhh, empleado
    
    -- Si es empleado, vincular
    empleado_id UUID REFERENCES empleados(id),
    
    -- Empresas a las que tiene acceso (para admin_rrhh)
    -- Se maneja en tabla separada
    
    activo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);
```

### 15. Acceso de Usuarios a Empresas

```sql
-- Qué empresas puede ver cada usuario
CREATE TABLE usuario_empresa (
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    empresa_id UUID NOT NULL REFERENCES empresas(id),
    
    PRIMARY KEY (usuario_id, empresa_id)
);
```

### 16. Historial de Cambios Salariales

```sql
-- Histórico de cambios de salario
CREATE TABLE historial_salarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empleado_id UUID NOT NULL REFERENCES empleados(id),
    
    salario_anterior DECIMAL(12,2),
    salario_nuevo DECIMAL(12,2) NOT NULL,
    fecha_cambio DATE NOT NULL,
    motivo TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES usuarios(id)
);

CREATE INDEX idx_historial_salarios_empleado ON historial_salarios(empleado_id);
```

### 17. Log de Auditoría

```sql
-- Log de auditoría general
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    usuario_id UUID REFERENCES usuarios(id),
    empresa_id UUID REFERENCES empresas(id),
    
    accion VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.
    tabla_afectada VARCHAR(100),
    registro_id UUID,
    
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_usuario ON audit_log(usuario_id);
CREATE INDEX idx_audit_fecha ON audit_log(created_at);
CREATE INDEX idx_audit_tabla ON audit_log(tabla_afectada);
```

---

## Funciones y Triggers

### Calcular Antigüedad

```sql
-- Función para calcular antigüedad
CREATE OR REPLACE FUNCTION calcular_antiguedad(fecha_ingreso DATE)
RETURNS TABLE(anos INT, meses INT, dias INT) AS $$
DECLARE
    diff INTERVAL;
BEGIN
    diff := age(CURRENT_DATE, fecha_ingreso);
    anos := EXTRACT(YEAR FROM diff);
    meses := EXTRACT(MONTH FROM diff);
    dias := EXTRACT(DAY FROM diff);
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;
```

### Calcular Días de Vacaciones según Plan

```sql
-- Función para obtener días de vacaciones según antigüedad y plan
CREATE OR REPLACE FUNCTION obtener_dias_vacaciones(
    p_plan_id UUID,
    p_ano_antiguedad INT
) RETURNS INT AS $$
DECLARE
    v_config JSONB;
    v_dias INT;
    v_key TEXT;
BEGIN
    -- Obtener configuración del plan
    SELECT configuracion_json INTO v_config
    FROM plan_prestacion_detalle pd
    JOIN tipos_prestacion tp ON pd.tipo_prestacion_id = tp.id
    WHERE pd.plan_id = p_plan_id AND tp.codigo = 'VACACIONES';
    
    -- Si no hay config, usar ley
    IF v_config IS NULL THEN
        SELECT valor_ley::JSONB INTO v_config
        FROM tipos_prestacion WHERE codigo = 'VACACIONES';
    END IF;
    
    -- Buscar el valor correspondiente al año
    -- Las claves son: 1,2,3,4,5,6,11,16,21,26,31 (rangos)
    v_dias := 12; -- Mínimo por defecto
    
    FOR v_key IN SELECT jsonb_object_keys(v_config) ORDER BY (jsonb_object_keys)::INT
    LOOP
        IF p_ano_antiguedad >= v_key::INT THEN
            v_dias := (v_config->>v_key)::INT;
        END IF;
    END LOOP;
    
    RETURN v_dias;
END;
$$ LANGUAGE plpgsql;
```

### Trigger para Generar Periodos Vacacionales

```sql
-- Trigger al crear/actualizar empleado para generar periodos
CREATE OR REPLACE FUNCTION generar_periodos_vacacionales()
RETURNS TRIGGER AS $$
DECLARE
    v_anos_antiguedad INT;
    v_fecha_inicio DATE;
    v_fecha_fin DATE;
    v_dias INT;
    i INT;
BEGIN
    -- Calcular años de antigüedad
    v_anos_antiguedad := EXTRACT(YEAR FROM age(CURRENT_DATE, NEW.fecha_ingreso));
    
    -- Generar periodo para cada año
    FOR i IN 1..v_anos_antiguedad + 1 LOOP
        v_fecha_inicio := NEW.fecha_ingreso + ((i-1) * INTERVAL '1 year');
        v_fecha_fin := NEW.fecha_ingreso + (i * INTERVAL '1 year') - INTERVAL '1 day';
        
        -- Solo si el periodo ya inició
        IF v_fecha_inicio <= CURRENT_DATE THEN
            v_dias := obtener_dias_vacaciones(NEW.plan_prestaciones_id, i);
            
            INSERT INTO periodos_vacacionales (
                empleado_id, numero_periodo, fecha_inicio_periodo, 
                fecha_fin_periodo, dias_derecho, fecha_vencimiento
            ) VALUES (
                NEW.id, i, v_fecha_inicio, v_fecha_fin, v_dias,
                v_fecha_inicio + INTERVAL '18 months' -- 6 meses después de generar
            )
            ON CONFLICT (empleado_id, numero_periodo) DO NOTHING;
        END IF;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_generar_periodos
AFTER INSERT OR UPDATE OF fecha_ingreso, plan_prestaciones_id ON empleados
FOR EACH ROW EXECUTE FUNCTION generar_periodos_vacacionales();
```

### Trigger de Auditoría

```sql
-- Trigger genérico de auditoría
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (tabla_afectada, registro_id, accion, datos_anteriores)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (tabla_afectada, registro_id, accion, datos_anteriores, datos_nuevos)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (tabla_afectada, registro_id, accion, datos_nuevos)
        VALUES (TG_TABLE_NAME, NEW.id, 'CREATE', to_jsonb(NEW));
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Aplicar a tablas principales
CREATE TRIGGER audit_empleados AFTER INSERT OR UPDATE OR DELETE ON empleados
FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER audit_contratos AFTER INSERT OR UPDATE OR DELETE ON contratos
FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER audit_solicitudes_vacaciones AFTER INSERT OR UPDATE OR DELETE ON solicitudes_vacaciones
FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

---

## Vistas Útiles

### Vista de Empleados con Antigüedad

```sql
CREATE VIEW v_empleados_antiguedad AS
SELECT 
    e.*,
    emp.razon_social AS empresa_nombre,
    (calcular_antiguedad(e.fecha_ingreso)).anos AS antiguedad_anos,
    (calcular_antiguedad(e.fecha_ingreso)).meses AS antiguedad_meses,
    (calcular_antiguedad(e.fecha_ingreso)).dias AS antiguedad_dias,
    e.fecha_ingreso + ((EXTRACT(YEAR FROM age(CURRENT_DATE, e.fecha_ingreso))::INT + 1) * INTERVAL '1 year') AS proximo_aniversario
FROM empleados e
JOIN empresas emp ON e.empresa_id = emp.id
WHERE e.estado = 'activo';
```

### Vista de Saldo de Vacaciones

```sql
CREATE VIEW v_saldo_vacaciones AS
SELECT 
    e.id AS empleado_id,
    e.nombre || ' ' || e.apellido_paterno AS empleado_nombre,
    e.empresa_id,
    SUM(pv.dias_derecho) AS total_dias_derecho,
    SUM(pv.dias_tomados) AS total_dias_tomados,
    SUM(pv.dias_pendientes) AS saldo_disponible,
    MIN(CASE WHEN pv.dias_pendientes > 0 THEN pv.fecha_vencimiento END) AS proximo_vencimiento
FROM empleados e
JOIN periodos_vacacionales pv ON e.id = pv.empleado_id
WHERE e.estado = 'activo'
GROUP BY e.id, e.nombre, e.apellido_paterno, e.empresa_id;
```

### Vista de Contratos por Vencer

```sql
CREATE VIEW v_contratos_por_vencer AS
SELECT 
    c.*,
    e.nombre || ' ' || e.apellido_paterno AS empleado_nombre,
    e.empresa_id,
    emp.razon_social AS empresa_nombre,
    c.fecha_fin - CURRENT_DATE AS dias_para_vencer
FROM contratos c
JOIN empleados e ON c.empleado_id = e.id
JOIN empresas emp ON e.empresa_id = emp.id
WHERE c.estado = 'vigente' 
  AND c.fecha_fin IS NOT NULL
  AND c.fecha_fin <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY c.fecha_fin;
```

---

## Índices Adicionales para Performance

```sql
-- Búsquedas frecuentes
CREATE INDEX idx_empleados_nombre ON empleados(nombre, apellido_paterno);
CREATE INDEX idx_empleados_activos_empresa ON empleados(empresa_id) WHERE estado = 'activo';

-- Consultas de calendario
CREATE INDEX idx_solicitudes_fechas_estado ON solicitudes_vacaciones(fecha_inicio, fecha_fin) 
    WHERE estado = 'aprobada';

-- Búsquedas de documentos
CREATE INDEX idx_documentos_activos ON documentos_empleado(empleado_id) WHERE activo = TRUE;
```
