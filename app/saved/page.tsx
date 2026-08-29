"use client";

import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Search,
  SlidersHorizontal,
  Play,
  MoreHorizontal,
  Copy,
  Edit2,
  Trash2,
  Plus,
  Bookmark,
  Clock,
  Filter,
  Loader2
} from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';
import { Modal } from '@/components/ui/modal';
import {
  getSavedSearches,
  createSavedSearch,
  updateSavedSearch,
  deleteSavedSearch,
  runSavedSearch,
  SavedSearch
} from '@/lib/api/search';

const FALLBACK_SEARCHES: SavedSearch[] = [
  {
    id: 's-1',
    user_id: 'default-user',
    name: 'Database Bottlenecks',
    query: 'Where do they discuss database bottlenecks and connection pools?',
    filters: ['Engineering Podcasts', 'All Speakers'],
    created_at: '2026-08-20T10:00:00Z',
    updated_at: '2026-08-28T10:00:00Z',
    last_run_at: '2026-08-28T10:00:00Z',
    last_run_formatted: 'Aug 28, 2026',
    run_count: 24,
  },
  {
    id: 's-2',
    user_id: 'default-user',
    name: 'Vector Database Discussions',
    query: 'Which episodes compare vector databases and pgvector?',
    filters: ['Data Science', 'Recent (30 days)'],
    created_at: '2026-08-15T14:30:00Z',
    updated_at: '2026-08-25T14:30:00Z',
    last_run_at: '2026-08-25T14:30:00Z',
    last_run_formatted: 'Aug 25, 2026',
    run_count: 12,
  },
  {
    id: 's-3',
    user_id: 'default-user',
    name: 'Engineering Hiring',
    query: 'What do the guests say about hiring senior engineers?',
    filters: ['Leadership'],
    created_at: '2026-08-10T09:15:00Z',
    updated_at: '2026-08-20T09:15:00Z',
    last_run_at: '2026-08-20T09:15:00Z',
    last_run_formatted: 'Aug 20, 2026',
    run_count: 45,
  }
];

export default function SavedSearchesPage() {
  const router = useRouter();
  const searchInputRef = useRef<HTMLInputElement>(null);
  
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('All');
  const [sortBy, setSortBy] = useState('Recently Used');

  // Modals state
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Selected item
  const [selectedSearch, setSelectedSearch] = useState<SavedSearch | null>(null);
  
  // Form State
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    query: '',
    filters: ''
  });

  // Action Menu State
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const loadSearches = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getSavedSearches();
      setSearches(data);
    } catch (err: any) {
      console.warn('Backend unavailable, using fallback saved searches:', err);
      setSearches(FALLBACK_SEARCHES);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSearches();
  }, [loadSearches]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.key === 'Escape') {
        setIsFormModalOpen(false);
        setIsDeleteModalOpen(false);
        setActiveMenuId(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    const handleOutsideClick = () => {
      if (activeMenuId) {
        setActiveMenuId(null);
      }
    };
    document.addEventListener('click', handleOutsideClick);
    return () => document.removeEventListener('click', handleOutsideClick);
  }, [activeMenuId]);

  const filteredSearches = useMemo(() => {
    const result = searches.filter(s => {
      const matchQuery = s.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         s.query.toLowerCase().includes(searchQuery.toLowerCase());
      if (!matchQuery) return false;
      
      if (filterType === 'Recently Used' && s.last_run_at) {
        const diff = Date.now() - new Date(s.last_run_at).getTime();
        return diff < 1000 * 60 * 60 * 24 * 14;
      }
      if (filterType === 'Most Used') {
        return (s.run_count || 0) >= 10;
      }
      return true;
    });

    result.sort((a, b) => {
      if (sortBy === 'Recently Used') {
        const dateA = a.last_run_at ? new Date(a.last_run_at).getTime() : 0;
        const dateB = b.last_run_at ? new Date(b.last_run_at).getTime() : 0;
        return dateB - dateA;
      } else if (sortBy === 'Recently Created') {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        return dateB - dateA;
      } else if (sortBy === 'Alphabetical') {
        return a.name.localeCompare(b.name);
      }
      return 0;
    });

    return result;
  }, [searches, searchQuery, filterType, sortBy]);

  const handleRunSearch = async (search: SavedSearch) => {
    try {
      await runSavedSearch(search.id);
    } catch (err) {
      console.warn('Run search API call warning:', err);
    }
    
    const params = new URLSearchParams();
    params.set('q', search.query);
    router.push(`/search?${params.toString()}`);
  };

  const handleOpenForm = (search?: SavedSearch) => {
    if (search) {
      setSelectedSearch(search);
      setFormData({
        name: search.name,
        description: search.description || '',
        query: search.query,
        filters: Array.isArray(search.filters) ? search.filters.join(', ') : ''
      });
    } else {
      setSelectedSearch(null);
      setFormData({
        name: '',
        description: '',
        query: '',
        filters: ''
      });
    }
    setIsFormModalOpen(true);
  };

  const handleSaveSearch = async () => {
    if (!formData.name.trim() || !formData.query.trim()) return;

    const filtersList = formData.filters.split(',').map(f => f.trim()).filter(Boolean);
    
    try {
      setSubmitting(true);
      if (selectedSearch) {
        const updated = await updateSavedSearch(selectedSearch.id, {
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          query: formData.query.trim(),
          filters: filtersList
        });
        setSearches(prev => prev.map(s => s.id === updated.id ? updated : s));
        showToast("Saved search updated.");
      } else {
        const created = await createSavedSearch({
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          query: formData.query.trim(),
          filters: filtersList
        });
        setSearches(prev => [created, ...prev]);
        showToast("Search saved successfully.");
      }
      setIsFormModalOpen(false);
    } catch (err: any) {
      alert(err.message || 'Failed to save search.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDuplicate = async (search: SavedSearch) => {
    try {
      const duplicated = await createSavedSearch({
        name: `${search.name} (Copy)`,
        description: search.description,
        query: search.query,
        filters: search.filters
      });
      setSearches(prev => [duplicated, ...prev]);
      showToast("Search duplicated.");
    } catch (err: any) {
      alert(err.message || 'Failed to duplicate search.');
    }
  };

  const handleCopyQuery = (query: string) => {
    navigator.clipboard.writeText(query);
    showToast("Query copied to clipboard.");
  };

  const handleDelete = async () => {
    if (!selectedSearch) return;
    try {
      await deleteSavedSearch(selectedSearch.id);
      setSearches(prev => prev.filter(s => s.id !== selectedSearch.id));
      setIsDeleteModalOpen(false);
      showToast("Saved search deleted.");
    } catch (err: any) {
      alert(err.message || 'Failed to delete saved search.');
    }
  };

  const toggleMenu = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    setActiveMenuId(activeMenuId === id ? null : id);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-16">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-[var(--color-surface)] border border-[var(--color-border)] shadow-lg rounded-md px-3.5 py-2.5 flex items-center gap-2 animate-in slide-in-from-bottom-5">
          <Bookmark className="w-3.5 h-3.5 text-[var(--color-accent)]" />
          <span className="text-xs text-[var(--color-primary)]">{toastMessage}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight text-[var(--color-primary)]">
            Saved Searches
          </h1>
          <p className="text-xs sm:text-sm text-[var(--color-secondary)]">
            Maintain semantic queries to run across your podcast intelligence index.
          </p>
        </div>
        <Button onClick={() => handleOpenForm()} variant="accent" className="gap-2 h-8 text-xs">
          <Plus className="w-3.5 h-3.5" />
          New Saved Search
        </Button>
      </div>
      
      {/* Search & Toolbar */}
      <div className="flex flex-col sm:flex-row gap-2.5 items-center">
        <div className="relative flex-1 w-full">
          <Search className="w-3.5 h-3.5 text-[var(--color-muted)] absolute left-3 top-1/2 -translate-y-1/2" />
          <input 
            ref={searchInputRef}
            type="text" 
            placeholder="Search saved queries... (/ to focus)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && filteredSearches.length > 0) {
                handleRunSearch(filteredSearches[0]);
              }
            }}
            className="w-full pl-9 pr-3 py-1.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md text-[var(--color-primary)] text-xs outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all placeholder:text-[var(--color-muted)]"
          />
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-primary)] text-xs rounded-md px-2.5 py-1.5 outline-none focus:border-[var(--color-accent)]"
          >
            <option value="All">All Searches</option>
            <option value="Recently Used">Recently Used</option>
            <option value="Most Used">Most Used</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-primary)] text-xs rounded-md px-2.5 py-1.5 outline-none focus:border-[var(--color-accent)]"
          >
            <option value="Recently Used">Recently Used</option>
            <option value="Recently Created">Recently Created</option>
            <option value="Alphabetical">Alphabetical</option>
          </select>
        </div>
      </div>
      
      {/* Main Table */}
      <div className="border border-[var(--color-border)] rounded-lg overflow-hidden bg-[var(--color-surface)]">
        {loading ? (
          <div className="flex items-center justify-center py-16 text-[var(--color-muted)] gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-[var(--color-accent)]" />
            <span className="text-xs font-mono">Loading queries...</span>
          </div>
        ) : filteredSearches.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow className="border-b-[var(--color-border)]">
                <TableHead className="w-full sm:w-2/3 text-xs">Search Details</TableHead>
                <TableHead className="hidden sm:table-cell text-right text-xs">Usage</TableHead>
                <TableHead className="text-right text-xs pr-4">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSearches.map((search) => (
                <TableRow key={search.id} className="hover:bg-[var(--color-surface-hover)] transition-colors group">
                  <TableCell className="py-3.5 align-top">
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-xs sm:text-sm text-[var(--color-primary)]">{search.name}</span>
                        {search.description && (
                          <span className="hidden md:inline text-xs text-[var(--color-muted)] line-clamp-1">
                            - {search.description}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-[var(--color-secondary)] font-mono bg-[var(--color-surface-elevated)] px-2 py-1 rounded border border-[var(--color-border)] inline-block max-w-full truncate">
                        &quot;{search.query}&quot;
                      </div>
                      <div className="flex flex-wrap gap-1 pt-0.5">
                        {Array.isArray(search.filters) && search.filters.map(f => (
                          <Badge key={typeof f === 'string' ? f : JSON.stringify(f)} variant="secondary" className="text-[10px] font-mono py-0">
                            {typeof f === 'string' ? f : 'Filter'}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </TableCell>
                  
                  <TableCell className="hidden sm:table-cell py-3.5 align-top text-right">
                    <div className="flex flex-col items-end space-y-0.5">
                      <span className="text-xs font-mono text-[var(--color-primary)]">{search.last_run_formatted || 'Never'}</span>
                      <span className="text-[11px] font-mono text-[var(--color-muted)]">{search.run_count || 0} runs</span>
                    </div>
                  </TableCell>
                  
                  <TableCell className="py-3.5 align-top text-right pr-4 relative">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button 
                        variant="secondary" 
                        size="sm"
                        className="h-7 text-xs gap-1.5"
                        onClick={() => handleRunSearch(search)}
                      >
                        <Play className="w-3 h-3 fill-current text-[var(--color-accent)]" />
                        Run
                      </Button>
                      
                      <div className="relative">
                        <Button 
                          variant="ghost" 
                          size="icon"
                          className="h-7 w-7 text-[var(--color-muted)] hover:text-[var(--color-primary)]"
                          onClick={(e) => toggleMenu(e, search.id)}
                        >
                          <MoreHorizontal className="w-3.5 h-3.5" />
                        </Button>
                        
                        {activeMenuId === search.id && (
                          <div 
                            className="absolute right-0 mt-1 w-44 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-md shadow-xl z-20 py-1"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <button 
                              className="w-full text-left px-3 py-1.5 text-xs text-[var(--color-primary)] hover:bg-[var(--color-surface-hover)] flex items-center gap-2"
                              onClick={() => { setActiveMenuId(null); handleOpenForm(search); }}
                            >
                              <Edit2 className="w-3.5 h-3.5" /> Edit
                            </button>
                            <button 
                              className="w-full text-left px-3 py-1.5 text-xs text-[var(--color-primary)] hover:bg-[var(--color-surface-hover)] flex items-center gap-2"
                              onClick={() => { setActiveMenuId(null); handleDuplicate(search); }}
                            >
                              <Copy className="w-3.5 h-3.5" /> Duplicate
                            </button>
                            <button 
                              className="w-full text-left px-3 py-1.5 text-xs text-[var(--color-primary)] hover:bg-[var(--color-surface-hover)] flex items-center gap-2"
                              onClick={() => { setActiveMenuId(null); handleCopyQuery(search.query); }}
                            >
                              <Search className="w-3.5 h-3.5" /> Copy Query
                            </button>
                            <div className="h-px bg-[var(--color-border)] my-1" />
                            <button 
                              className="w-full text-left px-3 py-1.5 text-xs text-rose-400 hover:bg-rose-500/10 flex items-center gap-2"
                              onClick={() => { setActiveMenuId(null); setSelectedSearch(search); setIsDeleteModalOpen(true); }}
                            >
                              <Trash2 className="w-3.5 h-3.5" /> Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-center px-4">
            <Bookmark className="w-6 h-6 text-[var(--color-muted)] mb-2" />
            <h3 className="text-xs font-semibold text-[var(--color-primary)]">No saved searches</h3>
            <p className="text-xs text-[var(--color-muted)] max-w-xs mt-1 mb-4">
              Save semantic queries to quickly return to them at any time.
            </p>
            <Button size="sm" variant="accent" onClick={() => handleOpenForm()}>Create Saved Search</Button>
          </div>
        )}
      </div>

      {/* Form Modal */}
      <Modal
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        title={selectedSearch ? "Edit Saved Search" : "Save Semantic Search"}
      >
        <div className="space-y-3.5 pt-2">
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Search Name</label>
            <Input 
              placeholder="e.g., Database Bottlenecks" 
              value={formData.name}
              onChange={e => setFormData(p => ({ ...p, name: e.target.value }))}
              className="h-8 text-xs"
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Semantic Query</label>
            <Input 
              placeholder="e.g., Where do they discuss database bottlenecks?" 
              value={formData.query}
              onChange={e => setFormData(p => ({ ...p, query: e.target.value }))}
              className="h-8 text-xs"
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-medium text-[var(--color-muted)]">Description (Optional)</label>
            <Input 
              placeholder="Brief note about this search" 
              value={formData.description}
              onChange={e => setFormData(p => ({ ...p, description: e.target.value }))}
              className="h-8 text-xs"
            />
          </div>
          
          <div className="flex justify-end gap-2 pt-3 border-t border-[var(--color-border)]">
            <Button variant="outline" size="sm" onClick={() => setIsFormModalOpen(false)}>Cancel</Button>
            <Button variant="accent" size="sm" onClick={handleSaveSearch} disabled={!formData.name || !formData.query || submitting}>
              {submitting ? "Saving..." : (selectedSearch ? "Save Changes" : "Save Search")}
            </Button>
          </div>
        </div>
      </Modal>
      
      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Saved Search?"
      >
        <div className="space-y-3 pt-2">
          <p className="text-xs text-[var(--color-secondary)]">
            This saved search query will be removed from your workspace.
          </p>
          <div className="flex justify-end gap-2 pt-3 border-t border-[var(--color-border)]">
            <Button variant="outline" size="sm" onClick={() => setIsDeleteModalOpen(false)}>Cancel</Button>
            <Button variant="danger" size="sm" onClick={handleDelete}>Delete</Button>
          </div>
        </div>
      </Modal>
      
    </div>
  );
}
