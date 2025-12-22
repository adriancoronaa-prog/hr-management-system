"use client";

import { useState, useEffect } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { useCanManage } from "@/components/auth/role-guard";
import { EmployeeView } from "@/components/vacaciones/employee-view";
import { ManagerView } from "@/components/vacaciones/manager-view";
import { Loader2 } from "lucide-react";

export default function VacacionesPage() {
  const { user } = useAuthStore();
  const canManage = useCanManage(); // true para admin, rrhh, empleador
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-horizon-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-semibold text-warm-900">
          Vacaciones
        </h1>
        <p className="text-sm text-warm-500 mt-1">
          {canManage
            ? "Gestiona las solicitudes de tu equipo"
            : "Consulta tu saldo y solicita días libres"}
        </p>
      </div>

      {/* Vista según rol */}
      {canManage ? <ManagerView /> : <EmployeeView />}
    </div>
  );
}
