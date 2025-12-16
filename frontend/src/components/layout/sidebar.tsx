"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { UserRole } from "@/components/auth/role-guard";
import {
  LayoutDashboard,
  MessageSquare,
  Users,
  Building2,
  FileText,
  Calendar,
  Receipt,
  LogOut,
  ChevronDown,
  Check,
  Plus,
  Loader2,
  BarChart3,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
  roles: UserRole[];
}

const navigation: NavItem[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard, roles: ["admin", "rrhh", "empleador", "empleado"] },
  { name: "Chat", href: "/chat", icon: MessageSquare, roles: ["admin", "rrhh", "empleador", "empleado"] },
  { name: "Empresas", href: "/empresas", icon: Building2, roles: ["admin"] },
  { name: "Empleados", href: "/empleados", icon: Users, roles: ["admin", "rrhh", "empleador"] },
  { name: "Nomina", href: "/nomina", icon: Receipt, roles: ["admin", "rrhh", "empleador"] },
  { name: "Contratos", href: "/contratos", icon: FileText, roles: ["admin", "rrhh", "empleador"] },
  { name: "Vacaciones", href: "/vacaciones", icon: Calendar, roles: ["admin", "rrhh", "empleador", "empleado"] },
  { name: "Reportes", href: "/reportes", icon: BarChart3, roles: ["admin", "rrhh", "empleador"] },
];

interface SidebarProps {
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
}

export function Sidebar({ collapsed = false, onCollapse }: SidebarProps) {
  const pathname = usePathname();
  const { user, empresas, empresaActual, setEmpresas, setEmpresaActual, logout } =
    useAuthStore();
  const [selectorOpen, setSelectorOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Cargar empresas al montar
  useEffect(() => {
    if (mounted && user) {
      loadEmpresas();
    }
  }, [mounted, user]);

  const loadEmpresas = async () => {
    setLoading(true);
    try {
      // Ruta sin /api/ porque baseURL ya incluye /api
      const response = await api.get("/empresas/");
      const rawData = response.data;
      const data = rawData.results || rawData;

      if (Array.isArray(data) && data.length > 0) {
        const empresasFormateadas = data.map((e: any) => ({
          id: e.id,
          razon_social: e.razon_social,
          nombre_comercial: e.nombre_comercial,
          rfc: e.rfc,
          estado: e.estado || "activo",
          empleados_count: e.empleados_count || 0,
        }));
        setEmpresas(empresasFormateadas);

        // Si no hay empresa activa, seleccionar la primera
        if (!empresaActual) {
          setEmpresaActual(empresasFormateadas[0]);
        }
      }
    } catch (error) {
      console.error("Error cargando empresas:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectEmpresa = async (empresa: any) => {
    setEmpresaActual(empresa);
    setSelectorOpen(false);

    // Invalidar todas las queries para recargar datos
    await queryClient.invalidateQueries();

    // Forzar recarga de la página para asegurar actualización completa
    window.location.reload();
  };

  const handleLogout = () => {
    logout();
    window.location.href = "/login";
  };

  if (!mounted) return null;

  const userRole = (user?.rol as UserRole) || "empleado";
  const filteredNavigation = navigation.filter((item) => {
    return item.roles.includes(userRole);
  });

  const empresaNombre =
    empresaActual?.nombre_comercial ||
    empresaActual?.razon_social ||
    "Seleccionar empresa";

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-40 flex flex-col bg-horizon-900 text-white transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b border-horizon-800 px-4">
        {!collapsed && (
          <span className="text-xl font-display font-bold tracking-tight">
            RRHH
          </span>
        )}
        {onCollapse && (
          <button
            onClick={() => onCollapse(!collapsed)}
            className="rounded-md p-1.5 text-horizon-400 hover:bg-horizon-800 hover:text-white"
          >
            {collapsed ? (
              <ChevronRight className="h-5 w-5" strokeWidth={1.5} />
            ) : (
              <ChevronLeft className="h-5 w-5" strokeWidth={1.5} />
            )}
          </button>
        )}
      </div>

      {/* Selector de Empresa */}
      {userRole !== "empleado" ? (
        <div
          className={cn(
            "border-b border-horizon-800",
            collapsed ? "px-2 py-3" : "px-3 py-3"
          )}
        >
          {loading ? (
            <div
              className={cn(
                "flex items-center gap-2 text-sm text-horizon-400",
                collapsed ? "justify-center p-2" : "px-3 py-2.5"
              )}
            >
              <Loader2 className="w-4 h-4 animate-spin" />
              {!collapsed && <span>Cargando...</span>}
            </div>
          ) : empresas.length === 0 ? (
            <Link
              href="/empresas/nueva"
              className={cn(
                "flex items-center gap-2 text-sm bg-horizon-700 hover:bg-horizon-600 rounded-lg transition-colors",
                collapsed ? "p-2 justify-center" : "px-3 py-2.5"
              )}
            >
              <Plus className="w-4 h-4" />
              {!collapsed && <span>Crear empresa</span>}
            </Link>
          ) : (
            <div className="relative">
              <button
                onClick={() => !collapsed && setSelectorOpen(!selectorOpen)}
                className={cn(
                  "flex items-center w-full text-sm bg-horizon-800 hover:bg-horizon-700 rounded-lg transition-colors",
                  collapsed ? "p-2 justify-center" : "justify-between px-3 py-2.5"
                )}
              >
                <div
                  className={cn(
                    "flex items-center gap-2 min-w-0",
                    collapsed ? "" : "flex-1"
                  )}
                >
                  <Building2 className="w-4 h-4 text-horizon-400 flex-shrink-0" />
                  {!collapsed && (
                    <span className="truncate font-medium">{empresaNombre}</span>
                  )}
                </div>
                {!collapsed && empresas.length > 1 && (
                  <ChevronDown
                    className={cn(
                      "w-4 h-4 text-horizon-400 flex-shrink-0 transition-transform duration-200 ml-2",
                      selectorOpen && "rotate-180"
                    )}
                  />
                )}
              </button>

              {/* Dropdown */}
              {!collapsed && selectorOpen && empresas.length > 1 && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setSelectorOpen(false)}
                  />

                  <div className="absolute left-0 right-0 mt-1 bg-horizon-800 rounded-lg shadow-xl border border-horizon-700 z-50 max-h-64 overflow-y-auto">
                    {empresas.map((empresa) => (
                      <button
                        key={empresa.id}
                        onClick={() => handleSelectEmpresa(empresa)}
                        className={cn(
                          "flex items-center justify-between w-full px-3 py-2.5 text-sm text-left transition-colors",
                          empresaActual?.id === empresa.id
                            ? "bg-horizon-700 text-white"
                            : "text-horizon-200 hover:bg-horizon-700 hover:text-white"
                        )}
                      >
                        <span className="truncate flex-1">
                          {empresa.nombre_comercial || empresa.razon_social}
                        </span>
                        {empresaActual?.id === empresa.id && (
                          <Check className="w-4 h-4 text-sage-400 flex-shrink-0 ml-2" />
                        )}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      ) : (
        <div
          className={cn(
            "border-b border-horizon-800",
            collapsed ? "px-2 py-3" : "px-3 py-3"
          )}
        >
          <div
            className={cn(
              "flex items-center gap-2 text-sm bg-horizon-800 rounded-lg",
              collapsed ? "p-2 justify-center" : "px-3 py-2.5"
            )}
          >
            <Building2 className="w-4 h-4 text-horizon-400 flex-shrink-0" />
            {!collapsed && (
              <span className="text-horizon-200 truncate font-medium">
                {empresaNombre}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Navegación */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {filteredNavigation.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg transition-colors",
                isActive
                  ? "bg-horizon-700 text-white font-medium"
                  : "text-horizon-300 hover:text-white hover:bg-horizon-800",
                collapsed && "justify-center px-2"
              )}
              title={collapsed ? item.name : undefined}
            >
              <item.icon className="w-5 h-5 shrink-0" strokeWidth={1.5} />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Usuario */}
      <div className="p-3 border-t border-horizon-800">
        <div
          className={cn(
            "flex items-center gap-3",
            collapsed ? "justify-center" : "px-3 py-2"
          )}
        >
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-horizon-600 to-horizon-700 flex items-center justify-center text-sm font-semibold flex-shrink-0">
            {user?.nombre?.[0]?.toUpperCase() ||
              user?.email?.[0]?.toUpperCase() ||
              "U"}
          </div>
          {!collapsed && (
            <>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {user?.nombre || "Usuario"}
                </p>
                <p className="text-xs text-horizon-400 truncate">
                  {user?.email}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-horizon-400 hover:text-white hover:bg-horizon-800 rounded-lg transition-colors"
                title="Cerrar sesión"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>
    </aside>
  );
}
