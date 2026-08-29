"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Sparkles, 
  Cpu, 
  Layers, 
  FileCheck, 
  Loader2, 
  AlertCircle, 
  RefreshCw, 
  Check
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Modal } from '@/components/ui/modal';
import { getInsights, EpisodeInsight } from '@/lib/api/episodes';

interface EpisodeInsightModalProps {
  episodeId: string | null;
  episodeTitle?: string;
  isOpen: boolean;
  onClose: () => void;
}

export function EpisodeInsightModal({
  episodeId,
  episodeTitle,
  isOpen,
  onClose,
}: EpisodeInsightModalProps) {
  const [insight, setInsight] = useState<EpisodeInsight | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const fetchInsights = useCallback(async () => {
    if (!episodeId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getInsights(episodeId);
      setInsight(data);
    } catch (err: any) {
      console.error('Failed to fetch episode insights:', err);
      setError(err.message || 'Unable to generate episode insights.');
    } finally {
      setLoading(false);
    }
  }, [episodeId]);

  useEffect(() => {
    if (isOpen && episodeId) {
      fetchInsights();
    }
  }, [isOpen, episodeId, fetchInsights]);

  const handleCopyResumeBullet = () => {
    if (insight?.resume_bullet) {
      navigator.clipboard.writeText(insight.resume_bullet);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Technical Episode Intelligence"
      description={episodeTitle || "AI-synthesized architectural blueprint and targeted competencies"}
      className="max-w-2xl"
      footer={
        <div className="flex items-center justify-between w-full">
          <div className="text-[11px] text-[var(--color-muted)] font-mono">
            {insight ? "Synthesized via Whisper Large & pgvector" : ""}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={onClose} className="h-8 text-xs">
              Close
            </Button>
            {error && (
              <Button variant="accent" size="sm" onClick={fetchInsights} className="h-8 text-xs gap-1.5">
                <RefreshCw className="w-3 h-3" /> Retry
              </Button>
            )}
          </div>
        </div>
      }
    >
      <div className="py-2">
        {loading ? (
          <div className="py-14 flex flex-col items-center justify-center text-center space-y-3">
            <div className="w-10 h-10 rounded-full bg-[var(--color-accent-subtle)] flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-[var(--color-accent)] animate-spin" />
            </div>
            <p className="text-xs font-semibold text-[var(--color-primary)]">
              Synthesizing Technical Blueprint...
            </p>
            <p className="text-[11px] text-[var(--color-muted)] max-w-xs font-mono">
              Extracting domain competencies, architecture patterns, and stack components.
            </p>
          </div>
        ) : error ? (
          <div className="py-10 flex flex-col items-center justify-center text-center space-y-3">
            <div className="w-10 h-10 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
              <AlertCircle className="w-5 h-5" />
            </div>
            <h3 className="text-xs font-semibold text-rose-400">
              Unable to generate episode insights.
            </h3>
            <p className="text-[11px] text-[var(--color-muted)] max-w-sm">
              The AI service could not analyze this episode transcript. Please retry.
            </p>
            <Button variant="outline" size="sm" onClick={fetchInsights} className="gap-1.5 text-xs h-8">
              <RefreshCw className="w-3 h-3" /> Retry
            </Button>
          </div>
        ) : insight ? (
          <div className="space-y-4 max-h-[65vh] overflow-y-auto pr-1">
            
            {/* SECTION 1: OVERVIEW & TARGET COMPETENCIES */}
            <div className="space-y-2.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-3.5 h-3.5 text-[var(--color-accent)]" />
                <h3 className="text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider font-mono">
                  Overview &amp; Target Competencies
                </h3>
              </div>
              <p className="text-xs sm:text-sm leading-relaxed text-[var(--color-primary)]">
                {insight.overview || "No overview available for this episode."}
              </p>
              {insight.competencies && insight.competencies.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {insight.competencies.map((comp, i) => (
                    <span key={i} className="text-[11px] font-medium font-mono bg-[var(--color-surface-elevated)] border border-[var(--color-border)] text-[var(--color-secondary)] px-2 py-0.5 rounded">
                      {comp}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* SECTION 2: CORE TECHNOLOGY STACK */}
            <div className="space-y-2.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Cpu className="w-3.5 h-3.5 text-emerald-400" />
                <h3 className="text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider font-mono">
                  Core Technology Stack
                </h3>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {insight.technologies && insight.technologies.length > 0 ? (
                  insight.technologies.map((tech, i) => (
                    <span 
                      key={i} 
                      className="px-2.5 py-0.5 bg-[var(--color-surface-elevated)] border border-[var(--color-border)] rounded text-xs font-mono text-emerald-300 font-medium"
                    >
                      {tech}
                    </span>
                  ))
                ) : (
                  <p className="text-xs text-[var(--color-muted)]">No technology items extracted.</p>
                )}
              </div>
            </div>

            {/* SECTION 3: ARCHITECTURAL BLUEPRINT */}
            <div className="space-y-2.5 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
              <div className="flex items-center gap-2">
                <Layers className="w-3.5 h-3.5 text-indigo-400" />
                <h3 className="text-[11px] font-bold text-[var(--color-muted)] uppercase tracking-wider font-mono">
                  Architectural Blueprint
                </h3>
              </div>
              <ul className="space-y-2 text-xs sm:text-sm text-[var(--color-primary)]">
                {insight.architecture && insight.architecture.length > 0 ? (
                  insight.architecture.map((arch, i) => (
                    <li key={i} className="flex items-start gap-2.5">
                      <span className="w-4 h-4 rounded-full bg-[var(--color-accent-subtle)] text-[var(--color-accent-hover)] text-[10px] font-bold font-mono flex items-center justify-center shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <span className="leading-relaxed">{arch}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-xs text-[var(--color-muted)]">No architecture blueprint generated.</li>
                )}
              </ul>
            </div>

            {/* SECTION 4: RESUME TRANSFORMATION */}
            {insight.resume_bullet && (
              <div className="space-y-2 bg-indigo-950/20 border border-indigo-500/30 rounded-lg p-4 relative">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileCheck className="w-3.5 h-3.5 text-[var(--color-accent)]" />
                    <h3 className="text-[11px] font-bold text-[var(--color-accent)] uppercase tracking-wider font-mono">
                      Resume Impact Transformation
                    </h3>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={handleCopyResumeBullet} 
                    className="h-6 px-2 text-[11px] gap-1 text-[var(--color-secondary)] hover:text-[var(--color-primary)]"
                  >
                    {copied ? (
                      <><Check className="w-3 h-3 text-emerald-400" /> Copied</>
                    ) : (
                      "Copy Bullet"
                    )}
                  </Button>
                </div>
                <p className="text-xs sm:text-sm italic leading-relaxed text-[var(--color-primary)] border-l-2 border-[var(--color-accent)] pl-2.5">
                  &quot;{insight.resume_bullet}&quot;
                </p>
              </div>
            )}

          </div>
        ) : null}
      </div>
    </Modal>
  );
}
