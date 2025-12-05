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
