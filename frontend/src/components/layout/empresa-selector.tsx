"use client";

import * as React from "react";
import { useState, useRef, useEffect } from "react";
import { Building2, ChevronDown, Check } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";
import { cn } from "@/lib/utils";

export function EmpresaSelector() {
  const { empresas, empresaActual, setEmpresaActual } = useAuthStore();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const empresaNombre =
    empresaActual?.nombre_comercial ||
    empresaActual?.razon_social ||
    "Sin empresa";

  if (!empresas || empresas.length <= 1) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 text-sm text-horizon-300">
        <Building2 className="h-4 w-4" strokeWidth={1.5} />
        <span className="truncate">{empresaNombre}</span>
      </div>
    );
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-2 w-full text-left text-sm text-horizon-200 hover:bg-horizon-800 rounded-lg transition-colors"
      >
        <Building2 className="h-4 w-4 flex-shrink-0" strokeWidth={1.5} />
        <span className="truncate flex-1">{empresaNombre}</span>
        <ChevronDown
          className={cn("h-4 w-4 transition-transform", open && "rotate-180")}
          strokeWidth={1.5}
        />
      </button>

      {open && (
        <div className="absolute left-0 right-0 mt-1 bg-horizon-800 border border-horizon-700 rounded-lg shadow-lg z-50 overflow-hidden">
          {empresas.map((empresa) => {
            const nombre =
              empresa.nombre_comercial || empresa.razon_social || "Empresa";
            return (
              <button
                key={empresa.id}
                onClick={() => {
                  setEmpresaActual(empresa);
                  setOpen(false);
                }}
                className={cn(
                  "flex items-center gap-2 w-full px-3 py-2 text-sm text-left transition-colors",
                  empresaActual?.id === empresa.id
                    ? "bg-horizon-700 text-white"
                    : "text-horizon-300 hover:bg-horizon-700 hover:text-white"
                )}
              >
                <span className="truncate flex-1">{nombre}</span>
                {empresaActual?.id === empresa.id && (
                  <Check className="h-4 w-4 flex-shrink-0" strokeWidth={1.5} />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
