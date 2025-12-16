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

export default api;
