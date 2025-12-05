import { create } from "zustand";
import { persist } from "zustand/middleware";
import axios from "axios";
import type { User, Empresa } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  empresas: Empresa[];
  empresaActual: Empresa | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  refreshAccessToken: () => Promise<boolean>;
  setEmpresaActual: (empresa: Empresa) => void;
  setEmpresas: (empresas: Empresa[]) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      empresas: [],
      empresaActual: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await axios.post(`${API_URL}/api/usuarios/login/`, {
            email,
            password,
          });

          // Backend devuelve: { access, refresh, usuario: { id, email, nombre, apellidos, rol, empresas } }
          const { access, refresh, usuario } = response.data;

          // Mapear usuario a user con el formato esperado
          const user = {
            id: usuario.id,
            email: usuario.email,
            nombre: `${usuario.nombre || ''} ${usuario.apellidos || ''}`.trim() || usuario.email,
            rol: usuario.rol,
            empresa: usuario.empresas?.[0] || null,
          };

          const empresas = usuario.empresas || [];

          set({
            user,
            token: access,
            refreshToken: refresh,
            isAuthenticated: true,
            isLoading: false,
            empresas,
            empresaActual: empresas[0] || null,
          });

          return true;
        } catch (error) {
          let errorMessage = "Error al iniciar sesion";

          if (axios.isAxiosError(error)) {
            if (error.response?.status === 401) {
              errorMessage = "Credenciales incorrectas";
            } else if (error.response?.data?.detail) {
              errorMessage = error.response.data.detail;
            } else if (error.response?.data?.error) {
              errorMessage = error.response.data.error;
            } else if (error.response?.data?.non_field_errors) {
              errorMessage = error.response.data.non_field_errors[0];
            }
          }

          set({
            isLoading: false,
            error: errorMessage,
          });

          return false;
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          empresas: [],
          empresaActual: null,
          error: null,
        });
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return false;

        try {
          const response = await axios.post(
            `${API_URL}/api/usuarios/token/refresh/`,
            { refresh: refreshToken }
          );

          set({ token: response.data.access });
          return true;
        } catch {
          get().logout();
          return false;
        }
      },

      setEmpresaActual: (empresa: Empresa) => {
        set({ empresaActual: empresa });
      },

      setEmpresas: (empresas: Empresa[]) => {
        const { empresaActual } = get();
        set({ empresas });

        // Si no hay empresa actual pero hay empresas, seleccionar la primera
        if (!empresaActual && empresas.length > 0) {
          set({ empresaActual: empresas[0] });
        }
        // Si la empresa actual ya no existe en la lista, seleccionar la primera
        else if (empresaActual && !empresas.find(e => e.id === empresaActual.id)) {
          set({ empresaActual: empresas.length > 0 ? empresas[0] : null });
        }
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        empresas: state.empresas,
        empresaActual: state.empresaActual,
      }),
    }
  )
);
