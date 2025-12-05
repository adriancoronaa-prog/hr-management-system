"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  FileText,
  Calendar,
  AlertCircle,
  UserPlus,
  ClipboardList,
  Palmtree,
  ChevronRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChatContainer } from "@/components/chat/chat-container";
import { useAuthStore } from "@/stores/auth-store";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

function formatCurrency(value: number): string {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
  }).format(value);
}

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  href?: string;
  loading?: boolean;
}

function MetricCard({ title, value, icon, subtitle, href, loading }: MetricCardProps) {
  const content = (
    <Card className="h-full min-h-[120px] transition-shadow hover:shadow-md">
      <CardContent className="flex h-full flex-col justify-between p-4">
        <div className="flex items-start justify-between">
          <p className="text-sm font-medium text-warm-500">{title}</p>
          <div className="rounded-md bg-horizon-50 p-2 text-horizon-600">
            {icon}
          </div>
        </div>
        <div>
          {loading ? (
            <Skeleton className="h-8 w-20" />
          ) : (
            <p className="text-2xl font-semibold text-warm-900">{value}</p>
          )}
          {subtitle && (
            <p className="mt-1 text-xs text-warm-400">{subtitle}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );

  if (href) {
    return (
      <Link href={href} className="block h-full">
        {content}
      </Link>
    );
  }
  return content;
}

interface ActionButtonProps {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
}

function ActionButton({ title, href, icon: Icon }: ActionButtonProps) {
  return (
    <Link
      href={href}
      className="flex items-center justify-between rounded-lg border border-warm-200 p-3 transition-colors hover:border-horizon-300 hover:bg-horizon-50 group"
    >
      <div className="flex items-center gap-3">
        <Icon className="h-5 w-5 text-warm-400 group-hover:text-horizon-600" strokeWidth={1.5} />
        <span className="text-sm text-warm-700 group-hover:text-warm-900">{title}</span>
      </div>
      <ChevronRight className="h-4 w-4 text-warm-300 group-hover:text-horizon-500" strokeWidth={1.5} />
    </Link>
  );
}

export default function DashboardPage() {
  const { user, empresaActual } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Query para estadísticas del dashboard
  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard-stats", empresaActual?.id],
    queryFn: async () => {
      if (!empresaActual?.id) {
        return {
          empleados_activos: 0,
          solicitudes_pendientes: 0,
          nomina_periodo: 0,
          proximos_vencimientos: 0,
        };
      }

      try {
        // Empleados activos
        const empResponse = await api.get("/empleados/");
        const empData = empResponse.data;
        const empleados = empData.results || empData;
        const empleadosActivos = Array.isArray(empleados)
          ? empleados.filter((e: any) => e.estado === "activo").length
          : 0;

        // Solicitudes de vacaciones pendientes
        let solicitudesPendientes = 0;
        try {
          const vacResponse = await api.get("/vacaciones/", {
            params: { estado: "pendiente" },
          });
          const vacData = vacResponse.data;
          const solicitudes = vacData.results || vacData;
          solicitudesPendientes = Array.isArray(solicitudes)
            ? solicitudes.length
            : 0;
        } catch {
          // Endpoint puede no existir
        }

        // Nómina del periodo actual
        let nominaPeriodo = 0;
        try {
          const nomResponse = await api.get("/nomina/periodos/");
          const nomData = nomResponse.data;
          const periodos = nomData.results || nomData;
          if (Array.isArray(periodos) && periodos.length > 0) {
            nominaPeriodo = periodos[0].total_neto || 0;
          }
        } catch {
          // Endpoint puede no existir
        }

        // Contratos por vencer (próximos 30 días)
        let proximosVencimientos = 0;
        try {
          const contResponse = await api.get("/contratos/", {
            params: { por_vencer: 30 },
          });
          const contData = contResponse.data;
          const contratos = contData.results || contData;
          proximosVencimientos = Array.isArray(contratos)
            ? contratos.length
            : 0;
        } catch {
          // Endpoint puede no existir
        }

        return {
          empleados_activos: empleadosActivos,
          solicitudes_pendientes: solicitudesPendientes,
          nomina_periodo: nominaPeriodo,
          proximos_vencimientos: proximosVencimientos,
        };
      } catch (error) {
        console.error("Error cargando estadísticas:", error);
        return {
          empleados_activos: 0,
          solicitudes_pendientes: 0,
          nomina_periodo: 0,
          proximos_vencimientos: 0,
        };
      }
    },
    enabled: mounted && !!empresaActual?.id,
  });

  const quickActions = [
    { title: "Nuevo empleado", href: "/empleados/nuevo", icon: UserPlus },
    { title: "Generar reporte", href: "/reportes", icon: ClipboardList },
    { title: "Ver vacaciones", href: "/vacaciones", icon: Palmtree },
  ];

  if (!mounted) return null;

  const empresaNombre =
    empresaActual?.nombre_comercial ||
    empresaActual?.razon_social ||
    "Sin empresa seleccionada";

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h1 className="text-2xl font-display font-semibold text-warm-900">
          Bienvenido, {user?.nombre?.split(" ")[0] || "Administrador"}
        </h1>
        <p className="text-warm-500 mt-1">{empresaNombre}</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard
          title="Empleados activos"
          value={stats?.empleados_activos?.toString() || "0"}
          icon={<Users className="h-5 w-5" strokeWidth={1.5} />}
          subtitle={empresaActual ? `En ${empresaNombre}` : "Selecciona una empresa"}
          href="/empleados"
          loading={isLoading}
        />
        <MetricCard
          title="Solicitudes pendientes"
          value={stats?.solicitudes_pendientes?.toString() || "0"}
          icon={<FileText className="h-5 w-5" strokeWidth={1.5} />}
          href="/solicitudes"
          loading={isLoading}
        />
        <MetricCard
          title="Nomina del periodo"
          value={formatCurrency(stats?.nomina_periodo || 0)}
          icon={<Calendar className="h-5 w-5" strokeWidth={1.5} />}
          href="/nomina"
          loading={isLoading}
        />
        <MetricCard
          title="Proximos vencimientos"
          value={stats?.proximos_vencimientos?.toString() || "0"}
          icon={<AlertCircle className="h-5 w-5" strokeWidth={1.5} />}
          subtitle="Contratos"
          href="/contratos"
          loading={isLoading}
        />
      </div>

      {/* Main content grid */}
      <div className="grid gap-6 lg:grid-cols-5">
        {/* Quick actions */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Acciones rapidas</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {quickActions.map((action) => (
              <ActionButton
                key={action.href}
                title={action.title}
                href={action.href}
                icon={action.icon}
              />
            ))}
          </CardContent>
        </Card>

        {/* Chat section */}
        <Card className="lg:col-span-3">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-base">Asistente IA</CardTitle>
            <Link href="/chat">
              <Button variant="ghost" size="sm">
                Abrir chat completo
              </Button>
            </Link>
          </CardHeader>
          <CardContent className="p-0">
            <div className="h-[400px]">
              <ChatContainer compact />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
