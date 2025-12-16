"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { Loader2 } from "lucide-react";

export type UserRole = "admin" | "rrhh" | "empleador" | "empleado";

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles: UserRole[];
  fallbackUrl?: string;
}

export function RoleGuard({
  children,
  allowedRoles,
  fallbackUrl = "/unauthorized",
}: RoleGuardProps) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Si no esta autenticado, redirigir a login
    if (!isAuthenticated || !user) {
      router.replace("/login");
      return;
    }

    // Verificar si el rol tiene acceso
    const userRole = (user.rol as UserRole) || "empleado";
    if (!allowedRoles.includes(userRole)) {
      router.replace(fallbackUrl);
    }
  }, [user, isAuthenticated, allowedRoles, fallbackUrl, router]);

  // Si no esta autenticado, mostrar loading
  if (!isAuthenticated || !user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-horizon-600" />
      </div>
    );
  }

  // Verificar rol
  const userRole = (user.rol as UserRole) || "empleado";
  if (!allowedRoles.includes(userRole)) {
    return null;
  }

  return <>{children}</>;
}

// HOC para usar en paginas
export function withRoleGuard<P extends object>(
  Component: React.ComponentType<P>,
  allowedRoles: UserRole[],
  fallbackUrl?: string
) {
  return function GuardedComponent(props: P) {
    return (
      <RoleGuard allowedRoles={allowedRoles} fallbackUrl={fallbackUrl}>
        <Component {...props} />
      </RoleGuard>
    );
  };
}

// Helper para verificar rol sin redireccion
export function useHasRole(allowedRoles: UserRole[]): boolean {
  const { user } = useAuthStore();
  const userRole = (user?.rol as UserRole) || "empleado";
  return allowedRoles.includes(userRole);
}

// Helper para verificar si puede gestionar (admin, rrhh, empleador)
export function useCanManage(): boolean {
  return useHasRole(["admin", "rrhh", "empleador"]);
}

// Helper para verificar si es admin o rrhh
export function useIsAdminOrHR(): boolean {
  return useHasRole(["admin", "rrhh"]);
}
