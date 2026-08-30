'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { 
  Plus, 
  Search, 
  Activity, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  Headphones, 
  Database, 
  Zap, 
  Play, 
  Sparkles, 
  Layers,
  ChevronRight,
  UploadCloud,
  Rss,
  FileAudio
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getEpisodes, Episode } from '@/lib/api/episodes';
import { getProcessingJobs, ProcessingJob } from '@/lib/api/processing';

export default function DashboardPage() {
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        const [episodesData, jobsData] = await Promise.all([
          getEpisodes(),
          getProcessingJobs()
        ]);
        setEpisodes(episodesData || []);
        setJobs(jobsData || []);
      } catch (err) {
        console.warn('Failed to fetch dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, []);

  const totalDurationHours = useMemo(() => {
    const totalSeconds = episodes.reduce((acc, ep) => acc + (ep.duration || 0), 0);
    return (totalSeconds / 3600).toFixed(1);
  }, [episodes]);

  const completedCount = useMemo(() => {
    return episodes.filter(e => (e.status || '').toLowerCase() === 'completed' || (e.status || '').toLowerCase() === 'indexed').length;
  }, [episodes]);

  const activeJobsCount = useMemo(() => {
    return jobs.filter(j => !['completed', 'failed', 'complete'].includes((j.status || '').toLowerCase())).length;
  }, [jobs]);

  const recentSearches = [
    { query: 'database connection pooling bottleneck', time: '2 hours ago', matchCount: 4 },
    { query: 'react server components streaming architecture', time: '5 hours ago', matchCount: 8 },
    { query: 'pgvector cosine similarity indexing', time: '1 day ago', matchCount: 12 },
    { query: 'distributed consensus raft vs paxos', time: '2 days ago', matchCount: 6 },
  ];

  return (
    <div className="space-y-10 relative pb-12">
      {/* Ambient Top Glow */}
      <div className="absolute -top-10 left-1/2 -translate-x-1/2 w-full max-w-4xl h-48 ambient-glow pointer-events-none -z-10" />

      {/* Hero Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-[var(--color-border)] pb-8">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <Badge variant="accent" dot>AI Intelligence Active</Badge>
            <span className="text-xs font-mono text-[var(--color-muted)]">v0.1.0-prod</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[var(--color-primary)]">
            Engineering Podcast Intelligence
          </h1>
          <p className="text-sm text-[var(--color-secondary)] max-w-2xl leading-relaxed">
            Index, search, and extract architectural blueprints from hours of long-form technical conversations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/search">
            <Button variant="secondary" className="gap-2">
              <Search className="w-4 h-4 text-[var(--color-muted)]" />
              Semantic Search
            </Button>
          </Link>
          <Link href="/episodes">
            <Button variant="accent" className="gap-2">
              <UploadCloud className="w-4 h-4" />
              Episode Library
            </Button>
          </Link>
        </div>
      </div>

      {/* Telemetry Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard 
          label="Indexed Audio Content" 
          value={totalDurationHours} 
          unit="hrs" 
          subtext={`across ${episodes.length} episodes (${completedCount} indexed)`} 
          icon={Headphones} 
        />
        <MetricCard 
          label="Active Pipeline Workers" 
          value={String(activeJobsCount)} 
          unit="tasks" 
          subtext={`${jobs.length} total processing jobs`} 
          icon={Activity} 
        />
        <MetricCard 
          label="Vector Engine" 
          value="pgvector" 
          unit="HNSW" 
          subtext="FastEmbed 384-dim semantic search" 
          icon={Zap} 
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Left Column: Recent Episodes */}
        <div className="xl:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Layers className="w-4 h-4 text-[var(--color-accent)]" />
              <h2 className="text-base font-semibold text-[var(--color-primary)] tracking-tight">Recent Episodes</h2>
            </div>
            <Link href="/episodes" className="text-xs font-medium text-[var(--color-muted)] hover:text-[var(--color-primary)] flex items-center gap-1 transition-colors">
              View all
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] overflow-hidden divide-y divide-[var(--color-border)]">
            {episodes.length === 0 ? (
              <div className="p-10 text-center text-[var(--color-muted)] space-y-3">
                <FileAudio className="w-7 h-7 mx-auto opacity-40 text-[var(--color-muted)]" />
                <p className="text-xs font-medium text-[var(--color-primary)]">No episodes ingested yet</p>
                <p className="text-[11px] text-[var(--color-muted)]">Import an RSS feed or upload an audio file to start generating semantic transcripts.</p>
                <div className="flex items-center justify-center gap-2 pt-2">
                  <Link href="/episodes">
                    <Button variant="accent" size="sm" className="text-xs gap-1.5 h-7">
                      <UploadCloud className="w-3 h-3" /> Go to Library
                    </Button>
                  </Link>
                </div>
              </div>
            ) : (
              episodes.slice(0, 5).map((ep) => (
                <div key={ep.id} className="p-4 hover:bg-[var(--color-surface-hover)] transition-colors flex items-center justify-between gap-4 group">
                  <div className="flex items-center gap-3.5 min-w-0">
                    <div className="w-8 h-8 rounded-md bg-[var(--color-surface-elevated)] border border-[var(--color-border)] flex items-center justify-center shrink-0 group-hover:border-[var(--color-accent)] transition-colors">
                      <Play className="w-3.5 h-3.5 text-[var(--color-muted)] group-hover:text-[var(--color-accent)] transition-colors" />
                    </div>
                    <div className="min-w-0">
                      <Link href={`/episodes/${ep.id}`} className="text-sm font-medium text-[var(--color-primary)] hover:text-[var(--color-accent)] transition-colors truncate block">
                        {ep.title}
                      </Link>
                      <div className="flex items-center gap-3 mt-1 text-xs text-[var(--color-muted)] font-mono">
                        <span>{ep.project_name || 'General'}</span>
                        <span>•</span>
                        <span>{formatDuration(ep.duration)}</span>
                        <span>•</span>
                        <span className="capitalize">{ep.status}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Link href={`/episodes/${ep.id}/player`}>
                      <Button variant="secondary" size="sm" className="h-7 text-xs">
                        Play & Transcript
                      </Button>
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Quick Semantic Searches Section */}
          <div className="space-y-4 pt-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[var(--color-accent)]" />
              <h3 className="text-sm font-semibold text-[var(--color-primary)] tracking-tight">Recent Semantic Queries</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {recentSearches.map((item, idx) => (
                <Link
                  key={idx}
                  href={`/search?q=${encodeURIComponent(item.query)}`}
                  className="p-3.5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-border-subtle)] hover:bg-[var(--color-surface-hover)] transition-all group flex flex-col justify-between"
                >
                  <p className="text-xs font-medium text-[var(--color-primary)] group-hover:text-[var(--color-accent)] transition-colors line-clamp-1">
                    &quot;{item.query}&quot;
                  </p>
                  <div className="flex items-center justify-between mt-3 text-[10px] font-mono text-[var(--color-muted)]">
                    <span>{item.matchCount} matched chunks</span>
                    <span>{item.time}</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Processing Pipeline Activity Stream */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-[var(--color-accent)]" />
              <h2 className="text-base font-semibold text-[var(--color-primary)] tracking-tight">Processing Pipeline</h2>
            </div>
            <Link href="/processing" className="text-xs font-medium text-[var(--color-muted)] hover:text-[var(--color-primary)]">
              View Queue
            </Link>
          </div>

          <div className="p-4 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] space-y-5">
            {jobs.length === 0 ? (
              <div className="py-6 text-center text-xs text-[var(--color-muted)]">
                No recent background jobs.
              </div>
            ) : (
              jobs.slice(0, 4).map((job, idx) => (
                <div key={job.id || idx} className="space-y-2 border-b border-[var(--color-border)] last:border-b-0 pb-4 last:pb-0">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-[var(--color-primary)] truncate max-w-[170px]">
                      {job.episode_title || 'Episode Processing'}
                    </span>
                    <Badge variant={job.status === 'completed' ? 'success' : job.status === 'failed' ? 'error' : 'accent'} dot>
                      {job.current_stage || job.status}
                    </Badge>
                  </div>
                  
                  <div className="w-full h-1.5 bg-[var(--color-surface-elevated)] rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-300 ${
                        job.status === 'completed' ? 'bg-emerald-500' : job.status === 'failed' ? 'bg-rose-500' : 'bg-indigo-500'
                      }`}
                      style={{ width: `${job.progress || (job.status === 'completed' ? 100 : 0)}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] font-mono text-[var(--color-muted)]">
                    <span>{job.progress || (job.status === 'completed' ? 100 : 0)}%</span>
                    <span>{job.duration_formatted || (job.status === 'completed' ? 'Indexed' : 'Processing')}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, unit, subtext, icon: Icon }: {
  label: string;
  value: string;
  unit: string;
  subtext: string;
  icon: any;
}) {
  return (
    <div className="p-4 sm:p-5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] hover:border-[var(--color-border-subtle)] transition-all flex flex-col justify-between">
      <div className="flex items-center justify-between text-[var(--color-muted)]">
        <span className="text-xs font-medium">{label}</span>
        <Icon className="w-4 h-4 text-[var(--color-accent)]" />
      </div>
      <div className="mt-3">
        <div className="flex items-baseline gap-1">
          <span className="text-2xl sm:text-3xl font-semibold font-mono text-[var(--color-primary)] tracking-tight">{value}</span>
          <span className="text-xs font-mono text-[var(--color-muted)]">{unit}</span>
        </div>
        <p className="text-[11px] text-[var(--color-muted)] font-mono mt-1">{subtext}</p>
      </div>
    </div>
  );
}

function formatDuration(seconds?: number): string {
  if (!seconds || seconds <= 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}
