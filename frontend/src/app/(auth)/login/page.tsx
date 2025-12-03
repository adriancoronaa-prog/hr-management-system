"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Mail, Lock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";

const loginSchema = z.object({
  email: z.string().email("Email invalido"),
  password: z.string().min(1, "La contrasena es requerida"),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    clearError();
    const success = await login(data.email, data.password);
    if (success) {
      // Usar window.location para forzar navegacion completa y evitar problemas de hidratacion
      window.location.href = "/";
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-2xl font-semibold tracking-tight">
          Sistema RRHH
        </CardTitle>
        <p className="text-sm text-warm-500">
          Ingresa tus credenciales para continuar
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="correo@empresa.com"
            leftIcon={<Mail className="h-4 w-4" strokeWidth={1.5} />}
            error={errors.email?.message}
            {...register("email")}
          />

          <Input
            label="Contrasena"
            type="password"
            placeholder="Tu contrasena"
            leftIcon={<Lock className="h-4 w-4" strokeWidth={1.5} />}
            error={errors.password?.message}
            {...register("password")}
          />

          {error && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-error">
              {error}
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            loading={isLoading}
          >
            Iniciar sesion
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
