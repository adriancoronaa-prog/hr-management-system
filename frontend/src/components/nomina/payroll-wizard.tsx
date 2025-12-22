"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { nominaApi, empleadosApi } from "@/lib/api";
import {
  PeriodoNomina,
  ReciboNomina,
  IncidenciaNomina,
  TIPO_PERIODO_OPTIONS,
  TIPO_INCIDENCIA_OPTIONS,
  Empleado,
} from "@/types";
import { formatCurrency } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import {
  Settings,
  AlertCircle,
  Calculator,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Plus,
  Trash2,
  Users,
  DollarSign,
  FileText,
  Loader2,
} from "lucide-react";

interface PayrollWizardProps {
  periodo?: PeriodoNomina;
  onClose: () => void;
  onComplete: () => void;
}

type WizardStep = "config" | "incidencias" | "precalculo" | "cierre";

const STEPS: { id: WizardStep; label: string; icon: React.ReactNode }[] = [
  { id: "config", label: "Configuracion", icon: <Settings className="h-4 w-4" /> },
  { id: "incidencias", label: "Incidencias", icon: <AlertCircle className="h-4 w-4" /> },
  { id: "precalculo", label: "Pre-Calculo", icon: <Calculator className="h-4 w-4" /> },
  { id: "cierre", label: "Cierre", icon: <CheckCircle className="h-4 w-4" /> },
];

export function PayrollWizard({ periodo, onClose, onComplete }: PayrollWizardProps) {
  const queryClient = useQueryClient();
  const [currentStep, setCurrentStep] = useState<WizardStep>("config");
  const [periodoId, setPeriodoId] = useState<string | undefined>(periodo?.id);
  const [showIncidenciaDialog, setShowIncidenciaDialog] = useState(false);

  // Form state for config
  const [formData, setFormData] = useState({
    tipo_periodo: periodo?.tipo_periodo || "quincenal",
    numero_periodo: periodo?.numero_periodo || 1,
    año: periodo?.año || new Date().getFullYear(),
    fecha_inicio: periodo?.fecha_inicio || "",
    fecha_fin: periodo?.fecha_fin || "",
    fecha_pago: periodo?.fecha_pago || "",
  });

  // Form state for new incidencia
  const [incidenciaData, setIncidenciaData] = useState({
    empleado: "",
    tipo: "falta",
    fecha_inicio: "",
    fecha_fin: "",
    monto: "",
    descripcion: "",
  });

  const stepIndex = STEPS.findIndex((s) => s.id === currentStep);

  // Queries
  const { data: incidencias = [], isLoading: loadingIncidencias } = useQuery({
    queryKey: ["incidencias-pendientes", periodoId],
    queryFn: async () => {
      const response = await nominaApi.getIncidenciasPendientes();
      return response.results || response;
    },
    enabled: currentStep === "incidencias" || currentStep === "precalculo",
  });

  const { data: resumen, isLoading: loadingResumen } = useQuery({
    queryKey: ["resumen-periodo", periodoId],
    queryFn: () => nominaApi.getResumenPeriodo(periodoId!),
    enabled: !!periodoId && (currentStep === "precalculo" || currentStep === "cierre"),
  });

  const { data: empleados = [] } = useQuery({
    queryKey: ["empleados-activos"],
    queryFn: async () => {
      const response = await empleadosApi.list({ estado: "activo" });
      return response.results || response;
    },
    enabled: showIncidenciaDialog,
  });

  // Mutations
  const createPeriodoMutation = useMutation({
    mutationFn: nominaApi.createPeriodo,
    onSuccess: (data) => {
      setPeriodoId(data.id);
      toast.success("Periodo creado correctamente");
      setCurrentStep("incidencias");
    },
    onError: () => {
      toast.error("Error al crear el periodo");
    },
  });

  const calcularMutation = useMutation({
    mutationFn: () => nominaApi.calcularPeriodo(periodoId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumen-periodo", periodoId] });
      toast.success("Nomina calculada correctamente");
      setCurrentStep("cierre");
    },
    onError: () => {
      toast.error("Error al calcular la nomina");
    },
  });

  const aprobarMutation = useMutation({
    mutationFn: () => nominaApi.aprobarPeriodo(periodoId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["nomina-periodos"] });
      toast.success("Nomina aprobada correctamente");
      onComplete();
    },
    onError: () => {
      toast.error("Error al aprobar la nomina");
    },
  });

  const createIncidenciaMutation = useMutation({
    mutationFn: nominaApi.createIncidencia,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidencias-pendientes"] });
      toast.success("Incidencia agregada");
      setShowIncidenciaDialog(false);
      setIncidenciaData({
        empleado: "",
        tipo: "falta",
        fecha_inicio: "",
        fecha_fin: "",
        monto: "",
        descripcion: "",
      });
    },
    onError: () => {
      toast.error("Error al agregar incidencia");
    },
  });

  const deleteIncidenciaMutation = useMutation({
    mutationFn: nominaApi.deleteIncidencia,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["incidencias-pendientes"] });
      toast.success("Incidencia eliminada");
    },
  });

  // Handlers
  const handleNext = () => {
    if (currentStep === "config") {
      if (!periodoId) {
        createPeriodoMutation.mutate({
          tipo_periodo: formData.tipo_periodo,
          numero_periodo: formData.numero_periodo,
          año: formData.año,
          fecha_inicio: formData.fecha_inicio,
          fecha_fin: formData.fecha_fin,
          fecha_pago: formData.fecha_pago || undefined,
        });
      } else {
        setCurrentStep("incidencias");
      }
    } else if (currentStep === "incidencias") {
      setCurrentStep("precalculo");
    } else if (currentStep === "precalculo") {
      calcularMutation.mutate();
    } else if (currentStep === "cierre") {
      aprobarMutation.mutate();
    }
  };

  const handleBack = () => {
    const prevIndex = stepIndex - 1;
    if (prevIndex >= 0) {
      setCurrentStep(STEPS[prevIndex].id);
    }
  };

  const handleAddIncidencia = () => {
    if (!incidenciaData.empleado || !incidenciaData.fecha_inicio) {
      toast.error("Completa los campos requeridos");
      return;
    }
    createIncidenciaMutation.mutate({
      empleado: incidenciaData.empleado,
      tipo: incidenciaData.tipo,
      fecha_inicio: incidenciaData.fecha_inicio,
      fecha_fin: incidenciaData.fecha_fin || undefined,
      monto: incidenciaData.monto ? parseFloat(incidenciaData.monto) : undefined,
      descripcion: incidenciaData.descripcion || undefined,
    });
  };

  const isLoading =
    createPeriodoMutation.isPending ||
    calcularMutation.isPending ||
    aprobarMutation.isPending;

  return (
    <div className="space-y-6">
      {/* Stepper */}
      <div className="flex items-center justify-between border-b border-warm-200 pb-4">
        {STEPS.map((step, index) => (
          <div
            key={step.id}
            className={`flex items-center gap-2 ${
              index <= stepIndex ? "text-horizon-600" : "text-warm-400"
            }`}
          >
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full ${
                index < stepIndex
                  ? "bg-horizon-600 text-white"
                  : index === stepIndex
                  ? "bg-horizon-100 text-horizon-600 border-2 border-horizon-600"
                  : "bg-warm-100 text-warm-400"
              }`}
            >
              {index < stepIndex ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                step.icon
              )}
            </div>
            <span className="hidden sm:inline text-sm font-medium">
              {step.label}
            </span>
            {index < STEPS.length - 1 && (
              <div
                className={`hidden sm:block w-12 h-0.5 mx-2 ${
                  index < stepIndex ? "bg-horizon-600" : "bg-warm-200"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="min-h-[400px]">
        {/* Step 1: Config */}
        {currentStep === "config" && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Configurar periodo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-sm font-medium text-warm-700">
                    Tipo de periodo
                  </label>
                  <select
                    className="mt-1 w-full rounded-md border border-warm-300 p-2 text-sm"
                    value={formData.tipo_periodo}
                    onChange={(e) =>
                      setFormData({ ...formData, tipo_periodo: e.target.value as "semanal" | "quincenal" | "mensual" })
                    }
                    disabled={!!periodoId}
                  >
                    {TIPO_PERIODO_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-warm-700">
                    Numero de periodo
                  </label>
                  <Input
                    type="number"
                    min={1}
                    value={formData.numero_periodo}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        numero_periodo: parseInt(e.target.value) || 1,
                      })
                    }
                    disabled={!!periodoId}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-warm-700">Año</label>
                  <Input
                    type="number"
                    min={2020}
                    max={2099}
                    value={formData.año}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        año: parseInt(e.target.value) || new Date().getFullYear(),
                      })
                    }
                    disabled={!!periodoId}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-warm-700">
                    Fecha de pago
                  </label>
                  <Input
                    type="date"
                    value={formData.fecha_pago}
                    onChange={(e) =>
                      setFormData({ ...formData, fecha_pago: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-warm-700">
                    Fecha inicio
                  </label>
                  <Input
                    type="date"
                    value={formData.fecha_inicio}
                    onChange={(e) =>
                      setFormData({ ...formData, fecha_inicio: e.target.value })
                    }
                    disabled={!!periodoId}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-warm-700">
                    Fecha fin
                  </label>
                  <Input
                    type="date"
                    value={formData.fecha_fin}
                    onChange={(e) =>
                      setFormData({ ...formData, fecha_fin: e.target.value })
                    }
                    disabled={!!periodoId}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Incidencias */}
        {currentStep === "incidencias" && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base">Incidencias del periodo</CardTitle>
              <Button size="sm" onClick={() => setShowIncidenciaDialog(true)}>
                <Plus className="h-4 w-4 mr-1" />
                Agregar
              </Button>
            </CardHeader>
            <CardContent>
              {loadingIncidencias ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : incidencias.length === 0 ? (
                <div className="text-center py-8 text-warm-500">
                  <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No hay incidencias pendientes</p>
                  <p className="text-sm">Puedes continuar al siguiente paso</p>
                </div>
              ) : (
                <div className="divide-y divide-warm-100">
                  {(incidencias as IncidenciaNomina[]).map((inc) => (
                    <div
                      key={inc.id}
                      className="flex items-center justify-between py-3"
                    >
                      <div>
                        <p className="font-medium text-warm-900">
                          {inc.empleado_nombre}
                        </p>
                        <p className="text-sm text-warm-500">
                          {inc.tipo_display || inc.tipo} • {inc.fecha_inicio}
                          {inc.monto ? ` • ${formatCurrency(inc.monto)}` : ""}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteIncidenciaMutation.mutate(inc.id)}
                      >
                        <Trash2 className="h-4 w-4 text-warm-400" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Step 3: Pre-Calculo */}
        {currentStep === "precalculo" && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Vista previa del calculo</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingResumen ? (
                <div className="space-y-4">
                  <div className="grid gap-4 sm:grid-cols-3">
                    {[1, 2, 3].map((i) => (
                      <Skeleton key={i} className="h-20" />
                    ))}
                  </div>
                  <Skeleton className="h-40" />
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="p-4 rounded-lg bg-warm-50">
                      <div className="flex items-center gap-2 text-warm-600 mb-1">
                        <Users className="h-4 w-4" />
                        <span className="text-sm">Empleados</span>
                      </div>
                      <p className="text-2xl font-semibold text-warm-900">
                        {resumen?.total_empleados || 0}
                      </p>
                    </div>
                    <div className="p-4 rounded-lg bg-sage-50">
                      <div className="flex items-center gap-2 text-sage-600 mb-1">
                        <DollarSign className="h-4 w-4" />
                        <span className="text-sm">Percepciones</span>
                      </div>
                      <p className="text-2xl font-semibold text-sage-700">
                        {formatCurrency(resumen?.total_percepciones || 0)}
                      </p>
                    </div>
                    <div className="p-4 rounded-lg bg-horizon-50">
                      <div className="flex items-center gap-2 text-horizon-600 mb-1">
                        <FileText className="h-4 w-4" />
                        <span className="text-sm">Neto a pagar</span>
                      </div>
                      <p className="text-2xl font-semibold text-horizon-700">
                        {formatCurrency(resumen?.total_neto || 0)}
                      </p>
                    </div>
                  </div>

                  <div className="border rounded-lg overflow-hidden">
                    <table className="w-full text-sm">
                      <thead className="bg-warm-50">
                        <tr>
                          <th className="text-left p-3 font-medium text-warm-700">
                            Empleado
                          </th>
                          <th className="text-right p-3 font-medium text-warm-700">
                            Percepciones
                          </th>
                          <th className="text-right p-3 font-medium text-warm-700">
                            Deducciones
                          </th>
                          <th className="text-right p-3 font-medium text-warm-700">
                            Neto
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-warm-100">
                        {(resumen?.recibos || []).slice(0, 5).map((recibo: ReciboNomina) => (
                          <tr key={recibo.id}>
                            <td className="p-3 text-warm-900">
                              {recibo.empleado_nombre}
                            </td>
                            <td className="p-3 text-right text-warm-600">
                              {formatCurrency(recibo.total_percepciones)}
                            </td>
                            <td className="p-3 text-right text-warm-600">
                              {formatCurrency(recibo.total_deducciones)}
                            </td>
                            <td className="p-3 text-right font-medium text-warm-900">
                              {formatCurrency(recibo.neto_a_pagar)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {(resumen?.recibos?.length || 0) > 5 && (
                      <div className="p-3 text-center text-sm text-warm-500 bg-warm-50">
                        Y {resumen.recibos.length - 5} empleados mas...
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Step 4: Cierre */}
        {currentStep === "cierre" && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Confirmar y aprobar</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="p-6 rounded-lg bg-sage-50 border border-sage-200">
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle className="h-8 w-8 text-sage-600" />
                    <div>
                      <h3 className="font-semibold text-sage-900">
                        Nomina lista para aprobar
                      </h3>
                      <p className="text-sm text-sage-600">
                        Revisa los totales antes de confirmar
                      </p>
                    </div>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-3">
                    <div>
                      <p className="text-sm text-sage-600">Empleados</p>
                      <p className="text-xl font-semibold text-sage-900">
                        {resumen?.total_empleados || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-sage-600">Total deducciones</p>
                      <p className="text-xl font-semibold text-sage-900">
                        {formatCurrency(resumen?.total_deducciones || 0)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-sage-600">Neto a dispersar</p>
                      <p className="text-xl font-semibold text-sage-900">
                        {formatCurrency(resumen?.total_neto || 0)}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-amber-50 border border-amber-200">
                  <p className="text-sm text-amber-800">
                    <strong>Importante:</strong> Una vez aprobada, la nomina no podra
                    ser modificada. Los recibos quedaran disponibles para su
                    descarga.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-warm-200">
        <Button variant="ghost" onClick={stepIndex === 0 ? onClose : handleBack}>
          <ChevronLeft className="h-4 w-4 mr-1" />
          {stepIndex === 0 ? "Cancelar" : "Atras"}
        </Button>
        <Button onClick={handleNext} disabled={isLoading}>
          {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
          {currentStep === "cierre" ? "Aprobar nomina" : "Siguiente"}
          {currentStep !== "cierre" && <ChevronRight className="h-4 w-4 ml-1" />}
        </Button>
      </div>

      {/* Dialog for adding incidencia */}
      <Dialog open={showIncidenciaDialog} onOpenChange={setShowIncidenciaDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Agregar incidencia</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-warm-700">Empleado</label>
              <select
                className="mt-1 w-full rounded-md border border-warm-300 p-2 text-sm"
                value={incidenciaData.empleado}
                onChange={(e) =>
                  setIncidenciaData({ ...incidenciaData, empleado: e.target.value })
                }
              >
                <option value="">Seleccionar empleado</option>
                {(empleados as Empleado[]).map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.nombre_completo || `${emp.nombre} ${emp.apellido_paterno}`}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-warm-700">Tipo</label>
              <select
                className="mt-1 w-full rounded-md border border-warm-300 p-2 text-sm"
                value={incidenciaData.tipo}
                onChange={(e) =>
                  setIncidenciaData({ ...incidenciaData, tipo: e.target.value })
                }
              >
                {TIPO_INCIDENCIA_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium text-warm-700">
                  Fecha inicio
                </label>
                <Input
                  type="date"
                  value={incidenciaData.fecha_inicio}
                  onChange={(e) =>
                    setIncidenciaData({
                      ...incidenciaData,
                      fecha_inicio: e.target.value,
                    })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium text-warm-700">
                  Fecha fin (opcional)
                </label>
                <Input
                  type="date"
                  value={incidenciaData.fecha_fin}
                  onChange={(e) =>
                    setIncidenciaData({
                      ...incidenciaData,
                      fecha_fin: e.target.value,
                    })
                  }
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-warm-700">
                Monto (opcional)
              </label>
              <Input
                type="number"
                step="0.01"
                placeholder="0.00"
                value={incidenciaData.monto}
                onChange={(e) =>
                  setIncidenciaData({ ...incidenciaData, monto: e.target.value })
                }
              />
            </div>
            <div>
              <label className="text-sm font-medium text-warm-700">
                Descripcion (opcional)
              </label>
              <Input
                placeholder="Notas adicionales..."
                value={incidenciaData.descripcion}
                onChange={(e) =>
                  setIncidenciaData({
                    ...incidenciaData,
                    descripcion: e.target.value,
                  })
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="ghost"
              onClick={() => setShowIncidenciaDialog(false)}
            >
              Cancelar
            </Button>
            <Button
              onClick={handleAddIncidencia}
              disabled={createIncidenciaMutation.isPending}
            >
              {createIncidenciaMutation.isPending && (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              )}
              Agregar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
