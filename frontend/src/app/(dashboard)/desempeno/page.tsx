"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { desempenoApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { useChatStore } from "@/stores/chat-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Target,
  TrendingUp,
  Users,
  Star,
  MessageSquare,
  Loader2,
  BarChart3,
  Award,
  Clock,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { AsignacionKPI, Evaluacion, Matriz9Box } from "@/types/desempeno";
import { CLASIFICACIONES_9BOX } from "@/types/desempeno";

export default function DesempenoPage() {
  const { user } = useAuthStore();
  const { setIsOpen, sendMessage } = useChatStore();
  const [activeTab, setActiveTab] = useState("mis-kpis");

  const isManager = user?.rol === 'admin' || user?.rol === 'empleador' || user?.rol === 'rrhh';

  // Query: Mis KPIs
  const { data: misKPIs, isLoading: loadingMisKPIs } = useQuery({
    queryKey: ["mis-kpis"],
    queryFn: desempenoApi.getMisKPIsActivos,
  });

  // Query: Resumen
  const { data: resumen } = useQuery({
    queryKey: ["resumen-kpis"],
    queryFn: desempenoApi.getResumenKPIs,
  });

  // Query: KPIs del equipo (solo managers)
  const { data: kpisEquipo, isLoading: loadingEquipo } = useQuery({
    queryKey: ["equipo-kpis"],
    queryFn: desempenoApi.getKPIsEquipo,
    enabled: isManager,
  });

  // Query: Mis evaluaciones
  const { data: misEvaluaciones } = useQuery({
    queryKey: ["mis-evaluaciones"],
    queryFn: desempenoApi.getMisEvaluaciones,
  });

  // Query: Matriz 9-box (solo managers)
  const { data: matriz9box } = useQuery({
    queryKey: ["matriz-9box"],
    queryFn: desempenoApi.getMatriz9Box,
    enabled: isManager,
  });

  const handleChatAction = (mensaje: string) => {
    setIsOpen(true);
    setTimeout(() => sendMessage(mensaje), 100);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Desempeno</h1>
          <p className="text-gray-500 mt-1">
            Gestiona KPIs, evaluaciones y desarrollo profesional
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => handleChatAction("Cuales son mis KPIs activos?")}
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Preguntar a IA
          </Button>
        </div>
      </div>

      {/* Resumen Cards */}
      {resumen && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Target className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{resumen.activos}</p>
                  <p className="text-sm text-gray-500">KPIs Activos</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-green-100 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {resumen.promedio_cumplimiento ? `${resumen.promedio_cumplimiento}%` : '-'}
                  </p>
                  <p className="text-sm text-gray-500">Cumplimiento Promedio</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-amber-100 rounded-lg">
                  <Clock className="h-6 w-6 text-amber-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{resumen.pendientes_cambio}</p>
                  <p className="text-sm text-gray-500">Cambios Pendientes</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Award className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{misEvaluaciones?.length || 0}</p>
                  <p className="text-sm text-gray-500">Evaluaciones</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="mis-kpis" className="gap-2">
            <Target className="h-4 w-4" />
            Mis KPIs
          </TabsTrigger>
          {isManager && (
            <TabsTrigger value="equipo" className="gap-2">
              <Users className="h-4 w-4" />
              Equipo
            </TabsTrigger>
          )}
          <TabsTrigger value="evaluaciones" className="gap-2">
            <BarChart3 className="h-4 w-4" />
            Evaluaciones
          </TabsTrigger>
          {isManager && (
            <TabsTrigger value="matriz" className="gap-2">
              <Star className="h-4 w-4" />
              Matriz 9-Box
            </TabsTrigger>
          )}
        </TabsList>

        {/* Tab: Mis KPIs */}
        <TabsContent value="mis-kpis" className="space-y-4">
          {loadingMisKPIs ? (
            <div className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
            </div>
          ) : !misKPIs || misKPIs.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Target className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900">Sin KPIs asignados</h3>
                <p className="text-gray-500 mt-1">
                  No tienes KPIs activos en este momento
                </p>
                <Button
                  className="mt-4"
                  onClick={() => handleChatAction("Asignarme un KPI de ejemplo")}
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Solicitar KPI via Chat
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {misKPIs.map((kpi) => (
                <KPICard
                  key={kpi.id}
                  kpi={kpi}
                  onAction={(action) => handleChatAction(action)}
                />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Tab: Equipo */}
        {isManager && (
          <TabsContent value="equipo" className="space-y-4">
            {loadingEquipo ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : !kpisEquipo || kpisEquipo.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <Users className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900">Sin KPIs de equipo</h3>
                  <p className="text-gray-500 mt-1">
                    No hay KPIs asignados a tu equipo
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {/* Agrupar por empleado */}
                {Object.entries(
                  kpisEquipo.reduce((acc, kpi) => {
                    const nombre = kpi.empleado_nombre || 'Sin asignar';
                    if (!acc[nombre]) acc[nombre] = [];
                    acc[nombre].push(kpi);
                    return acc;
                  }, {} as Record<string, AsignacionKPI[]>)
                ).map(([empleado, kpis]) => (
                  <Card key={empleado}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        {empleado}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {kpis.map((kpi) => (
                          <div
                            key={kpi.id}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <div>
                              <p className="font-medium">{kpi.nombre_kpi}</p>
                              <p className="text-sm text-gray-500">{kpi.periodo}</p>
                            </div>
                            <div className="text-right">
                              <ProgressBadge porcentaje={kpi.porcentaje_cumplimiento} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        )}

        {/* Tab: Evaluaciones */}
        <TabsContent value="evaluaciones" className="space-y-4">
          {!misEvaluaciones || misEvaluaciones.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <BarChart3 className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900">Sin evaluaciones</h3>
                <p className="text-gray-500 mt-1">
                  No tienes evaluaciones de desempeno registradas
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {misEvaluaciones.map((eval_) => (
                <EvaluacionCard key={eval_.id} evaluacion={eval_} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* Tab: Matriz 9-Box */}
        {isManager && (
          <TabsContent value="matriz" className="space-y-4">
            <Matriz9BoxGrid matriz={matriz9box || {}} />
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}

// Componente: KPI Card
function KPICard({ kpi, onAction }: { kpi: AsignacionKPI; onAction: (action: string) => void }) {
  const porcentaje = kpi.porcentaje_cumplimiento || 0;

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="font-semibold text-gray-900">{kpi.nombre_kpi}</h3>
            <p className="text-sm text-gray-500">{kpi.periodo}</p>
          </div>
          <div className="flex items-center gap-2">
            {kpi.tiene_cambios_pendientes && (
              <Badge variant="warning">
                <Clock className="h-3 w-3 mr-1" />
                Cambio pendiente
              </Badge>
            )}
            <Badge className={cn(
              kpi.estado === 'activo' ? 'bg-green-100 text-green-800' :
              kpi.estado === 'evaluado' ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            )}>
              {kpi.estado_display || kpi.estado}
            </Badge>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Progreso</span>
            <span className="font-medium">{porcentaje.toFixed(1)}%</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all",
                porcentaje >= 100 ? "bg-green-500" :
                porcentaje >= 70 ? "bg-blue-500" :
                porcentaje >= 40 ? "bg-amber-500" :
                "bg-red-500"
              )}
              style={{ width: `${Math.min(porcentaje, 100)}%` }}
            />
          </div>
        </div>

        {/* Meta y Logrado */}
        <div className="flex gap-6 text-sm mb-4">
          <div>
            <span className="text-gray-500">Meta:</span>
            <span className="font-medium ml-1">{kpi.meta.toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-500">Logrado:</span>
            <span className="font-medium ml-1">
              {kpi.valor_logrado?.toLocaleString() || '0'}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Peso:</span>
            <span className="font-medium ml-1">{kpi.peso}%</span>
          </div>
        </div>

        {/* Acciones */}
        <div className="flex gap-2 pt-4 border-t">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onAction(`Registrar avance en mi KPI ${kpi.nombre_kpi}`)}
          >
            <TrendingUp className="h-4 w-4 mr-1" />
            Registrar Avance
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onAction(`Solicitar cambio en mi KPI ${kpi.nombre_kpi}`)}
          >
            Solicitar Cambio
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Componente: Progress Badge
function ProgressBadge({ porcentaje }: { porcentaje?: number }) {
  const p = porcentaje || 0;
  return (
    <div className={cn(
      "px-2 py-1 rounded text-sm font-medium",
      p >= 100 ? "bg-green-100 text-green-800" :
      p >= 70 ? "bg-blue-100 text-blue-800" :
      p >= 40 ? "bg-amber-100 text-amber-800" :
      "bg-red-100 text-red-800"
    )}>
      {p.toFixed(0)}%
    </div>
  );
}

// Componente: Evaluacion Card
function EvaluacionCard({ evaluacion }: { evaluacion: Evaluacion }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-semibold text-gray-900">
              Evaluacion {evaluacion.tipo_display || evaluacion.tipo}
            </h3>
            <p className="text-sm text-gray-500">Periodo: {evaluacion.periodo}</p>
          </div>
          <div className="text-right">
            {evaluacion.puntuacion_final && (
              <p className="text-2xl font-bold text-horizon-600">
                {evaluacion.puntuacion_final}%
              </p>
            )}
            {evaluacion.clasificacion_9box && (
              <Badge variant="default">{evaluacion.clasificacion_9box}</Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Componente: Matriz 9-Box Grid
function Matriz9BoxGrid({ matriz }: { matriz: Matriz9Box }) {
  const grid = [
    ['Experto Tecnico', 'Alto Desempeno', 'Estrella'],
    ['Efectivo', 'Colaborador Clave', 'Futuro Lider'],
    ['Accion Requerida', 'En Desarrollo', 'Enigma'],
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matriz de Talento 9-Box</CardTitle>
        <CardDescription>
          Clasificacion del equipo por desempeno y potencial
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-2">
          {grid.map((row) => (
            row.map((cell) => {
              const empleados = matriz[cell] || [];
              const config = CLASIFICACIONES_9BOX.find(c => c.key === cell);

              return (
                <div
                  key={cell}
                  className={cn(
                    "p-3 rounded-lg min-h-[100px]",
                    config?.color || "bg-gray-100"
                  )}
                >
                  <p className="text-xs font-medium text-white/90 mb-2">
                    {config?.label || cell}
                  </p>
                  <div className="space-y-1">
                    {empleados.slice(0, 3).map((emp) => (
                      <p key={emp.id} className="text-xs text-white truncate">
                        {emp.nombre}
                      </p>
                    ))}
                    {empleados.length > 3 && (
                      <p className="text-xs text-white/70">
                        +{empleados.length - 3} mas
                      </p>
                    )}
                    {empleados.length === 0 && (
                      <p className="text-xs text-white/50 italic">Sin empleados</p>
                    )}
                  </div>
                </div>
              );
            })
          ))}
        </div>

        {/* Leyenda */}
        <div className="mt-4 flex justify-between text-xs text-gray-500">
          <div className="text-center">
            <p>Bajo Potencial</p>
          </div>
          <div className="text-center">
            <p>Potencial Medio</p>
          </div>
          <div className="text-center">
            <p>Alto Potencial</p>
          </div>
        </div>
        <div className="flex flex-col items-start text-xs text-gray-500 mt-2">
          <p>Alto Desempeno</p>
          <p>Desempeno Medio</p>
          <p>Bajo Desempeno</p>
        </div>
      </CardContent>
    </Card>
  );
}
