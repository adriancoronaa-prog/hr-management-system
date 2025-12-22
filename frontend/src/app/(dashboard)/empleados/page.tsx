"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/auth-store";
import { RoleGuard } from "@/components/auth/role-guard";
import api from "@/lib/api";
import Link from "next/link";

interface Empleado {
  id: string;
  nombre: string;
  apellido_paterno: string;
  apellido_materno?: string;
  nombre_completo?: string;
  puesto?: string;
  departamento?: string;
  estado: string;
  email_corporativo?: string;
  foto?: string;
}

export default function EmpleadosPage() {
  const { empresaActual } = useAuthStore();
  const [search, setSearch] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const { data, isLoading } = useQuery({
    queryKey: ["empleados", empresaActual?.id],
    queryFn: async () => {
      const response = await api.get("/empleados/");
      const rawData = response.data;
      return rawData.results || rawData;
    },
    enabled: mounted && !!empresaActual?.id,
  });

  const empleados: Empleado[] = data || [];

  // Función para obtener nombre completo
  const getNombreCompleto = (emp: Empleado) => {
    if (emp.nombre_completo) return emp.nombre_completo;
    const partes = [emp.nombre, emp.apellido_paterno, emp.apellido_materno].filter(Boolean);
    return partes.join(" ") || "Sin nombre";
  };

  const filteredEmpleados = empleados.filter((emp) => {
    const fullName = getNombreCompleto(emp).toLowerCase();
    const searchLower = search.toLowerCase();
    return (
      fullName.includes(searchLower) ||
      emp.puesto?.toLowerCase().includes(searchLower) ||
      emp.departamento?.toLowerCase().includes(searchLower)
    );
  });

  const empleadosActivos = empleados.filter((e) => e.estado === "activo").length;

  if (!mounted) return null;

  return (
    <RoleGuard allowedRoles={["admin", "rrhh", "empleador"]}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-display font-semibold text-warm-900">
            Empleados
          </h1>
          <p className="text-sm text-warm-500 mt-1">
            {empleadosActivos} empleado{empleadosActivos !== 1 ? "s" : ""} activo
            {empleadosActivos !== 1 ? "s" : ""} de {empleados.length} total
          </p>
        </div>
        <Link href="/empleados/nuevo">
          <Button>
            <Plus className="mr-2 h-4 w-4" strokeWidth={1.5} />
            Nuevo empleado
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="flex-1">
          <Input
            placeholder="Buscar empleado..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="h-4 w-4" strokeWidth={1.5} />}
          />
        </div>
        <Button variant="outline">
          <Filter className="mr-2 h-4 w-4" strokeWidth={1.5} />
          Filtros
        </Button>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-5 w-32" />
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-3 w-20" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && empleados.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="w-12 h-12 rounded-full bg-horizon-100 flex items-center justify-center mb-4">
              <Users className="h-6 w-6 text-horizon-600" strokeWidth={1.5} />
            </div>
            <h3 className="text-lg font-semibold text-warm-900 mb-2">
              No hay empleados registrados
            </h3>
            <p className="text-warm-500 mb-6 text-center max-w-sm">
              Agrega tu primer empleado para comenzar a gestionar tu equipo.
            </p>
            <Link href="/empleados/nuevo">
              <Button>
                <Plus className="mr-2 h-4 w-4" strokeWidth={1.5} />
                Agregar empleado
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* List */}
      {!isLoading && filteredEmpleados.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredEmpleados.map((empleado) => (
            <Link key={empleado.id} href={`/empleados/${empleado.id}`}>
              <Card className="cursor-pointer transition-all hover:shadow-md hover:border-horizon-300">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Avatar
                      name={getNombreCompleto(empleado)}
                      src={empleado.foto}
                      size="lg"
                    />
                    <div className="flex-1 overflow-hidden">
                      <h3 className="truncate font-medium text-warm-900">
                        {getNombreCompleto(empleado)}
                      </h3>
                      <p className="truncate text-sm text-warm-500">
                        {empleado.puesto || "Sin puesto asignado"}
                      </p>
                      <p className="truncate text-xs text-warm-400">
                        {empleado.departamento || "Sin departamento"}
                      </p>
                      <div className="mt-2">
                        <Badge
                          variant={
                            empleado.estado === "activo" ? "success" : "default"
                          }
                        >
                          {empleado.estado === "activo" ? "Activo" : empleado.estado}
                        </Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

        {/* No results from search */}
        {!isLoading && empleados.length > 0 && filteredEmpleados.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <p className="text-warm-500">
                No se encontraron empleados con "{search}"
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </RoleGuard>
  );
}
