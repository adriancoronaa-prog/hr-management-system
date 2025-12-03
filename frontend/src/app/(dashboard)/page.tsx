"use client";

import * as React from "react";
import Link from "next/link";
import {
  Users,
  FileText,
  Calendar,
  AlertCircle,
  ArrowRight,
  UserPlus,
  ClipboardList,
  Palmtree,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChatContainer } from "@/components/chat/chat-container";
import { useAuthStore } from "@/stores/auth-store";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  change?: string;
  href?: string;
}

function MetricCard({ title, value, icon, change, href }: MetricCardProps) {
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
          <p className="text-2xl font-semibold text-warm-900">{value}</p>
          {change && (
            <p className="mt-1 text-xs text-sage-600">{change}</p>
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
      className="flex items-center justify-between rounded-md border border-warm-200 p-3 transition-colors hover:bg-warm-50"
    >
      <div className="flex items-center gap-3">
        <Icon className="h-5 w-5 text-warm-500" strokeWidth={1.5} />
        <span className="text-sm font-medium text-warm-700">{title}</span>
      </div>
      <ArrowRight className="h-4 w-4 text-warm-400" strokeWidth={1.5} />
    </Link>
  );
}

export default function DashboardPage() {
  const { user, empresaActual } = useAuthStore();

  // Mock data - in real app, fetch from API
  const metrics = {
    empleados_activos: 22,
    solicitudes_pendientes: 5,
    nomina_periodo: "$485,230.00",
    proximos_vencimientos: 3,
  };

  const quickActions = [
    { title: "Nuevo empleado", href: "/empleados/nuevo", icon: UserPlus },
    { title: "Generar reporte", href: "/reportes", icon: ClipboardList },
    { title: "Ver vacaciones", href: "/vacaciones", icon: Palmtree },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome */}
      <div>
        <h2 className="text-xl font-semibold text-warm-900">
          Bienvenido, {user?.nombre?.split(" ")[0]}
        </h2>
        {empresaActual && (
          <p className="text-sm text-warm-500">
            {empresaActual.nombre_comercial || empresaActual.razon_social}
          </p>
        )}
      </div>

      {/* Metrics - 2 columns mobile, 4 columns desktop */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard
          title="Empleados activos"
          value={metrics.empleados_activos}
          icon={<Users className="h-5 w-5" strokeWidth={1.5} />}
          change="+2 este mes"
          href="/empleados"
        />
        <MetricCard
          title="Solicitudes pendientes"
          value={metrics.solicitudes_pendientes}
          icon={<FileText className="h-5 w-5" strokeWidth={1.5} />}
          href="/solicitudes"
        />
        <MetricCard
          title="Nomina del periodo"
          value={metrics.nomina_periodo}
          icon={<Calendar className="h-5 w-5" strokeWidth={1.5} />}
          href="/nomina"
        />
        <MetricCard
          title="Proximos vencimientos"
          value={metrics.proximos_vencimientos}
          icon={<AlertCircle className="h-5 w-5" strokeWidth={1.5} />}
          href="/contratos"
        />
      </div>

      {/* Main content grid - 5 columns: 2 for actions, 3 for chat */}
      <div className="grid gap-6 lg:grid-cols-5">
        {/* Quick actions - 2/5 width */}
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

        {/* Chat section - 3/5 width */}
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
