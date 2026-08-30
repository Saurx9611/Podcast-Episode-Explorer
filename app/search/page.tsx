"use client";

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { 
  Search, 
  Play, 
  FileText, 
  Bookmark, 
  Sparkles, 
  ChevronDown, 
  Clock, 
  Filter, 
  Loader2, 
  Check 
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { performSearch, createSavedSearch, SearchResultItem } from '@/lib/api/search';
import { getProjects, Project } from '@/lib/api/projects';

const FALLBACK_SEARCH_RESULTS: SearchResultItem[] = [
  {
    id: 'res-1',
    episode_id: 'ep-001',
    project: 'Engineering Podcast',
    episode_title: 'Scaling Distributed Systems',
    speaker: 'Priya Shah',
    speaker_color: 'text-emerald-400',
    start_time: 18,
    end_time: 28,
    timestamp: '00:18',
    time_sec: 18,
    score: 0.98,
    match_score: 98,
    context_before: "It wasn't a single moment, but rather a slow degradation of developer velocity. ",
    highlight: "Our database became the integration point for every team",
    context_after: ". If the billing team needed to add a column, they had to coordinate with the fulfillment team.",
    text: "Our database became the integration point for every team."
  },
  {
    id: 'res-2',
    episode_id: 'ep-001',
    project: 'Engineering Podcast',
    episode_title: 'Scaling Distributed Systems',
    speaker: 'Daniel Chen',
    speaker_color: 'text-amber-400',
    start_time: 102,
    end_time: 114,
    timestamp: '01:42',
    time_sec: 102,
    score: 0.86,
    match_score: 86,
    context_before: "When the event consumer started failing, we noticed that ",
    highlight: "database connections were queueing up, creating a massive bottleneck",
    context_after: " during the traffic spike.",
    text: "database connections were queueing up, creating a massive bottleneck during the traffic spike."
  },
  {
    id: 'res-3',
    episode_id: 'ep-002',
    project: 'System Design Sessions',
    speaker: 'Alex Morgan',
    speaker_color: 'text-indigo-400',
    episode_title: 'Migrating from Monolith to Microservices',
    start_time: 125,
    end_time: 142,
    timestamp: '02:05',
    time_sec: 125,
    score: 0.79,
    match_score: 79,
    context_before: "You have to be careful when extracting domains because the ",
    highlight: "shared database often becomes the primary bottleneck",
    context_after: " in a microservices transition.",
    text: "shared database often becomes the primary bottleneck in a microservices transition."
  }
];

function SearchContent() {
  const searchParams = useSearchParams();
  const initialQ = searchParams?.get('q') || "database bottleneck";
  
  const [query, setQuery] = useState(initialQ);
  const [results, setResults] = useState<SearchResultItem[]>(FALLBACK_SEARCH_RESULTS);
  const [loading, setLoading] = useState(false);
  const [executionTime, setExecutionTime] = useState<number>(38);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string>('all');
  const [threshold, setThreshold] = useState<number>(0.5);
  const [showFilters, setShowFilters] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState<string | null>(null);

  const executeSearch = async (qText: string) => {
    if (!qText.trim()) return;
    try {
      setLoading(true);
      const res = await performSearch({
        query: qText.trim(),
        project_id: selectedProjectId !== 'all' ? selectedProjectId : undefined,
        similarity_threshold: threshold,
        limit: 15,
      });

      if (res && res.results) {
        setResults(res.results);
        setExecutionTime(res.execution_time_ms || 0);
      }
    } catch (err: any) {
      console.warn('Backend search error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    async function loadProjects() {
      try {
        const projs = await getProjects();
        setProjects(projs);
      } catch {
        // Ignored
      }
    }
    loadProjects();
    executeSearch(initialQ);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(query);
  };

  const handleSaveSearch = async (resItem: SearchResultItem) => {
    try {
      await createSavedSearch({
        name: `Query: ${query.slice(0, 30)}`,
        query: query,
        description: `Saved from semantic search: "${resItem.highlight || resItem.text.slice(0, 40)}"`,
      });
      setSavedSuccess(resItem.id);
      setTimeout(() => setSavedSuccess(null), 2500);
    } catch (err: any) {
      alert(err.message || 'Failed to save search.');
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      
      {/* Search Header */}
      <div className="space-y-4">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <Badge variant="accent" dot>pgvector Indexing</Badge>
            <span className="text-xs font-mono text-[var(--color-muted)]">1536 Dimensions</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[var(--color-primary)]">
            Semantic Concept Search
          </h1>
          <p className="text-xs sm:text-sm text-[var(--color-secondary)]">
            Retrieve dialogue segments by meaning, concepts, and technical trade-offs across all episodes.
          </p>
        </div>

        {/* Search Input Bar */}
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-2.5">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[var(--color-muted)] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search concepts e.g. distributed locking, Kafka outbox pattern..."
              className="w-full pl-10 pr-4 py-2.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-primary)] text-sm outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)] transition-all placeholder:text-[var(--color-muted)]"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button 
              type="button" 
              variant={showFilters ? 'secondary' : 'outline'} 
              onClick={() => setShowFilters(!showFilters)} 
              className="gap-2 h-10 px-4 text-xs"
            >
              <Filter className="w-3.5 h-3.5" /> Filters
            </Button>
            <Button type="submit" variant="accent" disabled={loading} className="h-10 px-6 font-medium gap-2 text-xs">
              {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
              Search
            </Button>
          </div>
        </form>

        {/* Filter Toolbar */}
        {showFilters && (
          <div className="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg grid grid-cols-1 sm:grid-cols-2 gap-4 animate-in fade-in duration-150">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--color-muted)] font-mono">Scope to Project</label>
              <select
                value={selectedProjectId}
                onChange={(e) => {
                  setSelectedProjectId(e.target.value);
                  setTimeout(() => executeSearch(query), 50);
                }}
                className="w-full h-8 rounded-md border border-[var(--color-border)] bg-[var(--color-surface-elevated)] px-3 text-xs text-[var(--color-primary)] outline-none focus:border-[var(--color-accent)]"
              >
                <option value="all">All Projects</option>
                {projects.map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--color-muted)] font-mono">
                Cosine Similarity Threshold: {Math.round(threshold * 100)}%
              </label>
              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                onMouseUp={() => executeSearch(query)}
                className="w-full mt-1.5 accent-[var(--color-accent)] cursor-pointer"
              />
            </div>
          </div>
        )}
      </div>

      {/* Results Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs font-mono text-[var(--color-muted)] border-b border-[var(--color-border)] pb-3">
          <span className="text-[var(--color-primary)] font-medium">
            {loading ? 'Executing vector search...' : `${results.length} semantic segment match${results.length === 1 ? '' : 'es'}`}
          </span>
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-[var(--color-accent)]" /> {executionTime}ms
          </span>
        </div>

        {results.length === 0 ? (
          <div className="border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] p-12 text-center text-[var(--color-muted)] space-y-3">
            <Search className="w-7 h-7 mx-auto text-[var(--color-muted)]" />
            <p className="text-sm font-medium text-[var(--color-primary)]">No segments matched threshold &ge; {Math.round(threshold * 100)}%</p>
            <p className="text-xs text-[var(--color-muted)]">Try lowering the similarity threshold or refining query terminology.</p>
            <Button variant="outline" size="sm" onClick={() => { setThreshold(0.25); executeSearch(query); }}>
              Lower Threshold to 25% &amp; Search
            </Button>
          </div>
        ) : (
          <div className="border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] divide-y divide-[var(--color-border)] overflow-hidden">
            {results.map((res) => (
              <div key={res.id} className="p-5 hover:bg-[var(--color-surface-hover)] transition-all duration-150 flex flex-col gap-4 group">
                
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Badge variant="secondary" className="font-mono text-[10px] bg-[var(--color-surface-elevated)] shrink-0">
                      {res.project || 'General'}
                    </Badge>
                    <Link href={`/episodes/${res.episode_id}`} className="text-sm font-semibold text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors truncate">
                      {res.episode_title}
                    </Link>
                  </div>
                  
                  <Badge variant="accent" dot className="shrink-0 font-mono">
                    {res.match_score || Math.round(res.score * 100)}% Match
                  </Badge>
                </div>

                {/* Transcript Preview */}
                <div className="pl-3.5 border-l-2 border-[var(--color-accent)]/60 py-0.5 space-y-1.5">
                  <div className="flex items-center gap-2.5">
                    <span className="text-xs font-semibold text-indigo-300">{res.speaker || 'Speaker'}</span>
                    <Link href={`/episodes/${res.episode_id}/player?t=${res.time_sec || res.start_time}`}>
                      <span className="font-mono text-[11px] text-[var(--color-muted)] hover:text-[var(--color-primary)] flex items-center gap-1 transition-colors">
                        <Play className="w-2.5 h-2.5 fill-current text-[var(--color-accent)]" /> {res.timestamp}
                      </span>
                    </Link>
                  </div>
                  <p className="text-xs sm:text-sm leading-relaxed text-[var(--color-primary)]">
                    {res.context_before && <span className="text-[var(--color-muted)]">{res.context_before}</span>}
                    <span className="bg-[var(--color-accent-subtle)] text-[var(--color-accent-hover)] font-medium px-1 rounded mx-0.5">
                      {res.highlight || res.text}
                    </span>
                    {res.context_after && <span className="text-[var(--color-muted)]">{res.context_after}</span>}
                  </p>
                </div>

                {/* Quick Action Strip */}
                <div className="flex items-center gap-2.5 pt-1">
                  <Link href={`/episodes/${res.episode_id}/player?t=${res.time_sec || res.start_time}`}>
                    <Button variant="secondary" size="sm" className="gap-1.5 h-7 text-xs">
                      <Play className="w-3 h-3 fill-current text-[var(--color-accent)]" /> Play Match
                    </Button>
                  </Link>
                  <Link href={`/episodes/${res.episode_id}/player?t=${res.time_sec || res.start_time}`}>
                    <Button variant="ghost" size="sm" className="gap-1.5 h-7 text-xs text-[var(--color-muted)] hover:text-[var(--color-primary)]">
                      <FileText className="w-3 h-3" /> Transcript
                    </Button>
                  </Link>
                  <div className="flex-1"></div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => handleSaveSearch(res)}
                    className="h-7 gap-1.5 text-xs text-[var(--color-muted)] hover:text-[var(--color-primary)]"
                  >
                    {savedSuccess === res.id ? (
                      <><Check className="w-3 h-3 text-emerald-400" /> Saved</>
                    ) : (
                      <><Bookmark className="w-3 h-3" /> Save Result</>
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
    </div>
  );
}

export default function SemanticSearchPage() {
  return (
    <Suspense fallback={<div className="p-10 text-xs font-mono text-[var(--color-muted)]">Initializing pgvector query engine...</div>}>
      <SearchContent />
    </Suspense>
  );
}
