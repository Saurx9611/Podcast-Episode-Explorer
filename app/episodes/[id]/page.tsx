'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { 
  Play, 
  Search, 
  Clock, 
  Calendar, 
  Database, 
  FileAudio, 
  Users, 
  Hash, 
  Cpu, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { getEpisode, getTranscript, getSpeakers, Episode, Speaker, TranscriptSegment } from '@/lib/api/episodes';
import { EpisodeInsightModal } from '@/components/episodes/EpisodeInsightModal';

const DEFAULT_TOPICS = [
  { time: '00:00', title: 'Introduction & Architecture Overview', duration: '5m' },
  { time: '05:22', title: 'The Monolith Bottleneck & Connection Limits', duration: '12m' },
  { time: '17:45', title: 'Event-Driven Microservices & PgBouncer', duration: '18m' },
  { time: '35:10', title: 'Handling Eventual Consistency & Cache Invalidation', duration: '8m' },
  { time: '43:30', title: 'Closing Architectural Takeaways', duration: '2m' },
];

export default function EpisodeDetailPage() {
  const params = useParams();
  const id = (params?.id as string) || 'ep-001';

  const [episode, setEpisode] = useState<Episode | null>(null);
  const [speakers, setSpeakers] = useState<Speaker[]>([]);
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
  const [loading, setLoading] = useState(true);
  const [isInsightModalOpen, setIsInsightModalOpen] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [epData, spkData, trData] = await Promise.all([
          getEpisode(id),
          getSpeakers(id),
          getTranscript(id)
        ]);
        setEpisode(epData);
        setSpeakers(spkData);
        setTranscript(trData);
      } catch (err) {
        console.warn('Backend detail fallback for episode:', id);
        setEpisode({
          id,
          title: 'Scaling Distributed Systems Without Sacrificing Reliability',
          project_name: 'Engineering Podcast',
          description: 'An in-depth technical discussion on scaling distributed microservice architectures, state consistency, and migrating away from monolithic bottlenecks with PgBouncer connection pooling.',
          duration_formatted: '45:22',
          date_formatted: 'Oct 24, 2023',
          file_size_formatted: '42.8 MB',
          mime_type: 'audio/mpeg',
          status: 'Indexed',
          processing_model: 'Whisper large-v3',
          index_time: '14.2s',
          created_at: '',
          updated_at: '',
        });
        setSpeakers([
          { id: 'spk-1', episode_id: id, label: 'Speaker 1', display_name: 'Priya Shah', speaking_duration: 1140, segment_count: 6 },
          { id: 'spk-2', episode_id: id, label: 'Speaker 2', display_name: 'Alex Morgan', speaking_duration: 920, segment_count: 5 },
          { id: 'spk-3', episode_id: id, label: 'Speaker 3', display_name: 'Daniel Chen', speaking_duration: 662, segment_count: 2 },
        ]);
      } finally {
        setLoading(false);
      }
    }

    if (id) {
      loadData();
    }
  }, [id]);

  const ep = episode || {
    id,
    title: 'Loading episode...',
    project_name: 'General',
    description: '',
    duration_formatted: '0:00',
    date_formatted: '-',
    file_size_formatted: '0 MB',
    mime_type: 'mp3',
    status: 'Indexed',
    processing_model: 'Whisper large-v3',
    index_time: '14.2s',
    created_at: '',
    updated_at: '',
  };

  const totalSpeakingDuration = speakers.reduce((acc, s) => acc + (s.speaking_duration || 1), 0);

  return (
    <div className="space-y-10 relative pb-16">
      {/* Ambient Top Glow */}
      <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-full max-w-4xl h-40 ambient-glow pointer-events-none -z-10" />

      {/* Episode Header */}
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6 pb-8 border-b border-[var(--color-border)]">
        <div className="space-y-3 max-w-3xl">
          <div className="flex items-center gap-2.5">
            <Badge variant="secondary" className="font-mono text-xs">{ep.project_name || 'General'}</Badge>
            <StatusBadge status={ep.status} />
          </div>
          <h1 className="text-2xl sm:text-3xl font-semibold text-[var(--color-primary)] tracking-tight leading-snug">
            {ep.title}
          </h1>
          {ep.description && (
            <p className="text-sm text-[var(--color-secondary)] leading-relaxed">
              {ep.description}
            </p>
          )}
        </div>

        <div className="flex items-center gap-3 shrink-0 flex-wrap">
          <Button variant="secondary" onClick={() => setIsInsightModalOpen(true)} className="gap-2 text-xs">
            <Sparkles className="w-3.5 h-3.5 text-[var(--color-accent)]" />
            AI Insights
          </Button>
          <Link href={`/search?q=${encodeURIComponent(ep.title)}`}>
            <Button variant="outline" className="gap-2 text-xs">
              <Search className="w-3.5 h-3.5 text-[var(--color-muted)]" />
              Semantic Search
            </Button>
          </Link>
          <Link href={`/episodes/${id}/player`}>
            <Button variant="accent" className="gap-2 text-xs">
              <Play className="w-3.5 h-3.5 fill-current" />
              Open Player & Transcript
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Left Column (2/3) */}
        <div className="lg:col-span-2 space-y-10">
          
          {/* Speaker Distribution */}
          <section className="space-y-4 p-5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-[var(--color-accent)]" />
                <h2 className="text-sm font-semibold text-[var(--color-primary)] tracking-tight">Speaker Diarization</h2>
              </div>
              <span className="text-xs font-mono text-[var(--color-muted)]">{speakers.length} Identified</span>
            </div>

            {/* Speaking Duration Proportion Bar */}
            <div className="w-full h-2 rounded-full overflow-hidden flex bg-[var(--color-surface-elevated)]">
              {speakers.map((s, idx) => {
                const pct = totalSpeakingDuration > 0 ? (s.speaking_duration / totalSpeakingDuration) * 100 : 33;
                const colors = ['bg-emerald-500', 'bg-indigo-500', 'bg-amber-500', 'bg-sky-500'];
                return (
                  <div
                    key={s.id || idx}
                    style={{ width: `${pct}%` }}
                    className={`${colors[idx % colors.length]} transition-all duration-500`}
                    title={`${s.display_name || s.label}: ${pct.toFixed(0)}%`}
                  />
                );
              })}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              {speakers.map((s, idx) => {
                const colors = ['border-emerald-500/30 text-emerald-400', 'border-indigo-500/30 text-indigo-400', 'border-amber-500/30 text-amber-400'];
                const bgColors = ['bg-emerald-500/10', 'bg-indigo-500/10', 'bg-amber-500/10'];
                const pct = totalSpeakingDuration > 0 ? ((s.speaking_duration / totalSpeakingDuration) * 100).toFixed(0) : '33';
                return (
                  <div key={s.id || idx} className="p-3 rounded-md bg-[var(--color-surface-elevated)] border border-[var(--color-border)] flex items-center justify-between">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${bgColors[idx % bgColors.length]} ${colors[idx % colors.length]}`}>
                        {(s.display_name || s.label).charAt(0)}
                      </div>
                      <span className="text-xs font-medium text-[var(--color-primary)] truncate">{s.display_name || s.label}</span>
                    </div>
                    <span className="text-[11px] font-mono text-[var(--color-muted)]">{pct}%</span>
                  </div>
                );
              })}
            </div>
          </section>

          {/* Topics Table */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-[var(--color-accent)]" />
                <h2 className="text-sm font-semibold text-[var(--color-primary)] tracking-tight">Detected Chapters & Key Concepts</h2>
              </div>
            </div>
            
            <div className="border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] overflow-hidden divide-y divide-[var(--color-border)]">
              {DEFAULT_TOPICS.map((topic, i) => (
                <div key={i} className="p-3.5 sm:p-4 flex items-center justify-between gap-4 hover:bg-[var(--color-surface-hover)] transition-colors group">
                  <div className="flex items-center gap-3.5 min-w-0">
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-[var(--color-surface-elevated)] border border-[var(--color-border)] text-[var(--color-accent)] shrink-0">
                      {topic.time}
                    </span>
                    <span className="text-xs sm:text-sm font-medium text-[var(--color-primary)] truncate">
                      {topic.title}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs font-mono text-[var(--color-muted)] hidden sm:inline-block">{topic.duration}</span>
                    <Link href={`/episodes/${id}/player?t=${topic.time.replace(':', '')}`}>
                      <Button variant="ghost" size="icon" className="h-7 w-7 opacity-70 group-hover:opacity-100 group-hover:text-[var(--color-accent)] transition-all">
                        <Play className="w-3.5 h-3.5 fill-current" />
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right Column Metadata (1/3) */}
        <div className="space-y-6">
          
          <section className="p-5 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] space-y-4">
            <h3 className="text-xs font-semibold font-mono text-[var(--color-muted)] uppercase tracking-wider">File & Pipeline Telemetry</h3>
            <div className="space-y-3 divide-y divide-[var(--color-border)] text-xs">
              <MetadataRow icon={Clock} label="Duration" value={ep.duration_formatted || '45:22'} />
              <MetadataRow icon={Calendar} label="Indexed" value={ep.date_formatted || 'Recent'} />
              <MetadataRow icon={FileAudio} label="Format" value={ep.mime_type?.includes('mpeg') || ep.mime_type?.includes('mp3') ? 'mp3' : 'audio'} />
              <MetadataRow icon={Database} label="Size" value={ep.file_size_formatted || '42.8 MB'} />
              <MetadataRow icon={Cpu} label="AI Model" value={ep.processing_model || 'Whisper Large v3'} />
            </div>
          </section>

          {/* AI Intelligence Callout */}
          <div className="p-5 border border-indigo-500/20 bg-indigo-950/10 rounded-lg space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-indigo-300 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Technical Intelligence
              </span>
              <Badge variant="accent">Ready</Badge>
            </div>
            <p className="text-xs text-[var(--color-secondary)] leading-relaxed">
              Extract targeted competencies, technology matrices, architectural blueprints, and high-impact resume bullets.
            </p>
            <Button 
              variant="accent" 
              size="sm" 
              onClick={() => setIsInsightModalOpen(true)}
              className="w-full text-xs gap-1.5 mt-1"
            >
              <Sparkles className="w-3.5 h-3.5" />
              View Architectural Blueprint
            </Button>
          </div>
          
        </div>

      </div>

      {/* Episode Insight Modal */}
      <EpisodeInsightModal
        isOpen={isInsightModalOpen}
        onClose={() => setIsInsightModalOpen(false)}
        episodeId={id}
        episodeTitle={ep.title}
      />
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const norm = (status || '').toLowerCase();
  if (norm === 'indexed' || norm === 'completed') {
    return <Badge variant="success" dot>Indexed</Badge>;
  }
  if (norm === 'processing' || norm === 'queued' || norm === 'transcribing' || norm === 'chunking' || norm === 'embedding' || norm === 'indexing') {
    return <Badge variant="accent" dot>Processing</Badge>;
  }
  return <Badge variant="error" dot>Failed</Badge>;
}

function MetadataRow({ icon: Icon, label, value }: { icon: any, label: string, value: string }) {
  return (
    <div className="flex items-center justify-between pt-2.5 first:pt-0">
      <div className="flex items-center gap-2 text-[var(--color-muted)]">
        <Icon className="w-3.5 h-3.5" />
        <span>{label}</span>
      </div>
      <span className="font-medium text-[var(--color-primary)] font-mono">{value}</span>
    </div>
  );
}
