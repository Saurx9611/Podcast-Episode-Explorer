"use client"
import * as React from "react"
import { cn } from "@/lib/utils"

export interface TabsProps {
  defaultValue: string;
  className?: string;
  children: React.ReactNode;
}

const TabsContext = React.createContext<{
  value: string;
  onChange: (value: string) => void;
} | null>(null);

export function Tabs({ defaultValue, className, children }: TabsProps) {
  const [value, setValue] = React.useState(defaultValue);
  return (
    <TabsContext.Provider value={{ value, onChange: setValue }}>
      <div className={cn("flex flex-col gap-4", className)}>
        {children}
      </div>
    </TabsContext.Provider>
  )
}

export function TabsList({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={cn("inline-flex h-10 items-center justify-center rounded-md bg-[#161618] border border-[var(--color-border-subtle)] p-1 text-[var(--color-secondary)]", className)}>
      {children}
    </div>
  )
}

export function TabsTrigger({ value, className, children }: { value: string, className?: string, children: React.ReactNode }) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error("TabsTrigger must be used within Tabs");
  
  const isActive = context.value === value;
  
  return (
    <button
      onClick={() => context.onChange(value)}
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] disabled:pointer-events-none disabled:opacity-50",
        isActive ? "bg-[var(--color-border-subtle)] text-[var(--color-primary)] " : "hover:text-[var(--color-primary)] hover:bg-[var(--color-border-subtle)]/50",
        className
      )}
    >
      {children}
    </button>
  )
}

export function TabsContent({ value, className, children }: { value: string, className?: string, children: React.ReactNode }) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error("TabsContent must be used within Tabs");
  
  if (context.value !== value) return null;
  
  return (
    <div className={cn("mt-2 outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)]", className)}>
      {children}
    </div>
  )
}
