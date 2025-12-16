"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ShieldX, ArrowLeft, Home } from "lucide-react";

export default function UnauthorizedPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center p-8">
        <div className="flex justify-center mb-6">
          <div className="rounded-full bg-red-100 p-6">
            <ShieldX className="h-16 w-16 text-red-600" />
          </div>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Acceso Denegado
        </h1>

        <p className="text-gray-600 mb-8 max-w-md">
          No tienes permisos para acceder a esta sección.
          Contacta al administrador si crees que esto es un error.
        </p>

        <div className="flex gap-4 justify-center">
          <Button
            variant="outline"
            onClick={() => router.back()}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Volver
          </Button>

          <Button
            onClick={() => router.push("/dashboard")}
            className="flex items-center gap-2 bg-horizon-600 hover:bg-horizon-700"
          >
            <Home className="h-4 w-4" />
            Ir al Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
