import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, icon, ...props }, ref) => {
    return (
      <div className="relative flex items-center w-full">
        {icon && (
          <div className="absolute left-3 text-[var(--color-secondary)] pointer-events-none flex items-center justify-center">
            {icon}
          </div>
        )}
        <input
          type={type}
          className={cn(
            "flex h-9 w-full rounded-md border border-[var(--color-border-subtle)] bg-[#161618] px-3 py-1 text-sm  transition-colors",
            "file:border-0 file:bg-transparent file:text-sm file:font-medium",
            "placeholder:text-[var(--color-secondary)] text-[var(--color-primary)]",
            "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--color-accent)] focus-visible:border-[var(--color-accent)]",
            "disabled:cursor-not-allowed disabled:opacity-50",
            icon && "pl-9",
            className
          )}
          ref={ref}
          {...props}
        />
      </div>
    )
  }
)
Input.displayName = "Input"

export { Input }
