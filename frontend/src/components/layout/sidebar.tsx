"use client";

import * as React from "react";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquare,
  Users,
  Wallet,
  FileText,
  Calendar,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Building2,
  ChevronDown,
  Check,
  Plus,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Avatar } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuthStore } from "@/stores/auth-store";

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  { title: "Dashboard", href: "/", icon: LayoutDashboard },
  { title: "Chat", href: "/chat", icon: MessageSquare },
  { title: "Empresas", href: "/empresas", icon: Building2, adminOnly: true },
  { title: "Empleados", href: "/empleados", icon: Users },
  { title: "Nomina", href: "/nomina", icon: Wallet },
  { title: "Contratos", href: "/contratos", icon: FileText },
  { title: "Vacaciones", href: "/vacaciones", icon: Calendar },
  { title: "Reportes", href: "/reportes", icon: BarChart3 },
];

interface SidebarProps {
  collapsed: boolean;
  onCollapse: (collapsed: boolean) => void;
}

export function Sidebar({ collapsed, onCollapse }: SidebarProps) {
  const pathname = usePathname();
  const { user, empresaActual, empresas, logout, setEmpresaActual } =
    useAuthStore();
  const isAdmin = user?.rol === "admin";
  const [empresaDropdownOpen, setEmpresaDropdownOpen] = useState(false);

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-40 flex flex-col bg-horizon-900 transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b border-horizon-800 px-4">
        {!collapsed && (
          <span className="text-xl font-semibold text-white">RRHH</span>
        )}
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
      </div>

      {/* Empresa Activa - Siempre visible */}
      <div
        className={cn(
          "border-b border-horizon-800",
          collapsed ? "px-2 py-3" : "px-3 py-3"
        )}
      >
        {empresas.length > 0 ? (
          <div className="relative">
            <button
              onClick={() =>
                !collapsed && setEmpresaDropdownOpen(!empresaDropdownOpen)
              }
              className={cn(
                "w-full flex items-center gap-2 rounded-lg transition-colors",
                collapsed
                  ? "justify-center p-2 hover:bg-horizon-800"
                  : "px-3 py-2 hover:bg-horizon-800"
              )}
            >
              <Building2
                className="h-5 w-5 text-horizon-400 flex-shrink-0"
                strokeWidth={1.5}
              />
              {!collapsed && (
                <>
                  <div className="flex-1 text-left min-w-0">
                    <p className="text-sm font-medium text-white truncate">
                      {empresaActual?.nombre_comercial ||
                        empresaActual?.razon_social ||
                        "Seleccionar"}
                    </p>
                  </div>
                  {empresas.length > 1 && (
                    <ChevronDown
                      className={cn(
                        "h-4 w-4 text-horizon-400 transition-transform",
                        empresaDropdownOpen && "rotate-180"
                      )}
                      strokeWidth={1.5}
                    />
                  )}
                </>
              )}
            </button>

            {/* Dropdown */}
            {!collapsed && empresaDropdownOpen && empresas.length > 1 && (
              <div className="absolute left-0 right-0 mt-1 bg-horizon-800 border border-horizon-700 rounded-lg shadow-lg z-50 overflow-hidden">
                {empresas.map((empresa) => (
                  <button
                    key={empresa.id}
                    onClick={() => {
                      setEmpresaActual(empresa);
                      setEmpresaDropdownOpen(false);
                    }}
                    className={cn(
                      "flex items-center gap-2 w-full px-3 py-2 text-sm text-left transition-colors",
                      empresaActual?.id === empresa.id
                        ? "bg-horizon-700 text-white"
                        : "text-horizon-300 hover:bg-horizon-700 hover:text-white"
                    )}
                  >
                    <span className="truncate flex-1">
                      {empresa.nombre_comercial || empresa.razon_social}
                    </span>
                    {empresaActual?.id === empresa.id && (
                      <Check
                        className="h-4 w-4 flex-shrink-0"
                        strokeWidth={1.5}
                      />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <Link
            href="/empresas/nueva"
            className={cn(
              "flex items-center gap-2 rounded-lg bg-horizon-700 transition-colors hover:bg-horizon-600",
              collapsed ? "p-2 justify-center" : "px-3 py-2"
            )}
          >
            <Plus className="h-5 w-5 text-horizon-300" strokeWidth={1.5} />
            {!collapsed && (
              <span className="text-sm font-medium text-white">
                Crear empresa
              </span>
            )}
          </Link>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems
          .filter((item) => !item.adminOnly || isAdmin)
          .map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-horizon-800 text-white"
                    : "text-horizon-300 hover:bg-horizon-800 hover:text-white",
                  collapsed && "justify-center px-2"
                )}
                title={collapsed ? item.title : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" strokeWidth={1.5} />
                {!collapsed && <span>{item.title}</span>}
              </Link>
            );
          })}
      </nav>

      {/* User section */}
      <div className="border-t border-horizon-800 p-3">
        <DropdownMenu>
          <DropdownMenuTrigger
            className={cn(
              "flex w-full items-center gap-3 rounded-md px-2 py-2 text-left hover:bg-horizon-800",
              collapsed && "justify-center"
            )}
          >
            <Avatar
              name={user?.nombre}
              size="sm"
              className="border border-horizon-700"
            />
            {!collapsed && (
              <div className="flex-1 overflow-hidden">
                <p className="truncate text-sm font-medium text-white">
                  {user?.nombre}
                </p>
                <p className="truncate text-xs text-horizon-400">
                  {user?.email}
                </p>
              </div>
            )}
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" side="top" className="w-56">
            <DropdownMenuLabel>
              <div className="flex flex-col">
                <span>{user?.nombre}</span>
                <span className="text-xs font-normal text-warm-500">
                  {user?.email}
                </span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={logout}
              className="text-error focus:text-error"
            >
              <LogOut className="mr-2 h-4 w-4" strokeWidth={1.5} />
              Cerrar sesion
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
}
