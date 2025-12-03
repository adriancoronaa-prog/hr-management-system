"use client";

import * as React from "react";
import * as AvatarPrimitive from "@radix-ui/react-avatar";
import { cn, getInitials } from "@/lib/utils";

interface AvatarProps extends React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root> {
  src?: string | null;
  name?: string;
  size?: "sm" | "default" | "lg" | "xl";
}

const sizeClasses = {
  sm: "h-8 w-8 text-xs",
  default: "h-10 w-10 text-sm",
  lg: "h-12 w-12 text-base",
  xl: "h-16 w-16 text-lg",
};

const Avatar = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  AvatarProps
>(({ className, src, name, size = "default", ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex shrink-0 overflow-hidden rounded-full bg-warm-200",
      sizeClasses[size],
      className
    )}
    {...props}
  >
    {src && (
      <AvatarPrimitive.Image
        src={src}
        alt={name || "Avatar"}
        className="aspect-square h-full w-full object-cover"
      />
    )}
    <AvatarPrimitive.Fallback
      className="flex h-full w-full items-center justify-center bg-horizon-100 font-medium text-horizon-700"
    >
      {name ? getInitials(name) : "??"}
    </AvatarPrimitive.Fallback>
  </AvatarPrimitive.Root>
));
Avatar.displayName = "Avatar";

export { Avatar };
