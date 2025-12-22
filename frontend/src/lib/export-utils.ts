import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

// Extender tipo jsPDF para autotable
declare module "jspdf" {
  interface jsPDF {
    autoTable: (options: {
      head?: string[][];
      body: (string | number)[][];
      startY?: number;
      styles?: { fontSize?: number };
      headStyles?: { fillColor?: number[] };
      margin?: { left?: number };
    }) => void;
  }
}

// Exportar array de objetos a Excel
export function exportToExcel<T extends Record<string, unknown>>(
  data: T[],
  filename: string,
  sheetName: string = "Datos"
): void {
  const worksheet = XLSX.utils.json_to_sheet(data);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
  XLSX.writeFile(workbook, `${filename}.xlsx`);
}

// Exportar tabla a PDF
export function exportTableToPdf(
  columns: string[],
  rows: (string | number)[][],
  title: string,
  filename: string
): void {
  const doc = new jsPDF();

  // Titulo
  doc.setFontSize(16);
  doc.text(title, 14, 20);

  // Fecha
  doc.setFontSize(10);
  doc.text(
    `Generado: ${new Date().toLocaleDateString("es-MX", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    })}`,
    14,
    28
  );

  // Tabla
  doc.autoTable({
    head: [columns],
    body: rows,
    startY: 35,
    styles: { fontSize: 8 },
    headStyles: { fillColor: [59, 130, 246] },
  });

  doc.save(`${filename}.pdf`);
}

// Formato moneda MXN
export function formatCurrency(amount: number | undefined | null): string {
  if (amount === undefined || amount === null) return "$0.00";
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
  }).format(amount);
}

// Formato numero con separador de miles
export function formatNumber(num: number | undefined | null): string {
  if (num === undefined || num === null) return "0";
  return new Intl.NumberFormat("es-MX").format(num);
}

// Formato porcentaje
export function formatPercent(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

// Descargar blob del backend
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

// Formatear fecha
export function formatDate(
  dateString: string | null | undefined,
  format: "short" | "long" | "full" = "short"
): string {
  if (!dateString) return "-";
  try {
    const date = new Date(dateString);
    const options: Intl.DateTimeFormatOptions =
      format === "short"
        ? { day: "2-digit", month: "short" }
        : format === "long"
        ? { day: "2-digit", month: "short", year: "numeric" }
        : { day: "2-digit", month: "long", year: "numeric" };
    return date.toLocaleDateString("es-MX", options);
  } catch {
    return dateString;
  }
}

// Nombres de meses en espanol
export const MESES_ES = [
  "Ene",
  "Feb",
  "Mar",
  "Abr",
  "May",
  "Jun",
  "Jul",
  "Ago",
  "Sep",
  "Oct",
  "Nov",
  "Dic",
];

// Obtener nombre de mes
export function getNombreMes(mes: number): string {
  return MESES_ES[mes] || "";
}

// Colores para graficos (paleta del sistema)
export const CHART_COLORS = {
  primary: "#1e3a5f", // horizon-900
  secondary: "#059669", // sage-600
  accent: "#f59e0b", // amber-500
  muted: "#78716c", // warm-500
  success: "#22c55e",
  warning: "#eab308",
  error: "#ef4444",
  palette: [
    "#1e3a5f",
    "#059669",
    "#f59e0b",
    "#8b5cf6",
    "#ec4899",
    "#14b8a6",
    "#f97316",
    "#6366f1",
  ],
};
