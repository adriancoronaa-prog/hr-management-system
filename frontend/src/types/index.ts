// User types
export interface User {
  id: string;
  email: string;
  nombre: string;
  rol: "admin" | "empleador" | "rrhh" | "empleado";
  empresa?: Empresa;
  empleado?: Empleado;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}

// Empresa
export interface Empresa {
  id: string;
  rfc: string;
  razon_social: string;
  nombre_comercial?: string;
  logo?: string;
  estado?: string;
  empleados_count?: number;
  direccion?: string;
  telefono?: string;
  email?: string;
}

// Empleado
export interface Empleado {
  id: string;
  nombre: string;
  apellido_paterno: string;
  apellido_materno?: string;
  nombre_completo?: string;

  // Documentos mexicanos
  curp?: string;
  rfc?: string;
  nss_imss?: string;

  // Datos personales
  fecha_nacimiento?: string;
  genero?: string;
  estado_civil?: string;

  // Contacto
  telefono_personal?: string;
  email_personal?: string;
  email_corporativo?: string;

  // Dirección
  direccion_calle?: string;
  direccion_numero?: string;
  direccion_colonia?: string;
  direccion_cp?: string;
  direccion_municipio?: string;
  direccion_estado?: string;

  // Contacto emergencia
  emergencia_nombre?: string;
  emergencia_parentesco?: string;
  emergencia_telefono?: string;

  // Datos bancarios
  banco?: string;
  clabe?: string;

  // Datos laborales
  empresa: string;
  empresa_nombre?: string;
  puesto?: string;
  departamento?: string;
  fecha_ingreso: string;
  tipo_contrato?: "indefinido" | "temporal" | "obra" | "tiempo" | "capacitacion" | "prueba";
  jornada?: "diurna" | "nocturna" | "mixta";
  modalidad?: string;

  // Salario
  salario_diario?: number;
  salario_mensual?: number;

  // Jerarquía
  jefe_directo?: string;
  jefe_directo_nombre?: string;
  plan_prestaciones?: string;

  // Estado
  estado: "activo" | "baja" | "incapacidad";
  fecha_baja?: string;
  tipo_baja?: string;
  motivo_baja?: string;

  // Foto
  foto?: string;

  // Metadata
  antiguedad_anos?: number;
  created_at?: string;
  updated_at?: string;
}

// Opciones para formularios de empleado
export const GENERO_OPTIONS = [
  { value: "M", label: "Masculino" },
  { value: "F", label: "Femenino" },
  { value: "O", label: "Otro" },
];

export const ESTADO_CIVIL_OPTIONS = [
  { value: "soltero", label: "Soltero(a)" },
  { value: "casado", label: "Casado(a)" },
  { value: "divorciado", label: "Divorciado(a)" },
  { value: "viudo", label: "Viudo(a)" },
  { value: "union_libre", label: "Unión libre" },
];

export const TIPO_CONTRATO_OPTIONS = [
  { value: "indefinido", label: "Tiempo indefinido" },
  { value: "temporal", label: "Temporal" },
  { value: "obra", label: "Por obra determinada" },
  { value: "tiempo", label: "Por tiempo determinado" },
  { value: "capacitacion", label: "Capacitación inicial" },
  { value: "prueba", label: "Periodo de prueba" },
];

export const JORNADA_OPTIONS = [
  { value: "diurna", label: "Diurna" },
  { value: "nocturna", label: "Nocturna" },
  { value: "mixta", label: "Mixta" },
];

export const BANCOS_MEXICO = [
  { value: "BBVA", label: "BBVA México" },
  { value: "Santander", label: "Santander" },
  { value: "Banorte", label: "Banorte" },
  { value: "HSBC", label: "HSBC" },
  { value: "Scotiabank", label: "Scotiabank" },
  { value: "Citibanamex", label: "Citibanamex" },
  { value: "Inbursa", label: "Inbursa" },
  { value: "Azteca", label: "Banco Azteca" },
  { value: "BanCoppel", label: "BanCoppel" },
  { value: "Otro", label: "Otro" },
];

export const ESTADOS_MEXICO = [
  "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
  "Chiapas", "Chihuahua", "Ciudad de México", "Coahuila", "Colima",
  "Durango", "Estado de México", "Guanajuato", "Guerrero", "Hidalgo",
  "Jalisco", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca",
  "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa",
  "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas",
];

// Chat
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  archivo_nombre?: string;
  tipo_archivo?: string;
  accion?: ActionResponse;
}

export interface ActionResponse {
  success: boolean;
  mensaje?: string;
  error?: string;
  datos?: Record<string, unknown>;
  archivo?: {
    nombre: string;
    contenido_base64: string;
    tipo: string;
  };
}

export interface Conversation {
  id: string;
  titulo: string;
  created_at: string;
  updated_at: string;
  empleado_contexto?: Empleado;
  flujo_activo?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Dashboard metrics
export interface DashboardMetrics {
  empleados_activos: number;
  solicitudes_pendientes: number;
  nomina_periodo: number;
  proximos_vencimientos: number;
}

// Contrato
export interface Contrato {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  empresa_nombre?: string;

  // Tipo de contrato
  tipo_contrato: "indefinido" | "temporal" | "obra" | "tiempo" | "capacitacion" | "prueba";
  tipo_contrato_display?: string;

  // Fechas
  fecha_inicio: string;
  fecha_fin?: string | null;
  fecha_firma?: string;
  fecha_terminacion?: string;

  // Condiciones
  puesto?: string;
  departamento?: string;
  salario_mensual?: number;
  salario_diario?: number;
  jornada?: string;
  horario?: string;
  condiciones_especiales?: string;
  clausulas_adicionales?: string;

  // Estado
  estado: "vigente" | "vencido" | "renovado" | "cancelado" | "terminado";
  estado_display?: string;
  motivo_terminacion?: string;

  // Documento
  documento?: string;
  documento_url?: string;
  documento_firmado?: string;
  documento_firmado_url?: string;

  // Renovacion
  contrato_anterior?: string;
  numero_renovaciones?: number;

  // Calculados
  dias_para_vencer?: number | null;
  es_vigente?: boolean;
  esta_por_vencer?: boolean;

  // Metadata
  created_at?: string;
  updated_at?: string;
}

export const TIPO_CONTRATO_LARGO_OPTIONS = [
  { value: "indefinido", label: "Tiempo indefinido" },
  { value: "temporal", label: "Temporal" },
  { value: "obra", label: "Por obra determinada" },
  { value: "tiempo", label: "Por tiempo determinado" },
  { value: "capacitacion", label: "Capacitacion inicial" },
  { value: "prueba", label: "Periodo de prueba" },
];

export const ESTADO_CONTRATO_OPTIONS = [
  { value: "vigente", label: "Vigente" },
  { value: "vencido", label: "Vencido" },
  { value: "renovado", label: "Renovado" },
  { value: "cancelado", label: "Cancelado" },
  { value: "terminado", label: "Terminado" },
];

// Navigation
export interface NavItem {
  title: string;
  href: string;
  icon: string;
  badge?: number;
  children?: NavItem[];
}

// Vacaciones
export interface SolicitudVacaciones {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  empleado_puesto?: string;
  empresa_nombre?: string;

  fecha_inicio: string;
  fecha_fin: string;
  dias_solicitados: number;

  estado: "pendiente" | "aprobada" | "rechazada" | "cancelada";
  estado_display?: string;

  aprobado_por?: string;
  aprobador_nombre?: string;
  fecha_aprobacion?: string;

  comentarios?: string;
  notas?: string;

  puede_aprobar?: boolean;

  created_at?: string;
  updated_at?: string;
}

export interface ResumenVacaciones {
  empleado_id: string;
  empleado_nombre: string;
  fecha_ingreso: string;
  antiguedad_anios: number;
  dias_correspondientes_anio_actual: number;
  dias_tomados_anio_actual: number;
  dias_disponibles: number;
  dias_pendientes_anteriores: number;
  total_disponible: number;
  solicitudes_pendientes: number;
}

export interface EstadisticasVacaciones {
  pendientes: number;
  aprobadas: number;
  rechazadas: number;
  proximas_7_dias: number;
}

export const ESTADO_VACACIONES_OPTIONS = [
  { value: "pendiente", label: "Pendiente", color: "amber" },
  { value: "aprobada", label: "Aprobada", color: "green" },
  { value: "rechazada", label: "Rechazada", color: "red" },
  { value: "cancelada", label: "Cancelada", color: "warm" },
];

// Nomina
export interface PeriodoNomina {
  id: string;
  empresa: string;
  tipo_periodo: "semanal" | "quincenal" | "mensual";
  tipo_periodo_display?: string;
  numero_periodo: number;
  año: number;
  fecha_inicio: string;
  fecha_fin: string;
  fecha_pago?: string;
  estado: "borrador" | "calculado" | "autorizado" | "pagado" | "timbrado" | "cancelado";
  estado_display?: string;

  // Totales
  total_percepciones?: number;
  total_deducciones?: number;
  total_neto?: number;
  total_empleados?: number;

  // Auditoria
  fecha_calculo?: string;
  calculado_por?: string;
  fecha_autorizacion?: string;
  autorizado_por?: string;

  created_at?: string;
  updated_at?: string;
}

export interface ReciboNomina {
  id: string;
  periodo: string;
  periodo_info?: {
    tipo_periodo_display: string;
    numero_periodo: number;
    año: number;
    fecha_inicio: string;
    fecha_fin: string;
  };
  empleado: string;
  empleado_nombre?: string;
  empleado_puesto?: string;

  // Salario
  salario_diario: number;
  salario_base_cotizacion: number;
  dias_trabajados: number;
  dias_pagados?: number;

  // Totales
  total_percepciones: number;
  total_percepciones_gravadas?: number;
  total_percepciones_exentas?: number;
  total_deducciones: number;
  neto_a_pagar: number;

  // ISR
  base_gravable_isr?: number;
  isr_antes_subsidio?: number;
  subsidio_aplicado?: number;
  isr_retenido?: number;

  // IMSS
  cuota_imss_obrera?: number;
  cuota_imss_patronal?: number;

  // CFDI
  uuid_fiscal?: string;
  fecha_timbrado?: string;
  xml_cfdi?: string;
  pdf_cfdi?: string;

  estado: "borrador" | "calculado" | "timbrado" | "cancelado";
  estado_display?: string;

  created_at?: string;
}

export interface DetalleReciboNomina {
  id: string;
  recibo: string;
  concepto: string;
  concepto_nombre?: string;
  concepto_codigo?: string;
  tipo: "percepcion" | "deduccion" | "otro_pago";
  cantidad?: number;
  valor_unitario?: number;
  importe_gravado?: number;
  importe_exento?: number;
  importe_total: number;
}

export interface IncidenciaNomina {
  id: string;
  empleado: string;
  empleado_nombre?: string;
  periodo?: string;
  periodo_info?: string;
  tipo: "falta" | "incapacidad" | "vacaciones" | "permiso_cg" | "permiso_sg" | "horas_extra" | "bono" | "comision" | "descuento" | "prestamo" | "otro";
  tipo_display?: string;
  fecha_inicio: string;
  fecha_fin?: string;
  cantidad?: number;
  monto?: number;
  descripcion?: string;
  estado: "pendiente" | "aplicada" | "cancelada";
  created_at?: string;
}

export interface ResumenNomina {
  periodo: PeriodoNomina;
  total_empleados: number;
  total_percepciones: number;
  total_deducciones: number;
  total_neto: number;
  desglose_isr: number;
  desglose_imss: number;
  recibos: ReciboNomina[];
}

export const TIPO_PERIODO_OPTIONS = [
  { value: "semanal", label: "Semanal" },
  { value: "quincenal", label: "Quincenal" },
  { value: "mensual", label: "Mensual" },
];

export const ESTADO_PERIODO_OPTIONS = [
  { value: "borrador", label: "Borrador", color: "warm" },
  { value: "calculado", label: "Calculado", color: "amber" },
  { value: "autorizado", label: "Autorizado", color: "blue" },
  { value: "pagado", label: "Pagado", color: "green" },
  { value: "timbrado", label: "Timbrado", color: "green" },
  { value: "cancelado", label: "Cancelado", color: "red" },
];

export const TIPO_INCIDENCIA_OPTIONS = [
  { value: "falta", label: "Falta", tipo: "deduccion" },
  { value: "incapacidad", label: "Incapacidad", tipo: "deduccion" },
  { value: "vacaciones", label: "Vacaciones", tipo: "neutral" },
  { value: "permiso_cg", label: "Permiso con goce", tipo: "neutral" },
  { value: "permiso_sg", label: "Permiso sin goce", tipo: "deduccion" },
  { value: "horas_extra", label: "Horas extra", tipo: "percepcion" },
  { value: "bono", label: "Bono", tipo: "percepcion" },
  { value: "comision", label: "Comision", tipo: "percepcion" },
  { value: "descuento", label: "Descuento", tipo: "deduccion" },
  { value: "prestamo", label: "Prestamo", tipo: "deduccion" },
  { value: "otro", label: "Otro", tipo: "neutral" },
];

// Reportes - Dashboard Empresa
export interface DashboardEmpresa {
  empresa: {
    id: string;
    razon_social: string;
    nombre_comercial: string;
    rfc: string;
    regimen_fiscal?: string;
  };
  empleados: {
    total: number;
    activos: number;
    inactivos: number;
    bajas: number;
    antiguedad_promedio_anos: number;
    salario_diario_promedio: number;
    salario_mensual_promedio: number;
    nomina_mensual_estimada: number;
    por_departamento: Array<{ departamento: string; total: number }>;
  };
  nomina: {
    periodos_procesados_ano: number;
    total_percepciones_ano: number;
    total_deducciones_ano: number;
    total_neto_pagado_ano: number;
    ultimo_periodo: {
      fecha_pago: string | null;
      total_neto: number;
      empleados: number;
    } | null;
  };
  vacaciones: {
    dias_pendientes_total: number;
    dias_tomados_ano: number;
    pasivo_vacaciones: number;
  };
  costos_proyectados: {
    aguinaldo_proyectado: number;
    prima_vacacional_proyectada: number;
    nomina_mensual: number;
    costo_anual_estimado: number;
  };
  alertas: Array<{
    tipo: string;
    nivel: "warning" | "error" | "info";
    empleado: string;
    mensaje: string;
  }>;
  fecha_generacion: string;
}

// Datos para graficos
export interface DatosMensuales {
  mes: string;
  valor: number;
}

export interface EmpleadosPorDepartamento {
  departamento: string;
  cantidad: number;
  porcentaje: number;
}

export interface ContratosPorTipo {
  tipo: string;
  tipo_display: string;
  cantidad: number;
  porcentaje: number;
}

// Resumen de vacaciones
export interface ResumenVacacionesReporte {
  total_empleados: number;
  dias_otorgados_ano: number;
  dias_tomados_ano: number;
  dias_pendientes: number;
  solicitudes_pendientes: number;
  solicitudes_aprobadas: number;
  solicitudes_rechazadas: number;
  por_empleado: Array<{
    empleado_id: string;
    empleado_nombre: string;
    antiguedad_anos: number;
    dias_correspondientes: number;
    dias_tomados: number;
    dias_pendientes: number;
  }>;
}
