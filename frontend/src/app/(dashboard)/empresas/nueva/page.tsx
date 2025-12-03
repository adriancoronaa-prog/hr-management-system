"use client";

import * as React from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function NuevaEmpresaPage() {
  const router = useRouter();
  const { setEmpresaActual, setEmpresas, empresas } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    razon_social: "",
    nombre_comercial: "",
    rfc: "",
    registro_patronal: "",
    direccion: "",
    telefono: "",
    email: "",
    representante_legal: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await api.post("/empresas/", form);
      const nuevaEmpresa = response.data;

      // Actualizar lista de empresas en el store
      const empresaParaStore = {
        id: nuevaEmpresa.id,
        nombre: nuevaEmpresa.nombre_comercial || nuevaEmpresa.razon_social,
        nombre_comercial: nuevaEmpresa.nombre_comercial,
        razon_social: nuevaEmpresa.razon_social,
      };

      setEmpresas([...empresas, empresaParaStore]);

      // Si es la primera empresa, establecerla como activa
      if (empresas.length === 0) {
        setEmpresaActual(empresaParaStore);
      }

      router.push("/empresas");
    } catch (err: unknown) {
      console.error("Error creando empresa:", err);
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setError(axiosError.response?.data?.detail || "Error al crear la empresa");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/empresas"
          className="inline-flex items-center gap-2 text-sm text-warm-500 hover:text-warm-700 mb-4"
        >
          <ArrowLeft className="h-4 w-4" strokeWidth={1.5} />
          Volver a empresas
        </Link>
        <h1 className="text-2xl font-semibold text-warm-900">Nueva empresa</h1>
        <p className="text-sm text-warm-500 mt-1">
          Ingresa los datos de la empresa para comenzar
        </p>
      </div>

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-xl border border-warm-200 p-6 space-y-6"
      >
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Datos principales */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-warm-700 uppercase tracking-wider">
            Datos principales
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <Input
                label="Razon social *"
                type="text"
                name="razon_social"
                value={form.razon_social}
                onChange={handleChange}
                required
                placeholder="Empresa SA de CV"
              />
            </div>

            <div className="sm:col-span-2">
              <Input
                label="Nombre comercial"
                type="text"
                name="nombre_comercial"
                value={form.nombre_comercial}
                onChange={handleChange}
                placeholder="Nombre comercial (opcional)"
              />
            </div>

            <div>
              <Input
                label="RFC *"
                type="text"
                name="rfc"
                value={form.rfc}
                onChange={handleChange}
                required
                placeholder="XXX010101XXX"
                maxLength={13}
                className="uppercase"
              />
            </div>

            <div>
              <Input
                label="Registro patronal IMSS"
                type="text"
                name="registro_patronal"
                value={form.registro_patronal}
                onChange={handleChange}
                placeholder="Y01-12345-10-1"
              />
            </div>
          </div>
        </div>

        {/* Contacto */}
        <div className="space-y-4 pt-4 border-t border-warm-100">
          <h2 className="text-sm font-semibold text-warm-700 uppercase tracking-wider">
            Contacto
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-warm-700 mb-1">
                Direccion
              </label>
              <textarea
                name="direccion"
                value={form.direccion}
                onChange={handleChange}
                rows={2}
                placeholder="Calle, numero, colonia, ciudad, estado, CP"
                className="w-full px-3 py-2 border border-warm-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-horizon-500 focus:border-transparent resize-none"
              />
            </div>

            <div>
              <Input
                label="Telefono"
                type="tel"
                name="telefono"
                value={form.telefono}
                onChange={handleChange}
                placeholder="55 1234 5678"
              />
            </div>

            <div>
              <Input
                label="Email"
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                placeholder="contacto@empresa.com"
              />
            </div>

            <div className="sm:col-span-2">
              <Input
                label="Representante legal"
                type="text"
                name="representante_legal"
                value={form.representante_legal}
                onChange={handleChange}
                placeholder="Nombre del representante legal"
              />
            </div>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-warm-100">
          <Link
            href="/empresas"
            className="px-4 py-2 text-sm font-medium text-warm-700 hover:text-warm-900"
          >
            Cancelar
          </Link>
          <Button type="submit" loading={loading}>
            {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
            Crear empresa
          </Button>
        </div>
      </form>
    </div>
  );
}
