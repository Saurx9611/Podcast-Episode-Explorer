'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  AudioLines, 
  LayoutDashboard, 
  ListVideo, 
  Search, 
  FolderGit2,
  Activity,
  Bookmark,
  Settings,
  Mic2,
  Menu,
  X,
  ChevronRight,
  Sparkles,
  Command
} from 'lucide-react';
import { NotificationCenter } from './NotificationCenter';

const NAVIGATION = [
  { group: 'INTELLIGENCE', items: [
    { name: 'Overview', href: '/', icon: LayoutDashboard },
    { name: 'Episodes', href: '/episodes', icon: ListVideo },
    { name: 'Semantic Search', href: '/search', icon: Search },
    { name: 'Projects', href: '/projects', icon: FolderGit2 },
  ]},
  { group: 'WORKSPACE', items: [
    { name: 'Processing Pipeline', href: '/processing', icon: Activity },
    { name: 'Saved Searches', href: '/saved', icon: Bookmark },
    { name: 'Design System', href: '/design-system', icon: AudioLines },
  ]}
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  // Global Command+K shortcut to focus search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        router.push('/search');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [router]);

  // Enhanced Breadcrumb generator
  const generateBreadcrumbs = () => {
    const paths = pathname?.split('/').filter(Boolean) || [];
    if (paths.length === 0) {
      return (
        <div className="flex items-center gap-1.5 text-xs">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/80 animate-pulse"></span>
          <span className="font-medium text-[var(--color-primary)]">Workspace Live</span>
        </div>
      );
    }

    return (
      <div className="flex items-center text-xs font-medium">
        <Link href="/" className="text-[var(--color-muted)] hover:text-[var(--color-primary)] transition-colors hidden sm:inline-block">
          Explorer
        </Link>
        {paths.map((path, index) => {
          const isLast = index === paths.length - 1;
          const title = path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, ' ');

          return (
            <React.Fragment key={path}>
              <ChevronRight className="w-3.5 h-3.5 text-[var(--color-border-subtle)] mx-1.5 hidden sm:inline-block" />
              <span className={cn(
                "truncate max-w-[140px] sm:max-w-[220px]",
                isLast ? "text-[var(--color-primary)] font-semibold" : "text-[var(--color-secondary)] hidden sm:inline-block"
              )}>
                {title}
              </span>
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  const handleQuickSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    } else {
      router.push('/search');
    }
  };

  return (
    <div className="flex h-screen w-full bg-[var(--color-background)] overflow-hidden">
      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/70 z-40 lg:hidden backdrop-blur-xs transition-opacity duration-200"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 w-[250px] flex-shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface)] flex flex-col transition-transform duration-200 ease-out lg:static lg:translate-x-0",
        isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        {/* Brand Header */}
        <div className="h-14 flex items-center justify-between px-4 border-b border-[var(--color-border)]">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-7 h-7 rounded-md bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-sm shadow-indigo-500/30 group-hover:scale-105 transition-transform">
              <Mic2 className="w-4 h-4 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-[13px] font-semibold tracking-tight text-[var(--color-primary)] leading-none">Podcast Explorer</span>
              <span className="text-[10px] font-mono text-[var(--color-muted)] leading-none mt-1">Intelligence Platform</span>
            </div>
          </Link>
          <button
            className="lg:hidden p-1.5 text-[var(--color-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-elevated)] rounded-md transition-colors"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Nav Links */}
        <div className="flex-1 overflow-y-auto py-4 px-2.5 space-y-6">
          {NAVIGATION.map((section, idx) => (
            <div key={idx}>
              <div className="text-[10px] font-semibold font-mono text-[var(--color-muted)] mb-1.5 px-2.5 tracking-wider uppercase">
                {section.group}
              </div>
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const isActive = pathname === item.href || (item.href !== '/' && pathname?.startsWith(item.href));
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-[13px] font-medium transition-all duration-150 relative group",
                        isActive
                          ? "bg-[var(--color-accent-subtle)] text-[var(--color-accent-hover)] font-semibold"
                          : "text-[var(--color-secondary)] hover:bg-[var(--color-surface-elevated)] hover:text-[var(--color-primary)]"
                      )}
                    >
                      <item.icon className={cn(
                        "w-4 h-4 transition-colors",
                        isActive ? "text-[var(--color-accent)]" : "text-[var(--color-muted)] group-hover:text-[var(--color-primary)]"
                      )} />
                      <span>{item.name}</span>
                      {isActive && (
                        <span className="absolute right-2 w-1 h-3.5 bg-[var(--color-accent)] rounded-full" />
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Bottom User / Settings Card */}
        <div className="p-3 border-t border-[var(--color-border)] space-y-1.5 bg-[var(--color-surface)]">
          <Link
            href="/settings"
            className={cn(
              "flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-[13px] font-medium transition-colors",
              pathname?.startsWith('/settings')
                ? "bg-[var(--color-accent-subtle)] text-[var(--color-accent-hover)]"
                : "text-[var(--color-secondary)] hover:bg-[var(--color-surface-elevated)] hover:text-[var(--color-primary)]"
            )}
          >
            <Settings className="w-4 h-4 text-[var(--color-muted)]" />
            <span>Workspace Settings</span>
          </Link>
          
          <div className="flex items-center gap-2.5 p-2 rounded-md bg-[var(--color-surface-elevated)]/50 border border-[var(--color-border)]">
            <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-600 to-indigo-400 text-white flex items-center justify-center text-xs font-bold shrink-0">
              JD
            </div>
            <div className="flex flex-col min-w-0 flex-1">
              <span className="truncate text-xs font-medium text-[var(--color-primary)] leading-tight">Jane Doe</span>
              <span className="truncate text-[10px] text-[var(--color-muted)] font-mono leading-tight mt-0.5">Engineering Lead</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-[var(--color-background)]">
        {/* Top Header */}
        <header className="h-14 flex-shrink-0 border-b border-[var(--color-border)] bg-[var(--color-surface)]/80 backdrop-blur-md px-4 lg:px-8 flex items-center justify-between sticky top-0 z-20">
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden p-1.5 -ml-1.5 text-[var(--color-secondary)] hover:text-[var(--color-primary)] hover:bg-[var(--color-surface-elevated)] rounded-md transition-colors"
              onClick={() => setIsMobileMenuOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </button>
            {generateBreadcrumbs()}
          </div>

          <div className="flex items-center gap-2.5 sm:gap-4">
            {/* Quick Search Input */}
            <form onSubmit={handleQuickSearch} className="relative group hidden sm:flex items-center">
              <Search className="w-3.5 h-3.5 text-[var(--color-muted)] absolute left-3 group-focus-within:text-[var(--color-accent)] transition-colors" />
              <input
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="Search semantic concepts..."
                className="w-56 lg:w-72 h-8 pl-8 pr-12 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-md text-xs text-[var(--color-primary)] placeholder:text-[var(--color-muted)] outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
              />
              <div className="absolute right-2 flex items-center gap-0.5 pointer-events-none">
                <kbd className="bg-[var(--color-surface)] border border-[var(--color-border)] px-1.5 py-0.5 rounded text-[10px] font-mono text-[var(--color-muted)] flex items-center gap-0.5">
                  <Command className="w-2.5 h-2.5" /> K
                </kbd>
              </div>
            </form>

            <Link href="/search" className="sm:hidden p-1.5 text-[var(--color-secondary)] hover:text-[var(--color-primary)]">
              <Search className="w-4 h-4" />
            </Link>

            {/* In-App Notifications Center */}
            <NotificationCenter />
          </div>
        </header>

        {/* Page Content Container */}
        <div className="flex-1 overflow-auto bg-grid-subtle">
          <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
