"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { prestacionesApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Gift,
  Calculator,
  Wallet,
  Heart,
  Clock,
  GraduationCap,
  Users,
  Package,
  ChevronRight,
  Star,
  Loader2,
  Building2,
  Calendar,
  Percent,
  DollarSign,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { CATEGORIAS_PRESTACION } from "@/types/prestaciones";
import type { PlanPrestaciones, PrestacionAdicional } from "@/types/prestaciones";

const getCategoryIcon = (categoria: string) => {
  const icons: Record<string, React.ComponentType<{ className?: string }>> = {
    economica: Wallet,
    salud: Heart,
    tiempo: Clock,
    desarrollo: GraduationCap,
    familia: Users,
    otro: Package,
  };
  return icons[categoria] || Package;
};

const getCategoryStyle = (categoria: string) => {
  const cat = CATEGORIAS_PRESTACION.find(c => c.value === categoria);
  return cat?.color || 'text-gray-600 bg-gray-100';
};

export default function PrestacionesPage() {
  const { empresaActual } = useAuthStore();
  const [selectedPlan, setSelectedPlan] = useState<PlanPrestaciones | null>(null);

  const { data: planes, isLoading } = useQuery({
    queryKey: ["prestaciones-planes", empresaActual?.id],
    queryFn: prestacionesApi.getPlanes,
    enabled: !!empresaActual?.id,
  });

  const { data: referenciaLey } = useQuery({
    queryKey: ["prestaciones-referencia-ley"],
    queryFn: prestacionesApi.getReferenciaLey,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-horizon-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Prestaciones</h1>
          <p className="text-gray-500 mt-1">
            Gestiona los planes de prestaciones de {empresaActual?.nombre_comercial || empresaActual?.razon_social}
          </p>
        </div>
      </div>

      <Tabs defaultValue="planes" className="space-y-6">
        <TabsList>
          <TabsTrigger value="planes" className="gap-2">
            <Gift className="h-4 w-4" />
            Planes
          </TabsTrigger>
          <TabsTrigger value="calculadoras" className="gap-2">
            <Calculator className="h-4 w-4" />
            Calculadoras
          </TabsTrigger>
          <TabsTrigger value="ley" className="gap-2">
            <Building2 className="h-4 w-4" />
            Referencia Ley
          </TabsTrigger>
        </TabsList>

        {/* Tab: Planes */}
        <TabsContent value="planes" className="space-y-6">
          {!planes || planes.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Gift className="h-12 w-12 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900">Sin planes configurados</h3>
                <p className="text-gray-500 mt-1">
                  Usa el Chat IA para crear un plan de prestaciones
                </p>
                <p className="text-sm text-gray-400 mt-4">
                  Ejemplo: &quot;Crear plan de prestaciones estandar con vales de despensa y SGMM&quot;
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {planes.map((plan) => (
                <PlanCard
                  key={plan.id}
                  plan={plan}
                  onSelect={() => setSelectedPlan(plan)}
                  isSelected={selectedPlan?.id === plan.id}
                />
              ))}
            </div>
          )}

          {/* Detalle del plan seleccionado */}
          {selectedPlan && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Gift className="h-5 w-5" />
                  {selectedPlan.nombre}
                  {selectedPlan.es_default && (
                    <Badge variant="default" className="ml-2">
                      <Star className="h-3 w-3 mr-1" />
                      Default
                    </Badge>
                  )}
                </CardTitle>
                <CardDescription>{selectedPlan.descripcion}</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Prestaciones de ley mejoradas */}
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-700 mb-3">Prestaciones de Ley (Superiores al Minimo)</h4>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center gap-2 text-blue-700 mb-1">
                        <Calendar className="h-4 w-4" />
                        <span className="font-medium">Vacaciones Extra</span>
                      </div>
                      <p className="text-2xl font-bold text-blue-900">
                        +{selectedPlan.vacaciones_dias_extra} dias
                      </p>
                      <p className="text-xs text-blue-600">sobre los de ley</p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center gap-2 text-green-700 mb-1">
                        <Percent className="h-4 w-4" />
                        <span className="font-medium">Prima Vacacional</span>
                      </div>
                      <p className="text-2xl font-bold text-green-900">
                        {selectedPlan.prima_vacacional_porcentaje}%
                      </p>
                      <p className="text-xs text-green-600">minimo ley: 25%</p>
                    </div>
                    <div className="p-4 bg-amber-50 rounded-lg">
                      <div className="flex items-center gap-2 text-amber-700 mb-1">
                        <DollarSign className="h-4 w-4" />
                        <span className="font-medium">Aguinaldo</span>
                      </div>
                      <p className="text-2xl font-bold text-amber-900">
                        {selectedPlan.aguinaldo_dias} dias
                      </p>
                      <p className="text-xs text-amber-600">minimo ley: 15 dias</p>
                    </div>
                  </div>
                </div>

                {/* Prestaciones adicionales */}
                {selectedPlan.prestaciones_adicionales && selectedPlan.prestaciones_adicionales.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Prestaciones Adicionales</h4>
                    <div className="space-y-2">
                      {selectedPlan.prestaciones_adicionales.map((prest) => (
                        <PrestacionRow key={prest.id} prestacion={prest} />
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Tab: Calculadoras */}
        <TabsContent value="calculadoras" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <CalculadoraAguinaldo />
            <CalculadoraPrimaVacacional />
          </div>
        </TabsContent>

        {/* Tab: Referencia Ley */}
        <TabsContent value="ley" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Prestaciones Minimas de Ley (Mexico)</CardTitle>
              <CardDescription>
                Referencia de la Ley Federal del Trabajo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Vacaciones */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Vacaciones (Art. 76 LFT)</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-3 font-medium">Anos de servicio</th>
                          <th className="text-left py-2 px-3 font-medium">Dias de vacaciones</th>
                        </tr>
                      </thead>
                      <tbody>
                        {referenciaLey?.vacaciones_por_antiguedad ? (
                          Object.entries(referenciaLey.vacaciones_por_antiguedad).map(([anos, dias]) => (
                            <tr key={anos} className="border-b">
                              <td className="py-2 px-3">{anos} {parseInt(anos) === 1 ? 'ano' : 'anos'}</td>
                              <td className="py-2 px-3">{dias} dias</td>
                            </tr>
                          ))
                        ) : (
                          <>
                            <tr className="border-b"><td className="py-2 px-3">1 ano</td><td className="py-2 px-3">12 dias</td></tr>
                            <tr className="border-b"><td className="py-2 px-3">2 anos</td><td className="py-2 px-3">14 dias</td></tr>
                            <tr className="border-b"><td className="py-2 px-3">3 anos</td><td className="py-2 px-3">16 dias</td></tr>
                            <tr className="border-b"><td className="py-2 px-3">4 anos</td><td className="py-2 px-3">18 dias</td></tr>
                            <tr className="border-b"><td className="py-2 px-3">5 anos</td><td className="py-2 px-3">20 dias</td></tr>
                            <tr className="border-b"><td className="py-2 px-3">6-10 anos</td><td className="py-2 px-3">22 dias</td></tr>
                            <tr className="border-b"><td className="py-2 px-3">11-15 anos</td><td className="py-2 px-3">24 dias</td></tr>
                            <tr><td className="py-2 px-3">16-20 anos</td><td className="py-2 px-3">26 dias</td></tr>
                          </>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Prima vacacional */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Prima Vacacional (Art. 80 LFT)</h4>
                  <p className="text-gray-600">
                    Minimo {referenciaLey?.prima_vacacional_minima || 25}% sobre el salario correspondiente a los dias de vacaciones.
                  </p>
                </div>

                {/* Aguinaldo */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Aguinaldo (Art. 87 LFT)</h4>
                  <p className="text-gray-600">
                    Minimo {referenciaLey?.aguinaldo_minimo_dias || 15} dias de salario, pagadero antes del 20 de diciembre.
                    Si no se laboro el ano completo, se paga proporcional.
                  </p>
                </div>

                {/* Prima dominical */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Prima Dominical (Art. 71 LFT)</h4>
                  <p className="text-gray-600">
                    {referenciaLey?.prima_dominical || 25}% adicional sobre el salario de los dias domingo trabajados.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Componente: Card de Plan
function PlanCard({ plan, onSelect, isSelected }: { plan: PlanPrestaciones; onSelect: () => void; isSelected: boolean }) {
  return (
    <Card
      className={cn(
        "cursor-pointer transition-all hover:shadow-md",
        isSelected && "ring-2 ring-horizon-500"
      )}
      onClick={onSelect}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              {plan.nombre}
              {plan.es_default && (
                <Badge variant="default" className="text-xs">
                  <Star className="h-3 w-3 mr-1" />
                  Default
                </Badge>
              )}
            </CardTitle>
            {plan.descripcion && (
              <CardDescription className="mt-1">{plan.descripcion}</CardDescription>
            )}
          </div>
          <ChevronRight className={cn(
            "h-5 w-5 text-gray-400 transition-transform",
            isSelected && "rotate-90"
          )} />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex gap-4 text-sm">
          <div>
            <span className="text-gray-500">Aguinaldo:</span>
            <span className="font-medium ml-1">{plan.aguinaldo_dias} dias</span>
          </div>
          <div>
            <span className="text-gray-500">Prima:</span>
            <span className="font-medium ml-1">{plan.prima_vacacional_porcentaje}%</span>
          </div>
          {plan.vacaciones_dias_extra > 0 && (
            <div>
              <span className="text-gray-500">Vac. extra:</span>
              <span className="font-medium ml-1">+{plan.vacaciones_dias_extra}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Componente: Fila de prestacion adicional
function PrestacionRow({ prestacion }: { prestacion: PrestacionAdicional }) {
  const Icon = getCategoryIcon(prestacion.categoria);
  const colorClass = getCategoryStyle(prestacion.categoria);

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
      <div className={cn("p-2 rounded-lg", colorClass)}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1">
        <p className="font-medium text-gray-900">{prestacion.nombre}</p>
        {prestacion.descripcion && (
          <p className="text-xs text-gray-500">{prestacion.descripcion}</p>
        )}
      </div>
      <div className="text-right">
        <p className="font-medium text-gray-900">
          {prestacion.tipo_valor === 'monto' && '$'}
          {prestacion.valor}
          {prestacion.tipo_valor === 'porcentaje' && '%'}
        </p>
        <p className="text-xs text-gray-500 capitalize">{prestacion.periodicidad}</p>
      </div>
    </div>
  );
}

// Componente: Calculadora de Aguinaldo
function CalculadoraAguinaldo() {
  const [salarioDiario, setSalarioDiario] = useState<string>("");
  const [diasAguinaldo, setDiasAguinaldo] = useState<string>("15");
  const [diasTrabajados, setDiasTrabajados] = useState<string>("365");

  const calcular = () => {
    const sd = parseFloat(salarioDiario) || 0;
    const da = parseFloat(diasAguinaldo) || 15;
    const dt = parseFloat(diasTrabajados) || 365;

    const proporcional = dt < 365 ? dt / 365 : 1;
    const bruto = sd * da * proporcional;

    // ISR simplificado (aproximado)
    const exento = 30 * 248.93; // 30 UMAs (2024 aprox)
    const gravado = Math.max(0, bruto - exento);
    const isrAprox = gravado * 0.20; // Tasa aproximada
    const neto = bruto - isrAprox;

    return { bruto, exento: Math.min(bruto, exento), gravado, isrAprox, neto };
  };

  const resultado = salarioDiario ? calcular() : null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="h-5 w-5" />
          Calculadora de Aguinaldo
        </CardTitle>
        <CardDescription>Calcula el aguinaldo bruto y neto aproximado</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-700">Salario diario</label>
          <input
            type="number"
            value={salarioDiario}
            onChange={(e) => setSalarioDiario(e.target.value)}
            placeholder="0.00"
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-horizon-500 focus:border-transparent"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Dias aguinaldo</label>
            <input
              type="number"
              value={diasAguinaldo}
              onChange={(e) => setDiasAguinaldo(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-horizon-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Dias trabajados</label>
            <input
              type="number"
              value={diasTrabajados}
              onChange={(e) => setDiasTrabajados(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-horizon-500 focus:border-transparent"
            />
          </div>
        </div>

        {resultado && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Aguinaldo bruto:</span>
              <span className="font-medium">${resultado.bruto.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Parte exenta:</span>
              <span className="text-green-600">${resultado.exento.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">ISR aproximado:</span>
              <span className="text-red-600">-${resultado.isrAprox.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="flex justify-between pt-2 border-t font-medium">
              <span>Neto aproximado:</span>
              <span className="text-horizon-600">${resultado.neto.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Componente: Calculadora de Prima Vacacional
function CalculadoraPrimaVacacional() {
  const [salarioDiario, setSalarioDiario] = useState<string>("");
  const [diasVacaciones, setDiasVacaciones] = useState<string>("12");
  const [porcentajePrima, setPorcentajePrima] = useState<string>("25");

  const calcular = () => {
    const sd = parseFloat(salarioDiario) || 0;
    const dv = parseFloat(diasVacaciones) || 12;
    const pp = parseFloat(porcentajePrima) || 25;

    const salarioVacaciones = sd * dv;
    const prima = salarioVacaciones * (pp / 100);

    return { salarioVacaciones, prima };
  };

  const resultado = salarioDiario ? calcular() : null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Percent className="h-5 w-5" />
          Calculadora de Prima Vacacional
        </CardTitle>
        <CardDescription>Calcula la prima vacacional</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-700">Salario diario</label>
          <input
            type="number"
            value={salarioDiario}
            onChange={(e) => setSalarioDiario(e.target.value)}
            placeholder="0.00"
            className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-horizon-500 focus:border-transparent"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Dias vacaciones</label>
            <input
              type="number"
              value={diasVacaciones}
              onChange={(e) => setDiasVacaciones(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-horizon-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">% Prima</label>
            <input
              type="number"
              value={porcentajePrima}
              onChange={(e) => setPorcentajePrima(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-horizon-500 focus:border-transparent"
            />
          </div>
        </div>

        {resultado && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Salario vacaciones:</span>
              <span className="font-medium">${resultado.salarioVacaciones.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="flex justify-between pt-2 border-t font-medium">
              <span>Prima vacacional:</span>
              <span className="text-horizon-600">${resultado.prima.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
