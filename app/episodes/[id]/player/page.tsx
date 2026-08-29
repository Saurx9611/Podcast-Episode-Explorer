"use client";

import React, { useState, useEffect, useRef, useMemo, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { 
  Play, 
  Pause, 
  Search, 
  Rewind, 
  FastForward, 
  ChevronLeft,
  Share,
  Link as LinkIcon,
  Volume2,
  VolumeX,
  Check,
  CheckCircle2,
  Sparkles,
  Layers,
  Radio,
  Sliders
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { getEpisode, getTranscript, getSpeakers, Episode, Speaker, TranscriptSegment } from '@/lib/api/episodes';
import { ConnectedWaveformTimeline } from '@/components/player/ConnectedWaveformTimeline';

const FALLBACK_TRANSCRIPT: TranscriptSegment[] = [
  { id: 'seg-1', episode_id: 'ep-001', sequence_number: 1, start_time: 0, end_time: 18, start: '00:00', startSec: 0, speaker: { id: 'spk-1', episode_id: 'ep-001', label: 'Speaker 1', display_name: 'Alex Morgan', speaking_duration: 920, segment_count: 5 }, text: "Welcome back to the Engineering Podcast. Today we're diving deep into a topic that almost every growing engineering organization faces eventually: the transition from a monolithic architecture to microservices, and more specifically, how to manage state and consistency when you do that." },
  { id: 'seg-2', episode_id: 'ep-001', sequence_number: 2, start_time: 18, end_time: 28, start: '00:18', startSec: 18, speaker: { id: 'spk-2', episode_id: 'ep-001', label: 'Speaker 2', display_name: 'Priya Shah', speaking_duration: 1140, segment_count: 6 }, text: "Thanks Alex. It's great to be here. This is definitely one of those architectural challenges that looks straightforward on a whiteboard but gets incredibly messy in production." },
  { id: 'seg-3', episode_id: 'ep-001', sequence_number: 3, start_time: 28, end_time: 39, start: '00:28', startSec: 28, speaker: { id: 'spk-1', episode_id: 'ep-001', label: 'Speaker 1', display_name: 'Alex Morgan', speaking_duration: 920, segment_count: 5 }, text: "Exactly. Before we get into the solutions, let's talk about the pain points. When did you realize at your previous company that the monolith was no longer serving you?" },
  { id: 'seg-4', episode_id: 'ep-001', sequence_number: 4, start_time: 39, end_time: 62, start: '00:39', startSec: 39, speaker: { id: 'spk-2', episode_id: 'ep-001', label: 'Speaker 2', display_name: 'Priya Shah', speaking_duration: 1140, segment_count: 6 }, text: "It wasn't a single moment, but rather a slow degradation of developer velocity. Our database became the integration point for every team. If the billing team needed to add a column, they had to coordinate with the fulfillment team because they were querying the same tables. Deployments took hours, and rollbacks were terrifying." },
  { id: 'seg-5', episode_id: 'ep-001', sequence_number: 5, start_time: 62, end_time: 76, start: '01:02', startSec: 62, speaker: { id: 'spk-3', episode_id: 'ep-001', label: 'Speaker 3', display_name: 'Daniel Chen', speaking_duration: 662, segment_count: 2 }, text: "I'll add to that. The cognitive load for new engineers was immense. You couldn't just understand one domain; you had to understand how your changes might trigger side effects across a 5-million line codebase." },
  { id: 'seg-6', episode_id: 'ep-001', sequence_number: 6, start_time: 76, end_time: 81, start: '01:16', startSec: 76, speaker: { id: 'spk-1', episode_id: 'ep-001', label: 'Speaker 1', display_name: 'Alex Morgan', speaking_duration: 920, segment_count: 5 }, text: "So you decided to split it up. What was the first boundary you drew?" },
  { id: 'seg-7', episode_id: 'ep-001', sequence_number: 7, start_time: 81, end_time: 102, start: '01:21', startSec: 81, speaker: { id: 'spk-2', episode_id: 'ep-001', label: 'Speaker 2', display_name: 'Priya Shah', speaking_duration: 1140, segment_count: 6 }, text: "We started with the lowest risk, highest isolation component: email and notifications. It didn't need synchronous access to core transaction data, so we could wrap it in an event-driven interface. We set up a Kafka cluster and just started publishing domain events from the monolith." },
  { id: 'seg-8', episode_id: 'ep-001', sequence_number: 8, start_time: 102, end_time: 114, start: '01:42', startSec: 102, speaker: { id: 'spk-3', episode_id: 'ep-001', label: 'Speaker 3', display_name: 'Daniel Chen', speaking_duration: 662, segment_count: 2 }, text: "Which sounds great until you realize your event publisher and your database transaction aren't atomic. That's when we hit our first major distributed systems outage." },
  { id: 'seg-9', episode_id: 'ep-001', sequence_number: 9, start_time: 114, end_time: 125, start: '01:54', startSec: 114, speaker: { id: 'spk-1', episode_id: 'ep-001', label: 'Speaker 1', display_name: 'Alex Morgan', speaking_duration: 920, segment_count: 5 }, text: "The classic dual-write problem. Let's dig into that. How did you resolve it?" },
  { id: 'seg-10', episode_id: 'ep-001', sequence_number: 10, start_time: 125, end_time: 142, start: '02:05', startSec: 125, speaker: { id: 'spk-2', episode_id: 'ep-001', label: 'Speaker 2', display_name: 'Priya Shah', speaking_duration: 1140, segment_count: 6 }, text: "We eventually implemented the Transactional Outbox pattern. Instead of publishing to Kafka directly from the application code, we wrote the event to an 'outbox' table within the exact same database transaction that updated our core domain entities." },
  { id: 'seg-11', episode_id: 'ep-001', sequence_number: 11, start_time: 142, end_time: 165, start: '02:22', startSec: 142, speaker: { id: 'spk-3', episode_id: 'ep-001', label: 'Speaker 3', display_name: 'Daniel Chen', speaking_duration: 662, segment_count: 2 }, text: "Right, and then a separate background worker—often called a relay or a CDC process—tails that outbox table and actually pushes the messages to the broker. If the application crashes immediately after committing to the database, the event is still safely stored and will eventually be published." },
  { id: 'seg-12', episode_id: 'ep-001', sequence_number: 12, start_time: 165, end_time: 173, start: '02:45', startSec: 165, speaker: { id: 'spk-1', episode_id: 'ep-001', label: 'Speaker 1', display_name: 'Alex Morgan', speaking_duration: 920, segment_count: 5 }, text: "That guarantees at-least-once delivery. But how did you handle the potential for duplicate events downstream?" },
  { id: 'seg-13', episode_id: 'ep-001', sequence_number: 13, start_time: 173, end_time: 200, start: '02:53', startSec: 173, speaker: { id: 'spk-2', episode_id: 'ep-001', label: 'Speaker 2', display_name: 'Priya Shah', speaking_duration: 1140, segment_count: 6 }, text: "Idempotency. Every consumer of those events had to be designed to be idempotent. We enforced a strict pattern where every event had a unique ID, and consumers had to track which IDs they had already processed. It required a significant shift in how our teams thought about database writes." }
];

function formatTime(secs: number) {
  if (isNaN(secs) || secs < 0) return '00:00';
  const total = Math.floor(secs);
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function PlayerContent({ id }: { id: string }) {
  const searchParams = useSearchParams();
  const [episode, setEpisode] = useState<Episode | null>(null);
  const [transcript, setTranscript] = useState<TranscriptSegment[]>(FALLBACK_TRANSCRIPT);
  const [speakers, setSpeakers] = useState<Speaker[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [copiedId, setCopiedId] = useState<string | number | null>(null);
  const [searchFilter, setSearchFilter] = useState('');
  const [selectedSpeakerFilter, setSelectedSpeakerFilter] = useState<string>('all');
  
  const transcriptRefs = useRef<(HTMLDivElement | null)[]>([]);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const prevActiveIndex = useRef<number>(-1);
  const isUserScrolling = useRef<boolean>(false);
  const userScrollTimeout = useRef<NodeJS.Timeout | null>(null);

  // Load episode and transcript
  useEffect(() => {
    async function loadData() {
      try {
        const [epData, spkData, trData] = await Promise.all([
          getEpisode(id),
          getSpeakers(id),
          getTranscript(id)
        ]);
        setEpisode(epData);
        setSpeakers(spkData);
        if (trData && trData.length > 0) {
          setTranscript(trData);
        }
      } catch (err) {
        console.warn('Using fallback player data for episode:', id);
      }
    }

    if (id) {
      loadData();
    }
  }, [id]);

  const totalDurationSec = useMemo(() => {
    if (episode?.duration && episode.duration > 0) {
      return episode.duration;
    }
    if (transcript.length > 0) {
      const maxEnd = Math.max(...transcript.map(s => s.end_time || 0));
      if (maxEnd > 0) return maxEnd;
    }
    return 2722;
  }, [episode, transcript]);

  // Deep linking: seek to query param ?t=...
  useEffect(() => {
    const t = searchParams?.get('t');
    if (t) {
      const num = Number(t);
      if (!isNaN(num)) {
        setCurrentTime(num);
      }
    }
  }, [searchParams]);

  // Search match seconds across transcript
  const searchMatches = useMemo(() => {
    if (!searchFilter.trim()) return [];
    const q = searchFilter.toLowerCase();
    return transcript
      .filter(s => s.text.toLowerCase().includes(q))
      .map(s => (s.startSec !== undefined ? s.startSec : s.start_time));
  }, [transcript, searchFilter]);

  // Playback timer (smooth 250ms tick)
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime(t => {
          if (t >= totalDurationSec) {
            setIsPlaying(false);
            return totalDurationSec;
          }
          return t + (0.25 * playbackRate);
        });
      }, 250);
    }
    return () => clearInterval(interval);
  }, [isPlaying, playbackRate, totalDurationSec]);

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes((e.target as HTMLElement)?.tagName)) return;

      if (e.code === 'Space') {
        e.preventDefault();
        setIsPlaying(prev => !prev);
      } else if (e.code === 'ArrowRight' || e.key === 'l') {
        e.preventDefault();
        setCurrentTime(t => Math.min(t + 10, totalDurationSec));
      } else if (e.code === 'ArrowLeft' || e.key === 'j') {
        e.preventDefault();
        setCurrentTime(t => Math.max(t - 10, 0));
      } else if (e.key === 'k') {
        e.preventDefault();
        setIsPlaying(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [totalDurationSec]);

  // Determine active segment index
  const activeIndex = useMemo(() => {
    return transcript.findIndex((s, i) => {
      const segStart = s.startSec !== undefined ? s.startSec : s.start_time;
      const nextSeg = transcript[i + 1];
      const nextStart = nextSeg ? (nextSeg.startSec !== undefined ? nextSeg.startSec : nextSeg.start_time) : Infinity;
      return currentTime >= segStart && currentTime < nextStart;
    });
  }, [transcript, currentTime]);

  // Auto-scroll transcript when playing unless user manually scrolling
  useEffect(() => {
    if (isPlaying && activeIndex !== -1 && activeIndex !== prevActiveIndex.current && !isUserScrolling.current) {
      const activeEl = transcriptRefs.current[activeIndex];
      if (activeEl) {
        activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      prevActiveIndex.current = activeIndex;
    }
  }, [activeIndex, isPlaying]);

  // Track user manual scrolling to prevent jitter
  const handleTranscriptScroll = () => {
    isUserScrolling.current = true;
    if (userScrollTimeout.current) clearTimeout(userScrollTimeout.current);
    userScrollTimeout.current = setTimeout(() => {
      isUserScrolling.current = false;
    }, 2000);
  };

  const handleSeek = (newTime: number) => {
    setCurrentTime(Math.max(0, Math.min(newTime, totalDurationSec)));
  };

  const skipForward = () => handleSeek(currentTime + 15);
  const skipBackward = () => handleSeek(currentTime - 15);

  const togglePlaybackRate = () => {
    const rates = [1, 1.2, 1.5, 2];
    const nextIndex = (rates.indexOf(playbackRate) + 1) % rates.length;
    setPlaybackRate(rates[nextIndex]);
  };

  const copyTimestampLink = (sec: number, segmentId: string | number) => {
    const url = new URL(window.location.href);
    url.searchParams.set('t', Math.floor(sec).toString());
    navigator.clipboard.writeText(url.toString());
    
    setCopiedId(segmentId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredTranscript = useMemo(() => {
    return transcript.filter(segment => {
      const speakerName = segment.speaker?.display_name || segment.speaker?.label || (typeof segment.speaker === 'string' ? segment.speaker : 'Speaker');
      
      const matchesSearch = !searchFilter || 
        segment.text.toLowerCase().includes(searchFilter.toLowerCase()) ||
        speakerName.toLowerCase().includes(searchFilter.toLowerCase());

      const matchesSpeaker = selectedSpeakerFilter === 'all' || 
        (segment.speaker_id && segment.speaker_id === selectedSpeakerFilter) ||
        (segment.speaker?.id === selectedSpeakerFilter) ||
        (segment.speaker?.label === selectedSpeakerFilter);

      return matchesSearch && matchesSpeaker;
    });
  }, [transcript, searchFilter, selectedSpeakerFilter]);

  const activeSegment = activeIndex >= 0 ? transcript[activeIndex] : null;
  const activeSpeakerName = activeSegment?.speaker?.display_name || activeSegment?.speaker?.label || (typeof activeSegment?.speaker === 'string' ? activeSegment?.speaker : 'Speaker');

  return (
    <div className="flex flex-col h-[calc(100vh-56px)] bg-[var(--color-background)] overflow-hidden">
      
      {/* Top Breadcrumb Header */}
      <div className="h-14 flex items-center justify-between px-6 border-b border-[var(--color-border)] bg-[var(--color-surface)] shrink-0">
        <div className="flex items-center gap-4">
          <Link href={`/episodes/${id}`} className="text-[var(--color-muted)] hover:text-[var(--color-primary)] transition-colors">
            <ChevronLeft className="w-4 h-4" />
          </Link>
          <div className="h-3 w-px bg-[var(--color-border)]"></div>
          <div>
            <h1 className="text-xs sm:text-sm font-semibold text-[var(--color-primary)] tracking-tight">
              {episode?.title || 'Scaling Distributed Systems Without Sacrificing Reliability'}
            </h1>
            <p className="text-[10px] font-mono text-[var(--color-muted)]">
              {episode?.project_name || 'Engineering Podcast'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="accent" dot className="font-mono text-[10px]">Spatial-Temporal Connected</Badge>
          <Button variant="ghost" size="sm" className="gap-1.5 text-xs hidden sm:flex" onClick={() => copyTimestampLink(currentTime, 'current')}>
            <Share className="w-3.5 h-3.5" /> Share
          </Button>
        </div>
      </div>

      {/* Main Split View */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        
        {/* Left Column: Player Deck & Connected Waveform (Width 400px) */}
        <div className="w-full lg:w-[420px] shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface)] flex flex-col justify-between overflow-y-auto p-6 space-y-6">
          
          <div className="space-y-6">
            
            {/* Playback Controls & Waveform Ribbon Deck */}
            <div className="p-5 rounded-lg bg-[var(--color-surface-elevated)] border border-[var(--color-border)] space-y-6 shadow-xs">
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 text-[var(--color-muted)]">
                  <button onClick={() => setIsMuted(!isMuted)} className="hover:text-[var(--color-primary)] transition-colors">
                    {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                  </button>
                  <button onClick={togglePlaybackRate} className="text-xs font-mono font-medium hover:text-[var(--color-primary)] transition-colors bg-[var(--color-surface)] px-2 py-0.5 rounded border border-[var(--color-border)]">
                    {playbackRate.toFixed(1)}x
                  </button>
                </div>

                <div className="flex items-center gap-4">
                  <button onClick={skipBackward} className="text-[var(--color-muted)] hover:text-[var(--color-primary)] transition-colors active:scale-95">
                    <Rewind className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="w-12 h-12 flex items-center justify-center bg-[var(--color-primary)] text-[var(--color-background)] hover:bg-[#e2e8f0] rounded-full transition-all duration-150 active:scale-95 shadow-md shadow-black/40"
                  >
                    {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
                  </button>
                  <button onClick={skipForward} className="text-[var(--color-muted)] hover:text-[var(--color-primary)] transition-colors active:scale-95">
                    <FastForward className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* SIGNATURE INTERACTION: Connected Multi-Track Waveform Timeline */}
              <div className="space-y-1.5 pt-1">
                <ConnectedWaveformTimeline
                  currentTime={currentTime}
                  totalDuration={totalDurationSec}
                  segments={transcript}
                  speakers={speakers}
                  searchMatches={searchMatches}
                  onSeek={handleSeek}
                  isPlaying={isPlaying}
                />
              </div>

            </div>

            {/* Active Speaker Spotlight with Temporal Accent */}
            <div className="p-4 rounded-lg bg-[var(--color-surface-elevated)] border border-[var(--color-border)] space-y-2 relative overflow-hidden transition-all duration-300">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Radio className="w-3.5 h-3.5 text-[var(--color-accent)] animate-pulse" />
                  <span className="text-[10px] font-semibold font-mono text-[var(--color-muted)] uppercase tracking-wider">Active Speaker Spotlight</span>
                </div>
                {activeSegment && (
                  <span className="text-[11px] font-mono font-semibold text-[var(--color-accent)]">{activeSegment.start || formatTime(activeSegment.start_time)}</span>
                )}
              </div>
              
              {activeSegment ? (
                <div className="space-y-1.5 pt-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-emerald-400">{activeSpeakerName}</span>
                    <span className="text-[10px] font-mono text-[var(--color-muted)]">Segment #{activeSegment.sequence_number || (activeIndex + 1)}</span>
                  </div>
                  <p className="text-xs text-[var(--color-secondary)] line-clamp-3 leading-relaxed">
                    &quot;{activeSegment.text}&quot;
                  </p>
                </div>
              ) : (
                <p className="text-xs text-[var(--color-muted)]">Audio stopped.</p>
              )}
            </div>

          </div>

          {/* Precision Navigation Hotkeys */}
          <div className="space-y-2 pt-3 border-t border-[var(--color-border)]">
            <span className="text-[10px] font-semibold font-mono text-[var(--color-muted)] uppercase tracking-wider">Keyboard Navigation</span>
            <div className="space-y-1.5 text-xs text-[var(--color-muted)]">
              <div className="flex justify-between items-center">
                <span>Play / Pause</span>
                <kbd className="px-1.5 py-0.5 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded text-[10px] font-mono text-gray-300">Space / K</kbd>
              </div>
              <div className="flex justify-between items-center">
                <span>Seek ±10s</span>
                <kbd className="px-1.5 py-0.5 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded text-[10px] font-mono text-gray-300">J / L or ← / →</kbd>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Connected Synchronized Transcript (De-emphasized Non-Active Segments) */}
        <div className="flex-1 flex flex-col bg-[var(--color-background)] min-w-0">
          
          {/* Transcript Search Toolbar with Live Match Count */}
          <div className="p-3.5 px-6 border-b border-[var(--color-border)] bg-[var(--color-surface)]/90 backdrop-blur-xs flex items-center justify-between gap-4 shrink-0">
            <div className="w-full max-w-sm flex items-center gap-2">
              <Input 
                icon={<Search className="w-3.5 h-3.5" />} 
                placeholder="Filter dialogue by phrase or concept..." 
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="h-8 text-xs flex-1"
              />
              {searchMatches.length > 0 && (
                <Badge variant="accent" className="font-mono text-[10px] py-1 shrink-0">
                  {searchMatches.length} match{searchMatches.length === 1 ? '' : 'es'}
                </Badge>
              )}
            </div>
            
            {speakers.length > 0 && (
              <select
                value={selectedSpeakerFilter}
                onChange={(e) => setSelectedSpeakerFilter(e.target.value)}
                className="h-8 rounded-md border border-[var(--color-border)] bg-[var(--color-surface-elevated)] px-2.5 text-xs text-[var(--color-primary)] outline-none focus:border-[var(--color-accent)]"
              >
                <option value="all">All Speakers</option>
                {speakers.map(s => (
                  <option key={s.id} value={s.id}>{s.display_name || s.label}</option>
                ))}
              </select>
            )}
          </div>

          {/* Transcript Dialogue Stream */}
          <div 
            ref={scrollContainerRef}
            onScroll={handleTranscriptScroll}
            className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8 space-y-3 scroll-smooth"
          >
            <div className="max-w-4xl mx-auto space-y-3">
              {filteredTranscript.map((segment, index) => {
                const segStartSec = segment.startSec !== undefined ? segment.startSec : segment.start_time;
                const segStartTimeFormatted = segment.start || formatTime(segStartSec);
                const isActive = index === activeIndex;
                const speakerName = segment.speaker?.display_name || segment.speaker?.label || (typeof segment.speaker === 'string' ? segment.speaker : 'Speaker');

                const speakerColor = 
                  speakerName.includes('Priya') ? 'text-emerald-400' :
                  speakerName.includes('Alex') ? 'text-indigo-400' :
                  speakerName.includes('Daniel') ? 'text-amber-400' :
                  'text-sky-400';

                const speakerBorderColor = 
                  speakerName.includes('Priya') ? 'border-emerald-500/40 bg-emerald-950/10' :
                  speakerName.includes('Alex') ? 'border-indigo-500/40 bg-indigo-950/10' :
                  speakerName.includes('Daniel') ? 'border-amber-500/40 bg-amber-950/10' :
                  'border-sky-500/40 bg-sky-950/10';

                return (
                  <div 
                    key={segment.id || index} 
                    ref={el => { transcriptRefs.current[index] = el; }}
                    className={`group relative flex flex-col sm:flex-row gap-3 sm:gap-5 p-4 rounded-lg transition-all duration-300 border ${
                      isActive 
                        ? `${speakerBorderColor} shadow-md shadow-black/30 scale-[1.008] z-10 opacity-100` 
                        : isPlaying 
                          ? 'border-transparent opacity-45 hover:opacity-100 hover:bg-[var(--color-surface)]/60' 
                          : 'border-transparent opacity-85 hover:opacity-100 hover:bg-[var(--color-surface)]/60 hover:border-[var(--color-border)]'
                    }`}
                  >
                    {/* Timestamp Trigger */}
                    <div className="sm:w-16 shrink-0 flex items-center sm:items-start justify-between sm:justify-start pt-0.5">
                      <button 
                        onClick={() => {
                          handleSeek(segStartSec);
                          setIsPlaying(true);
                        }}
                        className={`font-mono text-xs transition-colors flex items-center gap-1.5 cursor-pointer ${
                          isActive 
                            ? 'text-[var(--color-accent)] font-bold' 
                            : 'text-[var(--color-muted)] group-hover:text-[var(--color-primary)]'
                        }`}
                      >
                        <span className="group-hover:hidden">{segStartTimeFormatted}</span>
                        <Play className="w-3.5 h-3.5 fill-current hidden group-hover:inline-block" />
                      </button>
                    </div>

                    {/* Dialogue Text */}
                    <div className="flex-1 space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-semibold ${speakerColor}`}>
                            {speakerName}
                          </span>
                          {isActive && (
                            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[var(--color-accent-subtle)] text-[var(--color-accent-hover)]">
                              Active Track
                            </span>
                          )}
                        </div>
                        
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-6 px-2 text-[11px] opacity-0 group-hover:opacity-100 transition-opacity gap-1 text-[var(--color-muted)] hover:text-[var(--color-primary)]"
                          onClick={() => copyTimestampLink(segStartSec, segment.id)}
                        >
                          {copiedId === segment.id ? (
                            <><Check className="w-3 h-3 text-emerald-400" /> Copied</>
                          ) : (
                            <><LinkIcon className="w-3 h-3" /> Copy Link</>
                          )}
                        </Button>
                      </div>

                      <p className={`text-sm leading-relaxed transition-colors ${
                        isActive ? 'text-[var(--color-primary)] font-normal' : 'text-[var(--color-secondary)] group-hover:text-[#cbd5e1]'
                      }`}>
                        {searchFilter.trim() ? (
                          highlightText(segment.text, searchFilter)
                        ) : (
                          segment.text
                        )}
                      </p>
                    </div>
                  </div>
                );
              })}
              <div className="h-28"></div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}

function highlightText(text: string, query: string) {
  if (!query) return text;
  const parts = text.split(new RegExp(`(${query})`, 'gi'));
  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <span key={i} className="bg-amber-400/20 text-amber-300 font-semibold px-0.5 rounded">
            {part}
          </span>
        ) : (
          part
        )
      )}
    </>
  );
}

export default function TranscriptExplorerPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  
  return (
    <Suspense fallback={
      <div className="flex h-full items-center justify-center bg-[var(--color-background)]">
        <div className="flex items-center gap-3 text-[var(--color-secondary)]">
          <div className="w-4 h-4 border-2 border-[var(--color-secondary)] border-t-[var(--color-accent)] rounded-full animate-spin"></div>
          <span className="text-sm font-medium font-mono">Initializing Temporal Engine...</span>
        </div>
      </div>
    }>
      <PlayerContent id={id} />
    </Suspense>
  );
}
