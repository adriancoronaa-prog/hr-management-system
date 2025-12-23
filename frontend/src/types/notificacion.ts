/**
 * Types para notificaciones
 */

export interface Notificacion {
  id: string;
  tipo: string;
  prioridad: string;
  titulo: string;
  mensaje: string;
  estado: string;
  leida: boolean;
  url_destino?: string | null;
  created_at: string;
}

export interface NotificacionCount {
  count: number;
}
