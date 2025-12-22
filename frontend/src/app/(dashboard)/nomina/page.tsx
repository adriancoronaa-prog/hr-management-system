"use client";

import { useState, useEffect } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { useCanManage } from "@/components/auth/role-guard";
import { PayrollHistory, PayrollWizard, MyPayslips } from "@/components/nomina";
import { PeriodoNomina } from "@/types";
import { Loader2 } from "lucide-react";

type ViewMode = "history" | "wizard";

export default function NominaPage() {
  const { user } = useAuthStore();
  const canManage = useCanManage(); // true para admin, rrhh, empleador
  const [mounted, setMounted] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>("history");
  const [selectedPeriodo, setSelectedPeriodo] = useState<PeriodoNomina | undefined>();

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

  const handleSelectPeriodo = (periodo: PeriodoNomina) => {
    setSelectedPeriodo(periodo);
    setViewMode("wizard");
  };

  const handleNewPeriodo = () => {
    setSelectedPeriodo(undefined);
    setViewMode("wizard");
  };

  const handleCloseWizard = () => {
    setSelectedPeriodo(undefined);
    setViewMode("history");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-semibold text-warm-900">
          Nomina
        </h1>
        <p className="text-sm text-warm-500 mt-1">
          {canManage
            ? viewMode === "wizard"
              ? "Procesa la nomina paso a paso"
              : "Gestiona los periodos de nomina"
            : "Consulta tus recibos de nomina"}
        </p>
      </div>

      {/* Vista segun rol */}
      {canManage ? (
        viewMode === "wizard" ? (
          <PayrollWizard
            periodo={selectedPeriodo}
            onClose={handleCloseWizard}
            onComplete={handleCloseWizard}
          />
        ) : (
          <PayrollHistory
            onSelectPeriodo={handleSelectPeriodo}
            onNewPeriodo={handleNewPeriodo}
          />
        )
      ) : (
        <MyPayslips />
      )}
    </div>
  );
}
