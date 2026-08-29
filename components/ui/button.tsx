import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "outline" | "ghost" | "danger" | "accent";
  size?: "sm" | "md" | "lg" | "icon";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "md", ...props }, ref) => {
    
    const variants = {
      default: "bg-[var(--color-primary)] text-[var(--color-background)] hover:bg-[#e2e8f0] shadow-sm active:bg-[#cbd5e1]",
      secondary: "bg-[var(--color-surface)] text-[var(--color-primary)] border border-[var(--color-border)] hover:bg-[var(--color-surface-hover)] hover:border-[var(--color-border-subtle)] shadow-xs",
      outline: "border border-[var(--color-border)] bg-transparent text-[var(--color-primary)] hover:bg-[var(--color-surface)] hover:border-[var(--color-border-subtle)]",
      ghost: "text-[var(--color-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-elevated)]",
      danger: "bg-[var(--color-error-bg)] text-[var(--color-error)] border border-[var(--color-error)]/30 hover:bg-[var(--color-error)] hover:text-white",
      accent: "bg-[var(--color-accent)] text-white hover:bg-[var(--color-accent-hover)] shadow-xs shadow-indigo-500/20 active:bg-indigo-700",
    };
    
    const sizes = {
      sm: "h-8 px-3 text-xs gap-1.5",
      md: "h-9 px-3.5 text-sm gap-2",
      lg: "h-10 px-5 text-sm gap-2.5",
      icon: "h-8 w-8 flex items-center justify-center p-0",
    };

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-md font-medium tracking-tight transition-all duration-150 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-1 focus-visible:ring-offset-[var(--color-background)] disabled:pointer-events-none disabled:opacity-40 select-none cursor-pointer",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
