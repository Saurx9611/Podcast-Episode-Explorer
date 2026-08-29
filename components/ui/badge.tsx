import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "error" | "accent";
  dot?: boolean;
}

function Badge({ className, variant = "default", dot = false, children, ...props }: BadgeProps) {
  
  const variants = {
    default: "border-[var(--color-border)] bg-[var(--color-surface-elevated)] text-[var(--color-primary)]",
    secondary: "border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-secondary)]",
    outline: "border-[var(--color-border)] text-[var(--color-secondary)] bg-transparent",
    success: "border-emerald-500/20 bg-emerald-500/10 text-emerald-400",
    warning: "border-amber-500/20 bg-amber-500/10 text-amber-400",
    error: "border-rose-500/20 bg-rose-500/10 text-rose-400",
    accent: "border-indigo-500/20 bg-indigo-500/10 text-indigo-400",
  };

  const dotColors = {
    default: "bg-[var(--color-primary)]",
    secondary: "bg-[var(--color-secondary)]",
    outline: "bg-[var(--color-muted)]",
    success: "bg-emerald-400 animate-pulse",
    warning: "bg-amber-400 animate-pulse",
    error: "bg-rose-400",
    accent: "bg-indigo-400 animate-pulse",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-medium tracking-tight transition-colors select-none",
        variants[variant],
        className
      )}
      {...props}
    >
      {dot && (
        <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", dotColors[variant])} />
      )}
      {children}
    </div>
  );
}

export { Badge };
