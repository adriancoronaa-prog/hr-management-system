"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "success" | "outline";
  size?: "sm" | "default" | "lg" | "icon";
  asChild?: boolean;
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "default",
      asChild = false,
      loading = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const variants = {
      primary:
        "bg-horizon-900 text-white hover:bg-horizon-800 active:bg-horizon-950",
      secondary:
        "bg-warm-100 text-warm-900 hover:bg-warm-200 active:bg-warm-300",
      ghost:
        "bg-transparent text-warm-700 hover:bg-warm-100 active:bg-warm-200",
      danger:
        "bg-error text-white hover:bg-red-700 active:bg-red-800",
      success:
        "bg-success text-white hover:bg-sage-600 active:bg-sage-700",
      outline:
        "border border-warm-300 bg-transparent text-warm-700 hover:bg-warm-50 active:bg-warm-100",
    };

    const sizes = {
      sm: "h-8 px-3 text-sm",
      default: "h-10 px-4 text-sm",
      lg: "h-12 px-6 text-base",
      icon: "h-10 w-10",
    };

    const baseClasses = cn(
      "inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
      variants[variant],
      sizes[size],
      className
    );

    // Si es asChild, usar Slot sin modificar children
    if (asChild) {
      return (
        <Slot className={baseClasses} ref={ref} {...props}>
          {children}
        </Slot>
      );
    }

    // Si no es asChild, renderizar button normal con loading
    return (
      <button
        className={baseClasses}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg
            className="h-4 w-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button };
