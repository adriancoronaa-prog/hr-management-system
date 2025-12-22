// Chat types
import type { Empleado } from "./empleado";

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
