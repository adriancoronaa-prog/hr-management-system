"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { RoleGuard } from "@/components/auth/role-guard";
import type { Empresa } from "@/types";
import {
  Building2,
  Plus,
  MoreHorizontal,
  Users,
  MapPin,
  Phone,
  Mail,
  CheckCircle,
  Edit,
  Trash2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { Skeleton } from "@/components/ui/skeleton";

export default function EmpresasPage() {
  const { user, empresaActual, setEmpresaActual } = useAuthStore();
  const [menuOpen, setMenuOpen] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["empresas"],
    queryFn: async () => {
      const response = await api.get("/empresas/");
      return response.data.results || response.data;
    },
  });

  const empresas: Empresa[] = data || [];

  const handleSetActiva = (empresa: Empresa) => {
    setEmpresaActual({
      id: empresa.id,
      rfc: empresa.rfc,
      razon_social: empresa.razon_social,
      nombre_comercial: empresa.nombre_comercial,
    });
    setMenuOpen(null);
    // Recargar para que todos los componentes usen la nueva empresa
    window.location.reload();
  };

  return (
    <RoleGuard allowedRoles={["admin"]}>
      <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-warm-900">Empresas</h1>
          <p className="text-sm text-warm-500 mt-1">
            {empresas.length} empresa{empresas.length !== 1 ? "s" : ""}{" "}
            registrada{empresas.length !== 1 ? "s" : ""}
          </p>
        </div>
        <Link
          href="/empresas/nueva"
          className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-horizon-600 text-white text-sm font-medium rounded-lg hover:bg-horizon-700 transition-colors"
        >
          <Plus className="h-4 w-4" strokeWidth={1.5} />
          Nueva empresa
        </Link>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-white rounded-xl border border-warm-200 p-5"
            >
              <div className="flex items-start gap-3 mb-4">
                <Skeleton className="h-10 w-10 rounded-lg" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-32 mb-2" />
                  <Skeleton className="h-3 w-24" />
                </div>
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && empresas.length === 0 && (
        <div className="bg-white rounded-xl border border-warm-200 p-12 text-center">
          <div className="mx-auto w-12 h-12 rounded-full bg-horizon-100 flex items-center justify-center mb-4">
            <Building2 className="h-6 w-6 text-horizon-600" strokeWidth={1.5} />
          </div>
          <h3 className="text-lg font-semibold text-warm-900 mb-2">
            No hay empresas registradas
          </h3>
          <p className="text-warm-500 mb-6 max-w-sm mx-auto">
            Crea tu primera empresa para comenzar a gestionar empleados, nomina
            y mas.
          </p>
          <Link
            href="/empresas/nueva"
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-horizon-600 text-white text-sm font-medium rounded-lg hover:bg-horizon-700 transition-colors"
          >
            <Plus className="h-4 w-4" strokeWidth={1.5} />
            Crear primera empresa
          </Link>
        </div>
      )}

      {/* Grid de empresas */}
      {!isLoading && empresas.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {empresas.map((empresa) => (
            <div
              key={empresa.id}
              className={cn(
                "bg-white rounded-xl border p-5 transition-all hover:shadow-md relative",
                empresaActual?.id === empresa.id
                  ? "border-horizon-500 ring-1 ring-horizon-500"
                  : "border-warm-200"
              )}
            >
              {/* Badge de activa */}
              {empresaActual?.id === empresa.id && (
                <div className="absolute -top-2 -right-2 bg-horizon-600 text-white text-xs font-medium px-2 py-0.5 rounded-full flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" strokeWidth={1.5} />
                  Activa
                </div>
              )}

              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-horizon-100 flex items-center justify-center">
                    <Building2
                      className="h-5 w-5 text-horizon-600"
                      strokeWidth={1.5}
                    />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-semibold text-warm-900 truncate">
                      {empresa.nombre_comercial || empresa.razon_social}
                    </h3>
                    <p className="text-xs text-warm-500">{empresa.rfc}</p>
                  </div>
                </div>

                {/* Menu */}
                <div className="relative">
                  <button
                    onClick={() =>
                      setMenuOpen(menuOpen === empresa.id ? null : empresa.id)
                    }
                    className="p-1 hover:bg-warm-100 rounded transition-colors"
                  >
                    <MoreHorizontal
                      className="h-5 w-5 text-warm-400"
                      strokeWidth={1.5}
                    />
                  </button>

                  {menuOpen === empresa.id && (
                    <>
                      <div
                        className="fixed inset-0 z-10"
                        onClick={() => setMenuOpen(null)}
                      />
                      <div className="absolute right-0 mt-1 w-44 bg-white border border-warm-200 rounded-lg shadow-lg z-20 overflow-hidden">
                        <button
                          onClick={() => handleSetActiva(empresa)}
                          className="flex items-center gap-2 w-full px-3 py-2.5 text-sm text-warm-700 text-left hover:bg-warm-50 hover:text-warm-900 transition-colors"
                        >
                          <CheckCircle className="h-4 w-4 text-horizon-500" strokeWidth={1.5} />
                          Establecer activa
                        </button>
                        <Link
                          href={`/empresas/${empresa.id}`}
                          className="flex items-center gap-2 w-full px-3 py-2.5 text-sm text-warm-700 text-left hover:bg-warm-50 hover:text-warm-900 transition-colors"
                          onClick={() => setMenuOpen(null)}
                        >
                          <Edit className="h-4 w-4 text-warm-500" strokeWidth={1.5} />
                          Editar
                        </Link>
                        <button className="flex items-center gap-2 w-full px-3 py-2.5 text-sm text-red-600 text-left hover:bg-red-50 transition-colors">
                          <Trash2 className="h-4 w-4" strokeWidth={1.5} />
                          Eliminar
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Info */}
              <div className="space-y-2 text-sm">
                {empresa.direccion && (
                  <div className="flex items-center gap-2 text-warm-600">
                    <MapPin
                      className="h-4 w-4 text-warm-400 flex-shrink-0"
                      strokeWidth={1.5}
                    />
                    <span className="truncate">{empresa.direccion}</span>
                  </div>
                )}
                {empresa.telefono && (
                  <div className="flex items-center gap-2 text-warm-600">
                    <Phone
                      className="h-4 w-4 text-warm-400 flex-shrink-0"
                      strokeWidth={1.5}
                    />
                    <span>{empresa.telefono}</span>
                  </div>
                )}
                {empresa.email && (
                  <div className="flex items-center gap-2 text-warm-600">
                    <Mail
                      className="h-4 w-4 text-warm-400 flex-shrink-0"
                      strokeWidth={1.5}
                    />
                    <span className="truncate">{empresa.email}</span>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="mt-4 pt-4 border-t border-warm-100 flex items-center justify-between">
                <div className="flex items-center gap-1 text-warm-500">
                  <Users className="h-4 w-4" strokeWidth={1.5} />
                  <span className="text-sm">
                    {empresa.empleados_count || 0} empleados
                  </span>
                </div>
                <span
                  className={cn(
                    "text-xs font-medium px-2 py-0.5 rounded-full",
                    empresa.estado === "activo"
                      ? "bg-sage-100 text-sage-700"
                      : "bg-warm-100 text-warm-600"
                  )}
                >
                  {empresa.estado === "activo" ? "Activa" : "Inactiva"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
      </div>
    </RoleGuard>
  );
}
