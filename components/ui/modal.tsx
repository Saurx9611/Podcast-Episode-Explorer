"use client"
import * as React from "react"
import { cn } from "@/lib/utils"
import { X } from "lucide-react"

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  footer?: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, description, children, className, footer }: ModalProps) {
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      document.addEventListener('keydown', handleKeyDown);
    } else {
      document.body.style.overflow = 'auto';
    }
    return () => {
      document.body.style.overflow = 'auto';
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div 
        className={cn(
          "bg-[var(--color-surface)] w-full max-w-lg rounded-lg shadow-lg overflow-hidden border border-[var(--color-border)] flex flex-col max-h-[90vh]",
          className
        )}
      >
        {(title || description) && (
          <div className="px-6 py-4 border-b border-[var(--color-border)] flex flex-col gap-1 bg-[#161618]">
            <div className="flex items-center justify-between">
              {title && <h2 className="text-lg font-semibold text-[var(--color-primary)]">{title}</h2>}
              <button 
                onClick={onClose}
                className="p-1.5 -mr-1.5 text-[var(--color-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-border-subtle)] rounded-md transition-colors ml-auto"
              >
                <X className="w-4 h-4" />
                <span className="sr-only">Close</span>
              </button>
            </div>
            {description && <p className="text-sm text-[var(--color-secondary)]">{description}</p>}
          </div>
        )}
        
        <div className="p-6 overflow-y-auto flex-1 text-[var(--color-primary)]">
          {children}
        </div>
        
        {footer && (
          <div className="px-6 py-4 border-t border-[var(--color-border)] bg-[#161618] flex items-center justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  )
}
