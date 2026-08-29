"use client";

import React, { useRef, useMemo, useState, useEffect } from 'react';
import { TranscriptSegment, Speaker } from '@/lib/api/episodes';
import { Sparkles } from 'lucide-react';

interface ConnectedWaveformTimelineProps {
  currentTime: number;
  totalDuration: number;
  segments: TranscriptSegment[];
  speakers: Speaker[];
  searchMatches?: number[]; // array of timestamp seconds matching current search
  onSeek: (seconds: number) => void;
  isPlaying: boolean;
}

export function ConnectedWaveformTimeline({
  currentTime,
  totalDuration,
  segments,
  speakers,
  searchMatches = [],
  onSeek,
  isPlaying,
}: ConnectedWaveformTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoverTime, setHoverTime] = useState<number | null>(null);
  const [hoverX, setHoverX] = useState<number | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Generate deterministic audio amplitude bars (120 bars)
  const barCount = 120;
  const waveformBars = useMemo(() => {
    const bars: { height: number; speakerColor: string; startTime: number; endTime: number }[] = [];
    
    for (let i = 0; i < barCount; i++) {
      const timeAtBar = (i / barCount) * (totalDuration || 2722);
      
      // Find segment at this timestamp
      const seg = segments.find(s => {
        const start = s.startSec !== undefined ? s.startSec : s.start_time;
        const end = s.end_time || (start + 20);
        return timeAtBar >= start && timeAtBar <= end;
      });

      let speakerColor = 'rgba(99, 102, 241, 0.4)'; // default indigo
      if (seg) {
        const speakerName = seg.speaker?.display_name || seg.speaker?.label || '';
        if (speakerName.includes('Priya') || seg.speaker_id?.includes('1')) {
          speakerColor = 'rgba(52, 211, 153, 0.7)'; // emerald
        } else if (speakerName.includes('Alex') || seg.speaker_id?.includes('2')) {
          speakerColor = 'rgba(99, 102, 241, 0.7)'; // indigo
        } else if (speakerName.includes('Daniel') || seg.speaker_id?.includes('3')) {
          speakerColor = 'rgba(251, 191, 36, 0.7)'; // amber
        } else {
          speakerColor = 'rgba(56, 189, 248, 0.7)'; // sky
        }
      }

      // Pseudo-random but deterministic amplitude profile
      const seed = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
      const rand = seed - Math.floor(seed);
      // Create organic speech patterns with occasional pauses
      const isPause = i % 18 === 0 || i % 29 === 0;
      const height = isPause ? 15 : Math.floor(25 + rand * 65);

      bars.push({
        height,
        speakerColor,
        startTime: timeAtBar,
        endTime: ((i + 1) / barCount) * (totalDuration || 2722)
      });
    }
    return bars;
  }, [segments, totalDuration]);

  const progressPercent = totalDuration > 0 ? Math.min((currentTime / totalDuration) * 100, 100) : 0;

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const pct = x / rect.width;
    const time = pct * totalDuration;
    setHoverTime(time);
    setHoverX(x);

    if (isDragging) {
      onSeek(time);
    }
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    setIsDragging(true);
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const time = (x / rect.width) * totalDuration;
    onSeek(time);
  };

  const handlePointerUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    const handleGlobalUp = () => setIsDragging(false);
    window.addEventListener('pointerup', handleGlobalUp);
    return () => window.removeEventListener('pointerup', handleGlobalUp);
  }, []);

  const formatMinSec = (secs: number) => {
    if (isNaN(secs) || secs < 0) return '00:00';
    const total = Math.floor(secs);
    const m = Math.floor(total / 60);
    const s = total % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-2 w-full select-none">
      {/* Waveform Container */}
      <div 
        ref={containerRef}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerLeave={() => {
          if (!isDragging) {
            setHoverTime(null);
            setHoverX(null);
          }
        }}
        className="relative h-14 w-full bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded-lg px-2 flex items-center cursor-pointer overflow-hidden group transition-colors hover:border-[var(--color-border-subtle)]"
      >
        {/* Background Amplitude Bars */}
        <div className="absolute inset-0 px-3 flex items-center justify-between gap-[2px]">
          {waveformBars.map((bar, idx) => {
            const barProgress = (idx / barCount) * 100;
            const isPlayed = barProgress <= progressPercent;
            
            return (
              <div
                key={idx}
                className="flex-1 flex flex-col items-center justify-center transition-all duration-75"
                style={{ height: '100%' }}
              >
                <div
                  className={`w-full rounded-full transition-all duration-150 ${
                    isPlayed 
                      ? 'opacity-90 scale-y-100' 
                      : 'opacity-25 hover:opacity-50 scale-y-90'
                  }`}
                  style={{
                    height: `${bar.height}%`,
                    backgroundColor: isPlayed ? bar.speakerColor : 'rgba(148, 163, 184, 0.4)',
                    boxShadow: isPlayed ? `0 0 6px ${bar.speakerColor}` : 'none'
                  }}
                />
              </div>
            );
          })}
        </div>

        {/* Speaker Track Base Strip at bottom of waveform */}
        <div className="absolute bottom-0 left-0 right-0 h-1 flex opacity-60">
          {waveformBars.map((bar, idx) => (
            <div 
              key={idx} 
              className="flex-1 h-full"
              style={{ backgroundColor: bar.speakerColor }}
            />
          ))}
        </div>

        {/* Search Match Indicators on the Timeline */}
        {searchMatches.map((matchSec, idx) => {
          const matchPct = totalDuration > 0 ? (matchSec / totalDuration) * 100 : 0;
          return (
            <div
              key={idx}
              className="absolute top-1 bottom-1 w-1 bg-amber-400 rounded-full shadow-xs shadow-amber-400/80 pointer-events-none z-10 animate-pulse"
              style={{ left: `${matchPct}%` }}
              title={`Match at ${formatMinSec(matchSec)}`}
            >
              <div className="w-2 h-2 rounded-full bg-amber-400 -translate-x-[2px] -translate-y-1" />
            </div>
          );
        })}

        {/* Active Playhead Line with Glow */}
        <div 
          className="absolute top-0 bottom-0 w-[2px] bg-white shadow-[0_0_12px_rgba(255,255,255,0.9)] z-20 pointer-events-none transition-all duration-75"
          style={{ left: `${progressPercent}%` }}
        >
          <div className="w-2.5 h-2.5 rounded-full bg-white shadow-md absolute top-0 -translate-x-[4px] -translate-y-[2px]" />
        </div>

        {/* Hover Scrubbing Cursor & Tooltip */}
        {hoverX !== null && hoverTime !== null && (
          <div 
            className="absolute top-0 bottom-0 w-[1px] bg-indigo-400/80 pointer-events-none z-30"
            style={{ left: `${hoverX}px` }}
          >
            <div className="absolute -top-7 -translate-x-1/2 bg-[var(--color-surface)] border border-[var(--color-border)] text-white text-[10px] font-mono px-1.5 py-0.5 rounded shadow-lg whitespace-nowrap">
              {formatMinSec(hoverTime)}
            </div>
          </div>
        )}
      </div>

      {/* Speaker Legend Bar underneath */}
      <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-muted)] px-1">
        <div className="flex items-center gap-3">
          <span className="text-[10px] uppercase font-semibold text-[var(--color-muted)]">Speakers:</span>
          {speakers.map((s, idx) => {
            const colors = ['bg-emerald-400 text-emerald-400', 'bg-indigo-400 text-indigo-400', 'bg-amber-400 text-amber-400', 'bg-sky-400 text-sky-400'];
            const color = colors[idx % colors.length];
            return (
              <div key={s.id || idx} className="flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${color.split(' ')[0]}`} />
                <span className="text-[11px] text-[var(--color-secondary)]">{s.display_name || s.label}</span>
              </div>
            );
          })}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[var(--color-primary)] font-semibold">{formatMinSec(currentTime)}</span>
          <span>/</span>
          <span>{formatMinSec(totalDuration)}</span>
        </div>
      </div>
    </div>
  );
}
