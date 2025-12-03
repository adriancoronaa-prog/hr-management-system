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
}

// Empleado
export interface Empleado {
  id: string;
  nombre: string;
  apellido_paterno: string;
  apellido_materno?: string;
  nombre_completo: string;
  email_corporativo?: string;
  email_personal?: string;
  puesto?: string;
  departamento?: string;
  fecha_ingreso: string;
  estado: "activo" | "baja" | "incapacidad";
  salario_diario?: number;
  salario_mensual?: number;
  foto?: string;
  empresa: Empresa;
}

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

// Navigation
export interface NavItem {
  title: string;
  href: string;
  icon: string;
  badge?: number;
  children?: NavItem[];
}
