/**
 * Types para perfil de usuario
 */

export interface UsuarioPerfil {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  nombre_completo: string;
  rol: 'administrador' | 'empleador' | 'empleado';
  rol_display: string;
  notificaciones_email: boolean;
  notificaciones_push: boolean;
  tema_oscuro: boolean;
  ultimo_acceso: string | null;
  fecha_registro: string | null;
  empleado?: {
    id: string;
    nombre_completo: string;
    puesto: string | null;
    departamento: string | null;
    empresa: string | null;
    fecha_ingreso: string | null;
  };
  empresas?: Array<{
    id: string;
    nombre: string;
  }>;
}

export interface ActualizarPerfilRequest {
  first_name?: string;
  last_name?: string;
  notificaciones_email?: boolean;
  notificaciones_push?: boolean;
  tema_oscuro?: boolean;
}

export interface CambiarPasswordRequest {
  password_actual: string;
  password_nuevo: string;
}
