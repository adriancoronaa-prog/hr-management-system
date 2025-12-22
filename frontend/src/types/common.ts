// Common/shared types

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
