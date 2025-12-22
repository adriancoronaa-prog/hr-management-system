"use client";

import { useState, useEffect } from "react";
import { RoleGuard } from "@/components/auth/role-guard";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ExecutiveDashboard,
  PayrollReport,
  VacationReport,
} from "@/components/reportes";
import { BarChart3, DollarSign, Calendar } from "lucide-react";

export default function ReportesPage() {
  const [activeTab, setActiveTab] = useState("dashboard");

  // Persistir tab activo en URL hash
  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (["dashboard", "nomina", "vacaciones"].includes(hash)) {
      setActiveTab(hash);
    }
  }, []);

  const handleTabChange = (value: string) => {
    setActiveTab(value);
    window.location.hash = value;
  };

  return (
    <RoleGuard allowedRoles={["admin", "rrhh", "empleador"]}>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-display font-semibold text-warm-900">
            Centro de Reportes
          </h1>
          <p className="text-warm-500 mt-1">
            Dashboard ejecutivo, analisis de nomina y vacaciones
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={handleTabChange}>
          <TabsList className="grid w-full grid-cols-3 lg:w-auto lg:inline-flex">
            <TabsTrigger value="dashboard" className="gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="nomina" className="gap-2">
              <DollarSign className="h-4 w-4" />
              <span className="hidden sm:inline">Nomina</span>
            </TabsTrigger>
            <TabsTrigger value="vacaciones" className="gap-2">
              <Calendar className="h-4 w-4" />
              <span className="hidden sm:inline">Vacaciones</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="mt-6">
            <ExecutiveDashboard />
          </TabsContent>

          <TabsContent value="nomina" className="mt-6">
            <PayrollReport />
          </TabsContent>

          <TabsContent value="vacaciones" className="mt-6">
            <VacationReport />
          </TabsContent>
        </Tabs>
      </div>
    </RoleGuard>
  );
}
