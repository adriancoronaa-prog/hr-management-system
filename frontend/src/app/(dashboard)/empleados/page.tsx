"use client";

import * as React from "react";
import { Plus, Search, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

// Mock data
const empleados = [
  {
    id: "1",
    nombre: "Juan Carlos",
    apellido_paterno: "Martinez",
    apellido_materno: "Lopez",
    puesto: "Desarrollador Senior",
    departamento: "Tecnologia",
    estado: "activo",
    email: "juan.martinez@empresa.com",
  },
  {
    id: "2",
    nombre: "Maria",
    apellido_paterno: "Garcia",
    apellido_materno: "Hernandez",
    puesto: "Contadora",
    departamento: "Finanzas",
    estado: "activo",
    email: "maria.garcia@empresa.com",
  },
  {
    id: "3",
    nombre: "Pedro",
    apellido_paterno: "Sanchez",
    apellido_materno: "Ruiz",
    puesto: "Gerente de Ventas",
    departamento: "Comercial",
    estado: "activo",
    email: "pedro.sanchez@empresa.com",
  },
];

export default function EmpleadosPage() {
  const [search, setSearch] = React.useState("");

  const filteredEmpleados = empleados.filter((emp) => {
    const fullName =
      `${emp.nombre} ${emp.apellido_paterno} ${emp.apellido_materno}`.toLowerCase();
    return fullName.includes(search.toLowerCase());
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-warm-900">Empleados</h2>
          <p className="text-sm text-warm-500">
            {empleados.length} empleados registrados
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" strokeWidth={1.5} />
          Nuevo empleado
        </Button>
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

      {/* List */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filteredEmpleados.map((empleado) => (
          <Card
            key={empleado.id}
            className="cursor-pointer transition-shadow hover:shadow-md"
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Avatar
                  name={`${empleado.nombre} ${empleado.apellido_paterno}`}
                  size="lg"
                />
                <div className="flex-1 overflow-hidden">
                  <h3 className="truncate font-medium text-warm-900">
                    {empleado.nombre} {empleado.apellido_paterno}
                  </h3>
                  <p className="truncate text-sm text-warm-500">
                    {empleado.puesto}
                  </p>
                  <p className="truncate text-xs text-warm-400">
                    {empleado.departamento}
                  </p>
                  <div className="mt-2">
                    <Badge
                      variant={
                        empleado.estado === "activo" ? "success" : "default"
                      }
                    >
                      {empleado.estado === "activo" ? "Activo" : "Inactivo"}
                    </Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredEmpleados.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-warm-500">No se encontraron empleados</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
