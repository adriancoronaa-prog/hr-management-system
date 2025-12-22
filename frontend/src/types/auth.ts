// Auth types
import type { Empresa } from "./empresa";
import type { Empleado } from "./empleado";

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
