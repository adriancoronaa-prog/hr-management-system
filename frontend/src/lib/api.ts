import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token and empresa_id
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const authStorage = localStorage.getItem("auth-storage");
      if (authStorage) {
        try {
          const { state } = JSON.parse(authStorage);
          if (state?.token) {
            config.headers.Authorization = `Bearer ${state.token}`;
          }
          // Agregar empresa_id como header
          if (state?.empresaActual?.id) {
            config.headers["X-Empresa-ID"] = state.empresaActual.id;
          }
        } catch {
          // Invalid storage format
        }
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (typeof window !== "undefined") {
        const authStorage = localStorage.getItem("auth-storage");
        if (authStorage) {
          try {
            const { state } = JSON.parse(authStorage);
            if (state?.refreshToken) {
              const response = await axios.post(
                `${API_URL}/api/usuarios/token/refresh/`,
                { refresh: state.refreshToken }
              );

              const newToken = response.data.access;

              // Update storage
              const newState = {
                ...state,
                token: newToken,
              };
              localStorage.setItem(
                "auth-storage",
                JSON.stringify({ state: newState })
              );

              // Retry original request
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return api(originalRequest);
            }
          } catch {
            // Refresh failed, clear auth
            localStorage.removeItem("auth-storage");
            window.location.href = "/login";
          }
        }
      }
    }

    return Promise.reject(error);
  }
);

// Helper to get empresa_id from auth storage
function getEmpresaId(): string | null {
  if (typeof window === "undefined") return null;
  const authStorage = localStorage.getItem("auth-storage");
  if (authStorage) {
    try {
      const { state } = JSON.parse(authStorage);
      return state?.empresaActual?.id || null;
    } catch {
      return null;
    }
  }
  return null;
}

// Chat API
export const chatApi = {
  sendMessage: async (
    message: string,
    conversationId?: string,
    file?: File
  ) => {
    const formData = new FormData();
    formData.append("mensaje", message);
    if (conversationId) {
      formData.append("conversacion_id", conversationId);
    }

    // Enviar empresa_id
    const empresaId = getEmpresaId();
    if (empresaId) {
      formData.append("empresa_id", empresaId);
    }

    if (file) {
      formData.append("archivo", file);
    }

    const response = await api.post("/chat/mensaje/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getConversations: async () => {
    const response = await api.get("/chat/conversaciones/");
    return response.data;
  },

  getConversation: async (id: string) => {
    const response = await api.get(`/chat/conversaciones/${id}/`);
    return response.data;
  },

  confirmAction: async (conversationId: string, confirm: boolean) => {
    const response = await api.post(
      `/chat/conversaciones/${conversationId}/confirmar_accion/`,
      { confirmar: confirm }
    );
    return response.data;
  },
};

// Empleados API
export const empleadosApi = {
  list: async (params?: Record<string, string>) => {
    const response = await api.get("/empleados/", { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get(`/empleados/${id}/`);
    return response.data;
  },

  create: async (data: Record<string, unknown>) => {
    const response = await api.post("/empleados/", data);
    return response.data;
  },

  update: async (id: string, data: Record<string, unknown>) => {
    const response = await api.patch(`/empleados/${id}/`, data);
    return response.data;
  },
};

// Nomina API
export const nominaApi = {
  // Periodos
  getPeriodos: async (params?: Record<string, string>) => {
    const response = await api.get("/nomina/periodos/", { params });
    return response.data;
  },

  getPeriodo: async (id: string) => {
    const response = await api.get(`/nomina/periodos/${id}/`);
    return response.data;
  },

  createPeriodo: async (data: {
    tipo_periodo: string;
    numero_periodo: number;
    año: number;
    fecha_inicio: string;
    fecha_fin: string;
    fecha_pago?: string;
  }) => {
    const response = await api.post("/nomina/periodos/", data);
    return response.data;
  },

  calcularPeriodo: async (id: string) => {
    const response = await api.post(`/nomina/periodos/${id}/calcular/`);
    return response.data;
  },

  aprobarPeriodo: async (id: string) => {
    const response = await api.post(`/nomina/periodos/${id}/aprobar/`);
    return response.data;
  },

  getResumenPeriodo: async (id: string) => {
    const response = await api.get(`/nomina/periodos/${id}/resumen/`);
    return response.data;
  },

  // Recibos
  getRecibos: async (params?: Record<string, string>) => {
    const response = await api.get("/nomina/recibos/", { params });
    return response.data;
  },

  getRecibo: async (id: string) => {
    const response = await api.get(`/nomina/recibos/${id}/`);
    return response.data;
  },

  getReciboPdf: async (id: string) => {
    const response = await api.get(`/nomina/recibos/${id}/pdf/`, {
      responseType: "blob",
    });
    return response.data;
  },

  timbrarRecibo: async (id: string) => {
    const response = await api.post(`/nomina/recibos/${id}/timbrar/`);
    return response.data;
  },

  // Mis recibos (para empleados)
  getMisRecibos: async () => {
    const response = await api.get("/nomina/recibos/mis_recibos/");
    return response.data;
  },

  // Incidencias
  getIncidencias: async (params?: Record<string, string>) => {
    const response = await api.get("/nomina/incidencias/", { params });
    return response.data;
  },

  getIncidenciasPendientes: async () => {
    const response = await api.get("/nomina/incidencias/pendientes/");
    return response.data;
  },

  createIncidencia: async (data: {
    empleado: string;
    tipo: string;
    fecha_inicio: string;
    fecha_fin?: string;
    cantidad?: number;
    monto?: number;
    descripcion?: string;
  }) => {
    const response = await api.post("/nomina/incidencias/", data);
    return response.data;
  },

  deleteIncidencia: async (id: string) => {
    const response = await api.delete(`/nomina/incidencias/${id}/`);
    return response.data;
  },
};

// Reportes API
export const reportesApi = {
  // Dashboard de empresa
  getDashboardEmpresa: async (empresaId: string) => {
    const response = await api.get(`/reportes/empresa/${empresaId}/dashboard/`);
    return response.data;
  },

  getDashboardEmpresaPdf: async (empresaId: string) => {
    const response = await api.get(`/reportes/empresa/${empresaId}/dashboard/pdf/`, {
      responseType: "blob",
    });
    return response.data;
  },

  // Dashboard de empleado
  getDashboardEmpleado: async (empleadoId: string, incluirLiquidacion: boolean = false) => {
    const response = await api.get(`/reportes/empleado/${empleadoId}/dashboard/`, {
      params: { incluir_liquidacion: incluirLiquidacion },
    });
    return response.data;
  },

  getDashboardEmpleadoPdf: async (empleadoId: string) => {
    const response = await api.get(`/reportes/empleado/${empleadoId}/dashboard/pdf/`, {
      responseType: "blob",
    });
    return response.data;
  },

  // Liquidacion
  calcularLiquidacion: async (
    empleadoId: string,
    fechaBaja?: string,
    esDespidoInjustificado: boolean = true
  ) => {
    const response = await api.get(`/reportes/empleado/${empleadoId}/liquidacion/`, {
      params: {
        fecha_baja: fechaBaja,
        es_despido_injustificado: esDespidoInjustificado,
      },
    });
    return response.data;
  },

  getLiquidacionPdf: async (
    empleadoId: string,
    fechaBaja?: string,
    esDespidoInjustificado: boolean = true
  ) => {
    const response = await api.get(`/reportes/empleado/${empleadoId}/liquidacion/pdf/`, {
      params: {
        fecha_baja: fechaBaja,
        es_despido_injustificado: esDespidoInjustificado,
      },
      responseType: "blob",
    });
    return response.data;
  },
};

// Vacaciones API
export const vacacionesApi = {
  getSolicitudes: async (params?: Record<string, string>) => {
    const response = await api.get("/vacaciones/solicitudes/", { params });
    return response.data;
  },

  getResumen: async () => {
    const response = await api.get("/vacaciones/solicitudes/resumen/");
    return response.data;
  },

  getEstadisticas: async () => {
    const response = await api.get("/vacaciones/solicitudes/estadisticas/");
    return response.data;
  },
};

// Contratos API
export const contratosApi = {
  list: async (params?: Record<string, string>) => {
    const response = await api.get("/contratos/", { params });
    return response.data;
  },

  getPorVencer: async () => {
    const response = await api.get("/contratos/por_vencer/");
    return response.data;
  },
};

// Usuarios/Perfil API
export const usuariosApi = {
  getPerfil: async () => {
    const response = await api.get("/usuarios/perfil/");
    return response.data;
  },

  actualizarPerfil: async (data: {
    first_name?: string;
    last_name?: string;
    notificaciones_email?: boolean;
    notificaciones_push?: boolean;
    tema_oscuro?: boolean;
  }) => {
    const response = await api.patch("/usuarios/perfil/actualizar/", data);
    return response.data;
  },

  cambiarPassword: async (data: {
    password_actual: string;
    password_nuevo: string;
  }) => {
    const response = await api.post("/usuarios/cambiar-password/", data);
    return response.data;
  },
};

// Notificaciones API
export const notificacionesApi = {
  getRecientes: async () => {
    const response = await api.get("/notificaciones/recientes/");
    return response.data;
  },

  getNoLeidasCount: async (): Promise<{ count: number }> => {
    const response = await api.get("/notificaciones/no_leidas/");
    return response.data;
  },

  marcarLeida: async (id: string) => {
    const response = await api.post(`/notificaciones/${id}/marcar_leida/`);
    return response.data;
  },

  marcarTodasLeidas: async () => {
    const response = await api.post("/notificaciones/marcar_todas_leidas/");
    return response.data;
  },
};

export default api;
